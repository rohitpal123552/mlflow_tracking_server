from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from mlflow_client import (
    get_all_models,
    get_model_versions,
    list_experiments,
    list_runs,
    get_latest_run_id_by_model
)
from logger import logger

app = FastAPI()

# Request Models
class ModelRequest(BaseModel):
    model_name: str

class ExperimentRequest(BaseModel):
    experiment_id: str

class RunIdByModelRequest(BaseModel):
    model_name: str

# Response Models
class ModelVersion(BaseModel):
    version: str
    run_id: str
    status: str

class RegisteredModel(BaseModel):
    name: str
    latest_versions: List[str]

class Experiment(BaseModel):
    experiment_id: str
    name: str

class RunIdResponse(BaseModel):
    run_id: str


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

@app.post("/run-id/", response_model=RunIdResponse)
def get_latest_run_id(request: RunIdByModelRequest):
    try:
        run_id = get_latest_run_id_by_model(request.model_name)
        logger.info(f"Retrieved latest run_id for model: {request.model_name}")
        return {"run_id": run_id}
    except Exception as e:
        logger.exception(f"Failed to get latest run_id for model: {request.model_name}")
        raise HTTPException(status_code=500, detail="Failed to get latest run_id")
