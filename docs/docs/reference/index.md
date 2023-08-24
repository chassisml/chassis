# Reference

## Chassis Basics
Chassis's goal is to make it easier for Python developers to turn machine learning models into fully-feature, containerized ML services.

Since machine learning development is typically performed in Python, Chassis was made to be a Python-first library, meaning that anything you need to define about how your ML model must operate as a service (e.g. writing a custom preprocessor, specifying if a GPU is required, asking for a specific Python or package versions, etc.) can be done simply in Python. After specifying how you want your model service to work, Chassis takes over the process of turning your trained model into a self-contained, ML-specific container image.

| 1: Define model details in Python 	| 2: Run builder.build_image() 	| 3: Receive ready-to-run model image 	|
|---	|---	|---	|
| Define model info with a simple python script 	| Send model info off to be built into a container 	| Get back a self-contained ML container image 	|
| You will:<ul>  <li>Load a pre-trained model</li> <li>Define a predict function</li> <li>List PIP dependencies</li> <li>Set harware requirements</li> <li>[Optional] Add model docs</li> </ul> 	| Chassis will:<ul> <li>Select base image</li> <li>Implement APIs</li> <li>Define layers</li> <li>Construct image</li> </ul> 	| Resulting image:<ul> <li>Bakes in model, dependencies, and server</li> <li>Provides `run`, `status`, and `shutdown` RPCs</li> <li>Runs on Docker, containerd, Modzy, and more</li> </ul> 	|

<div>
    <p><img style="float:right;max-width:60%;max-height:450px;padding-left:5em" src="../images/inside-chassis.png">One might wonder, what does a chassis container include? In short, it bakes in all of the code, dependencies, and other resources needed to run the model it was built around.<br/><br/>
    This includes all of the artifacts that define the model itself, pre and post-proessing, the inference function, and the weights file. This also include the specific Python version and packages that your model relies upon. If you optionally provide model documentation, it provides a model card, of sorts, that can be accessed anytime the container is running. Finally, the container provides a server that makes the model available for inference.</p>
</div>
