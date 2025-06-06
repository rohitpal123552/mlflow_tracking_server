from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

# Replace with your actual MLflow Tracking Server URL
MLFLOW_TRACKING_URI = "http://10.110.234.157:5000"

class ModelRequest(BaseModel):
    model_name: str

@app.post("/get-run-id/")
def get_run_id(request: ModelRequest):
    try:
        # Step 1: Get latest versions of the model
        url = f"{MLFLOW_TRACKING_URI}/api/2.0/mlflow/registered-models/get-latest-versions"
        payload = {
            "name": request.model_name,
            "stages": ["None", "Staging", "Production"]
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()
        if not data.get("model_versions"):
            raise HTTPException(status_code=404, detail="No versions found for the model")

        # Step 2: Return the run_id of the latest version
        run_id = data["model_versions"][0]["run_id"]
        return {"model_name": request.model_name, "run_id": run_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# mflow_client.py
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

def extract_model_names_from_runs(runs_data: List[Dict[str, Any]]) -> List[str]:
    try:
        model_names = set()
        for run in runs_data:
            tags = run.get("data", {}).get("tags", {})
            history = tags.get("mlflow.log-model.history")
            if history:
                try:
                    history_data = json.loads(history)
                    for entry in history_data:
                        if "artifact_path" in entry:
                            model_names.add(entry["artifact_path"])
                except json.JSONDecodeError:
                    logger.warning("Failed to parse model history JSON.")
            if "model_name" in tags:
                model_names.add(tags["model_name"])
        logger.debug(f"Extracted model names: {model_names}")
        return list(model_names)
    except Exception as e:
        logger.error(f"Error extracting model names from runs: {e}")
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

def get_artifacts(run_id: str, path: str = "") -> List[Dict[str, Any]]:
    try:
        artifacts = client.list_artifacts(run_id, path)
        logger.debug(f"Found {len(artifacts)} artifacts for run_id '{run_id}' at path '{path}'.")
        return [{"path": a.path, "is_dir": a.is_dir, "file_size": a.file_size} for a in artifacts]
    except Exception as e:
        logger.error(f"Error fetching artifacts for run_id '{run_id}': {e}")
        raise



# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from mlflow_client import (
    get_all_models,
    get_model_versions,
    get_artifacts,
    list_experiments,
    list_runs,
    extract_model_names_from_runs
)
from logger import logger

app = FastAPI()

# Request Models
class ModelRequest(BaseModel):
    model_name: str

class ArtifactRequest(BaseModel):
    run_id: str
    path: str = ""

class ExperimentRequest(BaseModel):
    experiment_id: str

# Response Models
class ModelVersion(BaseModel):
    version: str
    run_id: str
    status: str

class RegisteredModel(BaseModel):
    name: str
    latest_versions: List[str]

class Artifact(BaseModel):
    path: str
    is_dir: bool
    file_size: Optional[int]

class Experiment(BaseModel):
    experiment_id: str
    name: str

@app.get("/models/", response_model=List[RegisteredModel])
def list_models():
    try:
        models = get_all_models()
        logger.info("Successfully listed all models.")
        return models
    except Exception as e:
        logger.exception("Failed to list models")
        raise HTTPException(status_code=500, detail="Failed to list models")

@app.post("/model-versions/", response_model=List[ModelVersion])
def model_versions(request: ModelRequest):
    try:
        versions = get_model_versions(request.model_name)
        logger.info(f"Retrieved versions for model: {request.model_name}")
        return versions
    except Exception as e:
        logger.exception(f"Failed to get versions for model: {request.model_name}")
        raise HTTPException(status_code=500, detail="Failed to get model versions")

@app.post("/artifacts/", response_model=List[Artifact])
def list_artifacts(request: ArtifactRequest):
    try:
        artifacts = get_artifacts(request.run_id, request.path)
        logger.info(f"Retrieved artifacts for run_id: {request.run_id}")
        return artifacts
    except Exception as e:
        logger.exception(f"Failed to get artifacts for run_id: {request.run_id}")
        raise HTTPException(status_code=500, detail="Failed to get artifacts")

@app.get("/experiments/", response_model=List[Experiment])
def get_experiments():
    try:
        experiments = list_experiments()
        logger.info("Successfully listed experiments.")
        return experiments
    except Exception as e:
        logger.exception("Failed to list experiments")
        raise HTTPException(status_code=500, detail="Failed to list experiments")

@app.post("/runs/", response_model=List[Dict[str, Any]])
def get_runs(request: ExperimentRequest):
    try:
        runs = list_runs(request.experiment_id)
        logger.info(f"Retrieved runs for experiment_id: {request.experiment_id}")
        return runs
    except Exception as e:
        logger.exception(f"Failed to list runs for experiment_id: {request.experiment_id}")
        raise HTTPException(status_code=500, detail="Failed to list runs")

@app.post("/extract-model-names/", response_model=Dict[str, List[str]])
def extract_models_from_runs(request: ExperimentRequest):
    try:
        runs = list_runs(request.experiment_id)
        model_names = extract_model_names_from_runs(runs)
        logger.info(f"Extracted model names from experiment_id: {request.experiment_id}")
        return {"model_names": model_names}
    except Exception as e:
        logger.exception(f"Failed to extract model names from experiment_id: {request.experiment_id}")
        raise HTTPException(status_code=500, detail="Failed to extract model names")
