from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Update this to match your MLflow model server URL
MLFLOW_MODEL_URL = "http://mlflow-server:1234/invocations"

class PredictRequest(BaseModel):
    columns: list
    data: list

@app.post("/predict")
async def predict(request: PredictRequest):
    payload = request.dict()
    logging.info("Forwarding request to MLflow: %s", payload)

    try:
        response = requests.post(MLFLOW_MODEL_URL, json=payload)
        response.raise_for_status()
        return {"predictions": response.json()}
    except Exception as e:
        logging.error("Prediction failed: %s", str(e))
        return {"error": str(e)}
