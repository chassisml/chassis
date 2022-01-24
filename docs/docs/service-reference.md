# Chassisml API Reference 

Welcome to the Chassisml API Reference documentation homepage. The API is designed using the principles of REST services using standard HTTP verbs and status codes, implemented with [Flask](https://flask.palletsprojects.com/en/2.0.x/). On this page, you will find documentation for:

* Available REST endpoints in API Service
* Methods implemented within the each endpoint

## Endpoints

**`/health`** *(GET)*

* Confirms Chassis service is up and running 

**`/build`** *(POST)*

* Kicks off the container image build process

**`/job/{job_id}`** *(GET)*

* Retrieves the status of a chassis `/build` job

**`/job/{job_id}/download-tar`** *(GET)*

* Retrieves docker image tar archive from a volume attached to the Kubernetes cluster hosting chassis and downloads it to a local filepath

**`/test`** *(POST)*

* Creates a conda environment as specified by the user's model artifacts and runs the `ChassisModel` to ensure the model code can run within the provided conda environment


::: service.app
    :docstring:
    selection:
        members:
            - create_job_object
            - get_job_status
            - download_tar
            - build_image
            - test_model
    rendering:
        show_source: true
        show_category_heading: true
        show_root_toc_entry: false
        show_if_no_docstring: false
