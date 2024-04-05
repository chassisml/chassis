FROM python:{{ python_version }}-slim-bookworm AS pip-compile

RUN pip install --no-cache-dir pip-tools

{% if cuda_version -%}
ENV GPU=true
{%- else -%}
ENV GPU=false
{%- endif %}

COPY chassis/scripts scripts

COPY requirements.in .
RUN python -m piptools compile -q -o requirements.txt requirements.in

RUN python scripts/normalize_requirements.py

# ------------------------------------------------------------------------------

#FROM python:{{ python_version }}-slim-bookworm \
FROM ghcr.io/chassisml/openmodel-server-python-3.11:0.0.1

{{ apt_packages }}

ENV MODEL_PORT=9090
ENV METRICS_PORT=8080

#ENV MODEL_METADATA_PATH=/app/data/model_info
#ENV MODEL_IDENTIFIER
#ENV MODEL_VERSION

ENV LOG_LEVEL=info
ENV TELEMETRY_ENABLED=false
ENV TELEMETRY_ENDPOINT=""

ENV PYTHONPATH=/app

WORKDIR /app

{% for key,value in labels.items() -%}
LABEL {{key}}="{{value}}"
{% endfor %}


# Copy requirements file and pip install.
COPY --from=pip-compile requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app folder.
COPY chassis chassis

# Copy the app and data
COPY data data
