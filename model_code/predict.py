import json
import requests

# Load input data
with open("iris_test_input.json", "r") as f:
    input_data = f.read()

# Define the endpoint and headers
url = "http://127.0.0.1:5001/invocations"
headers = {"Content-Type": "application/json"}

# Send the request
response = requests.post(url, headers=headers, data=input_data)

# Print the response
try:
    print("Response from server:", response.json())
except json.JSONDecodeError:
    print("Server returned non-JSON response:")
    print(response.text)
