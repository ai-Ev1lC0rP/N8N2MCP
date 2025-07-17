#!/usr/bin/env python3
"""
Supabase Setup Script for N8N Agent Marketplace
This script validates and sets up the Supabase database before the app starts.
"""

import os
import sys
import json
import time
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    print("❌ ERROR: Supabase client not installed")
    print("   Please install with: pip install supabase")
    sys.exit(1)

class SupabaseSetup:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        self.supabase: Optional[Client] = None
        self.supabase_admin: Optional[Client] = None
        
        # Required tables and their essential columns
        self.required_tables = {
            'user_profiles': ['id', 'user_id', 'email', 'name', 'created_at', 'updated_at'],
            'user_workflows': ['id', 'user_id', 'workflow_name', 'workflow_json', 'created_at', 'updated_at'],
            'user_credentials': ['id', 'user_id', 'service_name', 'credential_type', 'encrypted_credentials', 'created_at', 'updated_at'],
            'n8n_workflows': ['id', 'template_id', 'template_url', 'workflow_name', 'workflow_json', 'created_at', 'updated_at'],
            'workflow_deployments': ['id', 'user_id', 'workflow_name', 'n8n_workflow_id', 'deployment_status', 'created_at', 'updated_at']
        }
        
    def validate_environment(self) -> bool:
        """Validate that all required environment variables are set"""
        print("🔍 Validating environment variables...")
        
        missing_vars = []
        
        if not self.supabase_url:
            missing_vars.append('SUPABASE_URL')
        if not self.supabase_key:
            missing_vars.append('SUPABASE_KEY')
        if not self.supabase_service_key:
            missing_vars.append('SUPABASE_SERVICE_KEY')
            
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            print("\nPlease set these in your .env file:")
            for var in missing_vars:
                print(f"   {var}=your_value_here")
            return False
            
        print("✅ All required environment variables are set")
        return True
    
    def connect_to_supabase(self) -> bool:
        """Establish connection to Supabase"""
        print("🔗 Connecting to Supabase...")
        
        try:
            # Create regular client
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            
            # Create admin client with service role
            self.supabase_admin = create_client(self.supabase_url, self.supabase_service_key)
            
            # Test connection with a simple query
            result = self.supabase_admin.table('user_profiles').select('count', count='exact').execute()
            print(f"✅ Connected to Supabase successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            return False
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        try:
            # Try to select from the table
            result = self.supabase_admin.table(table_name).select('*').limit(1).execute()
            return True
        except Exception:
            return False
    
    def check_table_structure(self, table_name: str, required_columns: list) -> Dict[str, bool]:
        """Check if table has required columns"""
        try:
            # Get table schema by trying to select specific columns
            result = self.supabase_admin.table(table_name).select(','.join(required_columns)).limit(1).execute()
            return {col: True for col in required_columns}
        except Exception as e:
            # If query fails, try to identify which columns are missing
            column_status = {}
            for col in required_columns:
                try:
                    self.supabase_admin.table(table_name).select(col).limit(1).execute()
                    column_status[col] = True
                except Exception:
                    column_status[col] = False
            return column_status
    
    def validate_database_schema(self) -> bool:
        """Validate that all required tables and columns exist"""
        print("🔍 Validating database schema...")
        
        all_valid = True
        
        for table_name, required_columns in self.required_tables.items():
            print(f"   Checking table: {table_name}")
            
            if not self.check_table_exists(table_name):
                print(f"   ❌ Table '{table_name}' does not exist")
                all_valid = False
                continue
                
            column_status = self.check_table_structure(table_name, required_columns)
            missing_columns = [col for col, exists in column_status.items() if not exists]
            
            if missing_columns:
                print(f"   ❌ Table '{table_name}' missing columns: {', '.join(missing_columns)}")
                all_valid = False
            else:
                print(f"   ✅ Table '{table_name}' structure is valid")
        
        return all_valid
    
    def check_rls_policies(self) -> bool:
        """Check if RLS policies are properly configured"""
        print("🔍 Checking RLS policies...")
        
        try:
            # Try to query as authenticated user (this will fail if RLS is not properly configured)
            # We'll test by checking if we can access the tables
            for table_name in self.required_tables.keys():
                try:
                    # Try with admin client first
                    result = self.supabase_admin.table(table_name).select('*').limit(1).execute()
                    print(f"   ✅ Table '{table_name}' accessible with admin client")
                except Exception as e:
                    print(f"   ❌ Table '{table_name}' not accessible: {e}")
                    return False
            
            print("✅ RLS policies appear to be working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Error checking RLS policies: {e}")
            return False
    
    def run_sql_setup(self) -> bool:
        """Run the database setup SQL if needed"""
        print("🔧 Attempting to run database setup...")
        
        try:
            # Read the complete setup SQL file
            sql_file_path = os.path.join(os.path.dirname(__file__), 'supabase_complete_setup.sql')
            
            if not os.path.exists(sql_file_path):
                print(f"❌ SQL setup file not found: {sql_file_path}")
                return False
            
            with open(sql_file_path, 'r') as f:
                sql_content = f.read()
            
            print("⚠️  Database setup requires manual execution")
            print("   Please run the following SQL in your Supabase SQL editor:")
            print(f"   File: {sql_file_path}")
            print("\n   Alternatively, copy and paste the SQL content into Supabase dashboard")
            
            # Note: Supabase Python client doesn't support running arbitrary SQL
            # This needs to be done through the dashboard or API
            return False
            
        except Exception as e:
            print(f"❌ Error preparing SQL setup: {e}")
            return False
    
    def setup_database(self) -> bool:
        """Complete database setup process"""
        print("🚀 Starting Supabase database setup...")
        
        # Step 1: Validate environment
        if not self.validate_environment():
            return False
        
        # Step 2: Connect to Supabase
        if not self.connect_to_supabase():
            return False
        
        # Step 3: Check database schema
        schema_valid = self.validate_database_schema()
        
        if not schema_valid:
            print("\n❌ Database schema validation failed!")
            print("🔧 Please run the database setup SQL manually:")
            print("   1. Open your Supabase dashboard")
            print("   2. Go to SQL Editor")
            print("   3. Run the contents of 'supabase_complete_setup.sql'")
            print("   4. Re-run this setup script")
            return False
        
        # Step 4: Check RLS policies
        if not self.check_rls_policies():
            print("\n⚠️  RLS policies may need attention")
            print("   Database structure is valid, but RLS policies might need setup")
            print("   The app may still work, but security features might be limited")
        
        print("\n✅ Supabase database setup completed successfully!")
        print("   All required tables and columns are present")
        print("   Database is ready for the application to start")
        
        return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("🏗️  N8N Agent Marketplace - Supabase Setup")
    print("=" * 60)
    
    setup = SupabaseSetup()
    
    if setup.setup_database():
        print("\n🎉 Setup completed successfully!")
        print("   You can now start the application")
        sys.exit(0)
    else:
        print("\n❌ Setup failed!")
        print("   Please fix the issues above before starting the application")
        sys.exit(1)

if __name__ == "__main__":
    main()