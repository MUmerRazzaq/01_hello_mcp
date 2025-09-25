# Hello World MCP Project

This project demonstrates a basic implementation of the Model Context Protocol (MCP) using Python, featuring both server and client implementations.

## Project Overview

This is a learning project following the Anthropic MCP Course, implementing a simple MCP server with tools for greeting users and managing documents.

## Project Structure

```
01_hello_mcp/
├── main.py                    # MCP Server implementation
├── client.py                  # Simple HTTP client
├── client_implementation.py   # Advanced MCP client
├── pyproject.toml            # Project dependencies
├── README.md                 # Basic project info
├── .python-version           # Python version specification
└── .gitignore               # Git ignore rules
```

## Features

### MCP Server ([main.py](main.py))

The server implements three main tools using the FastMCP framework:

1. **`hello`** - A greeting tool that takes a name parameter
2. **`read_document`** - Reads content from predefined documents
3. **`edit_document`** - Edits document content

#### Available Documents

- `deposition.md` - Testimony documentation
- `report.pdf` - Condenser tower report
- `financials.docx` - Budget and expenditures
- `outlook.pdf` - System performance projections
- `plan.md` - Implementation steps
- `spec.txt` - Technical requirements

### Client Implementations

#### Simple HTTP Client ([client.py](client.py))

- Direct HTTP requests to the MCP server
- Demonstrates basic tool calling functionality
- Uses standard `requests` library

#### Advanced MCP Client ([client_implementation.py](client_implementation.py))

- Proper MCP client using the official MCP library
- Implements async context management
- Features:
  - [`MCPclient`](client_implementation.py) class with async context management
  - [`tools_list()`](client_implementation.py) method to retrieve available tools
  - [`tool_call()`](client_implementation.py) method to execute tools

## Dependencies

From [pyproject.toml](pyproject.toml):

- `mcp[cli]>=1.12.1` - Model Context Protocol library
- `requests>=2.32.4` - HTTP client library
- `uvicorn>=0.35.0` - ASGI server

## Usage

### Running the Server

```bash
# Start the MCP server
uvicorn main:mcp_server --reload
```

The server will be available at `http://127.0.0.1:8000/mcp`

### Using the Simple Client

```bash
python client.py
```

### Using the Advanced Client

```bash
python client_implementation.py
```

## Key Learning Points

1. **MCP Server Setup**: Using [`FastMCP`](main.py) for quick server implementation
2. **Tool Definition**: Decorating functions with `@mcp.tool()` to expose them as MCP tools
3. **Parameter Validation**: Using Pydantic [`Field`](main.py) for parameter descriptions and validation
4. **Client Implementation**: Both simple HTTP and proper MCP client approaches
5. **Async Context Management**: Proper resource management in the MCP client

## Example Tool Calls

### Greeting Tool

```python
# Call the hello tool
tool_call = await client.tool_call("hello", {"name": "TestUser"})
```

### Document Operations

```python
# Read a document
content = await client.tool_call("read_document", {"id": "plan.md"})

# Edit a document
updated = await client.tool_call("edit_document", {
    "id": "plan.md",
    "old_content": "old text",
    "new_content": "new text"
})
```

## Next Steps

This project serves as a foundation for more advanced MCP implementations, including:

- Adding more complex tools
- Implementing resource management
- Adding authentication
- Scaling to production environments

## Technology Stack

- **Python 3.11+**
- **FastMCP** - Rapid MCP server development
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server
- **asyncio** - Asynchronous programming

---

_This project is part of learning the Model Context Protocol (MCP) by following the Anthropic MCP Course._
