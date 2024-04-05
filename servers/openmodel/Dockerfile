FROM rust:1.76-bookworm as builder

RUN apt-get update \
    && apt-get install -y python3.11-dev protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

ARG PROTO_DIR=/app/proto

COPY servers/openmodel/Cargo.toml servers/openmodel/Cargo.lock /app/
COPY servers/openmodel/build.rs /app/build.rs
COPY protos /app/proto
COPY servers/openmodel/python /app/python
COPY servers/openmodel/src /app/src

WORKDIR /app
RUN cargo build --release --locked --bin server


FROM python:3.11-slim-bookworm

LABEL org.opencontainers.image.source=https://github.com/chassisml/chassis

ENV MODEL_PORT=9090
ENV METRICS_PORT=8080

ENV LOG_LEVEL=info
ENV TELEMETRY_ENABLED=false
ENV TELEMETRY_ENDPOINT=""

COPY --from=builder /app/target/release/server /usr/local/bin/openmodel-server

ENTRYPOINT ["openmodel-server"]
