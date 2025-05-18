#
# A Makefile to simplify the usage of the project.
#
# Author: David Hurta
#

.PHONY: build
build:
	mkdir -p bin
	cd cloud-edge ; go build
	mv cloud-edge/cloud-edge bin/cloud-edge

.PHONY: all
all:
	build

.PHONY: format
format:
	terraform -chdir=terraform fmt

.PHONY: verify
verify: format
	terraform -chdir=terraform validate
	git diff --exit-code

# Targets to help quickly provision and configure default clusters.

provision:
	@terraform -chdir=terraform/ apply -var "do_token=${DO_PAT}"

auto-provision:
	@terraform -chdir=terraform/ apply -auto-approve -var "do_token=${DO_PAT}"

destroy:
	@terraform -chdir=terraform/ apply -auto-approve -var "do_token=${DO_PAT}" --destroy

k3s-setup:
	ansible-playbook playbooks/k3s.yaml

k3s: auto-provision k3s-setup

microk8s-setup:
	ansible-playbook playbooks/microk8s.yaml

microk8s: auto-provision microk8s-setup

kubernetes-setup:
	ansible-playbook playbooks/kubernetes.yaml

kubernetes: auto-provision kubernetes-setup

kubeedge-setup:
	ansible-playbook playbooks/kubeedge.yaml

kubeedge: auto-provision kubeedge-setup
