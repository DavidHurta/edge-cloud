#
# Terraform variables file.
#
# Author: David Hurta
#

variable "do_token" {
  sensitive = true
}
variable "pvt_key" {
  default = "~/.ssh/id_ed25519"
}
variable "region" {
  default = "fra1"
}
variable "image" {
  default = "ubuntu-24-04-x64"
}
variable "size" {
  default = "s-2vcpu-4gb"
}
variable "run_name" {
  default = "default"
}
variable "firewall" {
  type = object({
    enabled    = bool
    allowed_ip = string
  })
  default = {
    enabled    = false
    allowed_ip = "0.0.0.0"
  }
}

variable "clusters" {
  type = list(object({
    name = string

    nodes = list(object({
      type = string
    }))
  }))

  default = [
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

  validation {
    condition = alltrue([
      for cluster in var.clusters :
      alltrue([
        for node in cluster.nodes : contains(["edge", "cloud", "infra", "worker", "control-plane"], node.type)
      ])
    ])
    error_message = "A node type must be `control-plane`, `worker`, `infra`, `cloud`, or `edge`."
  }

  validation {
    condition     = length(var.clusters) == 1
    error_message = "Only one cluster is supported as of this time."
  }
}