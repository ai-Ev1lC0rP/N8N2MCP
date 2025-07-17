# N8N-Agent-Marketplace
Convert N8N agent / workflow into MCP servers, you can use it in Claude / Cursor / Super Chain 

## Demo 
[Demo Link](https://p2rdr5jbej.us-east-1.awsapprunner.com/)

<img width="1800" height="836" alt="Screenshot 2025-07-17 at 11 33 45 AM" src="https://github.com/user-attachments/assets/f8f49abb-00ce-4221-8bcf-5d27a7078a9a" />

## Features
🚀 MCP Server Creation : Convert your N8N workflow into MCP server for your agent to use
🎯 Easy Deployment: Direct deployment to your n8n instance without credential storage
🚀 My Workflows: Manage your uploaded and deployed workflows & MCP servers
📊 Real-time Configuration: Configure credentials and deploy workflows instantly
🔗 n8n Compatible: Designed to work seamlessly with n8n workflow automation
🔒 Secure Credential Handling: User API keys are transmitted once during deployment and never stored server-side
📤 Workflow Upload: Upload your own n8n workflows and create your MCP servers link

## Install 
**1. Clone the repository**
```
https://github.com/Super-Chain/N8N-Agent-Marketplace.git
cd N8N-Agent-Marketplace
pip install -r requirements.txt
python app.py 
```
The application will be available at http://localhost:5000

## How It Works

### Prerequisites

1. **N8N Instance**: Running n8n instance (cloud.n8n.io or self-hosted)
2. **API Access**: N8N API key with workflow and credential creation permissions  
3. **Environment Setup**: Configure `N8N_BASE_URL` and `X_N8N_API_KEY` in your environment

### Workflow Upload & Analysis

1. **Upload JSON**: Import n8n workflow JSON files via file upload or direct paste
2. **Automatic Parsing**: The system analyzes your workflow to extract:
   - Required credential types (OpenAI, Google, Slack, etc.)
   - Node count and complexity metrics
   - Connection topology and dependencies
3. **Smart Detection**: Identifies 50+ node types and their credential requirements

### Credential Configuration

1. **Dynamic Forms**: Generated forms based on detected node requirements
2. **Service-Specific Fields**: Tailored input fields for each service:
   - **OpenAI**: API key input with validation
   - **Google Services**: OAuth2 client ID/secret + refresh token
   - **Slack/Discord**: Bot tokens and workspace configuration
   - **Databases**: Connection strings, usernames, passwords
3. **Zero Storage**: Credentials are collected but never stored server-side

### One-Click Deployment

1. **Credential Injection**: Platform creates credentials directly in your n8n instance
2. **Workflow Creation**: Deploys the complete workflow with proper credential associations
3. **Duplicate Detection**: Prevents accidental re-deployment of existing workflows
4. **Status Tracking**: Monitors deployment success and provides feedback

1. **N8N Instance**: A running n8n instance (cloud or self-hosted)
2. **API Access**: N8N API key with workflow and credential creation permissions
3. **Environment Configuration**: Set `N8N_BASE_URL` and `X_N8N_API_KEY` in your `.env` file

## Project Structure

```
agent_marketplace/
├── app.py                      # Main Flask application with API endpoints
├── database.py                 # Supabase database manager
├── n8n_workflow_parser.py      # N8N workflow analysis and credential extraction
├── requirements.txt            # Python dependencies
├── readme.md                   # This documentation
├── .env                        # Environment configuration (create from .env.example)
├── templates/                  # HTML templates
│   ├── base.html              # Base template with modern styling
│   └── workflows.html         # Main marketplace and management interface
├── static/                     # Static assets
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript modules
│   │   └── workflow-credentials.js  # Credential form management
│   └── assets/                # Images and icons
```

## Core Components

### Backend (Python/Flask)
- **app.py**: Main application with REST API endpoints for workflow management, authentication, and deployment
- **database.py**: Supabase integration for user profiles, workflow storage, and deployment tracking
- **n8n_workflow_parser.py**: Analyzes n8n workflows to extract credential requirements and generate configuration forms

### Frontend (HTML/JS)
- **workflows.html**: Single-page application for browsing, uploading, and managing workflows
- **workflow-credentials.js**: Interactive credential configuration forms with validation and testing
