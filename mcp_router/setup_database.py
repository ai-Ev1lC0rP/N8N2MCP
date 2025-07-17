import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase setup
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_mcp_configs_table():
    """Create the mcp_configs table by attempting operations."""
    try:
        # Try to query the table first
        response = supabase.table('mcp_configs').select('id').limit(1).execute()
        logger.info("mcp_configs table already exists")
        return True
    except Exception as e:
        if "does not exist" in str(e):
            logger.info("Table doesn't exist. Please create it manually in Supabase dashboard.")
            logger.info("Go to: https://supabase.com/dashboard/project/upajkfvsfmrimhcimded/sql")
            logger.info("Run this SQL:")
            logger.info("""
            CREATE TABLE public.mcp_configs (
                id SERIAL PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                user_apikey TEXT NOT NULL,
                code TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            CREATE UNIQUE INDEX idx_mcp_configs_workflow_user ON public.mcp_configs(workflow_id, user_apikey);
            ALTER TABLE public.mcp_configs ENABLE ROW LEVEL SECURITY;
            """)
            return False
        else:
            logger.error(f"Unexpected error: {e}")
            return False

def create_rls_policies():
    """Create RLS policies to allow operations."""
    try:
        logger.info("Creating RLS policies...")
        logger.info("Please run this SQL in Supabase dashboard:")
        logger.info("""
        -- Policy to allow all operations for authenticated users
        CREATE POLICY "Allow all operations for authenticated users" ON public.mcp_configs
        FOR ALL USING (auth.role() = 'authenticated');
        
        -- Policy to allow all operations for service role (for API access)
        CREATE POLICY "Allow all operations for service role" ON public.mcp_configs
        FOR ALL USING (auth.role() = 'service_role');
        
        -- Policy to allow all operations for anon role (for your use case)
        CREATE POLICY "Allow all operations for anon role" ON public.mcp_configs
        FOR ALL USING (true);
        """)
        return False
    except Exception as e:
        logger.error(f"Error creating policies: {e}")
        return False

def test_table_connection():
    """Test if we can connect to and query the table."""
    try:
        response = supabase.table('mcp_configs').select('*').limit(1).execute()
        logger.info("Successfully connected to mcp_configs table")
        logger.info(f"Table has {len(response.data)} rows")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to table: {e}")
        return False

def insert_test_data():
    """Insert a test record to verify everything works."""
    try:
        test_data = {
            'workflow_id': 'test_workflow',
            'user_apikey': 'test_api_key',
            'code': 'print("test")'
        }
        
        response = supabase.table('mcp_configs').insert(test_data).execute()
        logger.info("Test data inserted successfully")
        
        # Clean up test data
        supabase.table('mcp_configs').delete().eq('workflow_id', 'test_workflow').execute()
        logger.info("Test data cleaned up")
        return True
    except Exception as e:
        if "row-level security policy" in str(e):
            logger.error("RLS policy is blocking operations. Please create policies.")
            create_rls_policies()
            return False
        else:
            logger.error(f"Failed to insert test data: {e}")
            return False

def main():
    """Main setup function."""
    logger.info("Starting database setup...")
    
    # Check if table exists
    if create_mcp_configs_table():
        # Test connection
        if test_table_connection():
            # Test insert/delete
            if insert_test_data():
                logger.info("✅ Database setup completed successfully!")
            else:
                logger.error("❌ Failed to test data operations - RLS policies needed")
        else:
            logger.error("❌ Failed to connect to table")
    else:
        logger.error("❌ Please create the table manually and run this script again")

if __name__ == "__main__":
    main()