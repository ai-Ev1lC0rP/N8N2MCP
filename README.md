# 🤖 N8N Agent Marketplace

**Transform Natural Language into AI-Powered Automation Tools**

The N8N Agent Marketplace is a revolutionary platform that bridges the gap between human intent and automated workflows. It combines the power of n8n automation with AI assistance, creating a complete ecosystem where anyone can build, share, and deploy intelligent automation tools that work seamlessly with AI assistants like Claude and Cursor.

## 🚀 What Makes This Special?

### The Complete AI Automation Pipeline

This isn't just another workflow tool - it's a complete transformation of how we think about automation:

1. **🧠 AI-Powered Creation** - Describe what you want in plain English, get a working automation
2. **🏪 Intelligent Marketplace** - Discover, share, and deploy pre-built automations instantly  
3. **🔧 AI Assistant Integration** - Turn any workflow into a tool your AI assistant can use
4. **⚡ Instant Integration** - Works out-of-the-box with Claude, Cursor, and Superchain

### Key Value Propositions

**For Individual Users:**
- **Zero Learning Curve**: Create complex automations using natural language
- **Instant Deployment**: Go from idea to working automation in minutes
- **AI Assistant Ready**: Your workflows become tools Claude, Cursor, and other AI assistants can use

**For Teams & Organizations:**
- **Workflow Library**: Build and share automation templates across your organization
- **Scalable Infrastructure**: Docker-based deployment with multi-tenant support
- **Secure by Design**: Enterprise-grade credential management and isolation

**For Developers:**
- **Open Source Ecosystem**: Extend and customize every component
- **Modern Architecture**: FastAPI, React-like frontends, and containerized deployment
- **MCP Protocol Support**: Future-proof integration with the growing MCP ecosystem

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   n8n-ai-genie │───▶│ agent_marketplace│───▶│   mcp_router    │
│                 │    │                  │    │                 │
│ Natural Language│    │   Workflow       │    │ AI Assistant    │
│       ↓         │    │   Management     │    │   Integration   │
│ n8n Workflows   │    │   & Deployment   │    │   (MCP Server)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### The Three-Module System

#### 🧙 **n8n-ai-genie** - AI-Powered Workflow Generator
Transform natural language descriptions into complete n8n workflows. No more learning complex automation syntax - just describe what you want.

- **Natural Language Interface**: "Send me a Slack notification when someone stars my GitHub repo"
- **Conversational Editing**: Modify existing workflows through chat
- **Multi-LLM Support**: Works with OpenAI, Claude, Gemini, Ollama, and more
- **Browser Plugin**: Enhances your existing n8n instance with AI superpowers

#### 🏪 **agent_marketplace** - Workflow Distribution Platform
A modern marketplace for discovering, sharing, and deploying n8n workflows with enterprise-grade security.

- **Workflow Discovery**: Browse pre-built automations by category and use case
- **One-Click Deployment**: Deploy workflows directly to your n8n instance
- **Secure Credential Management**: Your API keys never leave your control
- **User Management**: Multi-tenant support with role-based access

#### 🔧 **mcp_router** - AI Assistant Integration Layer
Convert any n8n workflow into a tool that AI assistants can discover and use automatically.

- **MCP Protocol Support**: Native integration with Claude, Cursor, and other MCP-compatible AI assistants
- **Dynamic Tool Generation**: Workflows become callable functions for AI assistants
- **Multi-Tenant Architecture**: Isolated instances for different users and organizations
- **RESTful Management**: Full API for programmatic workflow management

## 🎯 Use Cases & Examples

### For Business Automation
- **Customer Support**: AI assistant can trigger support workflows based on customer queries
- **Lead Management**: Automatically qualify and route leads through AI conversation
- **Report Generation**: AI can generate and distribute custom reports on demand

### For Content Creators
- **Social Media Management**: AI assistant publishes content across platforms
- **Content Analysis**: Automatic sentiment analysis and engagement tracking
- **Audience Insights**: AI-driven analytics and recommendation generation

