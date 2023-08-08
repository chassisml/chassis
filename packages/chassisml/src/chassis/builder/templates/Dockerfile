{%- if cuda_version -%}
FROM nvidia/cuda:{{ cuda_version }}-runtime-ubuntu20.04

# Install Python
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
{%- else -%}
FROM python:{{ python_version }}-slim-bullseye
{%- endif %}

{{ apt_packages }}

WORKDIR /app

# Copy requirements file and pip install.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint file and gRPC server implementation.
COPY entrypoint.py ./

# Copy app folder.
COPY chassis chassis

# Copy the app and data
COPY data data

CMD ["python3", "entrypoint.py"]