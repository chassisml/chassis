# gRPC

## Overview

Chassis builds model containers which support gRPC. Let's understand what it is and why it's used.

RPC stands for "Remote Procedure Call", and it is a newer model for API design. In this model, a client script is able to call remote procedures, which are actually executing server-side, as if they were executing locally. 

gRPC is an RPC framework built by Google that uses the HTTP 2.0 protocol under the hood. In gRPC, code "stubs" are auto-generated (in different languages) for the client and server, so the details of the RPC to HTTP mapping are abstracted away for developers.

## Benefits Versus Traditional REST

### Client-Server Interaction

Traditional REST (REpresentational State Transfer) APIs are built using HTTP 1.1, which can support unary interactions (client sends single request, server sends back single response). Since gRPC uses HTTP 2.0, it can handle more complex client-server interactions in addition to those unary interactions, such as: client streaming (client sends stream of messages, server sends back single response), server streaming (client sends single message, server sends back stream of messages), bidirectional streaming (client and server send messages to each other in two independent streams). 

### Data Transmission Format

Another key difference has to do with data transmission formats. REST mainly uses JSON or XML whereas gRPC uses protocol buffers (protobuf). Protobuf is a structured data serialization/deserialization mechanism developed by Google, and it is much more lightweight than JSON and XML. 

### The Bottom Line

These key differences contribute to the significant speed increase typically observed using gRPC APIs as opposed to traditional REST APIs.