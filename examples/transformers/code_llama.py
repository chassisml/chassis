# model imports
import torch
import transformers
from transformers import AutoTokenizer
torch.cuda.empty_cache()

# chassis imports
import json
import time
from typing import Mapping, Dict
from chassisml import ChassisModel
from chassis.builder import DockerBuilder, BuildOptions

# load model and dependencies
model = "codellama/CodeLlama-7b-hf"

tokenizer = AutoTokenizer.from_pretrained(model)
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    torch_dtype=torch.float16,
    device_map="auto",
)

# define predict function
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


# create chassis model
chassis_model = ChassisModel(predict)
chassis_model.add_requirements(["transformers", "torch", "accelerate"])
chassis_model.metadata.model_name = "Code Llama"
chassis_model.metadata.model_version = "0.0.1"
chassis_model.metadata.add_input(
    key="input",
    accepted_media_types=["text/plain"],
    max_size="5M",
    description="Code prompt"
)
chassis_model.metadata.add_output(
    key="generated_text",
    media_type="application/json",
    max_size="10M",
    description="Generated code by Code Llama model"
)

# test model
input = "# Python hello world function".encode()
results = chassis_model.test({"input": input})
print(results)

# build container
build_options = BuildOptions(cuda_version="11.0.3")
builder = DockerBuilder(chassis_model, build_options)

# local docker mode
start_time = time.time()
res = builder.build_image(name="code-llama", tag="0.0.1", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")