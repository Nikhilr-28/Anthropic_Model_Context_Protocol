from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# Tool 1: Read document contents
@mcp.tool()
def read_doc_contents(
    doc_id: str = Field(description="The ID of the document to read")
) -> str:
    """Read the contents of a document by its ID."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    return docs[doc_id]

# Tool 2: Edit document
@mcp.tool()
def edit_document(
    doc_id: str = Field(description="The ID of the document to edit"),
    old_string: str = Field(description="The string to find and replace"),
    new_string: str = Field(description="The string to replace with")
) -> str:
    """Edit a document by finding and replacing a string."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    
    if old_string not in docs[doc_id]:
        raise ValueError(f"String '{old_string}' not found in document '{doc_id}'")
    
    docs[doc_id] = docs[doc_id].replace(old_string, new_string)
    return f"Successfully replaced '{old_string}' with '{new_string}' in '{doc_id}'"

# Resource 1: Static resource - list all document IDs
@mcp.resource("docs://documents")
def list_documents() -> list[str]:
    """Return a list of all document IDs."""
    return list(docs.keys())

# Resource 2: Templated resource - get specific document content
@mcp.resource("docs://documents/{doc_id}")
def get_document(doc_id: str) -> str:
    """Return the contents of a specific document by ID."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    return docs[doc_id]

# Prompt 1: Format document in markdown
@mcp.prompt()
def format(doc_id: str = Field(description="The ID of the document to format")) -> str:
    """Rewrite a document in markdown format."""
    prompt_text = f"""Please rewrite the document '{doc_id}' in proper markdown format.

Steps:
1. Use the read_doc_contents tool to fetch the current document content
2. Reformat the content using proper markdown syntax (headers, lists, emphasis, etc.)
3. Use the edit_document tool to replace the old content with the new markdown-formatted content
4. Confirm the changes were successful

Make sure to preserve all the original information while improving the formatting."""
    
    return prompt_text

# Prompt 2: Summarize document
@mcp.prompt()
def summarize(doc_id: str = Field(description="The ID of the document to summarize")) -> str:
    """Summarize a document concisely."""
    prompt_text = f"""Please provide a concise summary of the document '{doc_id}'.

Steps:
1. Use the read_doc_contents tool to fetch the document content
2. Analyze the key points and main ideas
3. Provide a brief, clear summary (2-3 sentences)

Focus on the most important information and keep it concise."""
    
    return prompt_text


if __name__ == "__main__":
    mcp.run(transport="stdio")