#!/usr/bin/env bash

#
# A script to build and push the container image defined in 
# the `utils/host_dependencies/Dockerfile file`
#
# Author: David Hurta
#

repository="${1:-docker.io/davoska/edge-cloud-host-dependencies}"
short_hash=$(git rev-parse --short HEAD)
docker build --no-cache --push --file utils/host_dependencies/Dockerfile . --tag "${repository}:${short_hash}" --tag "${repository}":latest
