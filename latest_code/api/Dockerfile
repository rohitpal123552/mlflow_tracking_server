FROM python:3.10-slim

# Copy your code
WORKDIR /app
COPY . .

# Install dependencies
#RUN pip install mlflow pandas scikit-learn gunicorn
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Expose ports
EXPOSE 8000 5000


