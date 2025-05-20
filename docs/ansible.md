<!-- 
#
# Documentation for the Ansible project.
#
# Author: David Hurta
#
-->

# Ansible Project

The Ansible project enables to install the explored technologies on specified hosts.

It is recommended to be knowledgable regarding the main Ansible concepts and usage.

Visit the [Ansible documentation](https://docs.ansible.com/) to learn more.

## Prerequisites

Explore the [Ansible configuration file](../ansible.cfg) of the project to modify used
values, such as the location of the used private SSH key, location of the inventory file,
and more. Modify the values if necessary or specify them upon Ansible execution.

For example, by default, the location of the private key defaults to
`"$HOME/.ssh/id_ed25519"`, and the expected inventory file is `"terraform/inventory.yaml"`
to seamlessly integrate the Terraform and Ansible projects together.

## Usage Overview

Given a default configuration, install a technology by running the `ansible-playbook`. For example, to form a K3s cluster, run:

```sh
$ ansible-playbook playbooks/k3s.yaml 
```

The Kubeconfig will be created in the `playbooks` directory named as `kubeconfig`.

To use the kubeconfig using the `kubectl` tool, you may export its location. For example:

```sh
$ export KUBECONFIG="$(readlink -f playbooks/kubeconfig)"
$ kubectl get node
NAME                                     STATUS   ROLES           AGE     VERSION
default-cluster-cloud-8fc73ca7           Ready    cloud,worker    10m     v1.29.15
default-cluster-control-plane-c0d0ba8c   Ready    control-plane   11m     v1.29.15
default-cluster-edge-00acda60            Ready    edge,worker     10m     v1.29.15
default-cluster-infra-5a1e8ce8           Ready    infra           9m52s   v1.29.15
```

Create other technologies respectively. For example:

```sh
$ ansible-playbook playbooks/microk8s.yaml 
$ ansible-playbook playbooks/kubeedge.yaml 
$ ansible-playbook playbooks/kubernetes.yaml 
```

Makefile targets exist to simplify the usage using default values. For example to form a K3s cluster using an existing inventory file:

```sh
$ make k3s-setup
```

## Inventory Groups

The following are notable used Ansible Groups.

- `control_plane`: Control plane nodes. Control plane components and the Kubernetes metrics server are deployed.
- `infra`: Labeled infrastructure nodes. Prometheus server and relevant technologies are deployed. The Prometheus server is available at `http://prometheus-server.prometheus.svc` within the cluster.

  For example, to query the deployed Prometheus server within the cluster, run:

  ```sh
  curl -s 'http://prometheus-server.prometheus.svc:80/api/v1/query' --data-urlencode "query=$QUERY"
  ```

- `cloud`: Labeled cloud nodes intended for workload.
- `edge`: Labeled edge nodes intended for workload.
- `worker`: A set of `cloud` and `edge` nodes.

> [!NOTE]  
> High availability is not supported for all the technologies. Thus, precisely one host is supported for the `control_plane` group.

## Inventory File Structure Example

The project is intended to be used by combining the Terraform and Ansible projects. However, due to their nature they can be used separately. The following is an example structure expected by the written Ansible project.

```sh
$ ansible-inventory --graph
@all:
  |--@ungrouped:
  |--@cluster:
  |  |--@control_plane:
  |  |  |--161.35.216.170
  |  |--@worker:
  |  |  |--134.209.241.95
  |  |  |--165.227.138.3
  |  |--@infra:
  |  |  |--165.227.164.45
  |  |--@cloud:
  |  |  |--134.209.241.95
  |  |--@edge:
  |  |  |--165.227.138.3
```

The inventory can be viewed in more detail by running:

```sh
$ ansible-inventory --list
```

Output:

```json
{
    "_meta": {
        "hostvars": {
            "134.209.241.95": {
                "ansible_port": "22",
                "ansible_ssh_private_key_file": "~/.ssh/id_ed25519",
                "ansible_user": "root",
                "api_endpoint": "161.35.216.170",
                "ipv4_address": "134.209.241.95",
                "ipv4_address_private": "10.114.0.25",
                "kube_node_name": "default-cluster-cloud-8fc73ca7"
            },
            "161.35.216.170": {
                "ansible_port": "22",
                "ansible_ssh_private_key_file": "~/.ssh/id_ed25519",
                "ansible_user": "root",
                "api_endpoint": "161.35.216.170",
                "ipv4_address": "161.35.216.170",
                "ipv4_address_private": "10.114.0.27",
                "kube_node_name": "default-cluster-control-plane-c0d0ba8c"
            },
            "165.227.138.3": {
                "ansible_port": "22",
                "ansible_ssh_private_key_file": "~/.ssh/id_ed25519",
                "ansible_user": "root",
                "api_endpoint": "161.35.216.170",
                "ipv4_address": "165.227.138.3",
                "ipv4_address_private": "10.114.0.26",
                "kube_node_name": "default-cluster-edge-00acda60"
            },
            "165.227.164.45": {
                "ansible_port": "22",
                "ansible_ssh_private_key_file": "~/.ssh/id_ed25519",
                "ansible_user": "root",
                "api_endpoint": "161.35.216.170",
                "ipv4_address": "165.227.164.45",
                "ipv4_address_private": "10.114.0.24",
                "kube_node_name": "default-cluster-infra-5a1e8ce8"
            }
        }
    },
    "all": {
        "children": [
            "ungrouped",
            "cluster"
        ]
    },
    "cloud": {
        "hosts": [
            "134.209.241.95"
        ]
    },
    "cluster": {
        "children": [
            "control_plane",
            "worker",
            "infra",
            "cloud",
            "edge"
        ]
    },
    "control_plane": {
        "hosts": [
            "161.35.216.170"
        ]
    },
    "edge": {
        "hosts": [
            "165.227.138.3"
        ]
    },
    "infra": {
        "hosts": [
            "165.227.164.45"
        ]
    },
    "worker": {
        "hosts": [
            "134.209.241.95",
            "165.227.138.3"
        ]
    }
}
```
