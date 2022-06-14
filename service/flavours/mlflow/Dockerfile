FROM continuumio/miniconda3:latest

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

RUN apt-get update && apt-get install -y build-essential cmake
# create env
ENV CONDA_ENV chassis-env

COPY flavours/${MODEL_CLASS}/${MODEL_DIR}/conda.yaml ./conda.yaml
RUN conda env create --name $CONDA_ENV --file ./conda.yaml

COPY flavours/${MODEL_CLASS}/${MODEL_DIR} ./model/${MODEL_NAME}
COPY flavours/${MODEL_CLASS}/entrypoint.sh /

ENV MODEL_DIR ./model/${MODEL_NAME}
ENV INTERFACE ${INTERFACE}

SHELL ["/bin/bash", "-c"]

COPY flavours/${MODEL_CLASS}/requirements.txt .
RUN source activate $CONDA_ENV && pip install -r requirements.txt

COPY flavours/${MODEL_CLASS}/app.py .
COPY flavours/${MODEL_CLASS}/interfaces ./interfaces

# Overwrite the default one.
COPY ${MODZY_METADATA_PATH} ./interfaces/modzy/asset_bundle/0.1.0/model.yaml

ENTRYPOINT ["/bin/bash", "-c", "source activate $CONDA_ENV && python app.py"]
