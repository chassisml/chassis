from typing import Any

import yaml

MODEL_YAML = "model.yaml"


class InputOutputMismatchException(Exception):
    pass


def parse_complete_model_yaml(model_yaml_path=MODEL_YAML):
    with open(model_yaml_path, "r") as f:
        model_yaml = yaml.safe_load(f)

    # Extract Info
    info = (model_yaml["name"], model_yaml["version"], model_yaml["author"], model_yaml["type"], model_yaml["source"])

    # Extract description
    model_description = model_yaml["description"]
    description = (
        model_description["summary"],
        model_description["details"],
        model_description["technical"],
        model_description["performance"],
    )

    # Extract inputs and outputs
    def extract_io_data(data_type: str):
        assert data_type in ["inputs", "outputs"]
        raw_io_data = model_yaml[data_type]

        io_files = []
        for io_filename in raw_io_data:
            io_file_data = raw_io_data[io_filename]
            accepted_media_types = io_file_data["acceptedMediaTypes" if data_type == "inputs" else "mediaType"]
            max_size = io_file_data["maxSize"]
            description_ = io_file_data["description"]
            io_files.append((io_filename, accepted_media_types, max_size, description_))

        return io_files

    inputs = extract_io_data("inputs")
    outputs = extract_io_data("outputs")

    # Extract resources
    model_resources = model_yaml["resources"]
    resources = (model_resources["memory"]["size"], model_resources["cpu"]["count"], model_resources["gpu"]["count"])

    # Extract timeout
    model_timeout = model_yaml["timeout"]
    timeout = (model_timeout["status"], model_timeout["run"])

    # Extract the features
    model_features = model_yaml["features"]

    def feature_or_default(feature_name: str, default: Any = None) -> Any:
        return (
            model_features[feature_name]
            if feature_name in model_features and model_features[feature_name] is not None
            else default
        )

    adversarial_defense, retrainable, results_format, drift_format, explanation_format = map(
        feature_or_default, ["adversarialDefense", "retrainable", "resultsFormat", "driftFormat", "explanationFormat"]
    )
    batch_size = feature_or_default("maxBatchSize", 1)
    features = (adversarial_defense, batch_size, retrainable, results_format, drift_format, explanation_format)

    return info, description, inputs, outputs, resources, timeout, features
