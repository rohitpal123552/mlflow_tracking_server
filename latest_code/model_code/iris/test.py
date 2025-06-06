import mlflow
import os

mlflow.set_tracking_uri("http://192.168.1.100:32000")
mlflow.set_experiment("artifact-test")

with mlflow.start_run():
    # Create a test file
    os.makedirs("test_artifacts", exist_ok=True)
    with open("test_artifacts/hello.txt", "w") as f:
        f.write("Hello from MLflow!")

    # Log the file as an artifact
    mlflow.log_artifacts("test_artifacts", artifact_path="test_folder")

    print("Logged test artifact.")

