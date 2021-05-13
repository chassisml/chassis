package common

import (
	"fmt"
	"net/http"
	"net/url"
	"os"
	"path"

	"github.com/gin-gonic/gin"
)

// This env variable is populated by the
// Kaniko service when the image is built.
var modelName string = os.Getenv("MODEL_NAME")
var kfservingPort string = os.Getenv("KFSERVING_PORT")

// The host won't change since KFServing is running
// it's model service in the same container as the proxy.
var baseUrl string = fmt.Sprintf("http://127.0.0.1:%s/v2/models/", kfservingPort)

// Returns the baseUrl + the route, that could be status, infer...
func BuildUrlRoute(route string) string {
	u, err := url.Parse(baseUrl)

	if err != nil {
		panic("invalid url")
	}

	u.Path = path.Join(u.Path, fmt.Sprintf("/%s/%s", modelName, route))

	return u.String()
}

func FormatResponse(code int, status string, err error) gin.H {
	var message string

	if message = status; err != nil && status == "" {
		message = err.Error()
	}

	return gin.H{
		"statusCode": code,
		"status":     http.StatusText(code),
		"message":    message,
	}
}
