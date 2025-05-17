#
# Terraform resources for nodes.
#
# Author: David Hurta
#

locals {
  nodes = flatten([
    for cluster in var.clusters :
    [
      for node in cluster.nodes :
      {
        tags = concat((
          node.type == "control-plane" ? ["control-plane"] :
          node.type == "worker" ? ["worker"] :
          node.type == "infra" ? ["infra"] :
          node.type == "cloud" ? ["worker", "cloud"] :
          node.type == "edge" ? ["worker", "edge"] :
          []
        ), ["${var.run_name}-${cluster.name}-${random_id.cluster.hex}"])
        properties  = node
        cluster_ref = cluster
      }
    ]
  ])
  clusters = [
    for cluster in var.clusters : {
      id = "${var.run_name}-${cluster.name}-${random_id.cluster.hex}"
    }
  ]
}

resource "random_id" "cluster" {
  byte_length = 4
}

resource "random_id" "node" {
  count       = length(local.nodes)
  byte_length = 4
}

resource "digitalocean_tag" "cluster_tag" {
  count = length(local.clusters)
  name  = local.clusters[count.index].id
}

resource "digitalocean_droplet" "node" {
  count = length(local.nodes)

  image      = var.image
  name       = "${var.run_name}-${local.nodes[count.index].cluster_ref.name}-${local.nodes[count.index].properties.type}-${random_id.node[count.index].hex}"
  region     = var.region
  size       = var.size
  monitoring = true
  tags       = local.nodes[count.index].tags
  ssh_keys = [
    data.digitalocean_ssh_key.personal.id,
    data.digitalocean_ssh_key.ci.id
  ]

  connection {
    host    = self.ipv4_address
    user    = "root"
    type    = "ssh"
    timeout = "2m"
  }
}

resource "ansible_group" "cluster" {
  name     = "cluster"
  children = [ansible_group.control_plane.name, ansible_group.worker.name, ansible_group.infra.name, ansible_group.cloud.name, ansible_group.edge.name]
  variables = {
    "ansible_port"                 = 22
    "ansible_user"                 = "root"
    "api_endpoint"                 = length(digitalocean_loadbalancer.kube-loadbalancer) == 1 ? digitalocean_loadbalancer.kube-loadbalancer[0].ip : local.control_plane_nodes[0].ipv4_address
    "ansible_ssh_private_key_file" = var.pvt_key
  }
}

resource "ansible_group" "worker" {
  name = "worker"
}

resource "ansible_group" "control_plane" {
  name = "control_plane"
}

resource "ansible_group" "infra" {
  name = "infra"
}

resource "ansible_group" "cloud" {
  name = "cloud"
}

resource "ansible_group" "edge" {
  name = "edge"
}

resource "ansible_host" "host" {
  count = length(digitalocean_droplet.node)
  name  = digitalocean_droplet.node[count.index].ipv4_address
  groups = (
    # A node may have multiple tags, the following order of instructions is important due to precedence
    contains(digitalocean_droplet.node[count.index].tags, "control-plane") ? [ansible_group.control_plane.name] :
    contains(digitalocean_droplet.node[count.index].tags, "cloud") ? [ansible_group.worker.name, ansible_group.cloud.name] :
    contains(digitalocean_droplet.node[count.index].tags, "edge") ? [ansible_group.worker.name, ansible_group.edge.name] :
    contains(digitalocean_droplet.node[count.index].tags, "worker") ? [ansible_group.worker.name] :
    contains(digitalocean_droplet.node[count.index].tags, "infra") ? [ansible_group.infra.name] :
    []
  )
  variables = {
    "kube_node_name"       = digitalocean_droplet.node[count.index].name
    "ipv4_address"         = digitalocean_droplet.node[count.index].ipv4_address
    "ipv4_address_private" = digitalocean_droplet.node[count.index].ipv4_address_private
  }
}
