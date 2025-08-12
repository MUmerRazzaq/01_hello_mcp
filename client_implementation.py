from mcp import ClientSession , types
from mcp.client.streamable_http import streamablehttp_client
from contextlib import AsyncExitStack
import asyncio

class MCPclient:
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


async def main():
    async with MCPclient("http://127.0.0.1:8000/mcp") as client:
        tools = await client.tools_list()
        print(tools)
        tool_call = await client.tool_call("hello", {"name" : "user"})
        print("tool call result =======>" , tool_call)

asyncio.run(main())