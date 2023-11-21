# Introduction

## What does an Admission Controller Webhook do?

An Admission Controller Webhook is triggered when a Kubernetes resource (or resources) is created, modified or deleted. Essentially a HTTP request is sent to a specified Kubernetes Service in a namespace which returns a JSON response. Depending on that response an action is taken.

There are two categories of Admission Controllers, Validating and Mutating. A Validating Admission Controller validates the incoming request and returns a binary response, yes or no based on custom logic. An example can be that if a Pod resource doesn’t have certain labels the request is rejected with a message on why. A Mutating Admission Controller modifies the incoming request based on custom logic. An example can be that if an Ingress resource doesn’t have the correct annotations, the correct annotations will be added and the resource will be admitted.

# Writing a Validating Admission Controller Webhook

## Scenario

Specification:

- We are going to validate a Deployment, Pod and Statefulset resources to check it has a label `manage_by` with specific value `abriment`. If the label is not present then we reject the request.
- The above will happen when a new Deployment, Pod and Statefulset is created in namespaces with specific label `abriment/validation-webhooks: 'enabled'`.

## How to deploy

- First, we write a flask webservice:
    - Fetches the incoming request object. In our case we can assume the object will always be a Deployment resource when we register our Validating Controller below.
    - Check if the `manage_by` label exists and have `abriment`value . Return a JSON HTTP response if present with the allowed boolean set to True and a message.
    - If the above condition is not met we will always reject any resources from being created.

- Create a Docker image from validate.py with Flask and jsonify installed with [Dockerfile](./validate/Dockerfile)

- Generate a self signed CA, generate a csr and cert then create a secret based on this cert. with [certgen.sh](./validate/certgen.sh)

    I use these values:

    ```
    countryName                 = US
    stateOrProvinceName         = Illinois
    localityName                = Chicago
    organizationName            = Abriment
    commonName                  = Abriment Controller Webhook
    ```

- Create a Deployment from the created Docker image in a namespace. The service must be secured via SSL. Mount the secret created from the previous step as volumes in the Deployment. Also we can add certs in docker image.

- Create a Service pointing to the correct ports in same namespace as the Deployment.

- Register our [Validating Controller (ValidatingWebhookConfiguration)](./validate/webhook.yaml)


### Test and validate

First create namespace with `abriment/validation-webhooks: 'enabled'` lable because `namespaceSelector` in `webhook.yaml` is set to this value. If namespace doesn't have this lable this admission controller doesn't validate.

```bash
kubectl run testpod --image=nginx -n alirez
# Error from server: admission webhook "label-abriment.admission-controller.svc" denied the request: No labels exist. A manage_by label is required

kubectl run testpod2 --image=nginx -n alirez -l manage_by=ali
# Error from server: admission webhook "label-abriment.admission-controller.svc" denied the request: Wrong value for manage_by label

kubectl run testpod3 --image=nginx -n alirez -l manage_by=abriment
# pod/testpod3 created
```


# Writing a Mutating Admission Controller Webhook