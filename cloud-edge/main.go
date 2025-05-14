//
// Entry point for the application.
//
// Author: David Hurta
//

package main

import (
	"github.com/DavidHurta/edge-cloud/cloud-edge/cmd"

	_ "github.com/DavidHurta/edge-cloud/cloud-edge/cmd/apply"
	_ "github.com/DavidHurta/edge-cloud/cloud-edge/cmd/top"
)

func main() {
	cmd.Execute()
}
