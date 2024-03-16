data "digitalocean_ssh_key" "personal" {
  name = "personal"
}

data "digitalocean_ssh_key" "ci" {
  name = "ci"
}