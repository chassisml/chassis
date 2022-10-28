# Support for Common Data Types

When using Chassis, you must define a `process` function that serves as your model inference function. The sole parameter to this function, let's call it `input_bytes`, represents the input data for your model. This parameter will *always* be of type `bytes`, which means the beginning of your `process` function must account for this and be able to convert it to the expected data type for your model. This guide includes examples of how to decode raw bytes for common data types.

*Assume `input_bytes` is the parameter to your `process` function for each.*

## Text

### Bytes Decoding
``` python
text = input_bytes.decode()
```

### Corresponding `Process` Function
```python
def process(input_bytes):
    text = input_bytes.decode()
    '''
    Perform processing and inference on text
    '''
    return output
```

## Imagery

### Bytes Decoding
*OpenCV*
```py
import cv2
import numpy as np
img = cv2.imdecode(np.frombuffer(input_bytes, np.uint8), -1)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
```

*Pillow*
```py
import io
from PIL import Image
img = Image.open(io.BytesIO(input_bytes)).convert("RGB")
```

See also:

* [Native PyTorch function](https://pytorch.org/docs/stable/generated/torch.frombuffer.html)
* [Native Tensorflow function](https://www.tensorflow.org/api_docs/python/tf/io/decode_raw)

### Corresponding `Process` Function
```python
def process(input_bytes):
    img = cv2.imdecode(np.frombuffer(input_bytes, np.uint8), -1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    '''
    Perform processing and inference on img
    '''
    return output
```

## Tabular

### Bytes Decoding
```python
from io import StringIO
import pandas as pd
input_table = pd.read_csv(StringIO(str(input_bytes, "utf-8")))
```

### Corresponding `Process` Function
```python
def process(input_bytes):
    input_table = pd.read_csv(StringIO(str(input_bytes, "utf-8")))
    '''
    Perform processing and inference on input_table
    '''
    return output
```
