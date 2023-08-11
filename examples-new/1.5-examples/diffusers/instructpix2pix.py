
import time
import torch
import PIL
from PIL import Image
from diffusers import StableDiffusionInstructPix2PixPipeline, EulerAncestralDiscreteScheduler

import io
from typing import Mapping, Dict
from chassisml import ChassisModel
from chassis.builder import DockerBuilder, BuildOptions

# load model and define pipeline from diffusers package
model_id = "timbrooks/instruct-pix2pix"
pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(model_id, torch_dtype=torch.float16, safety_checker=None)
pipe.to("cuda")
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

# code directly from Hugging Face
# # download sample data
# url = "https://raw.githubusercontent.com/timothybrooks/instruct-pix2pix/main/imgs/example.jpg"
# def download_image(url):
#     image = PIL.Image.open(requests.get(url, stream=True).raw)
#     image = PIL.ImageOps.exif_transpose(image)
#     image = image.convert("RGB")
#     return image
# image = download_image(url)
# image.save("example.jpg")

# run inference
# img = Image.open("data/example.jpg").convert("RGB")
# prompt = "turn him into captain america"
# images = pipe(prompt, image=img, num_inference_steps=10, image_guidance_scale=1).images

# define predict function
def predict(inputs: Mapping[str, bytes]) -> Dict[str, bytes]:
    img = Image.open(io.BytesIO(inputs['image'])).convert("RGB")
    text = inputs['prompt'].decode()
    image_results = pipe(text, image=img, num_inference_steps=10, image_guidance_scale=1).images
    with io.BytesIO() as output:
        image_results[0].save(output, format="PNG")
        contents = output.getvalue()
    return {'results.png': contents}

# create chassis model object
chassis_model = ChassisModel(process_fn=predict)
# add metadata & requirements
chassis_model.add_requirements(["diffusers", "accelerate", "safetensors", "transformers", "Pillow"])
chassis_model.metadata.model_name = "Stable Diffusion Instruct Pix2Pix"
chassis_model.metadata.model_version = "0.0.1"
chassis_model.metadata.add_input(
    key="image",
    accepted_media_types=["image/jpeg", "image/png"],
    max_size="10M",
    description="Input image to be modified or transformed"
)
chassis_model.metadata.add_input(
    key="prompt",
    accepted_media_types=["text/plain"],
    max_size="1M",
    description="Text prompt with instructions for the model"
)
chassis_model.metadata.add_output(
    key="results.png",
    media_type="image/png",
    max_size="10M",
    description="AI-generated image based on input image and instructions prompt"
)

# test model
img_path = open("data/example.jpg", 'rb').read()
text = b"turn him into captain america"
results = chassis_model.test({"image": img_path, "prompt": text})
# test output results
test = Image.open(io.BytesIO(results[0]['results.png'])).convert("RGB")
test.save("example_out.png")


# define build options and builder object
build_options = BuildOptions(cuda_version="11.6.2")
builder = DockerBuilder(package=chassis_model, options=build_options)

# local docker mode
start_time = time.time()
res = builder.build_image(name="stable-diffusion-instructpix2pix", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")



