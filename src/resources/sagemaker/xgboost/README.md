# Selecting a custom Modzy base image
It is recommended that you use one of the following images:
```
326081595054.dkr.ecr.us-east-1.amazonaws.com/data-science/custom-images/modzy-py3.8-cuda-pt1.7:latest
326081595054.dkr.ecr.us-east-1.amazonaws.com/data-science/custom-images/modzy-py3.8-cuda-tf:latest
```

But there are also the following images:
```
326081595054.dkr.ecr.us-east-1.amazonaws.com/data-science/custom-images/modzy-py3.8:latest
326081595054.dkr.ecr.us-east-1.amazonaws.com/data-science/custom-images/modzy-py3.8-cuda:latest
326081595054.dkr.ecr.us-east-1.amazonaws.com/data-science/custom-images/modzy-py3.6:latest
326081595054.dkr.ecr.us-east-1.amazonaws.com/data-science/custom-images/modzy-py3.6-cuda:latest
326081595054.dkr.ecr.us-east-1.amazonaws.com/data-science/custom-images/modzy-py3.6-cuda-keras:latest
326081595054.dkr.ecr.us-east-1.amazonaws.com/data-science/custom-images/modzy-py3.6-cuda-pt1.2:latest
```

# A quick tour
Some noteworthy files and directories:
- `asset_bundle/*`
    - contains marketplace content such as demo inputs and outputs, documentation, etc...
- `flask_psc_model/*`
    - utility package that implements the container specification API with Flask; this shouldn't need to be edited (eventually the goal is to have this be an external pip installable library)
- `model_lib/*` 
    - an example model library package
- `model_lib/model.py`
    - contains the `ColorNamePredictorModel` class that wraps the model logic into an interface that the `flask_psc_model` package can understand
- `tests/*`
    - unit tests
- `app.py`
    - definition of the model app where we wrap the model defined in `model_lib` with the utilities from `flask_psc_model` 
- `Dockerfile`
    - the app container definition 
- `entrypoint.sh`
    - the script used to start the app server inside the container
- `gunicorn.conf.py`
    - configuration file for the Gunicorn web server used in the Docker container
- `model.yaml`
    - the model metadata containing documentation and technical requirements
- `requirements.txt`
    - pinned python library dependencies for reproducable environments

# Building and running the demo container
```bash
# build the app server image
docker build -t model-template:latest .

# run the app server container on port 8080
docker run --name model-template -e PSC_MODEL_PORT=8080 -p 8080:8080 -v /data:/data -d model-template:latest

# check the container status
curl -s "http://localhost:8080/status"

# run some inference jobs using curl
echo ffaa00 > /data/input.txt
curl -s -X POST -H "Content-Type: application/json" \
    --data "{\"type\":\"file\",\"input\":\"/data\",\"output\":\"/data\"}" \
    "http://localhost:8080/run"
cat /data/results.json

# or run some inference jobs using the utility cli
echo ffaa00 > /data/input.txt
python -m flask_psc_model.cli.run_job --url "http://localhost:8080/run" --input /data --output /data
cat /data/results.json

# stop the app server
curl -s -X POST "http://localhost:8080/shutdown"
# check that we exited with exit code 0
docker inspect model-template --format="{{.State.Status}} {{.State.ExitCode}}"
# cleanup the exited docker container
docker rm model-template

# save the container to a tar archive
docker save -o model-template-latest.tar model-template:latest
```

# Installing and running the dev server locally (no container)
```
# create and activate a virtual environment
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
# ^ if using Anaconda Python use conda to create a virtual env and install requirements instead

# run the app script
python app.py
# or use the Flask runner
FLASK_APP=app.py flask run

# now you can use `curl` or the `flask_psc_model.cli.run_job` to run jobs
# as described above
```

# Running the unit tests
```
# locally
python -m unittest

# in docker
docker run --rm --memory 512m --cpus 1 --shm-size 0m model-template:latest python -m unittest
```

Note that for Docker the `memory` and `cpus` values are set to match those stated in the resources section of the `model.yaml` file in order to match the resources that will be given to the deployed container (`shm-size` is set to 0 to check that the container is not using shared memory that may be limited when deployed). Adjust the values as needed when running the container, and remember to update the values in the `model.yaml` file!

If test files are large it may be better to exclude them from your model container. If excluded, you could instead mount the test directory as a volume into your application container and run the tests that way:

```
# in docker with test files mounted as a volume
docker run --rm --memory 512m --cpus 1 --shm-size 0m -v $(pwd)/test:/opt/app/test model-template:latest python -m unittest
```

Note that while very useful to ensure that your model code is working properly, the unit tests don't check that the container is configured properly to communicate with the outside world. 

