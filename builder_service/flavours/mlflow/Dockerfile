# The context is /workspace, which contains:
# - proxy
# - flavours
#   - sklearn
#   - pytorch
#   - xgboost

FROM continuumio/miniconda3:4.9.2

# At the moment it's always model.
ARG MODEL_DIR
# Could be: whatever the user specifies for the name of the model.
ARG MODEL_NAME
# The model filename.
ARG MODEL_FILENAME
# Could be: sklearn, pytorch, tf.
ARG MODEL_CLASS
# E.g.: 0.24.1
ARG MODULE_VERSION

RUN pip install mlflow

COPY flavours/${MODEL_CLASS}/${MODEL_DIR} /model/${MODEL_NAME}

COPY flavours/${MODEL_CLASS}/entrypoint.sh /

ENV MODEL_CLASS ${MODEL_CLASS}

ENV MODEL_NAME ${MODEL_NAME}
ENV MODEL_DIR /model/${MODEL_NAME}

ENTRYPOINT ["mlflow"]

CMD ["models", "serve", "-m", "$MODEL_DIR"]
