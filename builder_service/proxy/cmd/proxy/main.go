package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"proxy/internal/handlers"
	"proxy/internal/common"

	"github.com/gin-gonic/gin"
)

var proxyPort string = os.Getenv("PROXY_PORT")

func main() {
	quit := make(chan struct{})

	r := gin.Default()

	// Handlers for every KFServing routes.
	// This is just a proxy between Modzy and KFServing endpoints.
	r.GET("/", handlers.Alive)
	r.GET("/status", handlers.GetStatus)
	r.POST("/run", handlers.Infer)
	r.POST("/shutdown", handlers.Shutdown(quit))

	// KFServing routes.
	v2 := r.Group("/v2")
	{
		v2.GET("/health/live", handlers.Alive)

		v2Models := v2.Group("/models")
		{
			v2Models.GET("/",	handlers.KFServingRedirect)
			v2Models.GET(common.BuildUrlRoute("status", "/"), handlers.KFServingRedirect)
			v2Models.POST(common.BuildUrlRoute("infer", "/"), handlers.KFServingRedirect)
			v2Models.GET(common.BuildUrlRoute("explain", "/"), handlers.KFServingRedirect)
		}
	}

	srv := &http.Server{
		Addr:    fmt.Sprintf(":%s", proxyPort),
		Handler: r,
	}

	// Initializing the server in a goroutine so that
	// it won't block the graceful shutdown handling below.
	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %s\n", err)
		}
	}()

	// Block on channel.
	<-quit

	// The timeout is the maximum allowed for the current requests to complete.
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)

	defer cancel()

	log.Println("Shutting down server ...")

	// Shutdown cleanly.
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("Server forced to shutdown:", err)
	}
}
