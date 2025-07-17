from mcp.server.fastmcp import FastMCP

mcp = FastMCP("n8n")

@mcp.tool()
def get_require_credentials(instance_url: str, api_key: str) -> dict:
    """Get the result of a n8n workflow"""

    return {
        "instance_url": instance_url,
        "api_key": api_key
    }


@mcp.tool()
def execute_workflow(instance_url: str, api_key: str, workflow_id: str) -> dict:
    """Execute a n8n workflow"""

    return "test"

@mcp.tool()
def get_workflow_log(instance_url: str, api_key: str, workflow_id: str) -> dict:
    """Get the result of a n8n workflow"""
    return "test"

@mcp.tool()
def get_workflow_details(instance_url: str, api_key: str, workflow_id: str) -> dict:
    """Get the status of a n8n workflow"""
    
    return "test"

if __name__ == "__main__":
    mcp.run(transport="streamable_http")