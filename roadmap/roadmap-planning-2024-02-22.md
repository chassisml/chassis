Desired capabilities for the future of chassis:
 * Support for inferentia
 * LLM models are huge (2-7 billion paramters) need to put these models through something like TensorRT. It would be useful to have an easier way to deploy smaller more efficient models.
 * It would be great to build model images smaller and for builds to happen faster

Other desires:
 * Great to get rid of python. Can we eventually remove it entirely?

Is the Chassis SDK being used?
 * Yes, the CHassis SDK is in use. Some adjustments were required during the switch to v1.5 

Currently you're required to write out a process script to use chassis. How do we get rid of that?

The future idea would be to have the follow phases within a chassis container:
1. Bootstrapping
2. For each request you have raw data in
3. Pre-processing happens
4. Inference
5. Post-processing
6. Formatting

Right now 3-5 all happen all together, but they could be broken apart.
Acceleration is separated out which allows for inference to go through TensorRT, OpenVino, etc. Then you can pick out:
 * Pre-processor
 * Accelerator
 * Post-processor
 * Formatter
Can then natively compile everything to the hardware you're running on.
^Sounds great for the "happy path". Objections would be that if you want to do custom stuff, you'd have a hard time doing so.
We would still support a single predict function

Challenges include:
 * Python doesn't work well with gRPC
 * Can't cloud pickle
 * Other problems with how to give chassis info about the tensor format that's expected (e.g. in rust everything is statically typed, so we must know if it's a float, or int_32, etc.) so users would need to provide a lot more details

 What challenges can chassis solve that aren't already being solved today by other projects? Similar projects
 * https://github.com/ggerganov/llama.cpp
 * ONNX
 * Cog
 * Truss
 * BentoML

 What we like about chassis:
 * Portability: Write it once and then run it across nearly any device I'd like to run it on. Other providers can require more target-specific set-up.
 * Reproduceable: Everything is packaged end-to-end and contains all dependencies. Other systems require more work to go back in time to run previous versions of models. Downside is that it's less optimal.
 * Self-contained: Everything is grouped into one asset.
 * Simplifies pre and post-processing: Makes it easier to work with real data.

Taking a step back, what are we trying to do with chassis? Do we even care about what chassis is trying to solve at a high-level?

The best open source projects grow because they solve a real problem. Where is an area where this could be valuable?
 * This could be used for edge
 * This could be used to run across a range of tagets

 If we pick portability, that could include some kind of additional support for device-specific optimization?

Something important: Build once, run anywhere. The real value is being able to run it anywhere, but generally speaking data scientists know very little about getting models into production systems. This is a general problem for most companies trying to get machine learning models into production. This is why databricks is so popular.

Common refrain: "all I'm asking for is someone who knows data scientist and docker"

* Focus on automatically building inference containers for a set of specific target devices.
* Edge focus is phase n, cloud focus first.
* Cloud, desktops, laptops are the priority
* Focus on commodity hardware
* No specialized optimization, but let users select generic optimization options from a list (tensorRT, OpenVino)

Is it important to include pre-processing and post-processing?
 * Yes. The outputs from YOLO, for example, are some bounding boxes and need some specific outputs.

Is chassis a model server or an AI application server?
 * It's an API application.

Next steps:
 * Research similar projects
 * Develop proposed purpose statements by mid-March
 * Meet to discuss purpose and then refine roadmap priorities