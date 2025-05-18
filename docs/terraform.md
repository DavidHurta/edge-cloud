<!-- 
#
# Documentation for the Terraform project.
#
# Author: David Hurta
#
-->

# Terraform Project

There are several ways to utilize the Terraform project. It is recommended to be knowledgable
regarding the main Terraform concepts and usage.

Visit the [Terraform documentation](https://developer.hashicorp.com/terraform) to learn more.

## Prerequisites

### Required DigitalOcean Scopes

A personal access token for DigitalOcean is needed. The following are the required scopes.

|               | create | read | update | delete |
|---------------|:------:|:----:|:------:|:------:|
| account       |        |   ✅  |        |        |
| droplet       |    ✅   |   ✅  |    ✅   |    ✅   |
| firewall      |    ✅   |   ✅  |    ✅   |    ✅   |
| load_balancer |    ✅   |   ✅  |    ✅   |    ✅   |
| ssh_key       |        |   ✅  |        |        |
| tag           |    ✅   |   ✅  |       |    ✅   |

DigitalOcean may require additional scopes to be added to make the selection functional.

Export the token:

```sh
$ export DO_PAT=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Required DigitalOcean SSH Keys

The access to provisioned hosts is only allowed using SSH keys in the project.

Register public SSH keys in DigitalOcean named `ci` and `personal` to allow SSH connection
to provisioned hosts using the respective private keys.

## Usage

Assuming default values, provision a default cluster (defined [here](../terraform/terraform.tfvars)) of one control-plane, cloud, edge, and infrastructure node using:

```sh
$ make provision
```

You can also run the following command to auto-approve the provisioning:

```sh
$ make auto-provision
```

The equivalents to the mentioned commands are:

```sh
$ terraform -chdir=terraform/ apply -var "do_token=${DO_PAT}"
$ terraform -chdir=terraform/ apply -auto-approve -var "do_token=${DO_PAT}"
```

> [!IMPORTANT]  
> Do not forget to deprovision the resources!

To deprovision resources, run:

```sh
$ terraform -chdir=terraform/ apply -var "do_token=${DO_PAT}" --destroy
```

or run the following command to deprovision resources and auto-approve the decision:

```sh
$ make destroy
```

## Available Input Variables

The available variables are defined and available [here](../terraform/variables.tf).

The most notable variables are `clusters`, `firewall`, `size`, and `pvt_key`.

- `clusters`: Define a cluster topology (defaults to the mentioned default topology).
Based on this information, the Ansible project configures the nodes respectively.
- `firewall`: Configure a firewall (defaults to `disabled`).
- `size`: The used size of provisioned hosts (defaults to `"s-2vcpu-4gb"`).
- `pvt_key`: The file path to the private key to be used to access the hosts (defaults to `"~/.ssh/id_ed25519"`).

You may specify a variables files such as the [`terraform.tfvars`](../terraform/terraform.tfvars) file with all the information, provide flags, or combine both of the options.

For example, to specify a specific variables files, run:

```sh
$ terraform -chdir=terraform/ apply -var do_token=${DO_PAT} -var-file=terraform_large_cluster.tfvars
```

For example, to provision a default cluster with an enabled firewall and an allowed IP using the CLI command, run:

```sh
$ terraform -chdir=terraform/ apply -var do_token=${DO_PAT} -var="firewall={\"enabled\"=true,\"allowed_ip\":\"${PUBLIC_IP}\"}"
```

To provision a cluster of four nodes, including a single control-plane node, cloud, edge, 
and infrastructure node, define the following content:

```shell
clusters = [
  {
    name = "cluster"
    nodes = [
      {
        type = "control-plane"
      },
      {
        type = "infra"
      },

      {
        type = "cloud"
      },

      {
        type = "edge"
      },
    ]
  }
]
```
