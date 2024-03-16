package top

import (
	"github.com/spf13/cobra"

	"github.com/DavidHurta/edge-cloud/cloud-edge/cmd"
)

type options struct {
	kubeconfigPath string
	namespace      string
}

var o options

var topCmd = &cobra.Command{
	Use:   "top",
	Short: "Monitor running applications",
	Long: `The 'top' command enables you to monitor running services in a Kubernetes cluster.
	
Examples of usage:

To monitor services running in the namespace 'app':
$ cloud-edge top --namespace app --kubeconfig kubeconfig

To monitor services running in all namespaces:
$ cloud-edge top --namespace "" --kubeconfig kubeconfig

Note: 
The command utilizes the Kubernetes metrics API. Thus, a metrics-server must be
deployed in the cluster for the command to function.
	`,
	Run: func(cmd *cobra.Command, args []string) {
		o.kubeconfigPath, _ = cmd.Flags().GetString("kubeconfig")
		o.namespace, _ = cmd.Flags().GetString("namespace")
		run(o)
	},
}

func init() {
	cmd.RootCmd.AddCommand(topCmd)

	topCmd.PersistentFlags().StringP("kubeconfig", "k", "", "the path to the kubeconfig file")
	_ = topCmd.MarkPersistentFlagRequired("kubeconfig")

	topCmd.PersistentFlags().StringP("namespace", "n", "", "namespace to select pods; enter \"\" to select all pods in the cluster")
	_ = topCmd.MarkPersistentFlagRequired("namespace")
}
