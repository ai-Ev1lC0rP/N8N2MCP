#!/usr/bin/env python3
"""
Environment Setup Script for Agent Marketplace
This script helps you configure the required environment variables.
"""

import os
import sys
# Removed encryption key generation since we no longer need user credential storage

def create_env_file():
    """Create .env file with user input"""
    print("🚀 Setting up Agent Marketplace Environment")
    print("=" * 50)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📋 Please provide the following information:")
    print("(Press Enter to skip optional fields)")
    
    # Supabase Configuration (optional - simplified version doesn't require user auth)
    print("\n🔗 Supabase Configuration (Optional):")
    print("Get these from: https://app.supabase.com/project/[your-project]/settings/api")
    print("Note: This simplified version doesn't require user authentication.")
    supabase_url = input("Supabase URL (optional): ").strip()
    supabase_key = input("Supabase Anon Key (optional): ").strip()
    
    # N8N Configuration
    print("\n🔧 N8N Configuration (Optional):")
    n8n_api_key = input("N8N API Key (optional): ").strip()
    n8n_base_url = input("N8N Base URL (optional, e.g., https://n8n.yourdomain.com): ").strip()
    n8n_builder_url = input("N8N Builder URL (optional, e.g., https://builder.example.com): ").strip()
    
    # Create .env content
    env_content = f"""# Supabase Configuration (Optional - for workflow storage)
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# N8N Configuration
X_N8N_API_KEY={n8n_api_key}
N8N_BASE_URL={n8n_base_url}
N8N_BUILDER_URL={n8n_builder_url}

# Generated on: {os.popen('date').read().strip()}
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("\n✅ Environment file created successfully!")
        print("📁 File location: .env")
        
        if supabase_url and supabase_key:
            print("\n🎉 Supabase configuration detected!")
            print("   The application will use your Supabase database for workflow storage.")
        else:
            print("\n⚠️  No Supabase configuration provided.")
            print("   The application will run without database storage.")
        
        print("\n🔄 Please restart the application to apply changes:")
        print("   python app.py")
        
    except Exception as e:
        print(f"\n❌ Error creating .env file: {e}")
        return False
    
    return True

def check_current_config():
    """Check current environment configuration"""
    print("🔍 Current Environment Configuration:")
    print("=" * 40)
    
    # Load .env if it exists
    if os.path.exists('.env'):
        print("📁 .env file: ✅ Found")
        from dotenv import load_dotenv
        load_dotenv()
    else:
        print("📁 .env file: ❌ Not found")
    
    # Check optional variables
    optional_vars = {
        'SUPABASE_URL': 'Supabase Project URL (optional)',
        'SUPABASE_KEY': 'Supabase Anon Key (optional)',
        'X_N8N_API_KEY': 'N8N API Key (optional)',
        'N8N_BASE_URL': 'N8N Base URL (optional)',
        'N8N_BUILDER_URL': 'N8N Builder URL (optional)'
    }
    
    configured_count = 0
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'SECRET' in var:
                display_value = value[:8] + "..." if len(value) > 8 else value
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
            configured_count += 1
        else:
            print(f"➖ {var}: Not set")
    
    print(f"\n📊 Configuration Status: {configured_count}/{len(optional_vars)} optional variables set")
    
    # Check if Supabase is configured
    supabase_configured = os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY')
    if supabase_configured:
        print("🎉 Supabase: ✅ Configured (Database storage enabled)")
    else:
        print("⚠️  Supabase: ❌ Not configured (No database storage)")
    
    return supabase_configured

def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        check_current_config()
        return
    
    print("Agent Marketplace Environment Setup")
    print("Options:")
    print("1. Create new .env file")
    print("2. Check current configuration")
    print("3. Exit")
    
    choice = input("\nChoose an option (1-3): ").strip()
    
    if choice == '1':
        create_env_file()
    elif choice == '2':
        check_current_config()
    elif choice == '3':
        print("Goodbye!")
    else:
        print("Invalid choice. Please run the script again.")

if __name__ == '__main__':
    main() 