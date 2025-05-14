//
// The internal logic for the top subcommand of the cobra command.
//
// Author: David Hurta
//

package apply

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/util/yaml"
	applyconfigurationscorev1 "k8s.io/client-go/applyconfigurations/core/v1"
	"k8s.io/client-go/discovery"
	"k8s.io/client-go/dynamic"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/restmapper"
	"k8s.io/client-go/tools/clientcmd"

	"github.com/DavidHurta/edge-cloud/cloud-edge/lib/constants"
)

// Default buffer size for a document 5 MB
const bufferSize = 5 * 1e6

// Default field manager name
// A field manager name is required for the Apply method
const fieldManagerName = "cloudedge-cli"

type generic map[string]interface{}

func run(o options) {
	config, err := clientcmd.BuildConfigFromFlags("", o.kubeconfigPath)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Failed to create the configuration from the %s kubeconfig file: %s\n", o.kubeconfigPath, err.Error())
		os.Exit(constants.ECCommandError)
	}

	if o.createNamespace {
		client, _ := kubernetes.NewForConfig(config)
		namespace := applyconfigurationscorev1.Namespace(o.namespace)
		_, err = client.
			CoreV1().
			Namespaces().
			Apply(context.TODO(), namespace, metav1.ApplyOptions{FieldManager: fieldManagerName})
		if err != nil {
			_, _ = fmt.Fprintf(os.Stderr, "Failed to create the '%s' namespace: %s\n", o.namespace, err.Error())
			os.Exit(constants.ECCommandError)
		}
		fmt.Printf("The '%s' Namespace was successfully applied!\n", o.namespace)
	}

	// Create needed clients
	dynamicClient, err := dynamic.NewForConfig(config)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Failed to create a dynamic client: %s\n", err.Error())
		os.Exit(constants.ECCommandError)
	}

	discoveryClient, err := discovery.NewDiscoveryClientForConfig(config)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Failed to create a discovery client: %s\n", err.Error())
		os.Exit(constants.ECCommandError)
	}

	// To create an unstructured resource the GVR and GVK mapping is needed
	apiGroupResources, err := restmapper.GetAPIGroupResources(discoveryClient)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Failed to get API group resources: %s\n", err.Error())
		os.Exit(constants.ECCommandError)
	}
	mapper := restmapper.NewDiscoveryRESTMapper(apiGroupResources)

	// Iterate over YAML manifests files and apply the manifests
	// Exit on an error
	files, err := os.ReadDir(o.manifestsDirectory)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Failed to read the '%s' directory: %s\n", o.manifestsDirectory, err.Error())
		os.Exit(constants.ECCommandError)
	}
	for _, file := range files {
		path := filepath.Join(o.manifestsDirectory, file.Name())
		if !strings.HasSuffix(path, ".yaml") && !strings.HasSuffix(path, ".yml") {
			continue
		}

		// A YAML file may contain multiple objects
		// Iterate over them using the YAMLOrJSONDecoder
		content, _ := os.ReadFile(path)
		decoder := yaml.NewYAMLOrJSONDecoder(bytes.NewReader(content), bufferSize)
		objects := []generic{}
		var err error
		for {
			object := make(generic)
			err = decoder.Decode(&object)
			if err != nil {
				break
			}
			objects = append(objects, object)
		}
		if err != io.EOF {
			_, _ = fmt.Fprintf(os.Stderr, "Error while decoding the '%s' manifest file: %s\n", path, err.Error())
			os.Exit(constants.ECCommandError)
		}

		// Iterate over the found objects in the YAML manifest file
		for _, object := range objects {
			u := &unstructured.Unstructured{
				Object: object,
			}

			// Get resource mapping for the current GVK
			gvk := u.GroupVersionKind()
			mapping, err := mapper.RESTMapping(gvk.GroupKind(), gvk.Version)
			if err != nil {
				_, _ = fmt.Fprintf(os.Stderr, "Failed to get REST mapping for the '%s' GVK: %s\n", gvk.String(), err.Error())
				os.Exit(constants.ECCommandError)
			}

			// Attempt to apply the resource
			_, err = dynamicClient.
				Resource(mapping.Resource).
				Namespace(o.namespace).
				Apply(context.TODO(), u.GetName(), u, metav1.ApplyOptions{FieldManager: fieldManagerName})
			if err != nil {
				_, _ = fmt.Fprintf(os.Stderr, "Failed to create the '%s' '%s' resource: %s\n", gvk, u.GetName(), err.Error())
				os.Exit(constants.ECCommandError)
			}
			fmt.Printf("The resource '%s' named '%s' was successfully applied!\n", gvk.String(), u.GetName())
		}
	}
	os.Exit(constants.ECSuccess)
}
