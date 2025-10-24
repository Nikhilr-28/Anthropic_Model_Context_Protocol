# MCP Chat - Model Context Protocol Implementation

A command-line interface application demonstrating the **Model Context Protocol (MCP)** architecture, built as part of the Anthropic MCP certification course. This project implements both an MCP client and server to showcase how MCP enables seamless integration between AI models and external services.

## 🎯 Project Overview

This educational project implements a complete MCP system with:
- **Custom MCP Server** exposing document management capabilities
- **Custom MCP Client** connecting the application to the server
- **CLI Interface** for interactive chat with Claude
- **Document Management System** with in-memory storage

### Architecture

![MCP Architecture](docs/architecture_overview.png)

**Key Components:**
1. **MCP Client** - Wrapper class managing server connections
2. **Client Session** - Actual connection to the MCP server
3. **MCP Server** - Exposes tools, resources, and prompts
4. **Document Storage** - In-memory document management

## 🏗️ MCP Architecture

### Server Components

![Server Components](docs/server_components.png)

The MCP server implements three types of primitives:

#### **Tools** (Model-Controlled)
Tools that Claude can decide to execute:
- `read_doc_contents` - Reads document content by ID
- `edit_document` - Find and replace text in documents

#### **Resources** (App-Controlled)
Data endpoints the application can fetch:
- `docs://documents` - Lists all document IDs
- `docs://documents/{doc_id}` - Fetches specific document content

#### **Prompts** (User-Controlled)
Predefined workflows triggered by users:
- `/format` - Reformats documents in markdown
- `/summarize` - Generates concise summaries

### Communication Flow

![Communication Flow](docs/communication_flow.png)

