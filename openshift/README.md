# OpenShift Deployment Guide for Project Audit Tool

This guide provides the steps to build and deploy the Project Audit Tool to an OpenShift cluster.

## Prerequisites

1.  You have access to an OpenShift cluster.
2.  You have the `oc` (OpenShift CLI) tool installed and configured.
3.  You are logged into your OpenShift cluster (`oc login ...`).
4.  You have a project created in OpenShift. If not, create one using `oc new-project <your-project-name>`.

## Deployment Steps

### 1. Update Configuration

Before deploying, you must update the placeholder values in the YAML file:

*   **`openshift/app-deployment.yaml`**:
    *   Replace `<your-gemini-api-key-here>` with your actual Google Gemini API key.
    *   Replace `<your-project-name>` with the name of your OpenShift project where the app will be deployed. If you are deploying to a project other than the one you are currently switched to, uncomment and set the `namespace` fields.

### 2. Build and Push the Docker Image

OpenShift can build the container image directly from the source code and the `Dockerfile` provided.

1.  **Create a new build configuration** that points to your source code repository. For a local directory, you can start a binary build.

    ```bash
    # Navigate to the root directory of the project
    cd /path/to/project-audit-tool

    # Create a new build configuration using the Docker strategy
    oc new-build --name=project-audit-tool --strategy=docker --binary
    ```

2.  **Start the build**, uploading your local source code. This command will package your project directory, send it to OpenShift, and start the build process defined in `openshift/Dockerfile`.

    ```bash
    # The `.` indicates the current directory
    oc start-build project-audit-tool --from-dir=. --follow
    ```

    This will create an `ImageStreamTag` named `project-audit-tool:latest` in your project, which will be used by the deployment.

### 3. Deploy the Application

Now that the image is built and available in the internal OpenShift registry, you can deploy the application using the provided YAML file.

```bash
# Apply the consolidated YAML file
oc apply -f openshift/app-deployment.yaml
```

This command will create:
*   A `PersistentVolumeClaim` for stable storage.
*   A `Secret` to hold your API key.
*   A `DeploymentConfig` to manage your application pods.
*   A `Service` to expose the application internally.
*   A `Route` to make the application accessible via a public URL.

### 4. Verify the Deployment

1.  **Check the status of the deployment**:

    ```bash
    oc status
    ```

2.  **Get the public URL** for the application:

    ```bash
    oc get route project-audit-tool-route -o jsonpath='{.spec.host}'
    ```

    Open the returned URL in your web browser. You should see the Project Audit Tool login page.

## Accessing Logs

To view the logs from your running application pod, first get the pod name and then use the `oc logs` command:

```bash
oc get pods -l app=project-audit-tool

# Replace <pod-name> with the actual name from the command above
oc logs -f <pod-name>
```