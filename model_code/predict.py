import json
import requests
import time
from concurrent.futures import ThreadPoolExecutor

# Load input data once
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

# Send 4 requests every second
while True:
    with ThreadPoolExecutor(max_workers=4) as executor:
        for _ in range(4):
            executor.submit(send_request)
    time.sleep(0.5)  # Wait 1 second before sending the next batch






# import json
# import requests
# import time

# # Load input data
# with open("iris_test_input.json", "r") as f:
#     input_data = f.read()

# url = "http://10.106.179.193:80/invocations"
# headers = {"Content-Type": "application/json"}

# while True:
#     try:
#         response = requests.post(url, headers=headers, data=input_data)
#         print("Response:", response.json())
#     except Exception as e:
#         print("Error:", e)
#     time.sleep(0.5)  # Optional: wait 1 second between requests




# import json
# import requests

# # Load input data
# with open("iris_test_input.json", "r") as f:
#     input_data = f.read()

# # Define the endpoint and headers
# url = "http://10.106.179.193:80/invocations"
# headers = {"Content-Type": "application/json"}

# # Send the request
# response = requests.post(url, headers=headers, data=input_data)

# # Print the response
# try:
#     print("Response from server:", response.json())
# except json.JSONDecodeError:
#     print("Server returned non-JSON response:")
#     print(response.text)
