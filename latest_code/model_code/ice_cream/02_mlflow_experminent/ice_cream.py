import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
import model_pipeline as pipeline

def main():
    try:
        # Set up MLflow tracking
        mlflow.set_tracking_uri("http://10.109.47.85:5000")
        mlflow.set_experiment("ice cream")

        # Load and split data
        df = pd.read_csv("ice_cream.csv")
        X = df[['temp']]
        y = df.iloc[:, -1]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

        # Start MLflow run
        with mlflow.start_run():
            # Train model
            model = pipeline.model_train(X_train, y_train)

            # Predict
            y_train_pred, y_test_pred = pipeline.predict(model, X_train, X_test)

            # Evaluate
            mae, mse, rmse, r2 = pipeline.evaluate(y_test, y_test_pred)

            # Log metrics and artifacts
            pipeline.log_model(mae, mse, rmse, r2)

            # Register model
            pipeline.register_model(model)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
