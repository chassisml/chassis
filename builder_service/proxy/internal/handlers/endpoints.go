package handlers

import (
	"log"
	"net/url"
	"net/http"
	"net/http/httputil"

	"proxy/internal/common"

	"github.com/gin-gonic/gin"
)

func Alive(c *gin.Context) {
	c.String(http.StatusOK, "Alive!")
}

func GetStatus(c *gin.Context) {
	// Just make a request against KFServing status endpoint.
	resp, err := http.Get(route["status"])

	if err != nil {
		log.Print(err)

		c.AbortWithStatusJSON(
			http.StatusInternalServerError,
			common.FormatResponse(http.StatusInternalServerError, "", err),
		)
		return
	}

	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		c.AbortWithStatusJSON(
			http.StatusInternalServerError,
			common.FormatResponse(http.StatusInternalServerError, resp.Status, nil),
		)
		return
	}

	c.JSON(
		http.StatusOK,
		common.FormatResponse(http.StatusOK, resp.Status, nil),
	)
}

func Infer(c *gin.Context) {
	var body InferBody

	// Try to decode the json from the request.
	// Also check if the json from the requests fits Modzy
	// requirements. If not, ask for the missing field.
	if err := c.ShouldBindJSON(&body); err != nil {
		log.Print(err)

		c.AbortWithStatusJSON(
			http.StatusBadRequest,
			common.FormatResponse(http.StatusBadRequest, "", err),
		)
		return
	}

	// Process files in input directory, make requests against
	// KFServing endpoint and save the results in output directory.
	processedFiles, err := makeInferences(body.Input, body.Output)

	// This means that some of the files have not been
	// processed, so return error stating which files have failed.
	if err != nil {
		c.AbortWithStatusJSON(
			http.StatusBadRequest,
			common.FormatResponse(http.StatusBadRequest, "", err),
		)
	} else {
		// All files have been processed so just the return them as a list.
		var message string = "Processed files: " + processedFiles
		c.JSON(
			http.StatusOK,
			common.FormatResponse(http.StatusOK, message, nil),
		)
	}
}

func KFServingRedirect(c *gin.Context) {
	kfservingRoute := common.BuildKFServingRedirect(c.FullPath())
	remote, err := url.Parse(kfservingRoute)

	if err != nil {
		panic(err)
	}

	proxy := httputil.NewSingleHostReverseProxy(remote)

	proxy.Director = func(req *http.Request) {
		req.Header = c.Request.Header
		req.Host = remote.Host
		req.URL.Scheme = remote.Scheme
		req.URL.Host = remote.Host
		req.URL.Path = c.FullPath()
	}

	proxy.ServeHTTP(c.Writer, c.Request)
}

func Shutdown(quit chan struct{}) func(c *gin.Context) {
	return func(c *gin.Context) {
		c.Status(http.StatusAccepted)

		// Synchronize with quit channel and shutdown gracefully.
		quit <- struct{}{}
	}
}
