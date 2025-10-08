from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.prompts import base
from mcp.types import (PromptMessage, TextContent, ImageContent, 
                       SamplingMessage, ModelPreferences, ModelHint)
from pydantic import Field
import base64
import os
from pathlib import Path
import random
import asyncio




mcp = FastMCP(name="hello_mcp", stateless_http=False )
docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


images = {
    "diagram.png": "d:/MCP_Learning/01_hello_mcp/images/diagram.png",
    "chart.jpeg": "d:/MCP_Learning/01_hello_mcp/images/chart.jpeg",
    "screenshot.jpg": "d:/MCP_Learning/01_hello_mcp/images/screenshot.jpg",
}


# images_path = Path(__file__).parent / "images"
# images_path.mkdir(parents=True, exist_ok=True)
# image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}
# image_files = {
#     file.name: file
#     for file in images_path.iterdir()
#     if file.suffix.lower() in image_extensions and file.is_file()
# }


@mcp.tool(name="story_generator", description="Generate a short story based on a given topic.")
async def story_generator(topic: str, ctx : Context) -> str:
    """Generate a short story based on a given topic. Using Client LLM"""
    print(f"-> Server: Tool 'create_story' called with topic: '{topic}'")
    await ctx.info(f"-> Server: Tool 'create_story' called with topic: '{topic}'")
    try:
        print(f"-> Server: Sending 'sampling/create' request to client...")
        await ctx.info("-> Server: Sending 'sampling/create' request to client...")
        response = await ctx.session.create_message(
            messages=[
                SamplingMessage(role="user", content=TextContent(type="text", text=f"Write a short story in three lines about : {topic}.")),
            ],
            model_preferences=ModelPreferences(hints=[ModelHint(name="gemini-2.0-flash")]),
            # model_preferences=ModelPreferences(hints=[{"name": "gemini-2.0-flash"}]),
            max_tokens=500
            
        )

        print(f"-> Server: Received response from client: {response}")
        await ctx.info(f"-> Server: Received response from client.")
        if response.content.type == "text":
            return response.content.text
        return str(response)

    except Exception as e:
        print(f"-> Server: An error occurred during sampling: {e}")
        await ctx.error(f"-> Server: An error occurred during sampling: {e}")
        return f"Error asking client to generate story: {e}"





@mcp.tool()
async def get_db(ctx : Context , db_name: str) -> list[TextContent]:
    await ctx.info(f"connecting to db {db_name}")
    
    await ctx.report_progress(progress=25,total=100, message="starting connection")
    await asyncio.sleep(2)
    await ctx.report_progress(progress=50,total=100, message="connecting to db server")
    await asyncio.sleep(2)
    await ctx.report_progress(progress=75,total=100, message="connecting to db schema")
    await asyncio.sleep(2)
    if random.choice([False,True]):
        await ctx.error("failed to connect to db")
        await ctx.report_progress(progress=75,total=100, message="error connecting to db")
        raise Exception("failed to connect to db")

    await asyncio.sleep(2)
    progress = 100
    message = "connected to db"
    await ctx.report_progress(progress=progress,total=100, message=message)
    await ctx.info(f"connected to db {db_name}")
    return [TextContent(type="text", text=f"connected to db from {db_name}")]


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

@mcp.resource(uri="docs://documents",mime_type="application/json")
def list_documents() -> list[str]:
    """List all document IDs."""
    return list(docs.keys())


@mcp.resource(uri="docs://documents/{id}", mime_type="text/plain" )
def get_document(id: str) -> str:
    if id not in docs:
        raise ValueError(f"Document with id '{id}' not found.")
    return docs[id]




@mcp.resource(uri="images://images", mime_type="application/json")
def list_images() -> list[str]:
    """List all available image IDs."""
    return list(images.keys())


@mcp.resource(uri="images://images/{id}", mime_type="text/plain")
def get_image_base64(id: str) -> str:
    """Get image as base64 encoded string."""
    if id not in images:
        raise ValueError(f"Image with id '{id}' not found.")
    
    file_path = Path(images[id])
    if not file_path.exists():
        raise ValueError(f"Image file not found at path: {file_path}")
    
    with open(file_path, "rb") as f:
        image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')

@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format.",
)
def format_document(
    doc_content: str = Field(description="Contents of the document to format"),
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The contents of the document you need to reformat is:
    <document_content>
    {doc_content}
    </document_content>

    Add in headers, bullet points, tables, etc as necessary. Feel free to add in extra text, but don't change the meaning of the report.
    After the document has been edited, respond with the final version of the doc. Don't explain your changes.
    """

    return [base.UserMessage(prompt), base.AssistantMessage("Always respond with the final version of the document in markdown format.")]

@mcp.prompt(
    name="image", description="Get an image explanation."
)
def get_image(id: str) -> base.Message:
    if id not in images:
        raise ValueError(f"Image with id '{id}' not found.")
    
    file_path = Path(images[id])
    if not file_path.exists():
        raise ValueError(f"Image file not found at path: {file_path}")
    
    with open(file_path, "rb") as f:
        image_data = f.read()
        data = base64.b64encode(image_data).decode('utf-8')
        return base.UserMessage(
            content=ImageContent(
                type="image",
                data=data,
                mimeType=f"image/{file_path.suffix.lstrip('.')}",
            )
        )
        # return PromptMessage(
        #     role="user",
        #     content=ImageContent(
        #         type="image",
        #         data=data,
        #         mimeType=f"image/{file_path.suffix.lstrip('.')}",
        #     )
        # )




mcp_server = mcp.streamable_http_app()
