package cmd

import (
	"os"

	"github.com/spf13/cobra"
)

var RootCmd = &cobra.Command{
	Use:   "cloud-edge",
	Short: "A CLI application to deploy and monitor services in a Kubernetes cluster.",
}

func Execute() {
	err := RootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func init() {}
