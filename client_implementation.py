from mcp import ClientSession , types
from mcp.client.streamable_http import streamablehttp_client
from contextlib import AsyncExitStack
import asyncio
import json
from pydantic import AnyUrl

class MCPClient:
    def __init__(self, url):
        self.url = url
        self.stack = AsyncExitStack()
        self._sess = None
    async def __aenter__ (self):
        read, write ,_ = await self.stack.enter_async_context(
            streamablehttp_client(self.url)
        )

        self._sess = await self.stack.enter_async_context(
            ClientSession(read,write)
        )
        await self._sess.initialize()
        return self

    async def __aexit__ (self, *args):
        await self.stack.aclose()


    async def tools_list (self) -> types.ListToolsResult: 
        return (await self._sess.list_tools()).tools
    
    async def tool_call (self, tools_name ,*args , **kwargs) -> types.CallToolResult :
        return (await self._sess.call_tool(tools_name , *args , **kwargs))


    async def list_resources (self) -> types.ReadResourceResult:
        return (await self._sess.list_resources())

    async def template_resources (self) -> types.ListResourcesResult:
        return (await self._sess.list_resource_templates())

    async def read_resource(self, uri: str) -> types.ReadResourceResult:
        result = await self._sess.read_resource(AnyUrl(uri))
        resource = result.contents[0]
        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                try:
                    return json.loads(resource.text)
                except json.JSONDecodeError:
                    return resource.text  # Return as plain text if JSON is invalid            
        return resource.text
    

    




async def main():
    async with MCPClient("http://127.0.0.1:8000/mcp") as client:
        # tools = await client.tools_list() 
        # print( tools)
        # tool_call = await client.tool_call("edit_document", {"id" : "report.pdf",
        #                                                      "old_content": "The report details the state of a 20m condenser tower.",
        #                                                      "new_content": "The report details the state of a 30m condenser tower."})
        # print("\ntool call result:\n" , tool_call)
        all_resources = await client.list_resources()        
        uri = all_resources.resources[0].uri
        print("\nAll Resources:\n" , all_resources)
        resource_content = await client.read_resource(uri)
        print(f"\nResource content of {uri}:\n" , resource_content)
        templates = await client.template_resources()
        templates_uri = templates.resourceTemplates[0].uriTemplate
        print("\nAll Resource Templates:\n" , templates_uri)
        
        # for r in resource_content:
        #     result = await client.read_resource(f"{uri}/{r}")
        #     print(f"\nResource content of {uri}/{r}:\n", result)
        # return result

        for r in resource_content:
            uri = templates_uri.replace("{id}",r)
            result = await client.read_resource(uri)
            print(f"\nResource content of {uri}:\n", result)
        return result

if __name__ == "__main__":
    asyncio.run(main())
