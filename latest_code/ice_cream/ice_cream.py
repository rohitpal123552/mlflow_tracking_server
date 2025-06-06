import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
import model_pipeline as pipeline

def main():
    try:
        # Start MLflow tracking
        mlflow.set_tracking_uri("<IPADDRESS/LOCALHOST>:5000")
        mlflow.set_experiment("Experiment_Name")
        
        # Data extraction
        df = pd.read_csv("ice_cream.csv")
        X = df[['temp']]
        y = df.iloc[:, -1]
        
        # Split data into train/test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
        
        # Train Linear regression model
        model = pipeline.model_train(X_train, y_train)
        
        # Generate Prediction
        y_train_pred, y_test_pred = pipeline.predict(model, X_train, X_test)
        
        # Evaluate Model
        mae, mse, rmse, r2 = pipeline.evaluate(y_test, y_test_pred)
        
        # Log model artifacts
        pipeline.log_model(mae, mse, rmse, r2)
        
        # Register Model Version into Model Registry
        pipeline.register_model(model)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

