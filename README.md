# mlflow_tracking_server


FROM python:3.9-slim

RUN pip install --no-cache-dir mlflow

# Replace with your actual model URI (can also pass via env)
ENV MODEL_URI=runs:/b3478e0876cd4d17a579b47a8e1cbbee/model

EXPOSE 5000

CMD ["sh", "-c", "mlflow models serve -m $MODEL_URI --host 0.0.0.0 --port 5000"]


docker build -t your-dockerhub-user/mlflow-model:latest .
docker push your-dockerhub-user/mlflow-model:latest


apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlflow-model-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mlflow-model-server
  template:
    metadata:
      labels:
        app: mlflow-model-server
    spec:
      containers:
        - name: mlflow-model
          image: your-dockerhub-user/mlflow-model:latest
          ports:
            - containerPort: 5000
          env:
            - name: MODEL_URI
              value: runs:/b3478e0876cd4d17a579b47a8e1cbbee/model


apiVersion: v1
kind: Service
metadata:
  name: mlflow-model-server
spec:
  type: ClusterIP
  selector:
    app: mlflow-model-server
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000


Update your FastAPI MLFLOW_MODEL_URL to:

MLFLOW_MODEL_URL = "http://mlflow-model-server:5000/invocations"


curl http://<node-ip>:<nodePort>/invocations \
  -H "Content-Type: application/json" \
  --data '{
    "columns": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
    "data": [[5.1, 3.5, 1.4, 0.2]]
  }'
