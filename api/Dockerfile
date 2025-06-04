FROM python:3.10-slim

# Copy your code
WORKDIR /app
COPY . .

# Install dependencies
#RUN pip install mlflow pandas scikit-learn gunicorn
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt


# Expose ports
EXPOSE 8000 5000


# Set environment variable for model name
#ENV MODEL_NAME=iris-data
#ENV MODEL_ALIAS=production

# Run the script on container start
#CMD ["python", "mlflow_client.py"]

