import json
import requests
from concurrent.futures import ThreadPoolExecutor

# Load input data
with open("iris_test_input.json", "r") as f:
    input_data = f.read()

url = "http://10.106.179.193:80/invocations"
headers = {"Content-Type": "application/json"}

def send_request():
    try:
        response = requests.post(url, headers=headers, data=input_data)
        print("Response:", response.json())
    except Exception as e:
        print("Error:", e)

# Send 10 requests in parallel
with ThreadPoolExecutor(max_workers=50) as executor:
    for _ in range(50):
        executor.submit(send_request)

