# AI Agent Marketplace

A modern, embeddable agent marketplace that allows developers to integrate prebuilt n8n agents into their applications. Built with Flask and featuring a beautiful, responsive UI inspired by modern design principles.

## Features

- 🤖 **Pre-built N8N Workflows**: Browse and deploy specialized n8n workflows for various automation tasks
- 🎯 **Easy Deployment**: Direct deployment to your n8n instance without credential storage
- 🔍 **Smart Search**: Filter workflows by category, trending status, or search terms
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices
- 🚀 **My Workflows**: Manage your uploaded and deployed workflows in one place
- 📊 **Real-time Configuration**: Configure credentials and deploy workflows instantly
- 🔗 **n8n Compatible**: Designed to work seamlessly with n8n workflow automation
- 🔒 **Secure Credential Handling**: User API keys are transmitted once during deployment and never stored server-side
- 📤 **Workflow Upload**: Upload your own n8n workflows and manage them alongside marketplace templates

## Workflow Categories

- **Data Processing**: Extract and transform data from various sources
- **AI/ML Integration**: OpenAI, Claude, and other AI service integrations
- **Google Services**: Google Sheets, Drive, Gmail automation
- **Communications**: Telegram, Slack, email processing
- **HTTP APIs**: Custom API integrations and web service connections
- **File Management**: Process CSV, PDF, and other file formats
- **Productivity**: Calendar, scheduling, and task management

## Key Concepts

### Workflow Sources
- **Marketplace Templates**: Pre-built workflows imported from n8n.io or community templates
- **User Uploads**: Custom workflows uploaded directly by users via JSON files

### My Workflows
- Central place to manage all your workflows (uploaded and marketplace)
- View workflow details, credentials required, and deployment status
- Configure credentials and deploy directly to your n8n instance
- Track which workflows are active in your n8n setup

### Credential Management
- Credentials are collected in the UI but never stored server-side
- Transmitted securely once during deployment to configure your n8n instance
- Each service (OpenAI, Google, etc.) creates separate credential entries in n8n
- Supports OAuth2, API keys, and basic authentication patterns

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agent_marketplace
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Usage

### Setting Up Your N8N Instance

Before using the marketplace, ensure you have:

1. **N8N Instance**: A running n8n instance (cloud or self-hosted)
2. **API Access**: N8N API key with workflow and credential creation permissions
3. **Environment Configuration**: Set `N8N_BASE_URL` and `X_N8N_API_KEY` in your `.env` file

### Browsing and Deploying Workflows

1. **Browse Marketplace**: Visit the homepage to see all available workflows
2. **Search and Filter**: Use the search bar and category filters to find specific workflows
3. **Upload Custom Workflows**: Use "Upload Workflow" to add your own n8n JSON files
4. **View My Workflows**: Access all your workflows (uploaded and marketplace) in one place

### Deploying a Workflow

1. **Select Workflow**: Choose from marketplace templates or your uploaded workflows
2. **Configure Credentials**: Fill in required API keys and service credentials
   - OpenAI API keys for AI-powered nodes
   - Google OAuth2 credentials for Google services
   - Service-specific tokens and keys
3. **Deploy**: Click deploy to create the workflow in your n8n instance
   - Workflow name is automatically extracted from the workflow JSON
   - Deployed workflows are saved to both database tables for better organization
   - Duplicate deployments are automatically detected and prevented
4. **Manage**: View and manage deployed workflows in both your "My Workflows" section and n8n dashboard

### Credential Configuration Examples

#### OpenAI Integration
```
Service: OpenAI
API Key: sk-...your-openai-key
```

#### Google Services (Sheets, Drive)
```
Service: Google Sheets
Client ID: your-google-client-id
Client Secret: your-google-client-secret
Refresh Token: (obtained via OAuth flow)
```

#### HTTP API Services
```
Service: Custom API
Username: api (or your username)
Password: your-api-key-or-token
```

## API Endpoints

### Workflow Management

- `POST /api/parse-workflow` - Parse and analyze n8n workflow JSON
- `POST /api/parse-workflow-file` - Parse workflow from uploaded JSON file
- `POST /api/save-user-uploaded-workflow` - Save user-uploaded workflow
- `POST /api/save-workflow-to-marketplace` - Save workflow to marketplace
- `GET /api/user/uploaded-workflows` - Get user's uploaded workflows
- `GET /api/marketplace/workflows` - Get marketplace workflow templates
- `DELETE /api/user/uploaded-workflows/{id}` - Delete user's uploaded workflow

