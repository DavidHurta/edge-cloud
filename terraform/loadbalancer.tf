#
# Load balancer definition.
#
# Author: David Hurta
#

locals {
  # By evaluating whether a load-balancer is needed from input data, Terraform is able to 
  # determine the decision at plan stage. Using `control_plane_nodes` results in
  # the Terraform not being being able to determine the decision until the apply stage.
  loadbalancer_enabled = length([
    for node in local.nodes : node
    if contains(node.tags, "control-plane")
  ]) > 1

  control_plane_nodes = [
    for node in digitalocean_droplet.node : node
    if contains(node.tags, "control-plane")
  ]
}

resource "digitalocean_loadbalancer" "kube-loadbalancer" {
  name   = "loadbalancer-${var.run_name}"
  region = var.region
  count  = local.loadbalancer_enabled ? 1 : 0

  forwarding_rule {
    entry_port     = 6443
    entry_protocol = "tcp"

    target_port     = 6443
    target_protocol = "tcp"
  }

  // MicroK8s control nodes communicate over the 16443 port
  forwarding_rule {
    entry_port     = 16443
    entry_protocol = "tcp"

    target_port     = 16443
    target_protocol = "tcp"
  }

  forwarding_rule {
    entry_port     = 22
    entry_protocol = "tcp"

    target_port     = 22
    target_protocol = "tcp"
  }

  healthcheck {
    port     = 22
    protocol = "tcp"
  }

  droplet_ids = [for instance in local.control_plane_nodes : instance.id]
}