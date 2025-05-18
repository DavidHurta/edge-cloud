<!-- 
#
# Documentation for the GitHub Action workflows used in the project.
#
# Author: David Hurta
#
-->

# GitHub Actions

## Implemented Workflows

### End-to-End Testing

A workflow to run the end-to-end testing for the overall project.

The definition is available [here](../.github/workflows/e2e.yml).

### Check format and compilation of Go source code

A workflow to check the format of Go source files and their compilation.

The definition is available [here](../.github/workflows/check_go.yml).

### Check Terraform format and validate the source code

A workflow to check and validate Terraform files.

The definition is available [here](../.github/workflows/check_terraform.yml).

### Build and Push Host Dependencies Container Image

A workflow to build and push the 'host-dependencies' container image that is used in
the end-to-end testing workflow.

The definition is available [here](../.github/workflows/build_and_push_host_dependencies.yml).

## Required Secrets

[GitHub Actions Documentation regarding secrets.](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions)

|name|description|
|-|-|
|DB_METRICS_HOST|Host of a MySQL database|
|DB_METRICS_PASSWORD|Password to the database|
|DB_METRICS_PORT|Port to the database|
|DB_METRICS_USER|User to be used upon login to the database|
|DOCKERHUB_TOKEN_READ|Read-only API token to a DockerHub container registry|
|DOCKERHUB_TOKEN_READ_WRITE|Read-and-Write API token to a DockerHub container registry|
|DOCKERHUB_USERNAME|User to be used upon login to the registry|
|DO_PRIVATE_SSH_KEY_CI|Private SSH key to be used to access hosts (must correlate to a specified SSH key upon provisioning of resource using the Terraform project)|
|DO_TOKEN|DigitalOcean API token to be used to provision resources|

## Required Variables

[GitHub Actions Documentation regarding variables.](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/store-information-in-variables)

|name|description|
|-|-|
|DB_METRICS_DATABASE|Name of the MySQL database to be used|
|HOST_DEPENDENCIES_IMAGE_REPO|Repository of the used container image to be used for host dependencies|
