from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="hello_mcp", stateless_http=True)


@mcp.tool()
def hello(name: str) -> str:
    """Say hello to someone."""
    print(f"Hello, {name}!")
    return f"____________________Hello, {name}!____________________"



mcp_server = mcp.streamable_http_app()
