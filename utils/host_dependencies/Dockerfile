#
# A Dockerfile of main dependencies for the overall project.
# Used for end-to-end testing by a project's GitHub Actions workflow.
# 
# Author: David Hurta
#

FROM ubuntu:24.04
WORKDIR /install-dependencies
COPY requirements.yaml ./

# Instal general needed dependencies 
RUN apt -y update && apt -y install curl python3 python3-pip wget lsb-release jq

# Install terraform
# https://developer.hashicorp.com/terraform/install
RUN wget -O - https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list
RUN apt -y update && apt -y install terraform

# Install kubectl
# https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
RUN install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install k3sup
# https://github.com/alexellis/k3sup?tab=readme-ov-file#download-k3sup-tldr
RUN curl -sLS https://get.k3sup.dev | sh

# Install helm
# https://helm.sh/docs/intro/install/#from-apt-debianubuntu
RUN curl https://baltocdn.com/helm/signing.asc | gpg --dearmor |  tee /usr/share/keyrings/helm.gpg > /dev/null
RUN apt-get install apt-transport-https --yes
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | tee /etc/apt/sources.list.d/helm-stable-debian.list
RUN apt-get update
RUN apt-get install helm

# Install pipx
# https://pipx.pypa.io/stable/installation/#on-linux
RUN apt update
RUN apt -y install pipx

# Install the binaries to a well known directory included in the $PATH variable
ENV PIPX_BIN_DIR="/usr/local/bin"
RUN pipx install --include-deps ansible==11.1.0
RUN pipx inject ansible jmespath==1.0.1

# Download keadm
RUN wget https://github.com/kubeedge/kubeedge/releases/download/v1.19.1/keadm-v1.19.1-linux-amd64.tar.gz
RUN tar -zxvf keadm-v1.19.1-linux-amd64.tar.gz
RUN cp keadm-v1.19.1-linux-amd64/keadm/keadm /usr/local/bin/keadm

# Download ansible dependencies
RUN mkdir -p /collections/ansible_collections && ansible-galaxy collection install --requirements-file requirements.yaml --collections-path /collections/ansible_collections

# Add mysql command to export metrics
RUN apt -y install default-mysql-client

# Install go
RUN wget https://go.dev/dl/go1.23.4.linux-amd64.tar.gz
RUN rm -rf /usr/local/go && tar -C /usr/local -xzf go1.23.4.linux-amd64.tar.gz
ENV PATH="$PATH:/usr/local/go/bin"

# Install pipenv
RUN pipx install pipenv

ENTRYPOINT [ "bash" ]