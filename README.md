###### Setting up MLflow Tracking UI and Model Serving on Kubernetes

Goal:
  To set up MLflow Tracking UI and MLflow Model Server on a Kubernetes Cluster for end-to-end ML lifecycle management.

Use Case:
  Deploy and manage ML models with tracking and inference capabilities on a scalable infrastructure.

-- MLflow Tracking UI & Model Serving on Kubernetes
  how to deploy MLflow Tracking Server and Model Serving on a Kubernetes cluster for scalable ML experimentation and inference.

-- Objective
  MLflow Tracking UI to log and visualize experiments
  MLflow Model Server to serve trained models
  Kubernetes for scalable and resilient deployment

-- Prerequisites
  Before starting, ensure you have the following:
    A running Kubernetes cluster (Minikube, EKS, GKE, etc.)
    kubectl configured and working
    Docker installed and authenticated to your container registry

-- Step 1 – Containerize MLflow Tracking UI
  Create a Dockerfile for MLflow Tracking Server:
  place here dockerfile.mlflow image

  Build and push the image:
  docker build -t your-docker-user/mlflow-server .
  docker push your-docker-user/mlflow-server

-- Step 2 – Deploy MLflow to Kubernetes
  Create mlflow-ui-deployment.yaml:
  place here manifiests file image

-- Step 3 – Expose MLflow UI
  Create mlflow-ui-service.yaml:
  place here service manifiests image

  Apply the resources:
  kubectl apply -f mlflow-deployment.yaml
  kubectl apply -f mlflow-service.yaml

-- Step 4 – Use MLflow for Tracking & Serving
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

-- Step 5 – Containerize MLflow Model Server
  Create a Dockerfile for MLflow Model Server:
  place here dockerfile.model image

  Build and push the image:
  docker build -t your-docker-user/mlflow-model .
  docker push your-docker-user/mlflow-model

-- Step 6 – Deploy MLflow Model Server to Kubernetes
  Create mLflow-model-deployment.yaml:
  place here manifiests file image

-- Step 7 – Expose MLflow Model Server UI
  Create mLflow-model-service.yaml:
  place here service manifiests image

  Apply the resources:
  kubectl apply -f mLflow-model-deployment.yaml
  kubectl apply -f mLflow-model-service.yaml

-- Test Inference
  curl -X POST http://<mlflow-model-service-ip>:<port>/invocations \
     -H "Content-Type: application/json" \
     --data @input.json



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
