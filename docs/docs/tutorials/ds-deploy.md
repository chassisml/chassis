# Deploy Model to KServe

<!-- TODO: add link to google colab notebook -->

## Install Required Dependencies

* Install [Docker Desktop](https://docs.docker.com/get-docker/)
    * Try to run `docker ps`
        * If you get a permissions error, follow instructions [here](https://docs.docker.com/engine/install/linux-postinstall/)
* Install KServe:
```bash
curl -s "https://raw.githubusercontent.com/kserve/kserve/release-0.7/hack/quick_install.sh" | bash
```

## Required variables

There are some environment variables that must be defined for KServe to work:

- INTERFACE: kserve
- HTTP_PORT: port where kserve will be running
- PROTOCOL: it can be v1 or [v2](https://github.com/kserve/kserve/tree/master/docs/predict-api/v2)
- MODEL_NAME: a name for the model must be defined

## Deploy the model

For this tutorial, we will use the Chassis-generated container image uploaded as `bmunday131/sklearn-digits`. To deploy to KServe, we will use the [file](https://github.com/modzy/chassis/blob/main/service/flavours/mlflow/interfaces/kfserving/custom_v1.yaml) that defines the `InferenceService` for the protocol v1 of KServe.

```yaml
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: chassisml-sklearn-demo
spec:
  predictor:
    containers:
    - image: bmunday131/sklearn-digits:0.0.1
      name: chassisml-sklearn-demo-container
      imagePullPolicy: IfNotPresent
      env:
        - name: INTERFACE
          value: kserve
        - name: HTTP_PORT
          value: "8080"
        - name: PROTOCOL
          value: v1
        - name: MODEL_NAME
          value: digits
      ports:
        - containerPort: 8080
          protocol: TCP
```

In this case, the variable `MODEL_NAME` should not be necessary since it's defined when creating the image.

```bash
kubectl apply -f custom_v1.yaml
```

This should output a success message.

## Define required variables to query the pod

This is needed in order to be able to communicate with the deployed image.

The `SERVICE_NAME` must match the name defined in the `metadata.name` of the `InferenceService` created above.

The `MODEL_NAME` must match the name of your model. It can be defined by the data scientist when [making the request against `Chassis` service](https://chassis.ml/tutorials/ds-connect/) or overwritten in the `InferenceService` as defined above.

Mac:
```bash
minikube tunnel

# in another terminal:
export INGRESS_HOST=localhost
export INGRESS_PORT=80
```

Linux:
```bash
export INGRESS_HOST=$(minikube ip)
export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')
```

Mac or Linux:
```bash
export SERVICE_NAME=chassisml-sklearn-demo
export MODEL_NAME=digits
export SERVICE_HOSTNAME=$(kubectl get inferenceservice ${SERVICE_NAME} -o jsonpath='{.status.url}' | cut -d "/" -f 3)
```

## Query the model

Please note that you must base64 encode each input instance. For example:

```python
import json
import base64 as b64
instances = [[1,2,3,4],[5,6,7,8]]
input_dict = {'instances': [b64.b64encode(str(entry).encode()).decode() for entry in instances]}
json.dump(input_dict,open('kserve_input.json','w'))
```

Now you can just make a request to predict some data. Take into account that you must download [`inputsv1.json`](https://github.com/modzy/chassis/blob/main/service/flavours/mlflow/interfaces/kserve/inputsv1.json) before making the request. 

```bash
curl -H "Host: ${SERVICE_HOSTNAME}" "http://${INGRESS_HOST}:${INGRESS_PORT}/v1/models/${MODEL_NAME}:predict" -d@inputsv1.json | jq
```

The output should be similar to this:

```json
{
  "predictions": [
    {
      "data": {
        "drift": null,
        "explanation": null,
        "result": {
          "classPredictions": [
            {
              "class": "4",
              "score": "1"
            }
          ]
        }
      }
    },
    {
      "data": {
        "drift": null,
        "explanation": null,
        "result": {
          "classPredictions": [
            {
              "class": "8",
              "score": "1"
            }
          ]
        }
      }
    },
    {
      "data": {
        "drift": null,
        "explanation": null,
        "result": {
          "classPredictions": [
            {
              "class": "8",
              "score": "1"
            }
          ]
        }
      }
    },
    {
      "data": {
        "drift": null,
        "explanation": null,
        "result": {
          "classPredictions": [
            {
              "class": "4",
              "score": "1"
            }
          ]
        }
      }
    },
    {
      "data": {
        "drift": null,
        "explanation": null,
        "result": {
          "classPredictions": [
            {
              "class": "8",
              "score": "1"
            }
          ]
        }
      }
    }
  ]
}
```

In this case, the data was prepared for the protocol v1, but we can deploy
the image using the protocol v2 and make the request using the [data for v2](https://github.com/modzy/chassis/blob/main/service/flavours/mlflow/interfaces/kserve/inputsv2.json).

## Deploy the model locally

The model can also be deployed locally:

```bash
docker run --rm -p 8080:8080 \
-e INTERFACE=kserve \
-e HTTP_PORT=8080 \
-e PROTOCOL=v2 \
-e MODEL_NAME=digits \
carmilso/chassisml-sklearn-demo:latest
```

So we can query it this way. Take into account that you must download [`inputsv2.json`](https://github.com/modzy/chassis/blob/main/service/flavours/mlflow/interfaces/kserve/inputsv2.json) before making the request:

```bash
curl localhost:8080/v2/models/digits/infer -d@inputsv2.json
```

## Tutorial in Action

Follow along as we walk through this tutorial step by step!

<style>
.video-wrapper {
  position: relative;
  display: block;
  height: 0;
  padding: 0;
  overflow: hidden;
  padding-bottom: 56.25%;
  border: 1px solid gray;
}
.video-wrapper > iframe {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 0;
}
</style>

<div class="video-wrapper">
  <iframe width="1280" height="720" src="https://youtube.com/embed/f46xzB4L6I4" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>
