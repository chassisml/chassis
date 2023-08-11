```python
import json
from typing import Mapping, Dict

from chassis.builder import DockerBuilder, BuildOptions
from chassisml import ChassisModel


def predict(inputs: Mapping[str, bytes]) -> Dict[str, bytes]:
    result = {"Message": inputs["input"].decode()}
    return {"results.json": json.dumps(result).encode()}


model = ChassisModel(process_fn=predict)
model.metadata.model_name = "My Echo Model"
model.metadata.model_version = "1.0.0"
model.metadata.add_input("input", ["text/plain"])
model.metadata.add_output("results.json", "application/json")

# Build with Docker
local_build_options = BuildOptions(server="kserve")
builder = DockerBuilder(model, options=local_build_options)
builder.build_image("my-echo-model")
```

```shell
docker run --rm -it -e HTTP_PORT=45000 -e PROTOCOL=v1 -e MODEL_NAME=my-echo-model -p 45000:45000 my-echo-model 
```

```shell
# Test protocol v1
curl -i http://localhost:45000/v1/models/my-echo-model:predict -X POST -d '{"instances": ["b25lIHR3byB0aHJlZQo="]}' -H 'Content-Type: application/json'
```

```shell
docker run --rm -it -e HTTP_PORT=45000 -e PROTOCOL=v2 -e MODEL_NAME=my-echo-model -p 45000:45000 my-echo-model 
```

```shell
# Test protocol v2
curl -i http://localhost:45000/v1/models/my-echo-model:predict -X POST -d '{"inputs": [{"name": "input_0", "shape": [1,1], "datatype": "BYTES", "data": ["b25lIHR3byB0aHJlZQo="]}]}' -H 'Content-Type: application/json'
```

