#!/usr/bin/env sh

PACKAGE_ROOT="$(pwd)/../.."
CONTAINER_NAME="model-template"
CONTAINER_PORT=45000

# Integration test that runs the containerized server, and tests it from a local client
docker build --rm --label user=test-user -t example-model "${PACKAGE_ROOT}"
CONTAINER_ID=$(docker run --rm --label user=test-user --name "${CONTAINER_NAME}" -d -p "${CONTAINER_PORT}":"${CONTAINER_PORT}" example-model)
poetry run python "${PACKAGE_ROOT}/grpc_model/src/model_client.py"
docker kill "${CONTAINER_ID}"

