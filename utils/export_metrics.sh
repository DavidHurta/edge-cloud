#!/usr/bin/env bash

#
# A script to filter out Prometheus metrics provided in the standard input
# and insert them into a MySQL database in a defined format.
#
# Author: David Hurta
#

set -e 
set -o pipefail

TECHNOLOGY=$1
METRIC_TYPE=$2

TABLE="metrics"

case "$METRIC_TYPE" in
    "nodes_cpu" | "nodes_memory")
        cat - | jq -c '.data.result[]' | while read -r res; do 
        # "edge" may match words such as "kubeedge"
        SOURCE=$(echo "$res" | jq -r '.metric.node' | grep -o -E "\-(infra|cloud|edge|control-plane)\-")
        SOURCE="${SOURCE:1}"
        SOURCE="${SOURCE::-1}"
        VALUE=$(echo "$res" | jq -r '.value[1]')
        echo "Inserting a record into the database"
        mysql --user="$DB_USER" --password="$DB_PASSWORD" --host "$DB_HOST" --port="$DB_PORT" \
        -e "INSERT INTO $DB_DATABASE.$TABLE (Source,Technology,Value,Recorded,MetricType) VALUES ('$SOURCE','$TECHNOLOGY','$VALUE',NOW(),'$METRIC_TYPE');"
        done
        ;;

    "containers_cpu" | "containers_memory")
        cat - | jq -c '.data.result[]' | while read -r res; do 
        SOURCE=$(echo "$res" | jq -r '.metric.container')
        VALUE=$(echo "$res" | jq -r '.value[1]')
        echo "Inserting a record into the database"
        mysql --user="$DB_USER" --password="$DB_PASSWORD" --host "$DB_HOST" --port="$DB_PORT" \
        -e "INSERT INTO $DB_DATABASE.$TABLE (Source,Technology,Value,Recorded,MetricType) VALUES ('$SOURCE','$TECHNOLOGY','$VALUE',NOW(),'$METRIC_TYPE');"
        done
        ;;

    *)
        echo "Unknown metric type: $METRIC_TYPE"
        exit 1
        ;;
esac
