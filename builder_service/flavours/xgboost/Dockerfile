# The context is /workspace, which contains:
# - proxy
# - flavours
#   - sklearn
#   - pytorch
#   - xgboost

FROM gcr.io/kfserving/xgbserver

# At the moment it's always model.
ARG MODEL_DIR
# Could be: whatever the user specifies for the name of the model.
ARG MODEL_NAME
# Could be: sklearn, pytorch, tf.
ARG MODEL_CLASS
# Injected by the builder service.
ARG KFSERVING_PORT
# Injected by the builder service.
ARG PROXY_PORT
# E.g.: 1.3.3
ARG MODULE_VERSION

# For some reason "pip install" fails when running it with Kaniko
# Reinstalling pip before running that command seems to fix the bug.
RUN apt update && apt install -y curl
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py

# Install particular version of xgboost.
RUN pip install xgboost==${MODULE_VERSION}

COPY proxy/out/proxy-linux-amd64 /usr/local/bin/proxy
COPY proxy/scripts/wait-for-it.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/proxy

COPY flavours/${MODEL_CLASS}/example_inputs /example_inputs

COPY flavours/${MODEL_CLASS}/${MODEL_DIR} /model/${MODEL_NAME}

COPY flavours/${MODEL_CLASS}/entrypoint.sh /

ENV MODEL_NAME ${MODEL_NAME}
ENV MODEL_DIR /model/${MODEL_NAME}

ENV KFSERVING_PORT ${KFSERVING_PORT}
ENV PROXY_PORT ${PROXY_PORT}

ENTRYPOINT ["/entrypoint.sh"]
