resource "digitalocean_firewall" "cluster" {
  name  = local.clusters[count.index].id
  count = var.firewall.enabled == true ? length(local.clusters) : 0
  tags  = [local.clusters[count.index].id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "1-65535"
    source_addresses = [var.firewall.allowed_ip]
    source_tags      = [local.clusters[count.index].id]
  }

  inbound_rule {
    protocol         = "udp"
    port_range       = "1-65535"
    source_addresses = [var.firewall.allowed_ip]
    source_tags      = [local.clusters[count.index].id]
  }

  inbound_rule {
    protocol         = "icmp"
    source_addresses = [var.firewall.allowed_ip]
    source_tags      = [local.clusters[count.index].id]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  depends_on = [digitalocean_tag.cluster_tag]
}
