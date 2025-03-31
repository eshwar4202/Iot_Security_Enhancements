import asyncio
import aiocoap
import time
import hmac
import hashlib
import base64

# CoAP Server Details
COAP_SERVER_IP = "coap://192.168.115.142/sensor/data"
SECRET_KEY = b"your_secure_secret_key"


# Function to Compute HMAC-SHA1 with Base64 (Matches ESP32)
def compute_hmac(data):
    hmac_obj = hmac.new(SECRET_KEY, data.encode(), hashlib.sha1)
    hmac_bytes = hmac_obj.digest()
    base64_sig = base64.b64encode(hmac_bytes).decode("utf-8")
    return base64_sig[:10]  # Trim to 10 chars like ESP32


# Function to Send CoAP Request
async def send_coap_request(payload):
    protocol = await aiocoap.Context.create_client_context()
    request = aiocoap.Message(
        code=aiocoap.PUT, uri=COAP_SERVER_IP, payload=payload.encode()
    )
    response = await protocol.request(request).response
    print(f"📡 Sent: {payload} | Response: {response.code}")


# **1️⃣ Replay Attack Simulation**
async def replay_attack():
    payload = "A:100,200,300|G:10,20,30|H:75|S:98|S:" + compute_hmac(
        "A:100,200,300|G:10,20,30|H:75|S:98"
    )
    print("\n🚨 Simulating Replay Attack...")
    await send_coap_request(payload)
    await asyncio.sleep(2)  # Within 5 seconds
    await send_coap_request(payload)


# **2️⃣ DoS Attack Simulation**
async def dos_attack():
    print("\n🚨 Simulating DoS Attack...")
    payload = "A:200,300,400|G:15,25,35|H:80|S:99|S:" + compute_hmac(
        "A:200,300,400|G:15,25,35|H:80|S:99"
    )
    for _ in range(20):  # More than 50 requests
        await send_coap_request(payload)
        await asyncio.sleep(0)


# **3️⃣ Spoofing Attack Simulation**
async def spoofing_attack():
    print("\n🚨 Simulating Spoofing Attack...")
    abnormal_heart_rate = "A:50,60,70|G:5,10,15|H:250|S:95|S:" + compute_hmac(
        "A:50,60,70|G:5,10,15|H:250|S:95"
    )
    abnormal_spo2 = "A:30,40,50|G:3,6,9|H:85|S:50|S:" + compute_hmac(
        "A:30,40,50|G:3,6,9|H:85|S:50"
    )
    await send_coap_request(abnormal_heart_rate)
    await asyncio.sleep(1)
    await send_coap_request(abnormal_spo2)


# **4️⃣ MITM Attack Simulation**
async def mitm_attack():
    print("\n🚨 Simulating MITM Attack...")
    original_data = "A:75,85,95|G:7,8,9|H:72|S:97"
    fake_signature = "fake_sign"  # Incorrect signature
    payload = f"{original_data}|S:{fake_signature}"
    await send_coap_request(payload)


# **🔄 Run All Attacks**
async def main():
    await replay_attack()
    await asyncio.sleep(2)
    await dos_attack()
    await asyncio.sleep(2)
    await spoofing_attack()
    await asyncio.sleep(2)
    await mitm_attack()


asyncio.run(main())