### For Developers
- **CI/CD Automation**: AI assistant can deploy code, run tests, and manage releases
- **Infrastructure Management**: Automated scaling and monitoring through AI commands
- **Code Quality**: Automatic code review and quality checks triggered by AI

## 🚀 Quick Start Guide

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Node.js 16+
- A running n8n instance (self-hosted or cloud)

### 1. Set Up n8n-ai-genie (AI Workflow Generator)

```bash
cd n8n-ai-genie

# Install dependencies
pip install -r requirements.txt

# Configure your AI provider
cp .env.exmaple .env
# Edit config.json with your API keys

# Start the API server
python app.py

#configure the js
change the API_BASE_URL in .env to your deployed server url
# Install browser plugin
Copy n8n-genie-js/ to your n8n instance
```

**Usage:**
1. Open your n8n instance
2. Click the "AI Genie" button that appears
3. Describe your workflow: "Create a workflow that posts to Twitter when I get a new GitHub star"
4. Watch as AI generates a complete workflow
5. Test and deploy your automation

### 2. Set Up agent_marketplace (Workflow Management)

```bash
cd agent_marketplace

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
configure the .env.example
cp .env.example .env


#setup the supabase tables
python agent_marketplace/setup_supabase.py

# Start the marketplace
python app.py
```

**Usage:**
1. Visit `http://localhost:5000`
2. Register/login with your n8n instance details
3. Browse the workflow marketplace
4. Upload workflows from n8n-ai-genie
5. Deploy workflows to your n8n instance with one click

### 3. Set Up mcp_router (AI Assistant Integration)

```bash
cd mcp_router

# Install dependencies
pip install -r requirements.txt

#configure the environment variables
configure .env.example
cp .env.example .env

#setup the supabase tables
python mcp_router/setup_database.py


# Start the MCP router
python mcp_router.py
```

**Usage:**
1. Register a workflow as an MCP server:
```bash
curl -X POST "http://localhost:6545/n8n/build" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "your-workflow-id",
    "user_apikey": "your-api-key",
    "n8n_host": "your-n8n-instance.com"
  }'
```

2. Connect your AI assistant to the MCP server:
```
mcp://localhost:6545/mcp/your-workflow-id/your-api-key
```

3. Your AI assistant can now use your workflows as tools!

## 🐳 Docker Deployment

Each module includes a Dockerfile for easy deployment:

```bash

# build individual services
cd n8n-ai-genie && docker build -t n8n-ai-genie .
cd agent_marketplace && docker build -t agent-marketplace .
cd mcp_router && docker build -t mcp-router .
```

## 🛡️ Security Features

- **Zero-Trust Credential Management**: API keys never stored server-side
- **Multi-Tenant Isolation**: Complete separation between user instances
- **Encrypted Communication**: All data encrypted in transit and at rest
- **Role-Based Access Control**: Fine-grained permissions for teams
- **Audit Logging**: Complete audit trail of all automation executions

## 🤝 Contributing

We welcome contributions to all three modules! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite**: `npm test` or `pytest`
5. **Submit a pull request**


## 📚 Documentation

- **[n8n-ai-genie Documentation](./n8n-ai-genie/README.md)** - AI workflow generation
- **[agent_marketplace Documentation](./agent_marketplace/README.md)** - Workflow marketplace
- **[mcp_router Documentation](./mcp_router/README.md)** - MCP server integration


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **n8n Community** - For building an amazing automation platform
- **Anthropic** - For the Model Context Protocol and Claude integration
- **OpenAI** - For GPT models that power the AI workflow generation
- **Supabase** - For providing an excellent backend-as-a-service platform
- **Open Deepwiki** - Powering the n8n workflow generation feature

## 📞 Support & Community

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Join our community discussions
- **Discord**: Join our Discord server for real-time support
- **Documentation**: Comprehensive docs and tutorials

---

**Ready to transform how you work with automation?** Start with n8n-ai-genie to create your first AI-powered workflow, then explore the marketplace and make your automations available to AI assistants worldwide!

*Built with ❤️ by the SUPERCHAIN team for the AI automation community*