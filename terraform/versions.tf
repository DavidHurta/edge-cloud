terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "2.39.2"
    }

    ansible = {
      source  = "ansible/ansible"
      version = "1.3.0"
    }
  }
}