# Deployment of the Demonstration Kafka Application

The [demonstration Kafka application](https://github.com/DavidHurta/demo-edge-cloud-app)
is defined using Kubernetes manifest files in the
[`demo-app`](../demo-app/) directory, including a job to validate the application functionalities.

As of the moment, a pull secret is required for the `davoska/edge-cloud:latest` container image
to deploy the implemented Java services. A `docker-cfg` pull secret is defined in the manifest
files. Change the manifest files adequately if needed to specify another container image or
a different pull secret.

Thus, to deploy the application at the moment, create a pull secret. For example, by running:

```sh
$ kubectl create secret docker-registry docker-cfg --docker-username=$USERNAME --docker-password=$PASSWORD --namespace kafka-app
secret/docker-cfg created
```

Subsequently, the manifest files may be applied.
