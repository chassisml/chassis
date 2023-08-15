# Reference Documentation


## Chassis Basics
Chassis's goal is to make it easier for Python developers to turn machine learning models into fully-feature, containerized ML services.

Since machine learning tends to happen in Python, Chassis was made to be Python-first, meaning that anything you need to define about how your ML model must operate as a service (e.g. writing a custom pre-processing, specifying if a GPU is required, asking for a specific Python or package versions, etc.) can be done simply in Python. After specifying how you want your model service to work, Chassis takes over the process of turning your trained model into a self-contained, ML-specific container image.

| Step 1: Define model details in Python 	| Step 2: Run builder.build_image() 	| Step 3: Receive ready-to-run model image 	|
|---	|---	|---	|
| Define model info with a simple python script 	| Send model info off to be built into a container 	| Get back a self-contained ML container image 	|
| <ul>  <li>Load a pre-trained model</li> <li>Define a predict function</li> <li>List PIP dependencies</li> <li>Set harware requirements</li> <li>[Optional] Add model docs</li> </ul> 	| <ul> <li>Selects base image</li> <li>Implements APIs</li> <li>Defines layers</li> <li>Constructs image with Kaniko</li> </ul> 	| <ul> <li>Bakes in model, dependencies, and server</li> <li>Provides `run`, `status`, and `shutdown` RPCs</li> <li>Runs on docker, containerD, Modzy, and more</li> </ul> 	|

## Detailed Reference Docs
1. **Chassis SDK**: Full reference documentation for the Chassisml SDK Python package, which includes two namespace packages included within the library. For usage examples, visit our [Guides Section](../guides/index.md)
2. **[Interfaces](./interfaces.md)**: Provides summaries and explanations of the container interfaces Chassis supports

