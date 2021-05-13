# Please consult the README if you need help in selecting a base image
FROM scratch
FROM python:3 as application

# Create the application working directory
WORKDIR /opt/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpomp-dev

# Install Python requirements
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# ensure the entrypoint is executable
# NOTE: This is a defensive step in the case that entrypoint.sh is not already executable
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# create a system group and user with no login shell and access restricted
# to the application

# TODO: These were causing issues on the platform due to permissions
# RUN groupadd --system modzy-group && \
#     useradd --system --shell /bin/false --group modzy-group modzy-user && \
#     chown --recursive modzy-user:modzy-group /opt/app
# USER modzy-user

# copy application files into the container image
# NOTE: to avoid overly large container size, only copy the files actually needed by
#       explicitly specifying the needed files with the `COPY` command or adjusting
#       the `.dockerignore` file to ignore unneeded files
COPY model_lib ./model_lib
COPY app.py gunicorn.conf.py model.yaml ./
COPY flask_psc_model ./flask_psc_model

# environment variable to specify model server port
ENV PSC_MODEL_PORT 45000

ARG CIRCLE_REPOSITORY_URL
LABEL com.modzy.git.source="${CIRCLE_REPOSITORY_URL}"

ENTRYPOINT ["./entrypoint.sh"]
