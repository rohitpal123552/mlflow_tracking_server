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


