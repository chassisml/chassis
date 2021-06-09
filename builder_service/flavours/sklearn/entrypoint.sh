#!/bin/bash

python -m sklearnserver --model_dir /model/${MODEL_NAME} --model_name ${MODEL_NAME} --http_port ${KFSERVING_PORT} &

wait-for-it.sh localhost ${KFSERVING_PORT} proxy
