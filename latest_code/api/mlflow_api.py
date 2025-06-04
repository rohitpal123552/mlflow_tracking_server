from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mlflow_client import serve_model, update_model_alias
from logger import logger
import uvicorn

app = FastAPI()

class AliasUpdateRequest(BaseModel):
    model_name: str
    alias: str
    version: str

@app.post("/serve-model")
def serve_model_endpoint():
    try:
        serve_model()
        return {"message": "Model server started successfully."}
    except Exception as e:
        logger.error(f"Failed to serve model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-alias")
def update_model_alias_endpoint(request: AliasUpdateRequest):
    try:
        return update_model_alias(request.model_name, request.alias, request.version)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("mlflow_api:app", host="0.0.0.0", port=8000)
