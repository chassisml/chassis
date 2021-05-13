# Model Converter execution notes

## AWS connection

In order to gain access to resources on AWS more specifically ECR, it is necessary to set the following two keys as environment variables:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

## Importer service

The current implementation of the model converter assumes that the model-importer is running a service in the following location:

`http://MODZY_MI_HOST:MODZY_MI_PORT`

It means that the variables to be set for this are `MODZY_MI_HOST` where the service is hosted and `MODZY_MI_PORT` where input connections are received. The latter is not required and if empty it will make a standard call without port which goes to port 80 by default.

One important requirement for this `model-importer` service is that it is enaled to connect to a DB for example `intdev-db`.

## ECR connection

This implementation relies on the Kaniko framework for establishing a connection to ECR. It will then use an ECR Java client to fulfill some of the steps of the integration workflow.
1. Login to ECR
2. Issuing a ping command to verify connectivity
3. Try to create an ECR repository for hosting the newly created image or reuse an existing one
4. Verify if the image pushed with Kaniko exists in the repository.

The required input settings of this endpoint are the following ones:
- `MODZY_MC_ECR_REGISTRY`: The expected format for this value is the following `https://<registry_id>.dkr.ecr.<region_code>.amazonaws.com`.
- `MODZY_MC_ECR_REPO`: An ECR repository where the image will be registered.
- `MODZY_MC_ECR_USER`: It is a constant string set as `AWS`, according to AWS documentation.

## Kaniko settings

In order for kaniko to run as a service within **model-converter** container it is required to set the following environment variables with the specific values as shown below.

`AWS_SHARED_CREDENTIALS_FILE="/kaniko/.aws/credentials"`

`DOCKER_CONFIG="/kaniko/.docker"`

`AWS_SDK_LOAD_CONFIG="true"`

**Model-converter** will take care of provisioning any corresponding files for the container to run appropriately.

## Other settings

`MODZY_EXEC_ENVIRONMENT`: This represents where the deployed model image can be pulled from the modzy platform.

`MODZY_MC_DIR`: It has to be set as the path where `model-converter` will find the `app_config.yaml` with internal application settings.

## Docker

In order to generate the container for model-converter implementation the steps are as follows:

1. Build the image, if executed in model-converter host directory, an example would be:
   `docker build -t model-converter:latest .`

2. Run the created image, this will contain all the previously mentioned settings for executing the integration:
   `docker run -e AWS_ACCESS_KEY_ID=<xxxxxx> -e AWS_SECRET_ACCESS_KEY=<xxxxx> -e AWS_SHARED_CREDENTIALS_FILE="/kaniko/.aws/credentials" -e DOCKER_CONFIG="/kaniko/.docker" -e AWS_SDK_LOAD_CONFIG="true"  -e MODZY_MI_HOST=localhost -e MODZY_MI_PORT=9001 -e MODZY_MC_ECR_REGISTRY=https://<registry_id>.dkr.ecr.<region_code>.amazonaws.com -e MODZY_MC_ECR_REPO=data-science/model-converter -e MODZY_MC_ECR_USER=AWS -e MODZY_MC_DIR=src/main/resources/app_config.yml -e MODZY_EXEC_ENVIRONMENT=intdev1.modzy.engineering --name mc -d -p 8080:8080 --rm model-converter:latest`
   
## User Requests

- *aws_key_id* and *aws_access_key*: User access keys for retrieving artifac ts in s3.
- *s3Bucket*: Bucket name where the artifacts can be found.
- *weightsPath* and *resourcesPath*: Location within the s3 bucket were the model output and additional user provided resources can be provided. 
- *platform*: The model provider where the input artifacts were generated.
- *model_type*: The model type to be converted, it can eventually be any models incorporated inside the converter.

### These are the available routes within the model-converter service

1. `env-status`: It is used to check if any of the required variables is missing or not

#### Example request

`http://localhost:8080/env-status`

2. `check-endpoints`: It is a dry run to verify that the different interacting components are available and ready.
#### Example request

`http://localhost:8080/check-endpoints?aws_key_id=<xxxxx>&aws_access_key=<xxxxx>&s3Bucket=sagemaker-testing-ds&weightsPath=fm-sm%2Fmodel.tar.gz&resourcesPath=fm-sm%2Fresources.tar.gz&platform=sagemaker&model_type=factorization-machines`

3. `run-converter`: Kicks off the complete execution of **model-converter** pipeline.
#### Example request
`http://localhost:8080/run-converter?aws_key_id=AKIAUX272I2XL6D3MX7N&aws_access_key=M3Yq1VGhOaySVp8YjXRCZcOXl5zj5kNvgOVk5Oh4&s3Bucket=sagemaker-testing-ds&weightsPath=XGBoost%2Fweights.tar.gz&resourcesPath=XGBoost%2Fresources.tar.gz&platform=sagemaker&model_type=xgboost`