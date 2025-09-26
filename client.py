import requests

url = "http://127.0.0.1:8000/mcp/"

headers = {
    "Accept": "application/json,text/event-stream",
    "Content-Type": "application/json"
}

# body = {
#     "jsonrpc": "2.0",
#     "method": "tools/call",         # if using "tools/list" if will return a list of available tools
#     "params": {
#         "name": "read_document",
#         "arguments": {
#             "id": "report.pdf"
#         }
#     },
#     "id": 1
# }

body = {
    "jsonrpc": "2.0",
    "method": "resources/list",         # it will return a list of available resources
    "params": {      
        
    },
    "id": 1
}

resp = requests.post(url, headers=headers, json=body)
print(resp.status_code, resp.text)
