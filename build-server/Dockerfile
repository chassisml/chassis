FROM rust:1.68-bullseye as builder
# Set our initial workdir.
WORKDIR /app
# Create a new cargo project so we can download and build our dependencies
# independently of any other code changes.
RUN cargo new build-server
# Set our workdir to the new cargo project.
WORKDIR /app/build-server
# Copy in our Cargo.toml and Cargo.lock only.
COPY Cargo.toml Cargo.lock ./
# Build the new (empty) project with just our dependencies so they can be
# cached until the Cargo.toml or Cargo.lock file changes.
RUN cargo build --release --locked
# Now we can copy in our actual source code.
COPY manifests ./manifests
COPY src ./src
# And finally build our real application.
RUN cargo build --release --locked

# Unless we statically compile in libc into our binary, we need to use the
# 'cc' variant of the distroless container.
FROM gcr.io/distroless/cc-debian11:nonroot
# Copy in the built binary from the builder stage into a location in $PATH.
COPY --from=builder /app/build-server/target/release/chassis-build-server /usr/local/bin/chassis-build-server
# Finally set the default command to execute the server.
CMD ["chassis-build-server"]