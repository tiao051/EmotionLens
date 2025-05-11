import aiohttp

async def send_to_api_async(data, api_url):
    headers = {"Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(api_url, json=data, headers=headers, ssl=False) as response:
                print(f"➡️ Sent data to API: {response.status} {await response.text()}")
        except Exception as e:
            print(f"❌ Error sending data to API: {e}")