### Deployment

- `POST /api/deploy-workflow-to-n8n` - Deploy workflow to user's n8n instance
- `POST /api/import-n8n-template-enhanced` - Import and cache n8n.io templates

### Authentication

- `POST /api/auth/login` - User authentication (Supabase JWT)
- `POST /api/auth/logout` - User logout
- `GET /api/auth/user` - Get current user profile

### Validation

- `POST /api/validate-workflow` - Validate n8n workflow JSON structure
- `GET /api/health` - Health check endpoint

### Request Examples

#### Deploy Workflow
```javascript
// Direct deployment with credentials
fetch('/api/deploy-workflow-to-n8n', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_JWT_TOKEN'
    },
    body: JSON.stringify({
        workflow_json: { /* n8n workflow JSON */ },
        workflow_name: 'My Custom Workflow',
        user_credentials: {
            'OpenAI': { api_key: 'sk-...' },
            'Google Sheets': { 
                client_id: 'your-client-id',
                client_secret: 'your-client-secret'
            }
        }
    })
})
```

#### Upload Workflow
```javascript
// Upload custom workflow
const formData = new FormData();
formData.append('file', workflowFile);
formData.append('manual_workflow_name', 'My Workflow');

fetch('/api/parse-workflow-file', {
    method: 'POST',
    body: formData
})
```

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
└── migrations/                 # Database schema and migrations
    └── database_migration_unified_schema.sql
```

## Core Components

### Backend (Python/Flask)
- **app.py**: Main application with REST API endpoints for workflow management, authentication, and deployment
- **database.py**: Supabase integration for user profiles, workflow storage, and deployment tracking
- **n8n_workflow_parser.py**: Analyzes n8n workflows to extract credential requirements and generate configuration forms

### Frontend (HTML/JS)
- **workflows.html**: Single-page application for browsing, uploading, and managing workflows
- **workflow-credentials.js**: Interactive credential configuration forms with validation and testing

### Database Schema
- **user_profiles**: User authentication and n8n instance configuration
- **user_workflows**: User-uploaded workflows and marketplace subscriptions
- **n8n_workflows**: Marketplace workflow templates and metadata
- **workflow_deployments**: Tracking of deployed workflows and their status

## Development

### Adding New Marketplace Workflows

1. **Import from n8n.io**: Use the import endpoint to fetch templates from n8n community
2. **Upload Custom Templates**: Add pre-built workflows via the admin interface
3. **Metadata Configuration**: Set workflow descriptions, categories, and credential requirements

### Extending Credential Support

1. **Update Parser**: Add new service mappings in `n8n_workflow_parser.py`
2. **API Integration**: Extend credential creation logic in `create_credentials_in_n8n()`
3. **UI Forms**: Add custom field types in `workflow-credentials.js`

### Database Management

- **Dual Storage**: Deployed workflows are saved to both `n8n_workflows` (marketplace tracking) and `user_workflows` (personal management)
- **Duplicate Prevention**: Automatic checks prevent duplicate workflow deployments
- **Migrations**: Use Supabase SQL editor for schema changes
- **RLS Policies**: Ensure Row Level Security for user data isolation
- **Indexing**: Optimize queries for workflow search and filtering

### Testing Workflows

1. **Local n8n**: Set up local n8n instance for development
2. **Credential Testing**: Verify credential creation and workflow deployment
3. **Parser Validation**: Test workflow analysis with various n8n JSON formats

## Production Deployment

### Environment Setup

Required environment variables:
```bash
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key
FLASK_ENV=production

# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# N8N Integration
N8N_BASE_URL=https://your-n8n-instance.com
X_N8N_API_KEY=your-n8n-api-key

# Encryption (for any sensitive data)
ENCRYPTION_KEY=your-fernet-encryption-key
```

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# With configuration file
gunicorn -c gunicorn.conf.py app:app
```

### Using Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Database Initialization

1. **Supabase Setup**: Create project and configure authentication
2. **Schema Migration**: Run SQL migrations for tables and RLS policies
3. **User Management**: Configure Supabase Auth for JWT token handling

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation at `/documentation`
- Review the API endpoints for integration help

---

**Built with ❤️ by SUPERCHAIN team for the automation community**
