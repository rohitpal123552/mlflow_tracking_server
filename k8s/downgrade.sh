#!/bin/bash

set -euo pipefail

LOG_FILE="downgrade_model.log"
DEPLOYMENT_NAME="iris-model-deployment"
CONFIGMAP_NAME="iris-model-config"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error_exit() {
  log "ERROR: $1"
  exit 1
}

get_user_input() {
  read -p "Enter model name: " MODEL_NAME
  read -p "Enter alias: " ALIAS
  read -p "Enter version: " VERSION

  if [[ -z "$MODEL_NAME" || -z "$ALIAS" || -z "$VERSION" ]]; then
    error_exit "Model name, alias, and version must not be empty."
  fi
}

update_alias_api() {
  log "Calling API to update alias..."
  local response
  response=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://192.168.1.100:30080/update-alias \
    -H "Content-Type: application/json" \
    -d "{\"model_name\": \"$MODEL_NAME\", \"alias\": \"$ALIAS\", \"version\": \"$VERSION\"}")

  if [[ "$response" -ne 200 ]]; then
    error_exit "Failed to update alias. HTTP status code: $response"
  fi
  log "Alias updated successfully."
}

get_tracking_service_ip() {
  log "Fetching MLflow tracking service IP from Kubernetes..."
  SERVICE_IP=$(kubectl get svc -A -o jsonpath="{.items[?(@.metadata.name=='mlflow')].spec.clusterIP}" 2>/dev/null)

  if [[ -z "$SERVICE_IP" ]]; then
    error_exit "Could not find MLflow service IP. Ensure the service is named 'mlflow'."
  fi
  log "MLflow tracking URI resolved to: http://$SERVICE_IP:5000"
}

update_configmap_yaml() {
  log "Generating updated configmap.yaml..."
  cat <<EOF > configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: $CONFIGMAP_NAME
data:
  config.ini: |
    [mlflow]
    tracking_uri = http://$SERVICE_IP:5000
    model_name = $MODEL_NAME
    alias = $ALIAS
    port = 5000
EOF
}

apply_configmap_and_restart_deployment() {
  log "Applying updated ConfigMap..."
  kubectl apply -f configmap.yaml || error_exit "Failed to apply ConfigMap."

  log "Restarting deployment: $DEPLOYMENT_NAME..."
  kubectl rollout restart deployment "$DEPLOYMENT_NAME" || error_exit "Failed to restart deployment."
  log "Deployment restarted successfully."
}

main() {
  log "=== Starting model downgrade process ==="
  get_user_input
  update_alias_api
  get_tracking_service_ip
  update_configmap_yaml
  apply_configmap_and_restart_deployment
  log "=== Model downgrade process completed successfully ==="
}

main

