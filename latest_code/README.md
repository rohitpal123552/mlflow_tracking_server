###### Setting up MLflow Tracking UI and Model Serving on Kubernetes and autoscaling


-- Prerequisites
   Before starting, ensure you have the following:
      A running Kubernetes cluster (Minikube, EKS, GKE, etc.)
      kubectl configured and working
      Docker installed and authenticated to your container registry

-- Step 1 - Containerize MLflow Tracking UI
    Create a Dockerfile for MLflow Tracking Server:

  Build and push the image:
    docker build -t your-docker-user/<image-name> .
    docker push your-docker-user/<image-name>

-- Step 2 - Deploy MLflow to Kubernetes
    Create mlflow-ui-deployment.yaml:

-- Step 3 - Expose MLflow UI
    Create mlflow-ui-service.yaml:

  Apply the resources:
    kubectl apply -f mlflow-ui-deployment.yaml
    kubectl apply -f mlflow-ui-service.yaml

-- Step 4 - Use MLflow for Tracking & Serving
    Log experiments to the Tracking UI:
    import mlflow

      # Set our tracking server uri for logging
      mlflow.set_tracking_uri("http://<mlflow-service-ip>") # cluster-ip

      # Create a new MLflow Experiment
      mlflow.set_experiment("iris data")

      # Start an MLflow run
      with mlflow.start_run():
          # Log the hyperparameters
          mlflow.log_params(params)

          # Log the accuracy metric
          mlflow.log_metric("accuracy", accuracy)

          # Set a tag that we can use to remind ourselves what this run was for
          mlflow.set_tag("iris data")

          # Infer the model signature
          signature = infer_signature(X_train, lr.predict(X_train))

          # Log the model
          model_info = mlflow.sklearn.log_model(
              sk_model=lr,
              artifact_path="iris_model",
              signature=signature,
              input_example=X_train,
              registered_model_name="iris-data",
          )
          print("Logged run ID:", mlflow.active_run().info.run_id)

#### Deploy the Model using MLflow Model Serving

-- Step 5 - Containerize MLflow Model Server
    Create a Dockerfile for MLflow Model Server:
 
  Build and push the image:
    docker build -t your-docker-user/<image-name> .
    docker push your-docker-user/<image-name>

-- Step 6 - Deploy MLflow Model Server to Kubernetes
    Create mLflow-model-deployment.yaml:

-- Step 7 - Expose MLflow Model Server UI
    create mLflow-model-service.yaml:

  Apply the resources:
    kubectl apply -f iris-model-deployment.yml  # service manifiest included in same file
    # kubectl apply -f mLflow-model-service.yaml

-- Step 8 - Autoscale your Kubernetes pod using Horizontal Pod Autoscaler (HPA)

  Prerequisites
    1: A Kubernetes cluster (e.g., Minikube, EKS, GKE, AKS).
    2: Metrics Server installed and running in the cluster.
    3: A deployment or pod that you want to autoscale.
    4: Your application should expose resource metrics like CPU or memory.

  Step-by-Step Guide
  1. Install Metrics Server
     If not already installed, you can install it using:
     kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    
     Verify it's working:
     kubectl get deployment metrics-server -n kube-system

  2: Create the HPA
    Use the following command to create an HPA that scales based on CPU usage:
    kubectl autoscale deployment <your deployment-name> --cpu-percent=50 --min=1 --max=5

    This means:
      If CPU usage exceeds 50%, Kubernetes will scale up the pods.
      It will maintain between 1 and 5 replicas.
  
  3: Check HPA Status
    kubectl get hpa

    You'll see something like:
    NAME               REFERENCE                     TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
    iris-model-hpa   Deployment/<deployment-name>   10%/50%   1         5         1          1m

  4: Generate Load (Optional)
     To test autoscaling, you can generate CPU load using a tool like stress or a custom script inside the pod.  

    Optional: YAML-Based HPA

      apiVersion: autoscaling/v2
      kind: HorizontalPodAutoscaler
      metadata:
        name: iris-model-hpa
      spec:
        scaleTargetRef:
          apiVersion: apps/v1
          kind: Deployment
          name: <deployment-name>
        minReplicas: 1
        maxReplicas: 5
        metrics:
        - type: Resource
          resource:
            name: cpu
            target:
              type: Utilization
              averageUtilization: 50

    Apply the HPA:
    Save the above YAML to a file (e.g., iris-model-hpa.yaml) and apply it:
    kubectl apply -f iris-model-hpa.yaml

    
    # - --kubelet-insecure-tls
    # - --kubelet-preferred-address-types=InternalIP,Hostname,InternalDNS,ExternalDNS,ExternalIP

-- Step 9 - Deploy the model to run below command 
    curl -X POST http://<cluster-node-IP>:<nodeport>/serve-model

-- Step 10 - Test Inference
    curl -X POST http://<mlflow-model-service-ip>:<port>/invocations \
      -H "Content-Type: application/json" \
      --data @input.json

-- Step 11 - To downgrade model latest version to old version (eg. latest v5 to v3 or any other version)
   
  1: Here's a modular, function-based Bash script that:
      1. Accepts user inputs for model_name, alias, and version.
      2. Calls the API to update the alias.
      3. Fetches the MLflow tracking server IP from a running Kubernetes service.
      4. Updates the ConfigMap YAML file with the new values.
      5. Applies the updated ConfigMap and restarts the associated deployment.
      6. Includes logging for traceability.

  2:  Save the script as downgrade_model.sh.
      Make it executable:
      chmod +x latest_code/k8s/downgrade_model.sh
  3: Run it:
      ./latest_code/k8s/downgrade_model.sh.sh


<!--  curl http://10.100.198.240:5000/invocations \
   -H "Content-Type: application/json" \
   --data '{
     "inputs": [
       [5.1, 3.5, 1.4, 0.2],
       [6.2, 3.4, 5.4, 2.3],
       [5.9, 3.0, 5.1, 1.8]
     ]
   }'
 -->
 
