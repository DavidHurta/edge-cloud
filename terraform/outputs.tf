#
# Defined Terraform output.
#
# Author: David Hurta
#

output "nodes" {
  value = {
    for instance in digitalocean_droplet.node :
    instance.name => {
      "VM name:            " = instance.name
      "Public IPv4 Address:" = instance.ipv4_address
    }
  }
}
