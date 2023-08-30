# Support for Common Data Types

When using Chassis, you must define a `predict` function that serves as your model inference function. This function may include one or multiple input parameters, depending on your model. This parameter will *always* be a mapping of `str` to `bytes` (i.e., `Mapping[str, bytes]`), which means the beginning of your `process` function must account for this and be able to convert it to the expected data type for your model. This guide includes examples of how to decode raw bytes for common data types.

*Assume `input` is the key that represents a single input to your model in the mapping of `str` to `bytes` as your predict parameter.*

## Text

=== "Bytes Decoding"

    ``` python
    text = input_data['input'].decode()
    ```

=== "Process Function"

    ```python
    import json
    from typing import Mapping
    def predict(input_data: Mapping[str, bytes]) -> dict(str, bytes):
        text = input_data['input'].decode()
        '''
        Perform processing and inference on text
        '''
        return {"results.json": json.dumps(output).encode()}
    ```

## Imagery

*OpenCV*
=== "Bytes Decoding"

    ```python
    import cv2
    import numpy as np
    img = cv2.imdecode(np.frombuffer(input_data['input'], np.uint8), -1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    ```

=== "Process Function"

    ```python
    import json
    from typing import Mapping    
    def predict(input_data: Mapping[str, bytes]) -> dict(str, bytes):
        img = cv2.imdecode(np.frombuffer(input_data['input'], np.uint8), -1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        '''
        Perform processing and inference on img
        '''
        return {"results.json": json.dumps(output).encode()}
    ```

*Pillow*
=== "Bytes Decoding"

    ```python
    import io
    from PIL import Image
    img = Image.open(io.BytesIO(input_data['input'])).convert("RGB")
    ```

=== "Process Function"

    ```python
    import json
    from typing import Mapping    
    def predict(input_data: Mapping[str, bytes]) -> dict(str, bytes):
        img = Image.open(io.BytesIO(input_data['input'])).convert("RGB")
        '''
        Perform processing and inference on img
        '''
        return {"results.json": json.dumps(output).encode()}
    ```

See also:

* [Native PyTorch function](https://pytorch.org/docs/stable/generated/torch.frombuffer.html)
* [Native Tensorflow function](https://www.tensorflow.org/api_docs/python/tf/io/decode_raw)

## Tabular

=== "Bytes Decoding"

    ```python
    from io import StringIO
    import pandas as pd
    input_table = pd.read_csv(StringIO(str(input_data['input'], "utf-8")))
    ```

=== "Process Function"

    ```python
    import json
    from typing import Mapping    
    def predict(input_data: Mapping[str, bytes]) -> dict(str, bytes):
        input_table = pd.read_csv(StringIO(str(input_data['input'], "utf-8")))
        '''
        Perform processing and inference on input_table
        '''
        return {"results.json": json.dumps(output).encode()}
    ```
