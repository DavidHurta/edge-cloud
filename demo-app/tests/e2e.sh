#!/usr/bin/env bash

#
# A script to verify that the kafka broker in the cloud contains the necessary number of
# cloud-server-01 messages. This verifies the overall microservice application.
#
# Author: David Hurta
#

set -x
cd /opt/bitnami/kafka/bin/ || exit
for i in $(seq 1 10);
do
    echo "RUN NUMBER: $i"
    ./kafka-topics.sh --topic cloud-server-01 --describe --bootstrap-server kafka-cloud:9092
    ./kafka-console-consumer.sh --bootstrap-server kafka-cloud:9092 --topic cloud-server-01 --from-beginning --max-messages 10 --timeout-ms 15000 > artifact.txt
    cat artifact.txt
    NUMBER_OF_MESSAGES=$(cat artifact.txt | wc -l)
    if [[ "$NUMBER_OF_MESSAGES" -eq "10" ]]; then
        # the file contains only messages, in case messages do not exist, it is empty
        exit 0
    fi
    sleep 30
done
echo "error: No messages found"
exit 1