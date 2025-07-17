import httpx
import os
from dotenv import load_dotenv

load_dotenv()

N8N_INSTANCE_URL = os.getenv('N8N_INSTANCE_URL')
N8N_API_KEY = os.getenv('N8N_API_KEY')

if not N8N_INSTANCE_URL or not N8N_API_KEY:
    raise ValueError("N8N_INSTANCE_URL and N8N_API_KEY must be set in environment variables")

async def get_workflow_required_credentials(workflow_id: str) -> list:
    workflow_url = f"{N8N_INSTANCE_URL}workflows/{workflow_id}"
    headers = {"X-N8N-API-KEY": N8N_API_KEY}
    async with httpx.AsyncClient() as client:
        resp = await client.get(workflow_url, headers=headers, timeout=10)
        resp.raise_for_status()
        workflow = resp.json()
        nodes = workflow.get("nodes", [])
        required_credentials = []
        seen = set()
        for node in nodes:
            credentials = node.get("credentials", {})
            for cred_type, cred_ref in credentials.items():
                cred_id = cred_ref.get("id") if isinstance(cred_ref, dict) else None
                cred_name = cred_ref.get("name") if isinstance(cred_ref, dict) else None
                key = (cred_type, cred_id, cred_name)
                if key in seen:
                    continue
                seen.add(key)
                schema_url = f"{N8N_INSTANCE_URL}credentials/schema/{cred_type}"
                schema_resp = await client.get(schema_url, headers=headers, timeout=10)
                schema_resp.raise_for_status()
                schema = schema_resp.json()
                required_credentials.append({
                    "type": cred_type,
                    "id": cred_id,
                    "name": cred_name,
                    "schema": schema
                })
        return required_credentials

