##-------------------Step 1 - Train a model and prepare metadata for logging------------------------
import mlflow
from mlflow.models import infer_signature

import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


# Load the Iris dataset
X, y = datasets.load_iris(return_X_y=True)

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Define the model hyperparameters
params = {
    "solver": "lbfgs",
    "max_iter": 1000,
    "multi_class": "auto",
    "random_state": 8888,
}

# Train the model
lr = LogisticRegression(**params)
lr.fit(X_train, y_train)

# Predict on the test set
y_pred = lr.predict(X_test)

print(f"Prediction.... {y_pred}")
# Calculate metrics
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy----------{accuracy}")

## --------------------------Step 2-Log the model and its metadata to MLflow-------------------------
# Set our tracking server uri for logging
mlflow.set_tracking_uri("http://127.0.0.1:5000")

# Create a new MLflow Experiment
mlflow.set_experiment("iris data")

# Start an MLflow run
with mlflow.start_run():
    # Log the hyperparameters
    mlflow.log_params(params)

    # Log the loss metric
    mlflow.log_metric("accuracy", accuracy)

    # Set a tag that we can use to remind ourselves what this run was for
    mlflow.set_tag("Training Info", "Basic LR model for iris data")

    # Infer the model signature
    signature = infer_signature(X_train, lr.predict(X_train))

    # Log the model
    model_info = mlflow.sklearn.log_model(
        sk_model=lr,
        artifact_path="iris_model",
        signature=signature,
        input_example=X_train,
        registered_model_name="iris-data",
    )

    print("Logged run ID:", mlflow.active_run().info.run_id)


#     curl http://127.0.0.1:5001/invocations \
#   -H "Content-Type: application/json" \
#   --data '{
#     "inputs": [
#       [5.1, 3.5, 1.4, 0.2],
#       [6.2, 3.4, 5.4, 2.3],
#       [5.9, 3.0, 5.1, 1.8]
#     ]
#   }'
