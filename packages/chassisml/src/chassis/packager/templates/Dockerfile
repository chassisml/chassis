FROM balenalib/{{ arch }}-debian-python:{{ python_version }}-build AS build

{% if needs_cross_compiling -%}
RUN [ "cross-build-start" ]
{%- endif %}

# Copy requirements file and pip install.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

{% if needs_cross_compiling -%}
RUN [ "cross-build-end" ]
{%- endif %}

FROM balenalib/{{ arch }}-debian-python:{{ python_version }}-run

# Currently always "model"
ARG MODEL_DIR
ARG MODEL_NAME
ARG MODEL_CLASS
ARG INTERFACE
ARG MODZY_METADATA_PATH

# OMI annotations
LABEL ml.openmodel.interfaces=["${INTERFACE}"]
LABEL ml.openmodel.model_name="${MODEL_NAME}"
LABEL ml.openmodel.protocols=[["v2"]]
LABEL ml.openmodel.port="45000"

WORKDIR /app

COPY --from=build /usr/local/lib/python{{ python_version }}/site-packages /usr/local/lib/python{{ python_version }}/site-packages

# Copy the entrypoint file and gRPC server implementation.
COPY entrypoint.py ./

# Copy app folder.
COPY chassis chassis

# Copy the app and data
COPY data data

CMD ["python3", "entrypoint.py"]