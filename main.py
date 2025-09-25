from mcp.server.fastmcp import FastMCP
from pydantic import Field
mcp = FastMCP(name="hello_mcp", stateless_http=True)
docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

@mcp.tool()
def hello(name: str = Field(..., description="The name of the person to greet")) -> str:
    """Say hello to someone."""
    return f"\nHello, {name}!\n"


@mcp.tool(name="read_document", description="Read the contents of a document by its ID.")
def read_document(id: str = Field(..., description="The ID of the document to read")) -> str:
    if id not in docs:
        raise ValueError(f"Document with id '{id}' not found.")
    return docs.get(id, "document not found")

@mcp.tool(name="edit_document", description="Edit the contents of a document by its ID.")
def edit_document(id: str = Field(..., description="The ID of the document to edit"),
                  old_content: str = Field(..., description="The content that needs to be replaced including white spaces and new lines"),
                  new_content: str = Field(..., description="The new content that will replace the old content")) -> str:
    if id not in docs:
        raise ValueError(f"Document with id '{id}' not found.")
    if docs[id] != old_content:
        raise ValueError("Old content does not match.")
    docs[id] = new_content
    return docs[id]



mcp_server = mcp.streamable_http_app()
