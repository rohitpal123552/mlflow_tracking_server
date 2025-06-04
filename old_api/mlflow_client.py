import os
import json
import mlflow
from mlflow.tracking import MlflowClient
from mlflow.entities import Run
from typing import List, Dict, Any
from logger import logger

# Set the tracking URI from environment variable or fallback
mlflow.set_tracking_uri("http://10.110.234.157:5000")
# mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))

client = MlflowClient()

def list_experiments() -> List[Dict[str, str]]:
    try:
        experiments = client.search_experiments()
        logger.debug(f"Found {len(experiments)} experiments.")
        return [{"experiment_id": exp.experiment_id, "name": exp.name} for exp in experiments]
    except Exception as e:
        logger.error(f"Error listing experiments: {e}")
        raise

def list_runs(experiment_id: str) -> List[Dict[str, Any]]:
    try:
        runs = client.search_runs(experiment_ids=[experiment_id], max_results=100)
        logger.debug(f"Found {len(runs)} runs for experiment {experiment_id}.")
        return [run.to_dictionary() for run in runs]
    except Exception as e:
        logger.error(f"Error listing runs for experiment_id '{experiment_id}': {e}")
        raise

def get_all_models() -> List[Dict[str, Any]]:
    try:
        models = client.search_registered_models()
        logger.debug(f"Found {len(models)} registered models.")
        return [{"name": model.name, "latest_versions": [v.version for v in model.latest_versions]} for model in models]
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        raise

def get_model_versions(model_name: str) -> List[Dict[str, str]]:
    try:
        versions = client.get_latest_versions(model_name)
        logger.debug(f"Found {len(versions)} versions for model '{model_name}'.")
        return [{"version": v.version, "run_id": v.run_id, "status": v.status} for v in versions]
    except Exception as e:
        logger.error(f"Error fetching versions for model '{model_name}': {e}")
        raise

def get_latest_run_id_by_model(model_name: str) -> str:
    try:
        versions = client.get_latest_versions(model_name)
        if not versions:
            raise ValueError(f"No versions found for model '{model_name}'")
        latest_version = sorted(versions, key=lambda v: int(v.version), reverse=True)[0]
        logger.debug(f"Latest version for model '{model_name}' is {latest_version.version} with run_id {latest_version.run_id}")
        return latest_version.run_id
    except Exception as e:
        logger.error(f"Error fetching latest run_id for model '{model_name}': {e}")
        raise

run_id = get_latest_run_id_by_model('iris-data')
logger.info(f"Retrieved latest run_id for model: {'iris-data'}")
print(f'{{"run_id": "{run_id}"}}')
