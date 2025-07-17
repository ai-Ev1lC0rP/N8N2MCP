# Environment Variables for App Runner Deployment

## Required Variables

### Flask Configuration
- `FLASK_SECRET_KEY`: A secure random string for session encryption
  ```bash
  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
  ```

- `ENCRYPTION_KEY`: For encrypting stored credentials
  ```bash
  # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```

### N8N Integration
- `N8N_BASE_URL`: Your N8N instance URL (e.g., https://your-n8n.com)
- `X_N8N_API_KEY`: Your N8N API key
- `N8N_BUILDER_URL`: Your App Runner URL (set after deployment)

### Database (if using external DB)
- `DATABASE_URL`: Connection string for your database

## Setting Environment Variables

### Via AWS Console:
1. Go to your App Runner service
2. Click "Configuration" tab
3. Click "Configure" in Environment variables section
4. Add each variable with its value

### Via AWS CLI:
```bash
aws apprunner update-service \
  --service-arn your-service-arn \
  --source-configuration '{
    "CodeRepository": {
      "CodeConfiguration": {
        "CodeConfigurationValues": {
          "Runtime": "PYTHON_3",
          "BuildCommand": "pip install -r requirements.txt",
          "StartCommand": "python app.py",
          "Port": "5000",
          "RuntimeEnvironmentVariables": {
            "FLASK_SECRET_KEY": "your-secret-key",
            "ENCRYPTION_KEY": "your-encryption-key",
            "N8N_BASE_URL": "https://your-n8n.com",
            "X_N8N_API_KEY": "your-api-key"
          }
        }
      }
    }
  }'
``` 