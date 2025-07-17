import uvicorn
import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from starlette.types import ASGIApp, Scope, Receive, Send
from typing import Dict, Tuple, Optional, Any, List

from secret_manager import SecretManager
from credential_helper import get_workflow_required_credentials
from n8n_credential_extractor import N8NCredentialExtractor

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# N8N Constants
N8N_INSTANCE_URL = os.getenv('N8N_INSTANCE_URL')
N8N_API_KEY = os.getenv('N8N_API_KEY')

# Global variables for dynamic credentials
N8N_AUTH = None
BROWSER_ID = None

# Supabase setup
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not all([N8N_INSTANCE_URL, N8N_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class MCPPayload(BaseModel):
    user_apikey: str
    secrets: List[Dict[str, Any]] = []
    code: str
    workflow_id: str

class MCPProxyMiddleware:
    """
    Middleware that builds MCPs on-demand for each request and cleans up immediately.
    """
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path.startswith("/mcp/"):
            parts = path.split("/")
            if len(parts) >= 4:
                workflow_id, user_apikey = parts[2], parts[3]
                
                mcp_config = self._get_mcp_config(workflow_id, user_apikey)
                if not mcp_config:
                    await self.app(scope, receive, send)
                    return
                
                await self._handle_mcp_request(scope, receive, send, mcp_config)
                return
        
        await self.app(scope, receive, send)
    
    async def _handle_mcp_request(self, scope: Scope, receive: Receive, send: Send, mcp_config: dict):
        """Build MCP, handle request, cleanup - all in one go."""
        logger.info(f"Building MCP '{mcp_config['workflow_id']}' for user API key '{mcp_config['user_apikey'][:8]}...'")
        
        try:
            # Build MCP
            mcp = FastMCP(
                mcp_config['workflow_id'],
                stateless_http=True,
                streamable_http_path="/",
            )
            
            
            # Execute user code
            exec_namespace = {
                "mcp": mcp,
                # "SecretManager": SecretManager,
                "N8NConfigManager": N8NConfigManager,
                "user_apikey": mcp_config['user_apikey'],
                "workflow_id": mcp_config['workflow_id'],
                "N8N_INSTANCE_URL": N8N_INSTANCE_URL,
            }
            exec(mcp_config['code'], exec_namespace)
            
            # Get the ASGI app
            mcp_app = mcp.streamable_http_app()
            
            logger.info(f"MCP '{mcp_config['workflow_id']}' built successfully")
            
            # Run with session manager
            async with mcp.session_manager.run():
                # Adjust scope path for MCP
                mcp_scope = scope.copy()
                original_path = scope.get("path", "")
                mcp_path = original_path.replace(f"/mcp/{mcp_config['workflow_id']}/{mcp_config['user_apikey']}", "", 1) or "/"
                mcp_scope["path"] = mcp_path
                
                # Handle the request
                await mcp_app(mcp_scope, receive, send)
            
            logger.info(f"Cleaned up MCP '{mcp_config['workflow_id']}' for user API key '{mcp_config['user_apikey'][:8]}...'")
            
        except Exception as e:
            logger.error(f"Error in MCP request: {e}")
            await send({
                'type': 'http.response.start',
                'status': 500,
                'headers': [[b'content-type', b'text/plain']],
            })
            await send({
                'type': 'http.response.body',
                'body': f"MCP Error: {str(e)}".encode(),
            })
    
    def _get_mcp_config(self, workflow_id: str, user_apikey: str) -> Optional[dict]:
        """Get MCP configuration by name and user API key."""
        key = (workflow_id, user_apikey)
        return mcp_configs.get(key)

# Storage for MCP configurations indexed by (workflow_id, user_apikey)
mcp_configs: Dict[Tuple[str, str], dict] = {}

def load_mcp_configs_from_supabase():
    global mcp_configs
    try:
        response = supabase.table('mcp_configs').select('workflow_id, user_apikey, code').execute()
        
        loaded_configs = {}
        for row in response.data:
            key = (row["workflow_id"], row["user_apikey"])
            loaded_configs[key] = {
                "workflow_id": row["workflow_id"],
                "user_apikey": row["user_apikey"],
                "code": row["code"],
            }
        mcp_configs = loaded_configs
        logger.info(f"Loaded {len(mcp_configs)} MCP configurations from Supabase")
    except Exception as e:
        logger.error(f"Error loading MCP configs from Supabase: {e}")
        mcp_configs = {}

async def extract_n8n_credentials():
    """Extract N8N credentials on startup - required for app to start"""
    global N8N_AUTH, BROWSER_ID
    
    try:
        # Get credentials from environment
        username = os.getenv('N8N_USERNAME')
        password = os.getenv('N8N_PASSWORD')
        
        if not username or not password:
            raise ValueError("N8N_USERNAME and N8N_PASSWORD must be set in environment variables")
        
        logger.info("Extracting N8N credentials...")
        extractor = N8NCredentialExtractor(username, password, N8N_INSTANCE_URL)
        credentials = await extractor.extract_credentials()
        
        N8N_AUTH = credentials['n8n_auth']
        BROWSER_ID = credentials['browser_id']
        
        logger.info(f"Successfully extracted N8N credentials")
        logger.info(f"Browser ID: {BROWSER_ID[:8]}...")
        logger.info(f"Auth token: {N8N_AUTH[:20]}...")
        
    except Exception as e:
        logger.error(f"Failed to extract N8N credentials: {e}")
        raise RuntimeError(f"N8N credential extraction failed: {e}. App cannot start without valid credentials.")

app = FastAPI(title="MCP Router")
app.add_middleware(MCPProxyMiddleware)

@app.on_event("startup")
async def startup_event():
    await extract_n8n_credentials()
    load_mcp_configs_from_supabase()

async def register_mcp(payload: MCPPayload):
    """Register an MCP configuration that will be built on-demand."""
    key = (payload.workflow_id, payload.user_apikey)

    config = {
        "workflow_id": payload.workflow_id,
        "user_apikey": payload.user_apikey,
        "code": payload.code,
    }
    
    try:
        supabase.table('mcp_configs').upsert({
            'workflow_id': payload.workflow_id,
            'user_apikey': payload.user_apikey,
            'code': payload.code
        }).execute()
        mcp_configs[key] = config
        logger.info(f"Added MCP config to Supabase: {payload.workflow_id}")
    except Exception as e:
        logger.error(f"Error adding MCP config to Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save to database: {e}")

    path = f"/mcp/{payload.workflow_id}/{payload.user_apikey}"
    logger.info(
        f"Registered MCP '{payload.workflow_id}' for user API key '{payload.user_apikey[:8]}...'. Will build on-demand at {path}"
    )

    return {
        "status": "success",
        "workflow_id": payload.workflow_id,
        "user_apikey": payload.user_apikey,
        "path": path,
        "message": "MCP registered. Will be built on first request.",
    }

@app.get("/list")
async def list_mcps():
    """Lists all registered MCPs."""
    return {
        "mcps": [
            {
                "workflow_id": workflow_id,
                "user_apikey": user_apikey[:8] + "...",
                "path": f"/mcp/{workflow_id}/{user_apikey}",
                "status": "registered"
            }
            for (workflow_id, user_apikey), config in mcp_configs.items()
        ]
    }

@app.post("/remove/{workflow_id}/{user_apikey}")
async def remove_mcp(workflow_id: str, user_apikey: str):
    """Remove an MCP registration and its credential mapping."""
    key = (workflow_id, user_apikey)
    if key not in mcp_configs:
        raise HTTPException(status_code=404, detail="MCP not found.")
    
    try:
        supabase.table('mcp_configs').delete().eq('workflow_id', workflow_id).eq('user_apikey', user_apikey).execute()
        del mcp_configs[key]
        logger.info(f"Removed MCP config from Supabase: {workflow_id}")
    except Exception as e:
        logger.error(f"Error removing MCP config from Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to remove from database: {e}")

    logger.info(f"Removed MCP registration '{workflow_id}' for user API key '{user_apikey[:8]}...'.")
    return {"status": "success", "message": f"MCP '{workflow_id}' for user API key removed."}

class N8NConfigManager:
    """Manager for N8N configuration data - uses dynamically extracted credentials"""
    
    @classmethod
    def get_config(cls, workflow_id: str = "") -> Dict[str, str]:
        """Get N8N configuration with dynamically extracted credentials"""  
        return {
            "instance_url": N8N_INSTANCE_URL,
            "api_key": N8N_API_KEY,
            "workflow_id": workflow_id,
            "browser_id": BROWSER_ID,
            "n8n_auth": N8N_AUTH
        }

@app.get("/n8n/required_credentials/{workflow_id}")
async def get_n8n_credentials(workflow_id: str):
    """Get the credentials for a n8n workflow"""
    creds = await get_workflow_required_credentials(workflow_id)
    return creds

@app.get("/n8n/credentials/status")
async def get_n8n_credentials_status():
    """Get the status of N8N credentials"""
    return {
        "browser_id": BROWSER_ID[:8] + "..." if BROWSER_ID else None,
        "auth_token": N8N_AUTH[:20] + "..." if N8N_AUTH else None,
        "extracted": bool(N8N_AUTH and BROWSER_ID)
    }

N8N_MCP_CODE = """
@mcp.tool()
def execute_workflow() -> dict:

    config = N8NConfigManager.get_config(workflow_id)
    import httpx
    import json
        
    details_url = f"{N8N_INSTANCE_URL}/api/v1/workflows/{config['workflow_id']}"
    details_headers = {"X-N8N-API-KEY": config["api_key"]}

    try:
        details_response = httpx.get(details_url, headers=details_headers, timeout=10)
        details_response.raise_for_status()
        workflow_data = details_response.json()

        nodes = []
        for node in workflow_data.get("nodes", []):
            mapped_node = {
                "parameters": node.get("parameters", {}),
                "type": node.get("type"),
                "typeVersion": node.get("typeVersion"),
                "position": node.get("position", []),
                "id": node.get("id"),
                "name": node.get("name"),
            }
            if "credentials" in node:
                mapped_node["credentials"] = node["credentials"]
            for optional_field in ["executeOnce", "disabled", "notes", "color"]:
                if optional_field in node:
                    mapped_node[optional_field] = node[optional_field]
            nodes.append(mapped_node)

        execution_payload = {
            "workflowData": {
                "name": workflow_data.get("name"),
                "nodes": nodes,
                "pinData": workflow_data.get("pinData", {}),
                "connections": workflow_data.get("connections", {}),
                "active": workflow_data.get("active", False),
                "settings": workflow_data.get("settings", {}),
                "tags": workflow_data.get("tags", []),
                "versionId": workflow_data.get("versionId"),
                "meta": workflow_data.get("meta", {}),
                "id": workflow_data.get("id"),
            },
            "startNodes": [],
        }

        execution_url = f"{N8N_INSTANCE_URL}/rest/workflows/{config['workflow_id']}/run?partialExecutionVersion=2"
        execution_headers = {
            "browser-id": config["browser_id"],
            "cookie": f"n8n-auth={config['n8n_auth']}",
            "content-type": "application/json",
        }

        execution_response = httpx.post(
            execution_url.strip(),
            headers=execution_headers,
            json=execution_payload,
            timeout=30,
        )
        execution_response.raise_for_status()
        return execution_response.json()

    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_execution_log(execution_id: str) -> dict:
    \"\"\"Get the execution log of a n8n workflow\"\"\"
    config = N8NConfigManager.get_config(workflow_id)
    import httpx
    url = f"{N8N_INSTANCE_URL}/api/v1/executions/{execution_id}"
    headers = {"X-N8N-API-KEY": config["api_key"]}
    try:
        response = httpx.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_workflow_details() -> dict:
    \"\"\"Get the details of a n8n workflow\"\"\"
    config = N8NConfigManager.get_config(workflow_id)
    import httpx
    url = f"{N8N_INSTANCE_URL}/api/v1/workflows/{config['workflow_id']}"
    headers = {"X-N8N-API-KEY": config["api_key"]}
    try:
        response = httpx.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


"""

@app.post("/n8n/build")
async def n8n_builder(payload: dict):
    """Register a n8n MCP that will be built on-demand."""
    mcp_payload = MCPPayload(
        user_apikey=payload.get("user_apikey", ""),
        code=N8N_MCP_CODE,
        workflow_id=payload.get("workflow_id", ""),
    )
    return await register_mcp(mcp_payload)

if __name__ == "__main__":
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 6545))
    uvicorn.run(app, host=host, port=port, log_level="info")