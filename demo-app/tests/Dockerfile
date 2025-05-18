#
# A Dockerfile used to build an image containing the e2e.sh script
#
# Author: David Hurta
#

FROM docker.io/bitnami/kafka:3.6
COPY e2e.sh .
ENTRYPOINT [ "./e2e.sh" ]
