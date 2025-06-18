import requests
import httpx

import util

async def post_clipboard_item(item: str):
    print(f"Posting item: {item} with type: {type(item)}")
    
    url = "http://localhost:8000/user/1/clipboard"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={})
    
    response = requests.post(url, json={"text": item, "time": util.get_current_time()})

    if response.status_code == 200:
        print("Item posted successfully.")
    else:
        print(f"Failed to post item. Status code: {response.status_code}, Response: {response.text}")
    