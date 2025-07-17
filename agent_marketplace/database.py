import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from dotenv import load_dotenv  # type: ignore

# Load environment variables
load_dotenv()

try:
    from supabase import create_client, Client  # type: ignore
    SUPABASE_AVAILABLE = True
except ImportError:
    print("WARNING: Supabase module not available. Running in development mode.")
    SUPABASE_AVAILABLE = False

class SupabaseManager:
    """
    Manages Supabase database operations for N8N workflows and user credentials
    
    UNIFIED DATABASE SCHEMA:
    
    Both n8n_workflows and user_workflows tables should have the same structure:
    
    COMMON FIELDS:
    - id: Primary key (auto-generated)
    - user_id: UUID of the user who imported/uploaded the workflow
    - template_id: Unique identifier
      * For n8n workflows: the n8n.io template ID (numeric)
      * For user uploads: generated as "user-{user_id}-{uuid}"
    - template_url: Source URL
      * For n8n workflows: the n8n.io URL (e.g., "https://n8n.io/workflows/123")
      * For user uploads: synthetic URL (e.g., "user-upload://user-123-abc8")
    - workflow_name: Display name for the workflow
    - workflow_description: Description text
    - workflow_json: The actual N8N workflow data (JSON)
    - n8n_workflow_id: ID when deployed to an N8N instance (nullable)
    - created_at, updated_at: Timestamps
    - status: Workflow status (active, pending, etc.)
    - source: Source type ('n8n_marketplace' or 'user_upload')
    
    OPTIONAL FIELDS (may not exist in all deployments):
    - credentials_required: List of required credential types (JSON array)
    
    DIFFERENCES IN USAGE:
    - n8n_workflows: For workflows imported from n8n.io via URL
    - user_workflows: For workflows uploaded directly by users via file upload
    """
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')  # Service role key for admin operations
        self.n8n_api_key = os.getenv('X_N8N_API_KEY')
        self.n8n_base_url = os.getenv('N8N_BASE_URL', 'https://n8n.yourdomain.com')
        
        self.supabase: Optional[Client] = None  # Add Optional type hint
        self.supabase_admin: Optional[Client] = None  # Admin client with service role
        self.development_mode = not SUPABASE_AVAILABLE or self.supabase is None
        
        if SUPABASE_AVAILABLE and self.supabase_url and self.supabase_key:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            print(f"✅ Connected to Supabase database at {self.supabase_url}")
            
            # Create admin client with service role key if available
            if self.supabase_service_key:
                self.supabase_admin = create_client(self.supabase_url, self.supabase_service_key)
                print(f"✅ Connected to Supabase with service role (admin access)")
            else:
                print("⚠️ SUPABASE_SERVICE_KEY not set, using regular key (may hit RLS policies)")
                self.supabase_admin = self.supabase
        else:
            print("❌ ERROR: Supabase connection failed. Please check environment variables:")
            print(f"   SUPABASE_URL: {'✅ Set' if self.supabase_url else '❌ Missing'}")
            print(f"   SUPABASE_KEY: {'✅ Set' if self.supabase_key else '❌ Missing'}")
            print(f"   SUPABASE_SERVICE_KEY: {'✅ Set' if self.supabase_service_key else '❌ Missing'}")
            print(f"   Supabase module: {'✅ Available' if SUPABASE_AVAILABLE else '❌ Not installed'}")
    
    def init_database(self):
        """Initialize database tables if they don't exist"""
        try:
            # Always initialize Supabase database
            if not SUPABASE_AVAILABLE:
                print("ERROR: Supabase not available, cannot initialize database")
                return False
                
            print("Initializing Supabase database")
            # This would typically be done via Supabase SQL editor or migrations
            # For now, we'll assume tables exist
            print("Database initialized")
            return True
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False
    
    # User Management
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile information"""
        try:
            # Always try to get from Supabase first
            if not self.supabase:
                return None
                
            result = self.supabase.table('user_profiles').select('*').eq('user_id', user_id).execute()  # type: ignore
            if result.data:
                return result.data[0]
            
            # Fallback to mock profile if in development mode
            if self.development_mode:
                print(f"Using mock user profile for development user: {user_id}")
                return {
                    'user_id': user_id,
                    'email': 'dev@example.com',
                    'name': 'Development User',
                    'avatar_url': 'https://ui-avatars.com/api/?name=Dev&background=667eea&color=fff'
                }
            
            return None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def create_user_profile(self, user_id: str, email: str, name: str, avatar_url: Optional[str] = None) -> bool:
        """Create or update user profile"""
        try:
            # Always try to save to Supabase first
            if SUPABASE_AVAILABLE and self.supabase:
                # First check if user profile already exists
                existing = self.supabase.table('user_profiles').select('user_id').eq('user_id', user_id).execute()  # type: ignore
                
                if existing.data:
                    # User already exists, update instead
                    user_data = {
                        'email': email,
                        'name': name,
                        'avatar_url': avatar_url,
                        'updated_at': datetime.now().isoformat()
                    }
                    result = self.supabase.table('user_profiles').update(user_data).eq('user_id', user_id).execute()  # type: ignore
                    print(f"✅ Updated existing user profile for {email} in Supabase")
                else:
                    # Create new user profile
                    user_data = {
                        'user_id': user_id,
                        'email': email,
                        'name': name,
                        'avatar_url': avatar_url,
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    result = self.supabase.table('user_profiles').insert(user_data).execute()  # type: ignore
                    print(f"✅ Created new user profile for {email} in Supabase")
                
                return True
            else:
                # Fallback for development mode
                print(f"Mock creating user profile for {name} (Supabase not available)")
                return True
        except Exception as e:
            print(f"Error managing user profile: {e}")
            # Don't fail login just because profile creation failed
            return True
    
    # Credential Management
    def save_user_credential(self, user_id: str, service_name: str, credential_type: str, 
                           encrypted_credentials: Dict, metadata: Optional[Dict] = None, user_jwt: Optional[str] = None) -> bool:
        """Save user credentials to database"""
        try:
            if not self.supabase:
                print("ERROR: Supabase not available, cannot save user credentials")
                return False
            
            print(f"Saving credential for {service_name} to Supabase database")
            
            # Use JWT authentication if provided for RLS compliance
            if user_jwt and SUPABASE_AVAILABLE:
                print("DEBUG: Using user JWT for credential save authentication")
                supabase_client: Client = create_client(self.supabase_url, self.supabase_key)  # type: ignore
                supabase_client.auth.session = type('Session', (), {  # type: ignore
                    'access_token': user_jwt,
                    'refresh_token': '',
                    'user': {'id': user_id}
                })()
            else:
                print("DEBUG: No user JWT, using service client")
                supabase_client = self.supabase
            
            credential_data = {
                'user_id': user_id,
                'service_name': service_name,
                'credential_type': credential_type,
                'encrypted_credentials': json.dumps(encrypted_credentials),
                'metadata': json.dumps(metadata or {}),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Check if credential exists and update, otherwise insert
            existing = supabase_client.table('user_credentials').select('id').eq('user_id', user_id).eq('service_name', service_name).execute()  # type: ignore
            
            if existing.data:
                credential_data['updated_at'] = datetime.now().isoformat()
                result = supabase_client.table('user_credentials').update(credential_data).eq('user_id', user_id).eq('service_name', service_name).execute()  # type: ignore
            else:
                result = supabase_client.table('user_credentials').insert(credential_data).execute()  # type: ignore
            
            return True
        except Exception as e:
            print(f"Error saving user credential: {e}")
            return False
    
    def get_user_credentials(self, user_id: str, service_name: Optional[str] = None, user_jwt: Optional[str] = None) -> List[Dict]:
        """Get user credentials, optionally filtered by service"""
        try:
            if not self.supabase:
                print("ERROR: Supabase not available, cannot get user credentials")
                return []
                
            print(f"Getting credentials for {service_name or 'all services'} from Supabase database")
            
            # Use JWT authentication if provided for RLS compliance
            if user_jwt and SUPABASE_AVAILABLE:
                print("DEBUG: Using user JWT for credential retrieval authentication")
                query_client: Client = create_client(self.supabase_url, self.supabase_key)  # type: ignore
                query_client.auth.session = type('Session', (), {  # type: ignore
                    'access_token': user_jwt,
                    'refresh_token': '',
                    'user': {'id': user_id}
                })()
                query = query_client.table('user_credentials').select('*').eq('user_id', user_id)  # type: ignore
            else:
                print("DEBUG: No user JWT, using service client")
                query = self.supabase.table('user_credentials').select('*').eq('user_id', user_id)  # type: ignore
            
            if service_name:
                query = query.eq('service_name', service_name)
            
            result = query.execute()  # type: ignore
            
            # Decrypt credentials before returning
            credentials = []
            for cred in result.data:
                cred['encrypted_credentials'] = json.loads(cred['encrypted_credentials'])
                cred['metadata'] = json.loads(cred.get('metadata', '{}'))
                credentials.append(cred)
            
            return credentials
        except Exception as e:
            print(f"Error getting user credentials: {e}")
            return []
    
    def delete_user_credential(self, user_id: str, service_name: str) -> bool:
        """Delete a user credential"""
        try:
            result = self.supabase.table('user_credentials').delete().eq('user_id', user_id).eq('service_name', service_name).execute()  # type: ignore
            return True
        except Exception as e:
            print(f"Error deleting user credential: {e}")
            return False
    
    # N8N Workflow Management
    def check_workflow_exists(self, template_url: str, template_id: Optional[str] = None) -> Optional[Dict]:
        """Check if N8N template has been processed before"""
        try:
            if not self.supabase:
                print("ERROR: Supabase not available, cannot check workflow existence")
                return None
                
            print(f"Checking workflow existence for {template_url} in Supabase database")
                
            # First try exact URL match
            result = self.supabase.table('user_workflows').select('*').eq('template_url', template_url).execute()  # type: ignore
            if result.data:
                return result.data[0]
            
            # If template_id provided, try matching by template_id
            if template_id:
                result = self.supabase.table('user_workflows').select('*').eq('template_id', template_id).execute()  # type: ignore
                if result.data:
                    return result.data[0]
            
            # Try to extract template_id from URL and search by that
            import re
            url_match = re.search(r'workflows/(\d+)', template_url)
            if url_match:
                extracted_id = url_match.group(1)
                result = self.supabase.table('user_workflows').select('*').eq('template_id', extracted_id).execute()  # type: ignore
                if result.data:
                    return result.data[0]
            
            return None
        except Exception as e:
            print(f"Error checking workflow existence: {e}")
            return None
    
    def check_deployed_workflow_exists(self, user_id: str, workflow_name: str, n8n_workflow_id: Optional[str] = None) -> bool:
        """Check if a deployed workflow already exists in user_workflows to avoid duplicates"""
        try:
            if not self.supabase:
                return False
            
            # Check by workflow name and user
            result = self.supabase.table('user_workflows').select('id').eq('user_id', user_id).eq('workflow_name', workflow_name).execute()  # type: ignore
            
            if result.data:
                print(f"🔍 Found existing deployed workflow '{workflow_name}' for user {user_id}")
                return True
            
            # If n8n_workflow_id provided, also check by that
            if n8n_workflow_id:
                result = self.supabase.table('user_workflows').select('id').eq('user_id', user_id).eq('n8n_workflow_id', n8n_workflow_id).execute()  # type: ignore
                
                if result.data:
                    print(f"🔍 Found existing deployed workflow with n8n_id '{n8n_workflow_id}' for user {user_id}")
                    return True
            
            return False
        except Exception as e:
            print(f"Error checking deployed workflow existence: {e}")
            return False
    
    def save_n8n_workflow(self, template_id: str, template_url: str, workflow_name: str, 
                         workflow_json: Dict, n8n_workflow_id: Optional[str] = None, 
                         credentials_required: Optional[List[str]] = None, user_id: Optional[str] = None,
                         workflow_description: Optional[str] = None) -> bool:
        """Save N8N workflow information to database with unified schema"""
        try:
            if not self.supabase:
                print("ERROR: Supabase not available, cannot save workflow")
                return False
            
            print(f"Saving N8N workflow '{workflow_name}' to Supabase database")
                
            workflow_data = {
                'user_id': user_id,  # Add user_id for consistency
                'template_id': template_id,
                'template_url': template_url,
                'workflow_name': workflow_name,
                'workflow_description': workflow_description or f"N8N workflow template (Template ID: {template_id})",
                'workflow_json': workflow_json,
                'n8n_workflow_id': n8n_workflow_id,
                'credentials_required': json.dumps(credentials_required or []),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'status': 'active' if n8n_workflow_id else 'pending',
                'source': 'n8n_marketplace'
            }
            
            # Check if workflow exists and update, otherwise insert
            existing = self.check_workflow_exists(template_url, template_id)
            
            if existing:
                workflow_data['updated_at'] = datetime.now().isoformat()
                result = self.supabase.table('user_workflows').update(workflow_data).eq('template_url', template_url).execute()  # type: ignore
            else:
                result = self.supabase.table('user_workflows').insert(workflow_data).execute()  # type: ignore
            
            return True
        except Exception as e:
            print(f"Error saving N8N workflow: {e}")
            return False
    
    def update_marketplace_workflow_n8n_id(self, template_url: str, n8n_workflow_id: str) -> bool:
        """Update the N8N workflow ID after successful creation in marketplace workflows table"""
        try:
            if self.supabase is None:
                print("Supabase not available")
                return False
                
            result = self.supabase.table('user_workflows').update({
                'n8n_workflow_id': n8n_workflow_id,
                'status': 'active',
                'updated_at': datetime.now().isoformat()
            }).eq('template_url', template_url).execute()  # type: ignore
            
            return True
        except Exception as e:
            print(f"Error updating workflow N8N ID: {e}")
            return False
    
    def get_user_workflows(self, user_id: str) -> List[Dict]:
        """Get workflows created by a user"""
        try:
            if self.supabase is None:
                print("Supabase not available")
                return []
                
            result = self.supabase.table('user_workflows').select(
                '*, n8n_workflows(*)'
            ).eq('user_id', user_id).execute()  # type: ignore
            
            workflows = []
            for workflow in result.data:
                workflow['n8n_workflows']['workflow_json'] = json.loads(workflow['n8n_workflows']['workflow_json'])
                workflow['n8n_workflows']['credentials_required'] = json.loads(workflow['n8n_workflows']['credentials_required'])
                workflows.append(workflow)
            
            return workflows
        except Exception as e:
            print(f"Error getting user workflows: {e}")
            return []
    
    def save_user_workflow(self, user_id: str, template_url: str, credentials_used: Optional[Dict] = None) -> bool:
        """Save a workflow to user's collection"""
        try:
            if not self.supabase:
                print("ERROR: Supabase not available, cannot save user workflow")
                return False
                
            print(f"Saving user workflow for {user_id} to Supabase database")
                
            workflow_data = {
                'user_id': user_id,
                'template_url': template_url,
                'credentials_used': json.dumps(credentials_used or {}),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('user_workflows').insert(workflow_data).execute()  # type: ignore
            return True
        except Exception as e:
            print(f"Error saving user workflow: {e}")
            return False

    def get_marketplace_workflows(self) -> List[Dict]:
        """Get all workflows available in the marketplace"""
        try:
            if not self.supabase:
                print("ERROR: Supabase not available, cannot load marketplace workflows")
                return []
            
            print("Loading marketplace workflows from Supabase database")
                
            # Production mode - query Supabase
            result = self.supabase.table('user_workflows').select('*').execute()  # type: ignore
            
            workflows = []
            for workflow in result.data:
                workflow_data = {
                    'id': f"n8n-{workflow['template_id']}",
                    'name': workflow['workflow_name'],
                    'description': workflow.get('workflow_description') or f"N8N workflow template (Template ID: {workflow['template_id']})",
                    'category': 'Workflow',
                    'icon': '🔧',
                    'trending': False,
                    'tools': ['n8n_workflow'],
                    'template_id': workflow['template_id'],
                    'template_url': workflow['template_url'],
                    'workflow_json': workflow['workflow_json'],  # Include the actual workflow JSON
                    'node_count': len(workflow['workflow_json'].get('nodes', [])),
                    'credentials_required': json.loads(workflow.get('credentials_required', '[]')),
                    'created_at': workflow['created_at'],
                    'source': 'n8n_database'
                }
                workflows.append(workflow_data)
            
            return workflows
        except Exception as e:
            print(f"Error getting marketplace workflows: {e}")
            return []
    
    # N8N API Integration
    def create_n8n_workflow(self, workflow_json: Dict, workflow_name: str) -> Optional[str]:
        """Create workflow in N8N instance via API"""
        try:
            import requests
            
            if not self.n8n_api_key:
                print("N8N API key not configured")
                return None
            
            headers = {
                'X-N8N-API-KEY': self.n8n_api_key,
                'Content-Type': 'application/json'
            }
            
            # Prepare workflow data for N8N API
            n8n_payload = {
                'name': workflow_name,
                'nodes': workflow_json.get('nodes', []),
                'connections': workflow_json.get('connections', {}),
                'settings': workflow_json.get('settings', {})
            }
            
            response = requests.post(
                f"{self.n8n_base_url}/api/v1/workflows",
                headers=headers,
                json=n8n_payload,
                timeout=30
            )
            
            if response.status_code == 201:
                workflow_data = response.json()
                return workflow_data.get('id')
            else:
                print(f"Error creating N8N workflow: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating N8N workflow: {e}")
            return None
    
    def update_n8n_workflow_credentials(self, n8n_workflow_id: str, credentials: Dict) -> bool:
        """Update N8N workflow with user credentials"""
        try:
            import requests
            
            if not self.n8n_api_key:
                print("N8N API key not configured")
                return False
            
            headers = {
                'X-N8N-API-KEY': self.n8n_api_key,
                'Content-Type': 'application/json'
            }
            
            # This would involve updating the workflow nodes with credential IDs
            # Implementation depends on N8N API structure for credentials
            
            response = requests.patch(
                f"{self.n8n_base_url}/api/v1/workflows/{n8n_workflow_id}",
                headers=headers,
                json={'active': True},  # Activate after credentials are set
                timeout=30
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error updating N8N workflow credentials: {e}")
            return False

    def save_user_uploaded_workflow(self, user_id: str, workflow_name: str, workflow_json: Dict, 
                                   workflow_description: Optional[str] = None, credentials_required: Optional[List[str]] = None, user_jwt: Optional[str] = None,
                                   n8n_workflow_id: Optional[str] = None, mcp_link: Optional[str] = None, template_id: Optional[str] = None, source_override: Optional[str] = None) -> bool:
        """Save user-uploaded workflow directly to user_workflows table (not n8n_workflows)"""
        try:
            
            # Always save to Supabase database
            if not self.supabase:
                print("ERROR: Supabase not available, cannot save user workflow")
                return False
            
            print(f"Saving user-uploaded workflow '{workflow_name}' for user {user_id} to Supabase database")
                
            # Generate a unique template_id for the user-uploaded workflow if not provided
            if not template_id:
                template_id = f"user-{user_id}-{str(uuid.uuid4())[:8]}"
            
            # Determine the correct source
            if source_override:
                source = source_override
                print(f"💾 Using provided source override: {source}")
            else:
                source = 'user_upload'
                print(f"💾 Using default source: {source}")
            
            # Check for duplicates if template_id is provided (for n8n templates)
            if template_id and source == 'n8n_template':
                print(f"🔍 Checking for duplicate n8n template: {template_id} for user {user_id}")
                # Use user JWT for RLS authentication if provided
                if user_jwt:
                    auth_client: Client = create_client(self.supabase_url, self.supabase_key)  # type: ignore
                    auth_client.auth.session = type('Session', (), {  # type: ignore
                        'access_token': user_jwt,
                        'refresh_token': '',
                        'user': {'id': user_id}
                    })()
                    existing_check = auth_client.table('user_workflows').select('*').eq('user_id', user_id).eq('template_id', template_id).execute()  # type: ignore
                else:
                    existing_check = self.supabase.table('user_workflows').select('*').eq('user_id', user_id).eq('template_id', template_id).execute()  # type: ignore
                
                if existing_check.data:
                    print(f"✅ Template {template_id} already exists for user {user_id}, skipping duplicate save")
                    return True  # Return True as the workflow is already saved
            
            # Determine template URL based on source
            if source == 'n8n_template':
                template_url = f"https://n8n.io/workflows/{template_id}"
            else:
                template_url = f"user-upload://{template_id}"
            
            workflow_data = {
                'user_id': user_id,
                'template_id': template_id,
                'template_url': template_url,
                'workflow_name': workflow_name,
                'workflow_description': workflow_description or f"User-uploaded workflow: {workflow_name}",
                'workflow_json': workflow_json,
                'credentials_required': credentials_required or [],  # Store as array directly
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'source': source,
                'n8n_workflow_id': n8n_workflow_id,
                'mcp_link': mcp_link
            }
            
            # Use admin client with service role to bypass RLS policies
            print(f"DEBUG: user_jwt provided: {user_jwt is not None}")
            print(f"DEBUG: SUPABASE_SERVICE_KEY configured: {self.supabase_service_key is not None}")
            
            if SUPABASE_AVAILABLE and self.supabase_admin:
                print("DEBUG: Using admin client with service role (bypasses RLS)")
                result = self.supabase_admin.table('user_workflows').insert(workflow_data).execute()  # type: ignore
            else:
                print("DEBUG: Supabase admin not available, skipping database insert")
                return True
            
            return True
        except Exception as e:
            print(f"Error saving user-uploaded workflow: {e}")
            return False

    def _save_workflow_to_local_file(self, user_id: str, workflow_name: str, workflow_json: Dict, workflow_description: Optional[str] = None, credentials_required: Optional[List[str]] = None) -> bool:
        """Save workflow to local file for development mode"""
        try:
            file_path = 'user_uploaded_workflows.json'
            
            # Load existing workflows
            workflows = []
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    workflows = json.load(f)
            
            # Generate unique template_id
            template_id = f"user-{user_id}-{str(uuid.uuid4())[:8]}"
            
            # Create workflow data
            workflow_data = {
                'user_id': user_id,
                'template_id': template_id,
                'template_url': f"user-upload://{template_id}",
                'workflow_name': workflow_name,
                'workflow_description': workflow_description or f"User-uploaded workflow: {workflow_name}",
                'workflow_json': workflow_json,  # Keep as dict in local storage
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'status': 'active',
                'source': 'user_upload',
                'credentials_required': credentials_required or []
            }
            
            workflows.append(workflow_data)
            
            # Save back to file
            with open(file_path, 'w') as f:
                json.dump(workflows, f, indent=2)
            
            print(f"✅ Saved workflow '{workflow_name}' to local file: {file_path}")
            return True
            
        except Exception as e:
            print(f"Error saving workflow to local file: {e}")
            return False

    def _load_workflows_from_local_file(self, user_id: str) -> List[Dict]:
        """Load workflows from local file for development mode"""
        try:
            file_path = 'user_uploaded_workflows.json'
            if not os.path.exists(file_path):
                return []
            
            with open(file_path, 'r') as f:
                all_workflows = json.load(f)
            
            # Filter workflows for the specific user and ensure JSON parsing
            user_workflows = []
            for w in all_workflows:
                if w.get('user_id') == user_id and w.get('source') == 'user_upload':
                    workflow_data = w.copy()
                    
                    print(f"\n🔍 DEBUG: Processing workflow '{workflow_data.get('workflow_name')}'")
                    print(f"Raw workflow_json type: {type(workflow_data.get('workflow_json'))}")
                    
                    # Ensure workflow_json is properly parsed (handle both string and dict formats)
                    workflow_json = workflow_data.get('workflow_json')
                    
                    if isinstance(workflow_json, str):
                        print(f"📝 workflow_json is STRING, length: {len(workflow_json)}")
                        print(f"First 200 chars: {workflow_json[:200]}...")
                        try:
                            parsed_json = json.loads(workflow_json)
                            workflow_data['workflow_json'] = parsed_json
                            print(f"✅ Successfully parsed workflow_json from string")
                            print(f"Parsed JSON has {len(parsed_json.get('nodes', []))} nodes")
                        except json.JSONDecodeError as e:
                            print(f"❌ Failed to parse workflow_json: {e}")
                            print(f"Raw JSON that failed: {workflow_json}")
                            continue
                    elif isinstance(workflow_json, dict):
                        print(f"📦 workflow_json is already DICT with {len(workflow_json.get('nodes', []))} nodes")
                    else:
                        print(f"⚠️ Invalid workflow_json format: {type(workflow_json)}")
                        print(f"Value: {workflow_json}")
                        continue
                    
                    # Ensure credentials_required is properly parsed
                    credentials_required = workflow_data.get('credentials_required', [])
                    print(f"Credentials required type: {type(credentials_required)}, value: {credentials_required}")
                    
                    if isinstance(credentials_required, str):
                        try:
                            workflow_data['credentials_required'] = json.loads(credentials_required)
                            print(f"✅ Parsed credentials_required from string: {workflow_data['credentials_required']}")
                        except json.JSONDecodeError:
                            print(f"❌ Failed to parse credentials_required, setting to empty list")
                            workflow_data['credentials_required'] = []
                    elif not isinstance(credentials_required, list):
                        print(f"⚠️ credentials_required not a list, converting to empty list")
                        workflow_data['credentials_required'] = []
                    
                    print(f"✅ Final workflow data: name='{workflow_data.get('workflow_name')}', credentials={workflow_data.get('credentials_required')}")
                    user_workflows.append(workflow_data)
            
            print(f"✅ Loaded {len(user_workflows)} workflows from local file for user {user_id}")
            return user_workflows
            
        except Exception as e:
            print(f"Error loading workflows from local file: {e}")
            return []

    def get_user_uploaded_workflows(self, user_id: str, user_jwt: Optional[str] = None) -> List[Dict]:
        """Get workflows uploaded directly by a user"""
        try:
        
            # Always read from Supabase database using admin client
            if not self.supabase_admin:
                print("ERROR: Supabase admin not available, cannot load user workflows")
                return []
            
            print(f"Loading user-uploaded workflows for user {user_id} from Supabase database")
            
            # Production mode - query Supabase using admin client
            if not SUPABASE_AVAILABLE:
                print("Supabase not available, falling back to development mode behavior")
                return []
                
            result = self.supabase_admin.table('user_workflows').select('*').eq('user_id', user_id).execute()  # type: ignore
            
            workflows = []
            for workflow in result.data:
                # Only include user-uploaded workflows (source is 'user_upload' or template_id starts with 'user-')
                source = workflow.get('source', '')
                template_id = str(workflow.get('template_id', ''))
                
                if source == 'user_upload' or template_id.startswith('user-'):
                    workflow_data = workflow.copy()
                    # workflow_json is already a dict from JSONB, no need to parse
                    
        
            
                    # Handle credentials_required safely (may not exist in all schemas)
                    credentials_raw = workflow_data.get('credentials_required')                    
                    if credentials_raw is None:
                        print("   ⚠️ credentials_required is None/missing in database")
                        workflow_data['credentials_required'] = []
                    elif isinstance(credentials_raw, str):
                        try:
                            parsed_creds = json.loads(credentials_raw)
                            workflow_data['credentials_required'] = parsed_creds
                        except json.JSONDecodeError as e:
                            print(f"   ❌ Failed to parse credentials string: {e}")
                            workflow_data['credentials_required'] = []
                    elif isinstance(credentials_raw, list):
                        workflow_data['credentials_required'] = credentials_raw
                    else:
                        print(f"   ⚠️ Unexpected credentials format: {type(credentials_raw)}")
                        workflow_data['credentials_required'] = []
                    
                    print(f"   Final credentials_required: {workflow_data['credentials_required']}")
                    workflows.append(workflow_data)
            
            return workflows
        except Exception as e:
            print(f"Error getting user-uploaded workflows: {e}")
            return []

    def delete_user_uploaded_workflow(self, user_id: str, template_id: str) -> bool:
        """Delete a user's uploaded workflow"""
        try:
            # Always delete from Supabase database using admin client
            if not self.supabase_admin:
                print("ERROR: Supabase admin not available, cannot delete user workflow")
                return False
            
            print(f"Deleting user-uploaded workflow {template_id} for user {user_id} from Supabase database")
            
            # Production mode - delete from Supabase using admin client
            result = self.supabase_admin.table('user_workflows').delete().eq('user_id', user_id).eq('template_id', template_id).execute()  # type: ignore
            
            return len(result.data) > 0 if result.data else False
            
        except Exception as e:
            print(f"Error deleting user-uploaded workflow: {e}")
            return False

    def update_workflow_n8n_id(self, template_id: str, n8n_workflow_id: str, user_id: str) -> bool:
        """Update workflow with N8N workflow ID after deployment"""
        try:
            # Always update in Supabase database
            if not self.supabase:
                print("ERROR: Supabase not available, cannot update workflow N8N ID")
                return False
                
            print(f"Updating workflow N8N ID: {template_id} -> {n8n_workflow_id} in Supabase database")
                
            # Update n8n_workflows table
            result = self.supabase.table('user_workflows').update({
                'n8n_workflow_id': n8n_workflow_id,
                'updated_at': datetime.now().isoformat()
            }).eq('template_id', template_id).execute()  # type: ignore
            
            return True
        except Exception as e:
            print(f"Error updating workflow N8N ID: {e}")
            return False

    def update_user_workflow_n8n_id(self, user_id: str, workflow_name: str, n8n_workflow_id: str) -> bool:
        """Update user workflow with N8N workflow ID after successful creation"""
        try:
            # Always update in Supabase database
            if not self.supabase:
                print("ERROR: Supabase not available, cannot update user workflow N8N ID")
                return False
                
            print(f"Updating user workflow N8N ID: user={user_id}, workflow='{workflow_name}' -> {n8n_workflow_id}")
                
            # Update user_workflows table
            result = self.supabase.table('user_workflows').update({
                'n8n_workflow_id': n8n_workflow_id,
                'updated_at': datetime.now().isoformat()
            }).eq('user_id', user_id).eq('workflow_name', workflow_name).execute()  # type: ignore
            
            if result.data:
                print(f"✅ Successfully updated user workflow with n8n ID: {n8n_workflow_id}")
                return True
            else:
                print(f"⚠️  No user workflow found to update for user {user_id}, workflow '{workflow_name}'")
                return False
            
        except Exception as e:
            print(f"Error updating user workflow N8N ID: {e}")
            return False

    def update_user_workflow_mcp_link(self, user_id: str, n8n_workflow_id: str, mcp_link: str) -> bool:
        """Update user workflow with MCP link"""
        try:
            # Always update Supabase database using admin client
            if not self.supabase_admin:
                print("ERROR: Supabase admin not available, cannot update user workflow MCP link")
                return False
                
            print(f"Updating user workflow with n8n_workflow_id {n8n_workflow_id} with MCP link: {mcp_link} in Supabase database")
            
            # First, let's check if the workflow exists
            check_result = self.supabase_admin.table('user_workflows').select('*').eq('user_id', user_id).eq('n8n_workflow_id', n8n_workflow_id).execute()  # type: ignore
            print(f"DEBUG: Found {len(check_result.data) if check_result.data else 0} workflows with n8n_workflow_id {n8n_workflow_id}")
            
            if check_result.data:
                for workflow in check_result.data:
                    print(f"DEBUG: Found workflow: {workflow.get('workflow_name')} with template_id: {workflow.get('template_id')}")
                
            result = self.supabase_admin.table('user_workflows').update({
                'mcp_link': mcp_link,
                'updated_at': datetime.now().isoformat()
            }).eq('user_id', user_id).eq('n8n_workflow_id', n8n_workflow_id).execute()  # type: ignore
            
            if result.data:
                print(f"✅ Successfully updated user workflow with MCP link: {mcp_link}")
                return True
            else:
                print(f"⚠️ No user workflow found to update for user {user_id}, n8n_workflow_id {n8n_workflow_id}")
                return False
            
        except Exception as e:
            print(f"Error updating user workflow MCP link: {e}")
            return False
        
    def save_mcp_server_path(self, user_id: str, n8n_workflow_id: str, mcp_server_path: str, 
                           mcp_build_success: bool = False) -> bool:
        """Save MCP server path information for a deployed workflow"""
        try:
            # Always save to Supabase database
            if not self.supabase:
                print("ERROR: Supabase not available, cannot save MCP server path")
                return False
                
            print(f"Saving MCP server path for workflow {n8n_workflow_id} to Supabase database")
                
            # Update the corresponding workflow deployment record with MCP server information
            mcp_data = {
                'mcp_link': mcp_server_path,
            }
            
            result = self.supabase.table('user_workflows').update(mcp_data).eq('user_id', user_id).eq('n8n_workflow_id', n8n_workflow_id).execute()  # type: ignore
            
            if result.data:
                print(f"✅ Successfully saved MCP server path: {mcp_server_path}")
                return True
            else:
                print(f"⚠️ No deployment record found to update for user {user_id}, workflow {n8n_workflow_id}")
                return False
            
        except Exception as e:
            print(f"Error saving MCP server path: {e}")
            return False

    def get_user_mcp_servers(self, user_id: str) -> List[Dict]:
        """Get all MCP servers created by a user"""
        try:
            # Always get from Supabase database
            if not self.supabase:
                print("ERROR: Supabase not available, cannot get user MCP servers")
                return []
                
            print(f"Getting MCP servers for user {user_id} from Supabase database")
                
            result = self.supabase.table('user_workflows').select('*').eq('user_id', user_id).not_.is_('mcp_link', 'null').order('created_at', desc=True).execute()  # type: ignore
            return result.data
        except Exception as e:
            print(f"Error getting user MCP servers: {e}")
            return []

# Global instance
db_manager = SupabaseManager()