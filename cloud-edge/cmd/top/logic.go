package top

import (
	"context"
	"fmt"
	"os"
	"text/tabwriter"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
	metricsv1beta1 "k8s.io/metrics/pkg/apis/metrics/v1beta1"
	metricsclientset "k8s.io/metrics/pkg/client/clientset/versioned"

	"github.com/DavidHurta/edge-cloud/cloud-edge/lib/constants"
)

func run(o options) {
	w := tabwriter.NewWriter(os.Stdout, 1, 1, 3, ' ', 0)

	config, err := clientcmd.BuildConfigFromFlags("", o.kubeconfigPath)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Failed to create the configuration from the %s kubeconfig file: %s\n", o.kubeconfigPath, err.Error())
		os.Exit(constants.ECCommandError)
	}

	// Create clients
	metricsClient, err := metricsclientset.NewForConfig(config)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Failed to create the metrics client: %s\n", err.Error())
		os.Exit(constants.ECCommandError)
	}

	client, err := kubernetes.NewForConfig(config)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Failed to create the kubernetes client: %s\n", err.Error())
		os.Exit(constants.ECCommandError)
	}

	// Fetch pod information and metrics
	pods, err := client.CoreV1().Pods(o.namespace).List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Failed to list pods: %s\n", err.Error())
		os.Exit(constants.ECCommandError)
	}

	podMetricses, err := metricsClient.MetricsV1beta1().PodMetricses(o.namespace).List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Failed to list pod metrics: %s\n", err.Error())
		os.Exit(constants.ECCommandError)
	}

	// Output status of pods
	fmt.Fprintln(w, "NAMESPACE\tPOD\tCONTAINER\tSTATUS\tCPU(cores)\tMEMORY(bytes)\tNODE")
	for _, pod := range pods.Items {
		var podMetrics metricsv1beta1.PodMetrics
		for _, p := range podMetricses.Items {
			if p.Name == pod.Name {
				podMetrics = p
				break
			}
		}
		for _, containerStatus := range pod.Status.ContainerStatuses {
			status := ""
			var cpu, memory int64

			switch {
			case containerStatus.State.Waiting != nil:
				status = containerStatus.State.Waiting.Reason
				if status == "" {
					status = "Waiting"
				}
			case containerStatus.State.Running != nil:
				status = "Running"
			case containerStatus.State.Terminated != nil:
				status = containerStatus.State.Terminated.Reason
				if status == "" {
					status = "Terminated"
				}
			default:
				status = "Waiting"
			}

			for _, container := range podMetrics.Containers {
				if container.Name == containerStatus.Name {
					cpu = container.Usage.Cpu().MilliValue()
					memory = container.Usage.Memory().Value() / (1024 * 1024)
					break
				}
			}

			// Formatting inspired by https://github.com/kubernetes/kubectl/blob/master/pkg/metricsutil/metrics_printer.go
			fmt.Fprintf(w, "%s\t%s\t%s\t%s\t%dm\t%dMi\t%s\n", pod.Namespace, pod.Name, containerStatus.Name, status, cpu, memory, pod.Spec.NodeName)
		}
	}

	// Fetch node information and metrics
	nodes, err := client.CoreV1().Nodes().List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Failed to list nodes: %s\n", err.Error())
		os.Exit(constants.ECCommandError)
	}

	nodesMetricses, err := metricsClient.MetricsV1beta1().NodeMetricses().List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Failed to list node metrics: %s\n", err.Error())
		os.Exit(constants.ECCommandError)
	}

	// Output status of nodes
	fmt.Fprintln(w, "\nNODE\tREADY\tCPU(cores)\tMEMORY(bytes)")
	for _, node := range nodes.Items {
		var cpu, memory int64
		for _, n := range nodesMetricses.Items {
			if n.Name == node.Name {
				cpu = n.Usage.Cpu().MilliValue()
				memory = n.Usage.Memory().Value() / (1024 * 1024)
				break
			}
		}

		status := "Unknown"
		for _, cond := range node.Status.Conditions {
			if cond.Type == "Ready" {
				status = string(cond.Status)
				break
			}
		}

		fmt.Fprintf(w, "%s\t%s\t%dm\t%dMi\n", node.Name, status, cpu, memory)
	}
	w.Flush()
	os.Exit(constants.ECSuccess)
}
