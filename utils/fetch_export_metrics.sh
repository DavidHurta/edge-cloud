#!/usr/bin/env bash

set -e 
set -o pipefail

TECHNOLOGY=$1

fetch_and_export () {
    METRIC_TYPE=$1
    QUERY=$2
    JOB_NAME=${METRIC_TYPE/_/-} # a Job name must not contain a character like `_`, replace them with `-`
    kubectl create job --image=curlimages/curl "$JOB_NAME" -- curl -s 'http://prometheus-server.prometheus.svc:80/api/v1/query' --data-urlencode "query=$QUERY"
    kubectl wait --for=condition=complete --timeout=60s job/"$JOB_NAME"
    kubectl logs job/"$JOB_NAME" | jq
    kubectl logs job/"$JOB_NAME" | ./utils/export_metrics.sh "$TECHNOLOGY" "$METRIC_TYPE"
}

########## PromQL queries for nodes ##########
# Queries based on https://stackoverflow.com/a/55451854 and https://www.robustperception.io/understanding-machine-cpu-usage/

# Memory used in percentages
fetch_and_export 'nodes_memory' '100 * (1 - ((avg_over_time(node_memory_MemFree_bytes[10m]) + avg_over_time(node_memory_Cached_bytes[10m]) + avg_over_time(node_memory_Buffers_bytes[10m])) / avg_over_time(node_memory_MemTotal_bytes[10m])))'

# CPU used in percentages
fetch_and_export 'nodes_cpu' '(1 - avg(irate(node_cpu_seconds_total{mode="idle"}[10m])) by (node)) * 100'

########## PromQL queries for containers ##########
# Queries based on https://stackoverflow.com/a/71574509

# Memory used in MB
# container_memory_working_set_bytes = "Current working set of the container in bytes" (https://kubernetes.io/docs/reference/instrumentation/metrics/)
fetch_and_export 'containers_memory' 'avg_over_time(container_memory_working_set_bytes{container!=""}[10m]) / (1024 * 1024)'

# Number of used CPU cores in millicores (1000 means a single core was fully utilized)
# container_cpu_usage_seconds_total = "Cumulative cpu time consumed by the container in core-seconds" (https://kubernetes.io/docs/reference/instrumentation/metrics/)
fetch_and_export 'containers_cpu' 'rate(container_cpu_usage_seconds_total{container!=""}[10m]) * 1000'
