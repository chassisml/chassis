# FROM golang:1.14 AS go_builder
FROM golang:1.14 AS go_builder

RUN apt-get install -y --no-install-recommends git gcc g++
RUN go get -u github.com/awslabs/amazon-ecr-credential-helper/...
WORKDIR /go/src/github.com/awslabs/amazon-ecr-credential-helper
RUN git checkout "v0.3.1"
ENV CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64
RUN go build -ldflags "-s -w" -installsuffix cgo -a -o /ecr-login \
    ./ecr-login/cli/docker-credential-ecr-login

WORKDIR /go/src/github.com/GoogleContainerTools/kaniko
RUN git clone https://github.com/GoogleContainerTools/kaniko.git . && \
    git checkout "v1.5.2"
RUN make

WORKDIR /go/src/modzy/proxy
COPY proxy .
RUN make

########################################################################################################################

# FROM amazoncorretto:8 AS java_builder
FROM amazoncorretto:8 AS java_builder

WORKDIR /build/
COPY . ./
RUN ./mvnw clean package -q -D skipTests

########################################################################################################################

# Copy in only the compiled service to run a lightweight application
# FROM amazoncorretto:8 AS application
FROM amazoncorretto:8 as application

# RUN apk update && apk add bash

COPY --from=go_builder /ecr-login /usr/bin/docker-credential-ecr-login
COPY --from=go_builder /go/src/github.com/GoogleContainerTools/kaniko/out/executor /usr/local/bin/kaniko
COPY --from=go_builder /go/src/github.com/GoogleContainerTools/kaniko/files/nsswitch.conf /etc/nsswitch.conf
COPY --from=go_builder /go/src/modzy/proxy/out /workspace/proxy/out
COPY --from=go_builder /go/src/modzy/proxy/scripts /workspace/proxy/scripts

RUN mkdir /kaniko

WORKDIR /kaniko/model-converter
COPY --from=java_builder /build/target/dependency/BOOT-INF/lib /kaniko/model-converter/lib
COPY --from=java_builder /build/target/dependency/BOOT-INF/classes /kaniko/model-converter
COPY --from=java_builder /build/target/dependency/META-INF /kaniko/model-converter/META-INF
COPY ./src /kaniko/model-converter/src
COPY ./application.properties /kaniko/model-converter
COPY ./snapshot.sh /kaniko/model-converter
RUN chmod +x /kaniko/model-converter/snapshot.sh

RUN mkdir -p /kaniko/.aws
RUN mkdir -p /kaniko/.docker

ENV JAVA_OPTS="${JAVA_OPTS} \
        -XX:+PrintGC \
        -XX:+UnlockExperimentalVMOptions \
        -XX:+UseCGroupMemoryLimitForHeap \
        -Dcom.sun.management.jmxremote.port=8199 \
        -Dcom.sun.management.jmxremote.rmi.port=8199 \
        -Dcom.sun.management.jmxremote.authenticate=false \
        -Dcom.sun.management.jmxremote.local.only=false \
        -Djava.rmi.server.hostname=0.0.0.0 \
        -Dcom.sun.management.jmxremote.ssl=false \
        -Dspring.profiles.active=local"

ENV PATH="/kaniko/usr/bin:${PATH}"

ENTRYPOINT exec /usr/bin/java ${JAVA_OPTS} -cp '/kaniko/model-converter:/kaniko/model-converter/lib/*' 'com.bah.ai.modelconverter.api.ModelConverterServiceApplication'