**Message Flow:**
1. User sends query → Application code
2. Application requests tools via MCP Client
3. Client sends `ListToolsRequest` to MCP Server
4. Server responds with available tools
5. Application sends query + tools to Claude
6. Claude requests tool execution
7. Client sends `CallToolRequest` to MCP Server
8. Server executes tool (e.g., reads document)
9. Results flow back through the chain
10. User receives final response

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10+
- Anthropic API Key ([Get one here](https://console.anthropic.com/))

### Installation

#### Option 1: Using uv (Recommended)

```bash
# Install uv
pip install uv

# Clone the repository
git clone <your-repo-url>
cd cli_project

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

#### Option 2: Using pip

```bash
# Clone the repository
git clone <your-repo-url>
cd cli_project

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
CLAUDE_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_API_KEY=your-api-key-here
```

### Running the Application

```bash
uv run main.py
# or
python main.py
```

## 📚 Implementation Details

### MCP Server (`mcp_server.py`)

Implements all three MCP primitives using the FastMCP Python SDK:

**Tools:**
```python
@mcp.tool()
def read_doc_contents(doc_id: str = Field(description="The ID of the document to read")) -> str:
    """Read the contents of a document by its ID."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    return docs[doc_id]

@mcp.tool()
def edit_document(
    doc_id: str = Field(description="The ID of the document to edit"),
    old_string: str = Field(description="The string to find and replace"),
    new_string: str = Field(description="The string to replace with")
) -> str:
    """Edit a document by finding and replacing a string."""
    # Implementation details...
```

**Resources:**
```python
@mcp.resource("docs://documents")
def list_documents() -> list[str]:
    """Return a list of all document IDs."""
    return list(docs.keys())

@mcp.resource("docs://documents/{doc_id}")
def get_document(doc_id: str) -> str:
    """Return the contents of a specific document by ID."""
    # Implementation details...
```

**Prompts:**
```python
@mcp.prompt()
def format(doc_id: str = Field(description="The ID of the document to format")) -> str:
    """Rewrite a document in markdown format."""
    # Returns prompt text with instructions for Claude

@mcp.prompt()
def summarize(doc_id: str = Field(description="The ID of the document to summarize")) -> str:
    """Summarize a document concisely."""
    # Returns prompt text with instructions for Claude
```

### MCP Client (`mcp_client.py`)

Implements five key methods for server communication:

```python
async def list_tools(self) -> list[types.Tool]:
    """Return a list of tools defined by the MCP server."""
    result = await self.session().list_tools()
    return result.tools

async def call_tool(self, tool_name: str, tool_input: dict) -> types.CallToolResult | None:
    """Call a particular tool and return the result."""
    return await self.session().call_tool(tool_name, tool_input)

async def list_prompts(self) -> list[types.Prompt]:
    """Return a list of prompts defined by the MCP server."""
    result = await self.session().list_prompts()
    return result.prompts

async def get_prompt(self, prompt_name: str, args: dict[str, str]):
    """Get a particular prompt defined by the MCP server."""
    result = await self.session().get_prompt(prompt_name, arguments=args)
    return result.messages

async def read_resource(self, uri: str) -> Any:
    """Read a resource, parse the contents and return it."""
    result = await self.session().read_resource(AnyUrl(uri))
    resource = result.contents[0]
    
    if resource.mimeType == "application/json":
        return json.loads(resource.text)
    else:
        return resource.text
```

## 🧪 Testing & Results

### Test 1: Document Reference with @ Symbol

**Input:**
```
> what is @report.pdf about?
```

**Output:**
```
I'll need to read the document to answer your question about what report.pdf is about. Let me do that for you.

Response:
The report is about the state of a 20-meter condenser tower.
```

✅ **Result:** Document contents automatically included in context via resources.

---

### Test 2: Tool Usage - Edit Document

**Input:**
```
> in report.pdf, replace "20m" with "25m"
```

**Output:**
```
I'll replace "20m" with "25m" in the report.pdf document.

Response:
I've successfully replaced "20m" with "25m" in the report.pdf document.
```

✅ **Result:** Claude successfully used the `edit_document` tool.

---

### Test 3: Verify Edit Persistence

**Input:**
```
> read report.pdf again
```

**Output:**
```
I'll read report.pdf again for you.

Response:
The report details the state of a 25m condenser tower.
```

✅ **Result:** Edit persisted in memory storage.

---

### Test 4: Prompt Usage - Format Document

**Input:**
```
> /format deposition.md
```

**Output:**
```
I'll help you rewrite "deposition.md" in proper markdown format. Let me first read the current content.

Now I'll reformat this content using proper markdown syntax and then update the document.

Response:
I've successfully reformatted "deposition.md" with proper markdown formatting. The document now includes:
1. A main heading ("# Deposition")
2. A subheading ("## Summary")
3. Proper emphasis on the name with bold formatting ("**Angela Smith, P.E.**")

The changes have been successfully applied to the document while preserving all the original information.
```

✅ **Result:** Prompt workflow executed successfully, Claude used multiple tools.

---

### Test 5: Prompt Usage - Summarize Document

**Input:**
```
> /summarize financials.docx
```

**Output:**
```
I'll provide a concise summary of the "financials.docx" document. Let me first read its content.

Response:
The document outlines the project's budget and expenditures. It provides a financial overview that details the allocation of funds and current spending within the project framework.
```

✅ **Result:** Summarization prompt worked as expected.

---

### Test 6: Multiple Document Comparison

**Input:**
```
> compare @report.pdf and @outlook.pdf
```

**Output:**
```
I'll compare the content of both documents for you. Let me read them first.

Response:
The documents have different content and purposes:
- report.pdf focuses on the current state of a 25m condenser tower, providing information about its condition.
- outlook.pdf discusses projected future performance of the system, offering forward-looking analysis rather than current state assessment.

The first document is descriptive of existing infrastructure, while the second is predictive about system performance.
```

✅ **Result:** Multiple document resources loaded and compared successfully.

## 📁 Project Structure

```
cli_project/
├── .env                    # Environment configuration
├── .venv/                  # Virtual environment
├── main.py                 # Application entry point
├── mcp_server.py          # MCP server implementation
├── mcp_client.py          # MCP client implementation
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Project metadata
├── README.md              # This file
└── core/
    ├── chat.py            # Base chat functionality
    ├── cli_chat.py        # CLI-specific chat implementation
    ├── cli.py             # Command-line interface
    ├── claude.py          # Claude API wrapper
    └── tools.py           # Tool management utilities
```

## 🎓 Key Learnings

### MCP Primitives

1. **Tools** - Add capabilities to Claude
   - Model-controlled (Claude decides when to use)
   - Example: JavaScript execution, API calls
   - Use case: Extend Claude's abilities

2. **Resources** - Provide data to applications
   - App-controlled (application decides when to fetch)
   - Example: Document listings, autocomplete options
   - Use case: UI display, prompt augmentation

3. **Prompts** - Enable user workflows
   - User-controlled (triggered by user actions)
   - Example: Chat starter buttons, slash commands
   - Use case: Predefined workflows, templates

### MCP Benefits

- **Reduced Developer Burden** - Pre-built tools from service providers
- **Standardized Communication** - Consistent protocol for all services
- **Separation of Concerns** - Server handles tools, client handles communication
- **Reusability** - One MCP server can serve multiple applications

## 💰 Cost Considerations

**Claude Sonnet 4.5 Pricing:**
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens

**Estimated Costs for This Project:**
- Typical 20-30 message session: **$0.05 - $0.20**
- Extensive testing session: **< $1.00**
- Full course completion: **$2 - $5**

Very affordable for educational purposes!

## 🛠️ Development Tools

### MCP Inspector

Test your MCP server before deployment:

```bash
mcp dev mcp_server.py
```

This opens an in-browser debugger where you can:
- View all available tools, resources, and prompts
- Manually test tool invocations
- Verify server responses
- Debug issues before integration

## 📝 Available Documents

The server manages these in-memory documents:

- `deposition.md` - Testimony of Angela Smith, P.E.
- `report.pdf` - State of a 25m condenser tower
- `financials.docx` - Project budget and expenditures
- `outlook.pdf` - Projected system performance
- `plan.md` - Project implementation steps
- `spec.txt` - Technical equipment requirements

## 🎮 Usage Examples

### Basic Queries
```
> what's 2 + 2?
> explain quantum computing
```

### Document Operations
```
> read deposition.md
> what's in @financials.docx?
> edit spec.txt to replace "equipment" with "hardware"
```

### Commands (Prompts)
```
> /format plan.md
> /summarize outlook.pdf
```

### Multiple Documents
```
> compare @plan.md and @spec.txt
> what are the common themes in @deposition.md and @report.pdf?
```

## 🐛 Troubleshooting

### Common Issues

**1. API Key Error**
```
AssertionError: Error: ANTHROPIC_API_KEY cannot be empty
```
**Solution:** Add your API key to `.env` file

**2. Model Error**
```
AssertionError: Error: CLAUDE_MODEL cannot be empty
```
**Solution:** Add `CLAUDE_MODEL=claude-sonnet-4-5-20250929` to `.env`

**3. Import Errors (Pylance)**
```
Import "mcp" could not be resolved
```
**Solution:** These are editor warnings. Either:
- Select correct Python interpreter in VS Code
- Reload VS Code window
- Ignore (code will run fine)

**4. Credit Balance Error**
```
Your credit balance is too low to access the Anthropic API
```
**Solution:** Add credits at https://console.anthropic.com/settings/billing

## 🔗 Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Official MCP Servers](https://github.com/modelcontextprotocol)

## 📜 License

This project is built for educational purposes as part of the Anthropic MCP certification course.

## 🙏 Acknowledgments

- Anthropic for the MCP specification and course materials
- The MCP community for developing the protocol
- Claude for assisting with implementation and testing

## 📧 Contact

For questions or feedback about this implementation, please reach out through the course platform.

---

**Built with ❤️ as part of the Anthropic MCP Certification Course**
