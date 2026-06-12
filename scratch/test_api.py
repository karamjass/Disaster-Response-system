import requests

url = "http://127.0.0.1:8000/analyze"
data = {"symptoms": "A large fire in the warehouse, people trapped."}

try:
    response = requests.post(url, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
