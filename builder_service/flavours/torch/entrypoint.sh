#!/bin/bash

python -m pytorchserver --model_dir /model/${MODEL_NAME} --model_name ${MODEL_NAME} --http_port ${KFSERVING_PORT} --model_class_name Net &

wait-for-it.sh localhost ${KFSERVING_PORT} proxy
