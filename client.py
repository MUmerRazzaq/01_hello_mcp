import requests

url = "http://127.0.0.1:8000/mcp/"

headers = {
    "Accept": "application/json,text/event-stream",
    "Content-Type": "application/json"
}

body = {
    "jsonrpc": "2.0",
    "method": "tools/call",         # if using tools/list if will return a list of available tools
    "params": {
        "name": "hello",
        "arguments": {
            "name": "TestUser"
        }
    },
    "id": 1
}

resp = requests.post(url, headers=headers, json=body)
print(resp.status_code, resp.text)
