#
# Required Terraform provider resource.
#
# Author: David Hurta
#

provider "digitalocean" {
  token = var.do_token
}