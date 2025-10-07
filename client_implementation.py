from mcp import ClientSession , types
from mcp.shared.context import RequestContext
from mcp.client.streamable_http import streamablehttp_client
from contextlib import AsyncExitStack
import asyncio
import json
from pydantic import AnyUrl
from typing import Any
from agent import llm_agent

async def sampler(ctx: RequestContext[ClientSession, Any], param: types.CreateMessageRequestParams) -> types.CreateMessageResult | types.ErrorData:
    print("<- Client: Received 'sampling/create' request from server.")

    print(f"<- Client Parameters '{param}'.\n")
    print(f"<- Model Name '{param.modelPreferences.hints[0].name}'.\n")
    print(f"<- Client Request ID '{ctx.request_id}'.\n")
    print(f"<- Client Context '{ctx}'.\n")
    print(f"<- Client Message '{param.messages}'.\n")

    # mock_llm_response = (
    #     f"In a world of shimmering code, a brave little function set out to find the legendary Golden Bug. "
    #     f"It traversed treacherous loops and navigated complex conditionals. "
    #     f"Finally, it found not a bug, but a feature, more valuable than any treasure."
    # )

    print("-> Client: Sending story back to the server.")

    # Respond with a dictionary that matches the expected structure
    # return types.CreateMessageResult(
    #     role="assistant",
    #     content=types.TextContent(text=mock_llm_response, type="text"),
    #     model="openai/gpt-4o-mini",
    # )

    response_text = await llm_agent(input_text=str(param.messages[0].content.text), MODEL=param.modelPreferences.hints[0].name)
    return types.CreateMessageResult(  
        role="assistant",
        content=types.TextContent(type="text", text=response_text),
        model=param.modelPreferences.hints[0].name,
    )


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
            ClientSession(read, write, sampling_callback=sampler)
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
    
    async def prompts_list (self) -> types.ListPromptsResult:
        return (await self._sess.list_prompts()).prompts
    
    async def get_prompt (self, prompt_name , *args , **kwargs) -> types.GetPromptResult:
        return (await self._sess.get_prompt(prompt_name , *args , **kwargs))

    


async def fetch_and_print_resource(client: MCPClient, resource_uri: str):
    """Fetches a resource and recursively fetches its sub-resources if it's a collection."""
    print(f"\nFetching resource: {resource_uri}")
    try:
        content = await client.read_resource(resource_uri)
        print(f"Content of {resource_uri}:\n", str(content)[:200])

        if isinstance(content, list):
            # If the content is a list, fetch all sub-resources concurrently
            tasks = [
                fetch_and_print_resource(client, f"{resource_uri}/{item}")
                for item in content
            ]
            await asyncio.gather(*tasks)
    except Exception as e:
        print(f"Error fetching resource {resource_uri}: {e}")


async def main():
    async with MCPClient("http://127.0.0.1:8000/mcp") as client:
        # all_resources = await client.list_resources()
        
        # # Create a list of tasks to fetch all top-level resources concurrently
        # tasks = [
        #     fetch_and_print_resource(client, res.uri)
        #     for res in all_resources.resources
        # ]
        # await asyncio.gather(*tasks)
        # prompts = await client.prompts_list()
        # print("Available Prompts:", prompts)
        # for prompt in prompts:
        #     print(f" - {prompt.name}: {prompt.description}")
        # if "format" in [p.name for p in prompts]:
        #     formatted = await client.get_prompt("format", {"doc_content": "test document content"})
        #     print("Formatted Document:\n", formatted.messages[0].content.text)
        # tasks = [client.tool_call("story_generator", {"topic": "the sea"}) for _ in range(3)]
        # results = await asyncio.gather(*tasks)
        # for i, result in enumerate(results):
        #     print(f"Tool Call Result {i+1}:\n", result.content[0].text)

        tools = await client.tool_call("story_generator", {"topic": "the sea"})
        print("Tool Call Result:\n", tools)
        # print("Tool Call Result:\n", tools.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
