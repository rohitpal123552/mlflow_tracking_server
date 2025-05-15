import mlflow
from mlflow.models import infer_signature

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# ------------------ Step 1: Load data from CSV ------------------
df = pd.read_csv("iris_dataset.csv")
X = df.drop("target", axis=1)
y = df["target"]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ------------------ Step 2: Train the model ------------------
params = {
    "solver": "lbfgs",
    "max_iter": 1000,
    "multi_class": "auto",
    "random_state": 8888,
}

lr = LogisticRegression(**params)
lr.fit(X_train, y_train)
y_pred = lr.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")

# ------------------ Step 3: Log to MLflow ------------------
mlflow.set_tracking_uri("http://10.103.189.150:5000")
mlflow.set_experiment("iris data")

with mlflow.start_run():
    mlflow.log_params(params)
    mlflow.log_metric("accuracy", accuracy)
    mlflow.set_tag("Training Info", "LR model trained from CSV")

    signature = infer_signature(X_train, lr.predict(X_train))

    mlflow.sklearn.log_model(
        sk_model=lr,
        artifact_path="iris_model",
        signature=signature,
        input_example=X_train,
        registered_model_name="iris-data",
    )

    print("Logged run ID:", mlflow.active_run().info.run_id)