You can manually test the container API using `curl` or other HTTP clients or the cli runner discussed above. _[TODO: better way to automate this sort of external container testing.]_

# Minimal checklist to implement a new model
The following are the basic steps needed to update this repository with your own model:
1. Create a copy of the repository or copy these files into your existing repository.
1. Update the `model.yaml` metadata file with information about your model; ignore the "resources" and "timeout" section until after you implement the full containerized model. _This is a recommended first step because it will force you to think about the inputs and outputs of your model before you write any code :)_
1. Remove `model_lib` and replace with your model code.
1. Update the `requirements.txt` file with any additional dependencies for your model.
1. Define a class that extends from the `flask_psc_model.ModelBase` abstract base class and implements the required abstract methods.
    
    Your class will need to define:
    - `input_filenames`
    - `output_filenames`
    - `run`
    
    See `model_lib/model.py` for an example implementation and `flask_psc_model.ModelBase` docstrings for more info.
1. Update `app.py` to configure the model app with your newly implemented model class.
1. Update and write new unit tests in `tests/`.

    You will need to:
    - Add new test case data to `tests/data/` with sample inputs and expected outputs. 
        - The `examples` directory should contain files that are expected to run successfully along with their expected results. 
        - The `validation-error` directory should contain files that are not expected to run successfully along with expected error message text in order to test the model's error handling.
    - Add any model specific unit tests you desire to `tests/test_model.py`.
    - Update the application unit tests `tests/test_app.py` for your specific model. In particular, you may need to:
        - Update the `check_results` function to validate that the actual application run results match the expected results.
1. Increase the "timeout" in `model.yaml` if your model needs longer to run in the worst case (this will be loaded by the Gunicorn configuraton file and used to kill your model code if it takes too long to run).
1. Update the `Dockerfile` with all of your model app's code, data, and runtime dependencies.
1. Use the `Dockerfile` to build your container image and test things out.
1. Use the container image to determine appropriate final values for the "resources" and "timeout" sections of the `model.yaml` metadata file.

---------------------------------------------

# Docker Container Specification
The Docker container must expose an HTTP API on the port specified by the `PSC_MODEL_PORT` environment 
variable that implements the `/status`, `/run`, and `/shutdown` routes detailed below.

The container must start the HTTP server process by default when run with no command argument, e.g. 
when run as:
```bash
docker run image
```

You should use the _exec_ syntax in your Dockerfile to define a `CMD` that starts the server process:
```docker
COPY entrypoint.sh ./
CMD ["./entrypoint.sh"]
```

# HTTP API Specification

> The implementation of this HTTP API is provided by the `flask_psc_model` package.

## Response DTO:
_All_ routes should return `application/json` of the following format in the response body:
```
{
    "statusCode": 200,
    "status": "OK",
    "message": "the call went well or terribly"
}
```
The message should provide useful feedback on the cause of any model errors.

## status [GET /status]
Returns the status of the model (after doing any necessary model initialization).
+ Response
    + Status 200 - model is ready to run
    + Status 500 - error loading model

## run [POST /run]
Runs the model inference on a given input.
+ Request
    + Body - the job configuration object (`application/json`)
        ```
        {
            "type": "file",
            "input": "/path/to/input/directory",
            "output": "/path/to/output/directory"
        }
        ```
        - `type`: (reserved for future use) the type of the input and output; at this time this value will always be "file" 
        - `input`: the filesystem directory path from which the model should read input data files; this will exist prior to this HTTP route being called
        - `output`: the filesystem directory path where the model should write output data files; any files should be written prior to returning from the HTTP call
        
        The filenames for input and output files contained within the input and output directories will be specified in the model metadata.
+ Response
    + Status 200 - successful inference
    + Status 400 - invalid job configuration object
        - the job configuration object is malformed or the expected files do no exist or cannot be read or written
        - when running on the platform this should never occur but may be useful for debugging
    + Status 415 - invalid media type
        - the client did not post `application/json` in the HTTP body
        - when running on the platform this should never occur but may be useful for debugging
    + Status 422 - unprocessable input file
        - the model cannot run inference on the provided input files (for example an input file may be the wrong format, too large, too small, etc)
        - the response message should contain a detailed validation error that explains why the model cannot process a given input file
    + Status 500 - unexpected error running model

## shutdown [POST /shutdown]
The model server process should exit with exit code 0.
+ Request
    + Body - empty
+ Response (*the model server is not required to send a response and may simply drop the connection; however a response is encouraged*)
    + Status 202 - request accepted
        - the server process will exit after returning the response
    + Status 500 - unexpected error
