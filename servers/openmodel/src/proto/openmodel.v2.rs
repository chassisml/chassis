#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct OpenModelContainer {
    #[prost(string, tag = "1")]
    pub name: ::prost::alloc::string::String,
    #[prost(string, tag = "2")]
    pub version: ::prost::alloc::string::String,
    #[prost(message, optional, tag = "3")]
    pub author: ::core::option::Option<open_model_container::Author>,
    #[prost(message, optional, tag = "4")]
    pub biography: ::core::option::Option<open_model_container::Biography>,
}
/// Nested message and enum types in `OpenModelContainer`.
pub mod open_model_container {
    #[allow(clippy::derive_partial_eq_without_eq)]
    #[derive(Clone, PartialEq, ::prost::Message)]
    pub struct Author {
        #[prost(string, tag = "1")]
        pub name: ::prost::alloc::string::String,
        #[prost(string, tag = "2")]
        pub email: ::prost::alloc::string::String,
    }
    #[allow(clippy::derive_partial_eq_without_eq)]
    #[derive(Clone, PartialEq, ::prost::Message)]
    pub struct Biography {
        #[prost(string, tag = "1")]
        pub summary: ::prost::alloc::string::String,
    }
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct Point {
    #[prost(int64, tag = "1")]
    pub x: i64,
    #[prost(int64, tag = "2")]
    pub y: i64,
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct BoundingBox {
    #[prost(int64, tag = "1")]
    pub x: i64,
    #[prost(int64, tag = "2")]
    pub y: i64,
    #[prost(int64, tag = "3")]
    pub width: i64,
    /// rotation? degrees or radians?
    #[prost(int64, tag = "4")]
    pub height: i64,
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct ImageMask {
    #[prost(int64, tag = "1")]
    pub original_width: i64,
    #[prost(int64, tag = "2")]
    pub original_height: i64,
    /// Pick one or the other below.
    #[prost(int64, repeated, tag = "3")]
    pub rle: ::prost::alloc::vec::Vec<i64>,
    #[prost(bytes = "vec", repeated, tag = "4")]
    pub image: ::prost::alloc::vec::Vec<::prost::alloc::vec::Vec<u8>>,
    #[prost(message, repeated, tag = "5")]
    pub points: ::prost::alloc::vec::Vec<Point>,
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct TextSpan {
    #[prost(int64, tag = "1")]
    pub start: i64,
    #[prost(int64, tag = "2")]
    pub end: i64,
    #[prost(string, tag = "3")]
    pub text: ::prost::alloc::string::String,
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct Tensor {
    #[prost(int64, repeated, tag = "1")]
    pub shape: ::prost::alloc::vec::Vec<i64>,
    /// The `data_type` field should correspond to the field below that contains
    /// the data.
    #[prost(enumeration = "tensor::DataType", tag = "2")]
    pub data_type: i32,
    /// Only one of the following fields should be provided. `oneof` is not
    /// used because `oneof` doesn't allow repeated fields.
    /// The data must be flattened, one-dimensional, row-major order of the tensor
    /// elements. The size must match the shape defined above.
    #[prost(bool, repeated, tag = "3")]
    pub bool_data: ::prost::alloc::vec::Vec<bool>,
    #[prost(int32, repeated, tag = "4")]
    pub int32_data: ::prost::alloc::vec::Vec<i32>,
    #[prost(int64, repeated, tag = "5")]
    pub int64_data: ::prost::alloc::vec::Vec<i64>,
    #[prost(uint32, repeated, tag = "6")]
    pub uint32_data: ::prost::alloc::vec::Vec<u32>,
    #[prost(uint64, repeated, tag = "7")]
    pub uint64_data: ::prost::alloc::vec::Vec<u64>,
    #[prost(float, repeated, tag = "8")]
    pub float32_data: ::prost::alloc::vec::Vec<f32>,
    #[prost(double, repeated, tag = "9")]
    pub float64_data: ::prost::alloc::vec::Vec<f64>,
    /// This field allows for passing in a raw byte-representation of the tensor.
    /// The bytes should match the data type and shape defined above.
    #[prost(bytes = "vec", repeated, tag = "10")]
    pub raw_data: ::prost::alloc::vec::Vec<::prost::alloc::vec::Vec<u8>>,
}
/// Nested message and enum types in `Tensor`.
pub mod tensor {
    #[derive(
        Clone,
        Copy,
        Debug,
        PartialEq,
        Eq,
        Hash,
        PartialOrd,
        Ord,
        ::prost::Enumeration
    )]
    #[repr(i32)]
    pub enum DataType {
        UnknownTensorDataType = 0,
        Bool = 1,
        Int32 = 2,
        Int64 = 3,
        Uint32 = 4,
        Uint64 = 5,
        Float32 = 6,
        Float64 = 7,
    }
    impl DataType {
        /// String value of the enum field names used in the ProtoBuf definition.
        ///
        /// The values are not transformed in any way and thus are considered stable
        /// (if the ProtoBuf definition does not change) and safe for programmatic use.
        pub fn as_str_name(&self) -> &'static str {
            match self {
                DataType::UnknownTensorDataType => "UNKNOWN_TENSOR_DATA_TYPE",
                DataType::Bool => "BOOL",
                DataType::Int32 => "INT32",
                DataType::Int64 => "INT64",
                DataType::Uint32 => "UINT32",
                DataType::Uint64 => "UINT64",
                DataType::Float32 => "FLOAT32",
                DataType::Float64 => "FLOAT64",
            }
        }
        /// Creates an enum from field names used in the ProtoBuf definition.
        pub fn from_str_name(value: &str) -> ::core::option::Option<Self> {
            match value {
                "UNKNOWN_TENSOR_DATA_TYPE" => Some(Self::UnknownTensorDataType),
                "BOOL" => Some(Self::Bool),
                "INT32" => Some(Self::Int32),
                "INT64" => Some(Self::Int64),
                "UINT32" => Some(Self::Uint32),
                "UINT64" => Some(Self::Uint64),
                "FLOAT32" => Some(Self::Float32),
                "FLOAT64" => Some(Self::Float64),
                _ => None,
            }
        }
    }
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct Explanation {
    #[prost(oneof = "explanation::Explanation", tags = "3, 1, 2")]
    pub explanation: ::core::option::Option<explanation::Explanation>,
}
/// Nested message and enum types in `Explanation`.
pub mod explanation {
    #[allow(clippy::derive_partial_eq_without_eq)]
    #[derive(Clone, PartialEq, ::prost::Oneof)]
    pub enum Explanation {
        #[prost(message, tag = "3")]
        None(super::NoExplanation),
        #[prost(message, tag = "1")]
        Image(super::ImageExplanation),
        #[prost(message, tag = "2")]
        Text(super::TextExplanation),
    }
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct NoExplanation {}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct ImageExplanation {
    #[prost(message, optional, tag = "1")]
    pub mask: ::core::option::Option<ImageMask>,
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct TextExplanation {
    #[prost(message, repeated, tag = "1")]
    pub class_results: ::prost::alloc::vec::Vec<text_explanation::ClassResults>,
}
/// Nested message and enum types in `TextExplanation`.
pub mod text_explanation {
    #[allow(clippy::derive_partial_eq_without_eq)]
    #[derive(Clone, PartialEq, ::prost::Message)]
    pub struct TextSpanScore {
        #[prost(message, optional, tag = "1")]
        pub text_span: ::core::option::Option<super::TextSpan>,
        #[prost(double, tag = "2")]
        pub score: f64,
    }
    #[allow(clippy::derive_partial_eq_without_eq)]
    #[derive(Clone, PartialEq, ::prost::Message)]
    pub struct ClassResults {
        #[prost(string, tag = "1")]
        pub class: ::prost::alloc::string::String,
        #[prost(message, repeated, tag = "2")]
        pub scores: ::prost::alloc::vec::Vec<TextSpanScore>,
    }
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct ModelDrift {
    #[prost(message, optional, tag = "1")]
    pub data_drift: ::core::option::Option<DataDrift>,
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct DataDrift {
    #[prost(double, tag = "1")]
    pub score: f64,
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct PredictionOutput {
    #[prost(string, tag = "1")]
    pub key: ::prost::alloc::string::String,
    #[prost(oneof = "prediction_output::Result", tags = "4, 5, 6, 7, 8, 9, 10, 11")]
    pub result: ::core::option::Option<prediction_output::Result>,
}
/// Nested message and enum types in `PredictionOutput`.
pub mod prediction_output {
    #[allow(clippy::derive_partial_eq_without_eq)]
    #[derive(Clone, PartialEq, ::prost::Oneof)]
    pub enum Result {
        /// Tensor tensor = 3;
        #[prost(message, tag = "4")]
        Classification(super::ClassificationResult),
        #[prost(message, tag = "5")]
        MultiClassification(super::MultiClassificationResult),
        #[prost(message, tag = "6")]
        ObjectDetection(super::ObjectDetectionResult),
        #[prost(message, tag = "7")]
        Segmentation(super::SegmentationResult),
        #[prost(message, tag = "8")]
        NamedEntity(super::NamedEntityResult),
        #[prost(message, tag = "9")]
        Text(super::TextResult),
        #[prost(message, tag = "10")]
        Image(super::ImageResult),
        #[prost(message, tag = "11")]
        Data(super::DataResult),
    }
}
/// Image Classification
/// Text Classification
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct ClassificationResult {
    #[prost(message, repeated, tag = "1")]
    pub class_predictions: ::prost::alloc::vec::Vec<classification_result::Prediction>,
}
/// Nested message and enum types in `ClassificationResult`.
pub mod classification_result {
    #[allow(clippy::derive_partial_eq_without_eq)]
    #[derive(Clone, PartialEq, ::prost::Message)]
    pub struct Prediction {
        #[prost(string, tag = "1")]
        pub class: ::prost::alloc::string::String,
        #[prost(double, tag = "2")]
        pub score: f64,
    }
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct MultiClassificationResult {
    #[prost(message, repeated, tag = "1")]
    pub classifications: ::prost::alloc::vec::Vec<ClassificationResult>,
}
/// Object Detection
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct ObjectDetectionResult {
    #[prost(message, repeated, tag = "1")]
    pub detections: ::prost::alloc::vec::Vec<object_detection_result::Detection>,
}
/// Nested message and enum types in `ObjectDetectionResult`.
pub mod object_detection_result {
    #[allow(clippy::derive_partial_eq_without_eq)]
    #[derive(Clone, PartialEq, ::prost::Message)]
    pub struct Detection {
        #[prost(string, tag = "1")]
        pub class: ::prost::alloc::string::String,
        #[prost(double, tag = "2")]
        pub score: f64,
        #[prost(message, optional, tag = "3")]
        pub bounding_box: ::core::option::Option<super::BoundingBox>,
    }
}
/// Segmentation
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct SegmentationResult {
    #[prost(message, repeated, tag = "1")]
    pub segments: ::prost::alloc::vec::Vec<segmentation_result::Segment>,
}
/// Nested message and enum types in `SegmentationResult`.
pub mod segmentation_result {
    #[allow(clippy::derive_partial_eq_without_eq)]
    #[derive(Clone, PartialEq, ::prost::Message)]
    pub struct Segment {
        #[prost(string, tag = "1")]
        pub class: ::prost::alloc::string::String,
        #[prost(double, tag = "2")]
        pub score: f64,
        #[prost(message, optional, tag = "3")]
        pub image_mask: ::core::option::Option<super::ImageMask>,
        #[prost(message, optional, tag = "4")]
        pub bounding_box: ::core::option::Option<super::BoundingBox>,
    }
}
/// Named Entity Recognition
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct NamedEntityResult {
    #[prost(message, repeated, tag = "1")]
    pub entities: ::prost::alloc::vec::Vec<named_entity_result::NamedEntity>,
}
/// Nested message and enum types in `NamedEntityResult`.
pub mod named_entity_result {
    #[allow(clippy::derive_partial_eq_without_eq)]
    #[derive(Clone, PartialEq, ::prost::Message)]
    pub struct NamedEntity {
        #[prost(string, tag = "1")]
        pub entity_group: ::prost::alloc::string::String,
        #[prost(double, tag = "2")]
        pub score: f64,
        #[prost(message, optional, tag = "3")]
        pub text_span: ::core::option::Option<super::TextSpan>,
    }
}
/// Text summarization
/// Text generation
/// Translation
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct TextResult {
    #[prost(string, tag = "1")]
    pub text: ::prost::alloc::string::String,
}
/// Image/video
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct ImageResult {
    #[prost(bytes = "vec", tag = "1")]
    pub data: ::prost::alloc::vec::Vec<u8>,
}
/// Raw bytes
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct DataResult {
    #[prost(bytes = "vec", tag = "1")]
    pub data: ::prost::alloc::vec::Vec<u8>,
    #[prost(string, tag = "2")]
    pub content_type: ::prost::alloc::string::String,
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct StatusRequest {}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct StatusResponse {
    #[prost(enumeration = "status_response::Status", tag = "1")]
    pub status: i32,
}
/// Nested message and enum types in `StatusResponse`.
pub mod status_response {
    #[derive(
        Clone,
        Copy,
        Debug,
        PartialEq,
        Eq,
        Hash,
        PartialOrd,
        Ord,
        ::prost::Enumeration
    )]
    #[repr(i32)]
    pub enum Status {
        UnknownStatus = 0,
        Ok = 1,
    }
    impl Status {
        /// String value of the enum field names used in the ProtoBuf definition.
        ///
        /// The values are not transformed in any way and thus are considered stable
        /// (if the ProtoBuf definition does not change) and safe for programmatic use.
        pub fn as_str_name(&self) -> &'static str {
            match self {
                Status::UnknownStatus => "UNKNOWN_STATUS",
                Status::Ok => "OK",
            }
        }
        /// Creates an enum from field names used in the ProtoBuf definition.
        pub fn from_str_name(value: &str) -> ::core::option::Option<Self> {
            match value {
                "UNKNOWN_STATUS" => Some(Self::UnknownStatus),
                "OK" => Some(Self::Ok),
                _ => None,
            }
        }
    }
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct ContainerInfoRequest {}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct PredictRequest {
    #[prost(message, repeated, tag = "1")]
    pub inputs: ::prost::alloc::vec::Vec<predict_request::Input>,
    #[prost(map = "string, string", tag = "10")]
    pub tags: ::std::collections::HashMap<
        ::prost::alloc::string::String,
        ::prost::alloc::string::String,
    >,
}
/// Nested message and enum types in `PredictRequest`.
pub mod predict_request {
    #[allow(clippy::derive_partial_eq_without_eq)]
    #[derive(Clone, PartialEq, ::prost::Message)]
    pub struct Input {
        #[prost(string, tag = "1")]
        pub key: ::prost::alloc::string::String,
        #[prost(oneof = "input::Source", tags = "2, 3")]
        pub source: ::core::option::Option<input::Source>,
    }
    /// Nested message and enum types in `Input`.
    pub mod input {
        #[allow(clippy::derive_partial_eq_without_eq)]
        #[derive(Clone, PartialEq, ::prost::Oneof)]
        pub enum Source {
            #[prost(string, tag = "2")]
            Text(::prost::alloc::string::String),
            /// Tensor tensor = 4;
            #[prost(bytes, tag = "3")]
            Data(::prost::alloc::vec::Vec<u8>),
        }
    }
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct PredictResponse {
    #[prost(message, repeated, tag = "1")]
    pub outputs: ::prost::alloc::vec::Vec<PredictionOutput>,
    #[prost(message, optional, tag = "2")]
    pub explanation: ::core::option::Option<Explanation>,
    #[prost(message, optional, tag = "3")]
    pub drift: ::core::option::Option<ModelDrift>,
    #[prost(bool, tag = "7")]
    pub success: bool,
    #[prost(string, tag = "8")]
    pub error: ::prost::alloc::string::String,
    #[prost(message, optional, tag = "9")]
    pub timings: ::core::option::Option<predict_response::Timings>,
    #[prost(map = "string, string", tag = "10")]
    pub tags: ::std::collections::HashMap<
        ::prost::alloc::string::String,
        ::prost::alloc::string::String,
    >,
}
/// Nested message and enum types in `PredictResponse`.
pub mod predict_response {
    #[allow(clippy::derive_partial_eq_without_eq)]
    #[derive(Clone, PartialEq, ::prost::Message)]
    pub struct Timings {
        #[prost(message, optional, tag = "1")]
        pub model_execution: ::core::option::Option<::prost_types::Duration>,
        #[prost(message, optional, tag = "2")]
        pub preprocessing: ::core::option::Option<::prost_types::Duration>,
        #[prost(message, optional, tag = "3")]
        pub postprocessing: ::core::option::Option<::prost_types::Duration>,
        #[prost(message, optional, tag = "4")]
        pub formatting: ::core::option::Option<::prost_types::Duration>,
        #[prost(message, optional, tag = "5")]
        pub total: ::core::option::Option<::prost_types::Duration>,
    }
}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct ShutdownRequest {}
#[allow(clippy::derive_partial_eq_without_eq)]
#[derive(Clone, PartialEq, ::prost::Message)]
pub struct ShutdownResponse {}
/// Generated client implementations.
pub mod inference_service_client {
    #![allow(unused_variables, dead_code, missing_docs, clippy::let_unit_value)]
    use tonic::codegen::*;
    use tonic::codegen::http::Uri;
    #[derive(Debug, Clone)]
    pub struct InferenceServiceClient<T> {
        inner: tonic::client::Grpc<T>,
    }
    impl InferenceServiceClient<tonic::transport::Channel> {
        /// Attempt to create a new client by connecting to a given endpoint.
        pub async fn connect<D>(dst: D) -> Result<Self, tonic::transport::Error>
        where
            D: TryInto<tonic::transport::Endpoint>,
            D::Error: Into<StdError>,
        {
            let conn = tonic::transport::Endpoint::new(dst)?.connect().await?;
            Ok(Self::new(conn))
        }
    }
    impl<T> InferenceServiceClient<T>
    where
        T: tonic::client::GrpcService<tonic::body::BoxBody>,
        T::Error: Into<StdError>,
        T::ResponseBody: Body<Data = Bytes> + Send + 'static,
        <T::ResponseBody as Body>::Error: Into<StdError> + Send,
    {
        pub fn new(inner: T) -> Self {
            let inner = tonic::client::Grpc::new(inner);
            Self { inner }
        }
        pub fn with_origin(inner: T, origin: Uri) -> Self {
            let inner = tonic::client::Grpc::with_origin(inner, origin);
            Self { inner }
        }
        pub fn with_interceptor<F>(
            inner: T,
            interceptor: F,
        ) -> InferenceServiceClient<InterceptedService<T, F>>
        where
            F: tonic::service::Interceptor,
            T::ResponseBody: Default,
            T: tonic::codegen::Service<
                http::Request<tonic::body::BoxBody>,
                Response = http::Response<
                    <T as tonic::client::GrpcService<tonic::body::BoxBody>>::ResponseBody,
                >,
            >,
            <T as tonic::codegen::Service<
                http::Request<tonic::body::BoxBody>,
            >>::Error: Into<StdError> + Send + Sync,
        {
            InferenceServiceClient::new(InterceptedService::new(inner, interceptor))
        }
        /// Compress requests with the given encoding.
        ///
        /// This requires the server to support it otherwise it might respond with an
        /// error.
        #[must_use]
        pub fn send_compressed(mut self, encoding: CompressionEncoding) -> Self {
            self.inner = self.inner.send_compressed(encoding);
            self
        }
        /// Enable decompressing responses.
        #[must_use]
        pub fn accept_compressed(mut self, encoding: CompressionEncoding) -> Self {
            self.inner = self.inner.accept_compressed(encoding);
            self
        }
        /// Limits the maximum size of a decoded message.
        ///
        /// Default: `4MB`
        #[must_use]
        pub fn max_decoding_message_size(mut self, limit: usize) -> Self {
            self.inner = self.inner.max_decoding_message_size(limit);
            self
        }
        /// Limits the maximum size of an encoded message.
        ///
        /// Default: `usize::MAX`
        #[must_use]
        pub fn max_encoding_message_size(mut self, limit: usize) -> Self {
            self.inner = self.inner.max_encoding_message_size(limit);
            self
        }
        pub async fn status(
            &mut self,
            request: impl tonic::IntoRequest<super::StatusRequest>,
        ) -> std::result::Result<tonic::Response<super::StatusResponse>, tonic::Status> {
            self.inner
                .ready()
                .await
                .map_err(|e| {
                    tonic::Status::new(
                        tonic::Code::Unknown,
                        format!("Service was not ready: {}", e.into()),
                    )
                })?;
            let codec = tonic::codec::ProstCodec::default();
            let path = http::uri::PathAndQuery::from_static(
                "/openmodel.v2.InferenceService/Status",
            );
            let mut req = request.into_request();
            req.extensions_mut()
                .insert(GrpcMethod::new("openmodel.v2.InferenceService", "Status"));
            self.inner.unary(req, path, codec).await
        }
        pub async fn get_container_info(
            &mut self,
            request: impl tonic::IntoRequest<super::ContainerInfoRequest>,
        ) -> std::result::Result<
            tonic::Response<super::OpenModelContainer>,
            tonic::Status,
        > {
            self.inner
                .ready()
                .await
                .map_err(|e| {
                    tonic::Status::new(
                        tonic::Code::Unknown,
                        format!("Service was not ready: {}", e.into()),
                    )
                })?;
            let codec = tonic::codec::ProstCodec::default();
            let path = http::uri::PathAndQuery::from_static(
                "/openmodel.v2.InferenceService/GetContainerInfo",
            );
            let mut req = request.into_request();
            req.extensions_mut()
                .insert(
                    GrpcMethod::new("openmodel.v2.InferenceService", "GetContainerInfo"),
                );
            self.inner.unary(req, path, codec).await
        }
        pub async fn predict(
            &mut self,
            request: impl tonic::IntoRequest<super::PredictRequest>,
        ) -> std::result::Result<
            tonic::Response<super::PredictResponse>,
            tonic::Status,
        > {
            self.inner
                .ready()
                .await
                .map_err(|e| {
                    tonic::Status::new(
                        tonic::Code::Unknown,
                        format!("Service was not ready: {}", e.into()),
                    )
                })?;
            let codec = tonic::codec::ProstCodec::default();
            let path = http::uri::PathAndQuery::from_static(
                "/openmodel.v2.InferenceService/Predict",
            );
            let mut req = request.into_request();
            req.extensions_mut()
                .insert(GrpcMethod::new("openmodel.v2.InferenceService", "Predict"));
            self.inner.unary(req, path, codec).await
        }
        ///  rpc BatchPredict() returns () {}
        ///  rpc PredictStream(stream PredictRequest) returns (stream PredictResponse) {}
        pub async fn shutdown(
            &mut self,
            request: impl tonic::IntoRequest<super::ShutdownRequest>,
        ) -> std::result::Result<
            tonic::Response<super::ShutdownResponse>,
            tonic::Status,
        > {
            self.inner
                .ready()
                .await
                .map_err(|e| {
                    tonic::Status::new(
                        tonic::Code::Unknown,
                        format!("Service was not ready: {}", e.into()),
                    )
                })?;
            let codec = tonic::codec::ProstCodec::default();
            let path = http::uri::PathAndQuery::from_static(
                "/openmodel.v2.InferenceService/Shutdown",
            );
            let mut req = request.into_request();
            req.extensions_mut()
                .insert(GrpcMethod::new("openmodel.v2.InferenceService", "Shutdown"));
            self.inner.unary(req, path, codec).await
        }
    }
}
/// Generated server implementations.
pub mod inference_service_server {
    #![allow(unused_variables, dead_code, missing_docs, clippy::let_unit_value)]
    use tonic::codegen::*;
    /// Generated trait containing gRPC methods that should be implemented for use with InferenceServiceServer.
    #[async_trait]
    pub trait InferenceService: Send + Sync + 'static {
        async fn status(
            &self,
            request: tonic::Request<super::StatusRequest>,
        ) -> std::result::Result<tonic::Response<super::StatusResponse>, tonic::Status>;
        async fn get_container_info(
            &self,
            request: tonic::Request<super::ContainerInfoRequest>,
        ) -> std::result::Result<
            tonic::Response<super::OpenModelContainer>,
            tonic::Status,
        >;
        async fn predict(
            &self,
            request: tonic::Request<super::PredictRequest>,
        ) -> std::result::Result<tonic::Response<super::PredictResponse>, tonic::Status>;
        ///  rpc BatchPredict() returns () {}
        ///  rpc PredictStream(stream PredictRequest) returns (stream PredictResponse) {}
        async fn shutdown(
            &self,
            request: tonic::Request<super::ShutdownRequest>,
        ) -> std::result::Result<
            tonic::Response<super::ShutdownResponse>,
            tonic::Status,
        >;
    }
    #[derive(Debug)]
    pub struct InferenceServiceServer<T: InferenceService> {
        inner: _Inner<T>,
        accept_compression_encodings: EnabledCompressionEncodings,
        send_compression_encodings: EnabledCompressionEncodings,
        max_decoding_message_size: Option<usize>,
        max_encoding_message_size: Option<usize>,
    }
    struct _Inner<T>(Arc<T>);
    impl<T: InferenceService> InferenceServiceServer<T> {
        pub fn new(inner: T) -> Self {
            Self::from_arc(Arc::new(inner))
        }
        pub fn from_arc(inner: Arc<T>) -> Self {
            let inner = _Inner(inner);
            Self {
                inner,
                accept_compression_encodings: Default::default(),
                send_compression_encodings: Default::default(),
                max_decoding_message_size: None,
                max_encoding_message_size: None,
            }
        }
        pub fn with_interceptor<F>(
            inner: T,
            interceptor: F,
        ) -> InterceptedService<Self, F>
        where
            F: tonic::service::Interceptor,
        {
            InterceptedService::new(Self::new(inner), interceptor)
        }
        /// Enable decompressing requests with the given encoding.
        #[must_use]
        pub fn accept_compressed(mut self, encoding: CompressionEncoding) -> Self {
            self.accept_compression_encodings.enable(encoding);
            self
        }
        /// Compress responses with the given encoding, if the client supports it.
        #[must_use]
        pub fn send_compressed(mut self, encoding: CompressionEncoding) -> Self {
            self.send_compression_encodings.enable(encoding);
            self
        }
        /// Limits the maximum size of a decoded message.
        ///
        /// Default: `4MB`
        #[must_use]
        pub fn max_decoding_message_size(mut self, limit: usize) -> Self {
            self.max_decoding_message_size = Some(limit);
            self
        }
        /// Limits the maximum size of an encoded message.
        ///
        /// Default: `usize::MAX`
        #[must_use]
        pub fn max_encoding_message_size(mut self, limit: usize) -> Self {
            self.max_encoding_message_size = Some(limit);
            self
        }
    }
    impl<T, B> tonic::codegen::Service<http::Request<B>> for InferenceServiceServer<T>
    where
        T: InferenceService,
        B: Body + Send + 'static,
        B::Error: Into<StdError> + Send + 'static,
    {
        type Response = http::Response<tonic::body::BoxBody>;
        type Error = std::convert::Infallible;
        type Future = BoxFuture<Self::Response, Self::Error>;
        fn poll_ready(
            &mut self,
            _cx: &mut Context<'_>,
        ) -> Poll<std::result::Result<(), Self::Error>> {
            Poll::Ready(Ok(()))
        }
        fn call(&mut self, req: http::Request<B>) -> Self::Future {
            let inner = self.inner.clone();
            match req.uri().path() {
                "/openmodel.v2.InferenceService/Status" => {
                    #[allow(non_camel_case_types)]
                    struct StatusSvc<T: InferenceService>(pub Arc<T>);
                    impl<
                        T: InferenceService,
                    > tonic::server::UnaryService<super::StatusRequest>
                    for StatusSvc<T> {
                        type Response = super::StatusResponse;
                        type Future = BoxFuture<
                            tonic::Response<Self::Response>,
                            tonic::Status,
                        >;
                        fn call(
                            &mut self,
                            request: tonic::Request<super::StatusRequest>,
                        ) -> Self::Future {
                            let inner = Arc::clone(&self.0);
                            let fut = async move { (*inner).status(request).await };
                            Box::pin(fut)
                        }
                    }
                    let accept_compression_encodings = self.accept_compression_encodings;
                    let send_compression_encodings = self.send_compression_encodings;
                    let max_decoding_message_size = self.max_decoding_message_size;
                    let max_encoding_message_size = self.max_encoding_message_size;
                    let inner = self.inner.clone();
                    let fut = async move {
                        let inner = inner.0;
                        let method = StatusSvc(inner);
                        let codec = tonic::codec::ProstCodec::default();
                        let mut grpc = tonic::server::Grpc::new(codec)
                            .apply_compression_config(
                                accept_compression_encodings,
                                send_compression_encodings,
                            )
                            .apply_max_message_size_config(
                                max_decoding_message_size,
                                max_encoding_message_size,
                            );
                        let res = grpc.unary(method, req).await;
                        Ok(res)
                    };
                    Box::pin(fut)
                }
                "/openmodel.v2.InferenceService/GetContainerInfo" => {
                    #[allow(non_camel_case_types)]
                    struct GetContainerInfoSvc<T: InferenceService>(pub Arc<T>);
                    impl<
                        T: InferenceService,
                    > tonic::server::UnaryService<super::ContainerInfoRequest>
                    for GetContainerInfoSvc<T> {
                        type Response = super::OpenModelContainer;
                        type Future = BoxFuture<
                            tonic::Response<Self::Response>,
                            tonic::Status,
                        >;
                        fn call(
                            &mut self,
                            request: tonic::Request<super::ContainerInfoRequest>,
                        ) -> Self::Future {
                            let inner = Arc::clone(&self.0);
                            let fut = async move {
                                (*inner).get_container_info(request).await
                            };
                            Box::pin(fut)
                        }
                    }
                    let accept_compression_encodings = self.accept_compression_encodings;
                    let send_compression_encodings = self.send_compression_encodings;
                    let max_decoding_message_size = self.max_decoding_message_size;
                    let max_encoding_message_size = self.max_encoding_message_size;
                    let inner = self.inner.clone();
                    let fut = async move {
                        let inner = inner.0;
                        let method = GetContainerInfoSvc(inner);
                        let codec = tonic::codec::ProstCodec::default();
                        let mut grpc = tonic::server::Grpc::new(codec)
                            .apply_compression_config(
                                accept_compression_encodings,
                                send_compression_encodings,
                            )
                            .apply_max_message_size_config(
                                max_decoding_message_size,
                                max_encoding_message_size,
                            );
                        let res = grpc.unary(method, req).await;
                        Ok(res)
                    };
                    Box::pin(fut)
                }
                "/openmodel.v2.InferenceService/Predict" => {
                    #[allow(non_camel_case_types)]
                    struct PredictSvc<T: InferenceService>(pub Arc<T>);
                    impl<
                        T: InferenceService,
                    > tonic::server::UnaryService<super::PredictRequest>
                    for PredictSvc<T> {
                        type Response = super::PredictResponse;
                        type Future = BoxFuture<
                            tonic::Response<Self::Response>,
                            tonic::Status,
                        >;
                        fn call(
                            &mut self,
                            request: tonic::Request<super::PredictRequest>,
                        ) -> Self::Future {
                            let inner = Arc::clone(&self.0);
                            let fut = async move { (*inner).predict(request).await };
                            Box::pin(fut)
                        }
                    }
                    let accept_compression_encodings = self.accept_compression_encodings;
                    let send_compression_encodings = self.send_compression_encodings;
                    let max_decoding_message_size = self.max_decoding_message_size;
                    let max_encoding_message_size = self.max_encoding_message_size;
                    let inner = self.inner.clone();
                    let fut = async move {
                        let inner = inner.0;
                        let method = PredictSvc(inner);
                        let codec = tonic::codec::ProstCodec::default();
                        let mut grpc = tonic::server::Grpc::new(codec)
                            .apply_compression_config(
                                accept_compression_encodings,
                                send_compression_encodings,
                            )
                            .apply_max_message_size_config(
                                max_decoding_message_size,
                                max_encoding_message_size,
                            );
                        let res = grpc.unary(method, req).await;
                        Ok(res)
                    };
                    Box::pin(fut)
                }
                "/openmodel.v2.InferenceService/Shutdown" => {
                    #[allow(non_camel_case_types)]
                    struct ShutdownSvc<T: InferenceService>(pub Arc<T>);
                    impl<
                        T: InferenceService,
                    > tonic::server::UnaryService<super::ShutdownRequest>
                    for ShutdownSvc<T> {
                        type Response = super::ShutdownResponse;
                        type Future = BoxFuture<
                            tonic::Response<Self::Response>,
                            tonic::Status,
                        >;
                        fn call(
                            &mut self,
                            request: tonic::Request<super::ShutdownRequest>,
                        ) -> Self::Future {
                            let inner = Arc::clone(&self.0);
                            let fut = async move { (*inner).shutdown(request).await };
                            Box::pin(fut)
                        }
                    }
                    let accept_compression_encodings = self.accept_compression_encodings;
                    let send_compression_encodings = self.send_compression_encodings;
                    let max_decoding_message_size = self.max_decoding_message_size;
                    let max_encoding_message_size = self.max_encoding_message_size;
                    let inner = self.inner.clone();
                    let fut = async move {
                        let inner = inner.0;
                        let method = ShutdownSvc(inner);
                        let codec = tonic::codec::ProstCodec::default();
                        let mut grpc = tonic::server::Grpc::new(codec)
                            .apply_compression_config(
                                accept_compression_encodings,
                                send_compression_encodings,
                            )
                            .apply_max_message_size_config(
                                max_decoding_message_size,
                                max_encoding_message_size,
                            );
                        let res = grpc.unary(method, req).await;
                        Ok(res)
                    };
                    Box::pin(fut)
                }
                _ => {
                    Box::pin(async move {
                        Ok(
                            http::Response::builder()
                                .status(200)
                                .header("grpc-status", "12")
                                .header("content-type", "application/grpc")
                                .body(empty_body())
                                .unwrap(),
                        )
                    })
                }
            }
        }
    }
    impl<T: InferenceService> Clone for InferenceServiceServer<T> {
        fn clone(&self) -> Self {
            let inner = self.inner.clone();
            Self {
                inner,
                accept_compression_encodings: self.accept_compression_encodings,
                send_compression_encodings: self.send_compression_encodings,
                max_decoding_message_size: self.max_decoding_message_size,
                max_encoding_message_size: self.max_encoding_message_size,
            }
        }
    }
    impl<T: InferenceService> Clone for _Inner<T> {
        fn clone(&self) -> Self {
            Self(Arc::clone(&self.0))
        }
    }
    impl<T: std::fmt::Debug> std::fmt::Debug for _Inner<T> {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            write!(f, "{:?}", self.0)
        }
    }
    impl<T: InferenceService> tonic::server::NamedService for InferenceServiceServer<T> {
        const NAME: &'static str = "openmodel.v2.InferenceService";
    }
}
