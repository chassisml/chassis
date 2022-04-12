# The context is /workspace, which contains:
# - flavours
#   - mlflow

FROM continuumio/miniconda3:4.9.2-alpine AS build

# At the moment it's always model.
ARG MODEL_DIR
# Should be: mlflow.
ARG MODEL_CLASS
# Interface.
ARG INTERFACE
# This is the model.yaml file.
ARG MODZY_METADATA_PATH

WORKDIR /app

COPY flavours/${MODEL_CLASS}/${MODEL_DIR}/conda.yaml ./conda.yaml

ENV CONDA_ENV chassis-env

RUN apk update \
    && apk --no-cache --update add build-base 
# Create conda environment.
RUN conda env create --name $CONDA_ENV --file ./conda.yaml
# Install conda-pack.
RUN conda install -c conda-forge conda-pack
# Use conda-pack to create a standalone enviornment in /venv.
RUN conda-pack -n $CONDA_ENV -o /tmp/env.tar && \
  mkdir /venv && tar xf /tmp/env.tar -C /venv

####################################

FROM debian:buster-slim AS runtime

# At the moment it's always model.
ARG MODEL_DIR
# Could be: whatever the user specifies for the name of the model.
ARG MODEL_NAME
# Should be: mlflow.
ARG MODEL_CLASS
# Interface.
ARG INTERFACE
# This is the model.yaml file.
ARG MODZY_METADATA_PATH

#OMI Annotations

LABEL ml.openmodel.interfaces=["${INTERFACE}"]
LABEL ml.openml.model_name="${MODEL_NAME}"
LABEL ml.openmodel.protocols=[["v2"]]
LABEL ml.openmodel.port="45000"


WORKDIR /app

COPY flavours/${MODEL_CLASS}/${MODEL_DIR} ./model/${MODEL_NAME}
COPY flavours/${MODEL_CLASS}/entrypoint.sh /

ENV MODEL_DIR ./model/${MODEL_NAME}
ENV INTERFACE ${INTERFACE}

COPY --from=build /venv /venv

SHELL ["/bin/bash", "-c"]

# Run conda-unpack to re-create symlinks and set everything up.
RUN source /venv/bin/activate && conda-unpack

RUN apt-get update && apt-get install -y build-essential
COPY flavours/${MODEL_CLASS}/requirements.txt .
RUN source /venv/bin/activate && pip install -r requirements.txt

COPY flavours/${MODEL_CLASS}/app.py .
COPY flavours/${MODEL_CLASS}/interfaces ./interfaces

# Overwrite the default one.
COPY ${MODZY_METADATA_PATH} ./interfaces/modzy/asset_bundle/0.1.0/model.yaml

ENTRYPOINT ["/entrypoint.sh"]

CMD ["python", "app.py"]
