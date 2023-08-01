import pytest

from chassis.metadata import ModelMetadata
from chassis.protos.v1.model_pb2 import StatusResponse


def test_legacy_metadata():
    md = ModelMetadata.legacy()

    data = md.serialize()
    obj: StatusResponse = StatusResponse.FromString(data)
    assert len(obj.inputs) == 1
    assert len(obj.outputs) == 1
    assert obj.inputs[0].filename == "input"
    assert obj.inputs[0].accepted_media_types == ["application/octet-stream"]
    assert obj.outputs[0].filename == "results.json"
    assert obj.outputs[0].media_type == "application/json"


def test_set_model_name():
    md = ModelMetadata.default()
    md.model_name = "My Awesome Model"

    data = md.serialize()
    obj: StatusResponse = StatusResponse.FromString(data)
    assert obj.model_info.model_name == "My Awesome Model"


def test_add_input():
    # Create a default metadata object.
    md = ModelMetadata.default()
    # Verify that its inputs are empty.
    data = md.serialize()
    obj: StatusResponse = StatusResponse.FromString(data)
    assert obj.inputs == []
    # Now add an input.
    md.add_input("image.jpg", accepted_media_types=["image/jpeg"])
    # Now verify that it was saved correctly.
    data = md.serialize()
    obj: StatusResponse = StatusResponse.FromString(data)
    assert len(obj.inputs) == 1
    assert obj.inputs[0].filename == "image.jpg"
    assert obj.inputs[0].accepted_media_types == ["image/jpeg"]
    assert obj.inputs[0].max_size == "1M"


def test_add_multiple_inputs():
    # Create a default metadata object.
    md = ModelMetadata.default()
    # Verify that its inputs are empty.
    data = md.serialize()
    obj: StatusResponse = StatusResponse.FromString(data)
    assert obj.inputs == []
    # Now add some inputs.
    md.add_input("image.jpg", accepted_media_types=["image/jpeg"], max_size="100M")
    md.add_input("config.json", accepted_media_types=["application/json"])
    # Now verify that it was saved correctly.
    data = md.serialize()
    obj: StatusResponse = StatusResponse.FromString(data)
    assert len(obj.inputs) == 2
    assert obj.inputs[0].filename == "image.jpg"
    assert obj.inputs[0].accepted_media_types == ["image/jpeg"]
    assert obj.inputs[0].max_size == "100M"
    assert obj.inputs[1].filename == "config.json"
    assert obj.inputs[1].accepted_media_types == ["application/json"]


def test_add_output():
    # Create a default metadata object.
    md = ModelMetadata.default()
    # Verify that its inputs are empty.
    data = md.serialize()
    obj: StatusResponse = StatusResponse.FromString(data)
    assert obj.outputs == []
    # Now add an input.
    md.add_output("results", media_type="application/json")
    # Now verify that it was saved correctly.
    data = md.serialize()
    obj: StatusResponse = StatusResponse.FromString(data)
    assert len(obj.outputs) == 1
    assert obj.outputs[0].filename == "results"
    assert obj.outputs[0].media_type == "application/json"
    assert obj.outputs[0].max_size == "1M"


def test_add_multiple_outputs():
    # Create a default metadata object.
    md = ModelMetadata.default()
    # Verify that its inputs are empty.
    data = md.serialize()
    obj: StatusResponse = StatusResponse.FromString(data)
    assert obj.outputs == []
    # Now add an input.
    md.add_output("results", media_type="application/json")
    md.add_output("explanation", media_type="text/plain", max_size="10K")
    # Now verify that it was saved correctly.
    data = md.serialize()
    obj: StatusResponse = StatusResponse.FromString(data)
    assert len(obj.outputs) == 2
    assert obj.outputs[0].filename == "results"
    assert obj.outputs[0].media_type == "application/json"
    assert obj.outputs[0].max_size == "1M"
    assert obj.outputs[1].filename == "explanation"
    assert obj.outputs[1].media_type == "text/plain"
    assert obj.outputs[1].max_size == "10K"
