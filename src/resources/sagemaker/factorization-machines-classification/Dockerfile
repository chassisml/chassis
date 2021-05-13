# Please consult the README if you need help in selecting a base image
FROM scratch
FROM python:3 as application

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      curl \
      libopenblas-dev \
      unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ensure the entrypoint is executable
# NOTE: This is a defensive step in the case that entrypoint.sh is not already executable
COPY entrypoint.sh /opt/app/
RUN chmod +x /opt/app/entrypoint.sh

# create a system group and user with no login shell and access restricted
# to the application
# RUN groupadd --system modzy-group && \
#     useradd --system --shell /bin/false --group modzy-group modzy-user && \
#     chown --recursive modzy-user:modzy-group /opt/app
# USER modzy-user

# copy application files into the container image
# NOTE: to avoid overly large container size, only copy the files actually needed by
#       explicitly specifying the needed files with the `COPY` command or adjusting
#       the `.dockerignore` file to ignore unneeded files
COPY model_lib /opt/app/model_lib
COPY app.py gunicorn.conf.py model.yaml /opt/app/
COPY flask_psc_model ./flask_psc_model

# environment variable to specify model server port
ENV PSC_MODEL_PORT 45000

WORKDIR /opt/app/model_lib/weights
RUN unzip -o /opt/app/model_lib/weights/model_algo-1 && \
    mv /opt/app/model_lib/weights/symbol.json model-symbol.json && \
    mv /opt/app/model_lib/weights/params /opt/app/model_lib/weights/model-0000.params && \
    rm /opt/app/model_lib/weights/model_algo-1

ENTRYPOINT ["/opt/app/entrypoint.sh"]
