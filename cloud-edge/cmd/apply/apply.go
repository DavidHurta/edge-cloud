package apply

import (
	"github.com/spf13/cobra"

	"github.com/DavidHurta/edge-cloud/cloud-edge/cmd"
)

type options struct {
	manifestsDirectory string
	kubeconfigPath     string
	namespace          string
	createNamespace    bool
}

var o options

var applyCmd = &cobra.Command{
	Use:   "apply",
	Short: "Deploy applications",
	Long: `The 'apply' command enables you to apply Kubernetes manifest files via the API server.

Examples of usage:

Apply all Kubernetes manifest files in the 'app' directory to the 'app' namespace.
Create the namespace if it does not already exists:

$ ./cloud-edge apply --directory app --namespace app --create-namespace --kubeconfig kubeconfig
	`,
	Run: func(cmd *cobra.Command, args []string) {
		o.manifestsDirectory, _ = cmd.Flags().GetString("directory")
		o.kubeconfigPath, _ = cmd.Flags().GetString("kubeconfig")
		o.namespace, _ = cmd.Flags().GetString("namespace")
		o.createNamespace, _ = cmd.Flags().GetBool("create-namespace")
		run(o)
	},
}

func init() {
	cmd.RootCmd.AddCommand(applyCmd)
	applyCmd.PersistentFlags().StringP("directory", "d", "", "the directory that contain the Kubernetes YAML manifests to be applied")
	_ = applyCmd.MarkPersistentFlagRequired("directory")

	applyCmd.PersistentFlags().StringP("kubeconfig", "k", "", "the path to the kubeconfig file")
	_ = applyCmd.MarkPersistentFlagRequired("kubeconfig")

	applyCmd.PersistentFlags().StringP("namespace", "n", "", "the namespace into which apply the manifests")
	_ = applyCmd.MarkPersistentFlagRequired("namespace")

	applyCmd.PersistentFlags().BoolP("create-namespace", "c", false, "indicate whether to create the specified namespace before applying manifests into it")
}
