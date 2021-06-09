FROM tensorflow/serving

ARG MODEL_DIR
ARG MODEL_NAME

ENV MODEL_NAME ${MODEL_NAME}
RUN echo $MODEL_NAME

COPY ${MODEL_DIR} /model/${MODEL_NAME}

ENV MODEL_DIR /model/${MODEL_NAME}

RUN echo $MODEL_DIR

ENTRYPOINT tensorflow_model_server --model_name=${MODEL_NAME} --model_base_path=${MODEL_DIR}
