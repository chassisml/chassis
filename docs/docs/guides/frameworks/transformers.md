
This page provides examples that build model containers from models developed from the **[:hugging: Transformers](https://huggingface.co/docs/transformers/index)** library.

Each example requires the `transformers` package be installed at a minimum. Use pip to install this in your Python environment:

```bash
pip install transformers
```

<!-- !!! tip "GPU Recommended"
    Like most computer vision-based and Generative AI-based models, fast performance is heavily dependent on available hardware resources. For a smoother experience, it is highly recommended that you only follow these examples if you have access to a GPU.  -->


## Text Classification

This example was adapted from the `bhadresh-savani/distilbert-base-uncased-emotion` model from Hugging Face. View the original model card [here](https://huggingface.co/bhadresh-savani/distilbert-base-uncased-emotion).


!!! info "Source Code"
    If you prefer to view the source code directly, reference this example and utility data files [here](https://github.com/modzy/chassis/blob/main/examples/transformers/distilbert_text_classification.py).

First, install the additional dependencies required by this model.

```bash
pip install torch numpy
```

Now, simply copy the below example code in your Python environment and editor of choice. 

!!! example

    The below code can be used to build a model container out of a transformers example model. Be sure to view the code annotations for more details.

    === "Python"

    ```python
    import time
    import json
    import torch
    import numpy as np
    from typing import Mapping, Dict
    from transformers import AutoTokenizer, AutoModelForSequenceClassification #(1)

    from chassisml import ChassisModel #(2)
    from chassis.builder import DockerBuilder #(3)

    # load model with AutoTokenizer package #(4)
    tokenizer = AutoTokenizer.from_pretrained("bhadresh-savani/distilbert-base-uncased-emotion")
    distilbert_model = AutoModelForSequenceClassification.from_pretrained("bhadresh-savani/distilbert-base-uncased-emotion")

    # define labels from model config #(5)
    labels = distilbert_model.config.id2label

    # define predict function #(6)
    def predict(inputs: Mapping[str, bytes]) -> Dict[str, bytes]:
        text = inputs['input.txt'].decode()
        inputs = tokenizer(text, return_tensors="pt")
        # run preprocessed data through model
        with torch.no_grad():
            logits = distilbert_model(**inputs).logits
            softmax = torch.nn.functional.softmax(logits, dim=1).detach().cpu().numpy()
            
        # postprocess 
        indices = np.argsort(softmax)[0][::-1]
        results = {
            "data": {
                "result": {
                    "classPredictions": [{"class": labels[i], "score": round(softmax[0][i].item(), 4)} for i in indices]
                }
            }
        }        
        return {'results.json': json.dumps(results).encode()}

    # create chassis model object
    chassis_model = ChassisModel(process_fn=predict)                       # (7)
    # add metadata & requirements
    chassis_model.add_requirements(["transformers", "torch", "numpy"])     # (8)
    chassis_model.metadata.model_name = "DistilBERT Text Classification"   # (9)
    chassis_model.metadata.model_version = "0.0.1"
    chassis_model.metadata.add_input(                                                                    
        key="input.txt",
        accepted_media_types=["text/plain"],
        max_size="10M",
        description="Input text to be classified by model"
    )
    chassis_model.metadata.add_output(
        key="results.json",
        media_type="application/json",
        max_size="1M",
        description="Classification predictions of six emotions classes and the corresponding confidence score"
    )

    # test model  # (10)
    text = open("data/input.txt", 'rb').read()
    results = chassis_model.test({"input.txt": text})
    print(results)

    # define builder object # (11)
    builder = DockerBuilder(package=chassis_model)    

    # local docker mode #(12)
    start_time = time.time()
    res = builder.build_image(name="distilbert-text-classification", show_logs=True)
    end_time = time.time()
    print(res)
    print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")
    ```

    1. Here, we simply import the objects we will need from the `transformers` library
    2. Now, we will import the `ChassisModel` class from the Chassis SDK    
    3. In addition to the `ChassisModel` object, we need to import a Builder object. The two available options, `DockerBuilder` and `RemoteBuilder`, will both build the same container but in different execution environments. Since we'd like to build a container locally with Docker, we will import the `DockerBuilder` object.     
    4. Here, we are loading our model in the exact way the model card on Hugging Face recommends
    5. With our loaded model, we can access the human-readable labels the model can predict. We will load them into a `labels` variable and reference it in our `predict` function below
    6. Here, we will define a *single* predict function, which you can think of as an inference function for your model. This function can access in-memory objects (e.g., `tokenizer`, `distilbert_model`, and `labels` which are all in-memory objects loaded above), and the only requirement is it must convert input data from raw bytes form to the data type your model expects. See this **[guide](../common-data-types.md)** for help on converting common data types. In this example, we process the raw bytes text data with a Python native `decode()` function, pass this processed data through to our model for predictions, and encode the output as base64-encoded JSON.  
    7. Now, we will simply create a `ChassisModel` object directly from our predict function.
    8. With our `ChassisModel` object defined, there are a few optional methods we can call. Here, we will add the Python libraries our model will need to run. You can pass a list of packages you would list in a `requirements.txt` file that will be installed with Pip.
    9. In the next few lines, we will define the four minimum metadata fields that are required before building our container. These fields represent your model's name, version, inputs, and outputs. *NOTE: There are many other optional fields you can choose to document if preferred.* 
    10. Before kicking off the Chassis job, we can test our `ChassisModel` object by passing through sample data.
    11. After our test has passed, we can prepare our model build context. To do so, we will define our builder object, which as mentioned before, will be `DockerBuilder`. This builder object uses your local Docker daemon to build a model container and store it on your machine.
    12. With our builder object defined with our model predict function, we can kick off the build using the `DockerBuilder.build_image` function to build a Docker container locally.

## Code Llama (LLM)

This example was adapted from the `codellama/CodeLlama-7b-hf` Code Llama model in the Hugging Face Transformers format. View the original model card [here](https://huggingface.co/codellama/CodeLlama-7b-hf).


!!! info "Source Code"
    If you prefer to view the source code directly, reference this example and utility data files [here](https://github.com/modzy/chassis/blob/main/examples/transformers/code_llama.py).

!!! tip "GPU Recommended"
    Large Language Models (LLMs) are very resource intensive and run better with accelerated hardware. For a smoother experience, it is highly recommended that you only follow these examples if you have access to a GPU.

!!! warning "Disk Storage Needed"
    This LLM results in a container that is roughly 20GB in size. Ensure your machine has enough disk space left to handle this container before continuing.     

First, install the additional dependencies required by this model.

```bash
pip install torch accelerate
```

Now, simply copy the below example code in your Python environment and editor of choice. 

!!! example

    The below code can be used to build a model container from Meta's Code Llama base model (7B params). Be sure to view the code annotations for more details.

    === "Python"

    ```python
    import json
    import time
    from typing import Mapping, Dict    
    import torch
    import transformers
    from transformers import AutoTokenizer #(1)
    torch.cuda.empty_cache() 

    from chassisml import ChassisModel #(2)
    from chassis.builder import DockerBuilder, BuildOptions #(3)

    # load model and dependencies #(4)
    model = "codellama/CodeLlama-7b-hf"

    tokenizer = AutoTokenizer.from_pretrained(model)
    pipeline = transformers.pipeline(
        "text-generation",
        model=model,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    # define predict function #(5)
    def predict(inputs: Mapping[str, bytes]) -> Dict[str, bytes]:
        prompt = inputs['input'].decode()
        sequences = pipeline(
            prompt,
            do_sample=True,
            top_k=10,
            temperature=0.1,
            top_p=0.50,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
            max_length=500,
        )
        return {"generated_text": json.dumps(sequences[0]["generated_text"]).encode()}

    # create chassis model object
    chassis_model = ChassisModel(process_fn=predict)                            # (6)
    # add metadata & requirements
    chassis_model.add_requirements(["transformers", "torch", "accelerate"])     # (7)
    chassis_model.metadata.model_name = "Code Llama"                            # (8)
    chassis_model.metadata.model_version = "0.0.1"
    chassis_model.metadata.add_input(                                                                    
        key="input",
        accepted_media_types=["text/plain"],
        max_size="10M",
        description="Code prompt"
    )
    chassis_model.metadata.add_output(
        key="generated_text",
        media_type="application/json",
        max_size="10M",
        description="Generated code by Code Llama model"
    )

    # test model  # (9)
    input = "# Python hello world function".encode()
    results = chassis_model.test({"input": input})
    print(results)

    # define builder object # (10)
    build_options = BuildOptions(cuda_version="11.0.3")
    builder = DockerBuilder(chassis_model, build_options)

    # local docker mode #(11)
    start_time = time.time()
    res = builder.build_image(name="distilbert-text-classification", show_logs=True)
    end_time = time.time()
    print(res)
    print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")
    ```

    1. Here, we simply import the objects we will need from the `transformers` library
    2. Now, we will import the `ChassisModel` class from the Chassis SDK    
    3. In addition to the `ChassisModel` object, we need to import a Builder object. The two available options, `DockerBuilder` and `RemoteBuilder`, will both build the same container but in different execution environments. Since we'd like to build a container locally with Docker, we will import the `DockerBuilder` object. Notice we also import `BuildOptions`. We will use this object to define the cuda version our models needs to run.     
    4. Here, we are loading our model in the exact way the model card on Hugging Face recommends. In this example, we will use the transformers pipeline functionality.
    5. Here, we will define a *single* predict function, which you can think of as an inference function for your model. This function can access in-memory objects (e.g., `tokenizer` and `pipeline`, which are both in-memory objects loaded above), and the only requirement is it must convert input data from raw bytes form to the data type your model expects. See this **[guide](../common-data-types.md)** for help on converting common data types. In this example, we process the raw bytes text data with a Python native `decode()` function, pass this processed data through to our model for predictions, and encode the output as base64-encoded JSON.  
    6. Now, we will simply create a `ChassisModel` object directly from our predict function.
    7. With our `ChassisModel` object defined, there are a few optional methods we can call. Here, we will add the Python libraries our model will need to run. You can pass a list of packages you would list in a `requirements.txt` file that will be installed with Pip.
    8. In the next few lines, we will define the four minimum metadata fields that are required before building our container. These fields represent your model's name, version, inputs, and outputs. *NOTE: There are many other optional fields you can choose to document if preferred.* 
    9. Before kicking off the Chassis job, we can test our `ChassisModel` object by passing through sample data.
    10. After our test has passed, we can prepare our model build context. To do so, we will define our builder object, which as mentioned before, will be `DockerBuilder`. This builder object uses your local Docker daemon to build a model container and store it on your machine. We will also define a `BuildOptions` variable, which allows us to configure container-level dependencies, including cuda version, architecture(s) to build, and more.
    11. With our builder object defined with our model predict function, we can kick off the build using the `DockerBuilder.build_image` function to build a Docker container locally.