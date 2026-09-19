import requests
import json
import time

# The URL of our local FastAPI server
url = "http://127.0.0.1:8000/predict"

# A realistic transaction payload with the exact 25 features our model expects
payload = {
    "TransactionAmt": 150.50,
    "dist1": 15.0,
    "dist2": None,
    "ProductCD": "W",
    "card1": 10486.0,
    "card2": 514.0,
    "card3": 150.0,
    "card4": "mastercard",
    "card5": 219.0,
    "card6": "credit",
    "addr1": 315.0,
    "addr2": 87.0,
    "P_emaildomain": "gmail.com",
    "R_emaildomain": None,
    "M1": "T",
    "M2": "T",
    "M3": "T",
    "M4": "M0",
    "M5": "F",
    "M6": "T",
    "M7": None,
    "M8": None,
    "M9": None,
    "DeviceType": "desktop",
    "DeviceInfo": "Windows"
}

print(f"Sending test transaction to {url}...")
print(json.dumps(payload, indent=2))

try:
    start_time = time.time()
    response = requests.post(url, json=payload)
    end_time = time.time()
    
    if response.status_code == 200:
        print("\n✅ SUCCESS!")
        print(f"Latency: {(end_time - start_time) * 1000:.2f} ms")
        print("\nAPI Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\n❌ FAILED with status code {response.status_code}")
        print(response.text)
except requests.exceptions.ConnectionError:
    print(f"\n❌ CONNECTION ERROR: Could not connect to {url}.")
    print("Are you sure the FastAPI server or Docker container is running on port 8000?")
