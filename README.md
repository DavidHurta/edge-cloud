<!-- 
#
# The README file of the project.
#
# Author: David Hurta
#
-->

# Exploring the Cloud Edge World

## Documentation

To view the full documentation, including required dependencies, click [`here`](docs/README.md).

## Notes

- The project is being developed and tested on Ubuntu 24.04 LTS
- Developed using Kubernetes 1.29
- Project is intended to be used for learning, development, and testing purposes.

## Quick Usage Overview

To provision a default infrastructure run:

```sh
$ terraform -chdir=terraform/ apply -var do_token=${DO_PAT}
```

To configure the provisioned infrastructure to deploy a container management technology run:

```sh
# Supported technology values at the moment are: kubernetes, k3s, microk8s, kubeedge
$ ansible-playbook playbooks/${TECHNOLOGY}.yaml
```

To auto-provision and configure a default cluster of a chosen technology, run:

```sh
$ make ${TECHNOLOGY}
```

To build the CLI application `cloud-edge` run the following command to compile the application:

```sh
$ make build
```

An example of applying Kubernetes manifests using the subcommand `cloud-edge apply`:

```sh
$ ./bin/cloud-edge apply --directory demo-app/ --namespace kafka-app --create-namespace --kubeconfig playbooks/kubeconfig
The 'kafka-app' Namespace was successfully applied!
The resource 'apps/v1, Kind=Deployment' named 'demo-app-sensor' was successfully applied!
The resource 'apps/v1, Kind=Deployment' named 'demo-app-edge' was successfully applied!
The resource 'apps/v1, Kind=Deployment' named 'demo-app-cloud' was successfully applied!
The resource 'batch/v1, Kind=Job' named 'e2e' was successfully applied!
The resource 'apps/v1, Kind=Deployment' named 'kafka-cloud' was successfully applied!
The resource '/v1, Kind=Service' named 'kafka-cloud' was successfully applied!
The resource 'apps/v1, Kind=Deployment' named 'kafka-edge' was successfully applied!
The resource '/v1, Kind=Service' named 'kafka-edge' was successfully applied!
The resource '/v1, Kind=ConfigMap' named 'kafka-mirror-configuration' was successfully applied!
The resource 'apps/v1, Kind=Deployment' named 'kafka-mirror' was successfully applied!
The resource 'apps/v1, Kind=Deployment' named 'kafka-ui' was successfully applied!
```

An example of monitoring the created application using the subcommand `cloud-edge top`:

```sh
$ ./bin/cloud-edge top --namespace kafka-app --kubeconfig playbooks/kubeconfig
NAMESPACE   POD                                CONTAINER      STATUS      CPU(cores)   MEMORY(bytes)   NODE
kafka-app   demo-app-cloud-59c48df48c-f5nfz    app-cloud      Running     26m          100Mi           stage-cluster-cloud-d64a99bc
kafka-app   demo-app-edge-79bcc6f546-5gsbq     app-edge       Running     22m          130Mi           stage-cluster-edge-ecd6fad4
kafka-app   demo-app-sensor-55bf485dd8-7fkth   app-sensor     Running     26m          106Mi           stage-cluster-edge-ecd6fad4
kafka-app   demo-app-sensor-55bf485dd8-mvjrn   app-sensor     Running     28m          110Mi           stage-cluster-edge-ecd6fad4
kafka-app   e2e-9bdt4                          e2e            Completed   0m           0Mi             stage-cluster-cloud-d64a99bc
kafka-app   kafka-cloud-7985f5b6d-lrcq5        kafka-cloud    Running     102m         390Mi           stage-cluster-cloud-d64a99bc
kafka-app   kafka-edge-7fdb69fd47-b2j66        kafka-edge     Running     70m          405Mi           stage-cluster-edge-ecd6fad4
kafka-app   kafka-mirror-9f94d4dd9-77t54       kafka-mirror   Running     24m          441Mi           stage-cluster-edge-ecd6fad4
kafka-app   kafka-ui-5bfbfd49c-2ktqq           kafka-ui       Running     8m           240Mi           stage-cluster-cloud-d64a99bc

NODE                                   READY   CPU(cores)   MEMORY(bytes)
stage-cluster-cloud-d64a99bc           True    277m         1980Mi
stage-cluster-control-plane-9f50ec4d   True    119m         1001Mi
stage-cluster-edge-ecd6fad4            True    413m         3226Mi
stage-cluster-infra-cdcb9ee0           True    37m          961Mi
```
