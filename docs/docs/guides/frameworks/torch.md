
This page provides examples that build model containers from models developed with **[:simple-pytorch: PyTorch](https://pytorch.org/)**.

Each example requires the `torch` package be installed at a minimum. Use pip to install this in your Python environment:

```bash
pip install torch
```

## ResNet 50 Image Classification

This example was adapted from the `torchvision` guides for using pre-trained models and weights. View the **[torchvision](https://pytorch.org/vision/main/models.html)** documentation for reference.


!!! info "Source Code"
    If you prefer to view the source code directly, reference this example and utility data files [here](TODO - add link).

First, install the additional dependencies required by this model.

```bash
pip install torchvision Pillow
```

Now, simply copy the below example code in your Python environment and editor of choice. 

!!! example

    The below code can be used to build a model container from a `torchvision` pre-trained image classification model. Be sure to view the code annotations for more details.

    === "Python"

    ```python
    import time
    import io
    import json
    import torch
    from PIL import Image
    from typing import Mapping, Dict
    from torchvision.models import resnet50, ResNet50_Weights #(1)

    from chassisml import ChassisModel #(2)
    from chassis.builder import DockerBuilder #(3)

    # load and initialize model with the best available weights #(4)
    weights = ResNet50_Weights.DEFAULT 
    model = resnet50(weights=weights)
    model.eval() #(5)

    # define the inference transforms
    preprocess = weights.transforms() #(6)

    # define predict function #(7)
    def predict(inputs: Mapping[str, bytes]) -> Dict[str, bytes]:
        
        # preprocess
        decoded = Image.open(io.BytesIO(inputs['image'])).convert("RGB")
        batch = preprocess(decoded).unsqueeze(0)
        
        # run inference and apply softmax
        prediction = model(batch).squeeze(0).softmax(0)
        
        # postprocess and format results
        _, indices = torch.sort(prediction, descending=True)
        print(indices[:5])
        inference_result = {
            "classPredictions": [
                {"class": weights.meta["categories"][idx.item()], "score": round(prediction[idx].item(),4)}
            for idx in indices[:5] ]
        }

        structured_output = {
            "data": {
                "result": inference_result,
                "explanation": None,
                "drift": None,
            }
        }
        
        return {'results.json', json.dumps(structured_output).encode()}

    # create chassis model object
    chassis_model = ChassisModel(process_fn=predict)                        # (8)
    # add metadata & requirements
    chassis_model.add_requirements(["torch", "torchvision", "Pillow"])      # (9)
    chassis_model.metadata.model_name = "ResNet 50 Image Classification"    # (10)
    chassis_model.metadata.model_version = "0.0.1"
    chassis_model.metadata.add_input(                                                                    
        key="image",
        accepted_media_types=["image/jpeg", "image/png"],
        max_size="10M",
        description="Image to be classified by model"
    )
    chassis_model.metadata.add_output(
        key="results.json",
        media_type="application/json",
        max_size="1M",
        description="Classification predictions including human-readable label and the corresponding confidence score"
    )

    # test model # (11)
    img_bytes = open("data/airplane.jpg", 'rb').read()
    results = chassis_model.test({"image": img_bytes})
    print(results)

    # define builder object # (12)
    builder = DockerBuilder(package=chassis_model)    

    # local docker mode # (13)
    start_time = time.time()
    res = builder.build_image(name="resnet5-image-classification", show_logs=True)
    end_time = time.time()
    print(res)
    print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")

    ```

    1. Here, we simply import the pre-trained ResNet 50 weights file and architecture
    2. Now, we will import the `ChassisModel` class from the Chassis SDK    
    3. In addition to the `ChassisModel` object, we need to import a Builder object. The two available options, `DockerBuilder` and `RemoteBuilder`, will both build the same container but in different execution environments. Since we'd like to build a container locally with Docker, we will import the `DockerBuilder` object.     
    4. Here, we will load our model using the torchvision models method and will pass the pre-trained weights as a parameter
    5. It is important to set your model to `eval` mode. This will turn off layers only applicable for training
    6. Our in-memory model object includes an embedded preprocessing object that we will extract into its own variable
    7. Here, we will define a *single* predict function, which you can think of as an inference function for your model. This function can access in-memory objects (e.g., `preprocess` and `model`), and the only requirement is it must convert input data from raw bytes form to the data type your model expects. See this **[guide](../how-to-guides/common-data-types.md)** for help on converting common data types. In this example, we process the raw bytes and convert to an image using the Pillow library, pass this processed data through to our model for predictions, and encode the output as base64-encoded JSON.  
    8. Now, we will simply create a `ChassisModel` object directly from our predict function.
    9. With our `ChassisModel` object defined, there are a few optional methods we can call. Here, we will add the Python libraries our model will need to run. You can pass a list of packages you would list in a `requirements.txt` file that will be installed with Pip.
    10. In the next few lines, we will define the four minimum metadata fields that are required before building our container. These fields represent your model's name, version, inputs, and outputs. *NOTE: There are many other optional fields you can choose to document if preferred.* 
    11. Before kicking off the Chassis job, we can test our `ChassisModel` object by passing through sample data.
    12. After our test has passed, we can prepare our model build context. To do so, we will define our builder object, which as mentioned before, will be `DockerBuilder`. This builder object uses your local Docker daemon to build a model container and store it on your machine.
    13. With our builder object defined with our model predict function, we can kick off the build using the `DockerBuilder.build_image` function to build a Docker container locally.
