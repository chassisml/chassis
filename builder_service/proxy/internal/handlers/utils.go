package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"image/jpeg"
	_ "image/png"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path"
	"strings"

	"proxy/internal/common"
)

var imageType string = os.Getenv("IMAGE_TYPE")

// This is used to store all the KFServing routes.
var route = map[string]string {
	"status": common.BuildUrlRoute("status"),
	"infer":  common.BuildUrlRoute("infer"),
}

// Json coming from the run endpoint will fit this
// struct, that accomplish with the Modzy API requirements.
type InferBody struct {
	Type   string `json:"type" binding:"required"`
	Input  string `json:"input" binding:"required"`
	Output string `json:"output" binding:"required"`
}

func readFileAndMime(filePath string, file os.FileInfo) string {
	fileName := file.Name()

	// Avoid directories and hidden files.
	if !file.IsDir() && !strings.HasPrefix(fileName, ".") {
		buf, _ := ioutil.ReadFile(filePath)
		contentType := getMimeType(filePath, &buf)

		return contentType
	}

	return ""
}

func getMimeType(fileName string, buf *[]byte) string {
	var contentType string
	contentType = http.DetectContentType(*buf)
	// Keep only first result since it's the type of object:
	// - image/jpeg, image/png -> will result in image.
	contentType = strings.Split(contentType, "/")[0]

	// Text type has no subcategory, so guess
	// it from the extension of the file.
	if contentType == "text" {
		fileNameSplitted := strings.Split(fileName, ".")

		return fileNameSplitted[len(fileNameSplitted)-1]
	}

	return contentType
}

func rgbaToGrayPixel(r uint32, g uint32, b uint32, a uint32) uint8 {
	lum := 0.299*float64(r) + 0.587*float64(g) + 0.114*float64(b)

	return color.Gray{uint8(lum / 256)}.Y
}

func rgbaToRGBPixel(r uint32, g uint32, b uint32, a uint32) []int {
	lum := []int{int(r / 257), int(g / 257), int(b / 257)}

	return lum
}

func getInstanceFromGreyImage(height int, width int, img image.Image) map[string][][]int {
	var pixels []int

	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			p := int(rgbaToGrayPixel(img.At(x, y).RGBA()))
			pixels = append(pixels, p)
		}
	}

	values := map[string][][]int{"instances": {pixels}}

	return values
}

func getInstanceFromRGBImage(height int, width int, img image.Image) map[string][][][]int {
	var pixels [][]int

	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			p := rgbaToRGBPixel(img.At(x, y).RGBA())
			pixels = append(pixels, p)
		}
	}

	values := map[string][][][]int{"instances": {pixels}}

	return values
}

func getJSONBuffer(filePath string) []byte {
	// Assume that the json is already a map with the key "instances".
	content, _ := ioutil.ReadFile(filePath)

	return content
}

// Reads the content of the files depending on its
// type and requests against the KFServing infer endpoint.
func makePostRequest(contentType string, filePath string) []byte {
	var buf []byte

	if contentType == "image" {
		var values interface{}

		existingImageFile, _ := os.Open(filePath)
		defer existingImageFile.Close()

		img, _ := jpeg.Decode(existingImageFile)

		bounds := img.Bounds()
		width, height := bounds.Max.X, bounds.Max.Y

		if imageType == "color" {
			values = getInstanceFromRGBImage(height, width, img)
		} else {
			values = getInstanceFromGreyImage(height, width, img)
		}

		buf, _ = json.Marshal(values)
	} else if contentType == "json" {
		buf = getJSONBuffer(filePath)
	}

	resp, err := http.Post(route["infer"], "application/json", bytes.NewBuffer(buf))

	if err != nil || resp.StatusCode != http.StatusOK {
		log.Print(err, resp.Status)

		return nil
	}

	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)

	return body
}

func makeInferences(inputDir string, outputDir string) (string, error) {
	// Check that input directory exists in the filesystem.
	if _, err := os.Stat(inputDir); os.IsNotExist(err) {
		return "", fmt.Errorf("Input directory %s doesn't exist", inputDir)
	}

	// Create the output directory and ignore
	// errors (just in case it already exists).
	_ = os.MkdirAll(outputDir, 0755)

	var err error

	files, err := ioutil.ReadDir(inputDir)

	if err != nil {
		log.Fatal(err)
	}

	var processedFiles []string
	var unprocessedFiles []string

	var contentType string

	// Iterate over every file in the input directory.
	for _, file := range files {
		var fileName string = file.Name()
		var filePath string = path.Join(inputDir, fileName)

		// Add file to unprocessed files if it's not supported.
		if contentType = readFileAndMime(filePath, file); len(contentType) == 0 {
			log.Print("File not processed: ", fileName)
			unprocessedFiles = append(unprocessedFiles, fileName)
			continue
		}

		var bodyBuf []byte

		log.Print("Processing file: ", filePath)

		// Add file to unprocessed files if there is any error making the request.
		if bodyBuf = makePostRequest(contentType, filePath); bodyBuf == nil {
			log.Print("File not processed: ", fileName)
			unprocessedFiles = append(unprocessedFiles, fileName)
			continue
		}

		// Add file to unprocessed files if there is any error saving the result to filesystem.
		if err := ioutil.WriteFile(path.Join(outputDir, fileName+".json"), bodyBuf, 0644); err != nil {
			log.Print(err)
			unprocessedFiles = append(unprocessedFiles, fileName)
			continue
		}

		log.Print("File processed: ", fileName)
		processedFiles = append(processedFiles, fileName)
	}

	if err = nil; len(unprocessedFiles) > 0 {
		err = fmt.Errorf("Unprocessed files: %s", strings.Join(unprocessedFiles, ", "))
	}
	return strings.Join(processedFiles, ", "), err
}
