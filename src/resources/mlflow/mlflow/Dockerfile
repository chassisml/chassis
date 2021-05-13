# This Dockerfile is used to build a container image that contains everything
# necessary to run the model application.
#
# It must define a `CMD` that starts the application server on the port
# specified by the `PSC_MODEL_PORT` environment variable.
#
# Other than for simple CPU-only models, this file will likely need to be updated
# to support different model requirements.
#
FROM scratch
FROM ubuntu:20.04

# ensure UTF-8 locale; at the moment setting "LANG=C" on Linux can break Python 3
# http://bugs.python.org/issue19846
ENV LANG=C.UTF-8 \
  # prevent Python from buffering stdin/stdout for immediate logging output
  PYTHONUNBUFFERED=1 \
  # prevent Python from writing out pyc files
  PYTHONDONTWRITEBYTECODE=1 \
  # avoid messages of apt-get install
  DEBIAN_FRONTEND=noninteractive \
  PYENV_ROOT="/.pyenv" \
  PATH="/.pyenv/bin:/.pyenv/shims:$PATH"

# install essential packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends --allow-unauthenticated \
      software-properties-common \
    && rm -rf /var/lib/apt/lists/*
  
RUN add-apt-repository ppa:deadsnakes/ppa \ 
    && apt-get update \
    && apt-get install -y --no-install-recommends --allow-unauthenticated \
    python3.6 python3-pip

#RUN git clone --depth=1 https://github.com/pyenv/pyenv.git /.pyenv && \
#    pyenv install 3.8.5 && pyenv global 3.8.5

# create the application working directory
WORKDIR /opt/app

COPY model_lib/ model_lib/
COPY model_lib/conda_to_pip.py model_lib/
COPY model_lib/weights/conda.yaml model_lib/weights/
RUN /usr/bin/python3.6 -m model_lib.conda_to_pip

# install python requirements
COPY requirements.txt requirements.txt
RUN /usr/bin/python3.6 -m pip install --no-cache-dir --upgrade pip && \
    /usr/bin/python3.6 -m pip install --no-cache-dir -r mlflow_reqs.txt && \
    /usr/bin/python3.6 -m pip install --no-cache-dir -r requirements.txt

# copy application files into the container image
# NOTE: to avoid overly large container size, only copy the files actually needed by
#       explicitely specifying the needed files with the `COPY` command or adjusting
#       the `.dockerignore` file to ignore unneeded files
COPY . ./

# ensure the entrypoint is executable
# NOTE: this isn't necessary if the entrypoint.sh script is properly marked and checked
#       into git as executable
RUN chmod +x entrypoint.sh

# environment variable to specify model server port
ENV PSC_MODEL_PORT 80

# start the application server
# NOTE: the _exec_ syntax with square brackets should always be used when defining
#       the `CMD`
CMD ["./entrypoint.sh"]
