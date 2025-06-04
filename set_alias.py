import mlflow
from mlflow.tracking import MlflowClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api.logger import logger
from configparser import ConfigParser

# Load tracking URI from config
config = ConfigParser()
config.read('./api/config/config.ini')
TRACKING_URI = config.get('mlflow', 'tracking_uri')

# Set MLflow tracking URI
mlflow.set_tracking_uri(TRACKING_URI)
client = MlflowClient()

# FastAPI app
app = FastAPI()

# Request body model
class AliasUpdateRequest(BaseModel):
    model_name: str
    alias: str
    version: str

@app.post("/update-alias")
def update_model_alias(request: AliasUpdateRequest):
    try:
        client.set_registered_model_alias(request.model_name, request.alias, request.version)
        logger.info(f"Alias '{request.alias}' set to version '{request.version}' for model '{request.model_name}'")
        return {
            "message": f"Alias '{request.alias}' set to version '{request.version}' for model '{request.model_name}'."
        }
    except Exception as e:
        logger.error(f"Failed to update alias: {e}")
        raise HTTPException(status_code=500, detail=str(e))
