# The context is /workspace, which contains:
# - flavours
#   - mlflow

FROM continuumio/miniconda3:4.9.2-alpine AS build

# At the moment it's always model.
ARG MODEL_DIR
# Should be: mlflow.
ARG MODEL_CLASS

WORKDIR /app

COPY flavours/${MODEL_CLASS}/${MODEL_DIR}/conda.yaml ./conda.yaml

ENV CONDA_ENV containerizer-env

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

WORKDIR /app

COPY flavours/${MODEL_CLASS}/${MODEL_DIR} ./model/${MODEL_NAME}
COPY flavours/${MODEL_CLASS}/entrypoint.sh /

ENV MODEL_DIR ./model/${MODEL_NAME}

COPY --from=build /venv /venv

SHELL ["/bin/bash", "-c"]

# Run conda-unpack to re-create symlinks and set everything up.
RUN source /venv/bin/activate && conda-unpack

ENTRYPOINT ["/entrypoint.sh"]

CMD mlflow models serve --no-conda --model-uri $MODEL_DIR
