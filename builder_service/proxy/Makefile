GO_FILES := $(shell find . -type f -name '*.go' -not -path "./vendor/*")
PROXY_PACKAGE := cmd/proxy/main.go

out/proxy: $(GO_FILES)
	go build -o $@ $(PROXY_PACKAGE)

run:
	go run $(PROXY_PACKAGE)

dockerbuild:
	docker run --rm --name gocompiler -v $(shell pwd):/proxy -w /proxy golang:1.14 make
