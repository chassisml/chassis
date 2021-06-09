#!/bin/bash

python -m xgbserver --model_dir /model/${MODEL_NAME} --model_name ${MODEL_NAME} --http_port ${KFSERVING_PORT} &

wait-for-it.sh localhost ${KFSERVING_PORT} proxy
