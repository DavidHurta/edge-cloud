//
// Helper package intended for various helper functions.
//
// Author: David Hurta
//

package helper

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"

	"github.com/DavidHurta/edge-cloud/cloud-edge/lib/constants"
)

func ExecuteCommand(cmd *exec.Cmd) (int, bytes.Buffer) {
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	if err := cmd.Run(); err != nil {
		fmt.Fprintln(os.Stderr, "", cmd.Stderr)
		if exitError, ok := err.(*exec.ExitError); ok {
			fmt.Fprintf(os.Stderr, "failed to execute: %s\n", cmd.Args)
			fmt.Fprintf(os.Stderr, "the command exited with a code: %d\n", exitError.ExitCode())
			fmt.Fprintf(os.Stderr, "the command exited with stderr: %s\n", stderr.String())
			return constants.ECCommandError, stdout
		}
		return constants.ECCommandError, stdout
	}
	return constants.ECSuccess, stdout
}
