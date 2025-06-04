import subprocess
import mlflow
from mlflow.tracking import MlflowClient
from configparser import ConfigParser
from logger import logger

# Load configuration
config = ConfigParser()
config.read('/app/config/config.ini')

# Read values from config
tracking_uri = config.get('mlflow', 'tracking_uri')
model_name = config.get('mlflow', 'model_name')
alias = config.get('mlflow', 'alias')
port = config.getint('mlflow', 'port', fallback=5000)

mlflow.set_tracking_uri(tracking_uri)
client = MlflowClient()

def serve_model():
    model_uri = f"models:/{model_name}@{alias}"
    logger.info(f"Serving model from URI: {model_uri}")
    
    subprocess.Popen([
        "mlflow", "models", "serve",
        "-m", model_uri,
        "--host", "0.0.0.0",
        "-p", str(port),
        "--no-conda"
    ])

def update_model_alias(model_name: str, alias: str, version: str):
    try:
        client.set_registered_model_alias(model_name, alias, version)
        logger.info(f"Alias '{alias}' set to version '{version}' for model '{model_name}'")
        return {"message": f"Alias '{alias}' set to version '{version}' for model '{model_name}'."}
    except Exception as e:
        logger.error(f"Failed to update alias: {e}")
        raise










# import os
# import subprocess
# import mlflow
# from mlflow.tracking import MlflowClient
# from configparser import ConfigParser
# from logger import logger

# # Load configuration
# config = ConfigParser()
# config.read('/app/config/config.ini')  # Path inside the container

# # Read values from config
# tracking_uri = config.get('mlflow', 'tracking_uri')
# model_name = config.get('mlflow', 'model_name')
# alias = config.get('mlflow', 'alias')  # No fallback, must be provided

# mlflow.set_tracking_uri(tracking_uri)
# client = MlflowClient()

# def serve_model(model_name: str, alias: str, port: int = 5000):
#     model_uri = f"models:/{model_name}@{alias}"
#     logger.info(f"Serving model from URI: {model_uri}")
    
#     subprocess.run([
#         "mlflow", "models", "serve",
#         "-m", model_uri,
#         "--host", "0.0.0.0",
#         "-p", str(port),
#         "--no-conda"
#     ])

# if __name__ == "__main__":
#     serve_model(model_name, alias)






# import os
# import subprocess
# import mlflow
# from mlflow.tracking import MlflowClient
# from logger import logger

# mlflow.set_tracking_uri("http://10.110.234.157:5000")
# client = MlflowClient()

# def serve_model(model_name: str, alias: str = "production", port: int = 5000):
#     model_uri = f"models:/{model_name}@{alias}"
#     logger.info(f"Serving model from URI: {model_uri}")
    
#     # Serve the model using subprocess
#     subprocess.run([
#         "mlflow", "models", "serve",
#         "-m", model_uri,
#         "--host", "0.0.0.0",
#         "-p", str(port),
#         "--no-conda"
#     ])

# def get_latest_run_id_by_model(model_name: str) -> str:
#     try:
#         versions = client.get_latest_versions(model_name)
#         if not versions:
#             raise ValueError(f"No versions found for model '{model_name}'")
#         latest_version = sorted(versions, key=lambda v: int(v.version), reverse=True)[0]
#         logger.info(f"Latest version for model '{model_name}' is {latest_version.version} with run_id {latest_version.run_id}")
#         return latest_version.run_id
#     except Exception as e:
#         logger.error(f"Error fetching latest run_id for model '{model_name}': {e}")
#         raise

# # def serve_model(model_name: str, artifact_path: str = "model", port: int = 5000):
# #     run_id = get_latest_run_id_by_model(model_name)
# #     model_uri = f"runs:/{run_id}/{artifact_path}"
# #     logger.info(f"Serving model from URI: {model_uri}")
    
# #     # Serve the model using subprocess
# #     subprocess.run([
# #         "mlflow", "models", "serve",
# #         "-m", model_uri,
# #         "--host", "0.0.0.0",
# #         "-p", str(port),
# #         "--no-conda"
# #     ])

# if __name__ == "__main__":
#     model_name = os.getenv("MODEL_NAME", "iris-data")
#     alias = os.getenv("MODEL_ALIAS", "production")
#     serve_model(model_name, alias)
