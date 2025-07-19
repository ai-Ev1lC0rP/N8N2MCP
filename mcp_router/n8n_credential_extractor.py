import asyncio
import os
import json
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from datetime import datetime

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

class N8NCredentialExtractor:
    def __init__(self, username: str, password: str, instance_url: str):
        self.username = username
        self.password = password
        self.instance_url = instance_url
    
    async def extract_credentials(self) -> dict:
        """Extract browser ID and auth token from N8N"""
        print("Starting N8N credential extraction...")
        
        try:
            async with async_playwright() as p:
                print("Playwright initialized successfully")
                
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--disable-software-rasterizer']
                )
                print("Browser launched successfully")
                
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36'
                )
                page = await context.new_page()
                print("Page created successfully")
                
                try:
                    # Navigate to login page
                    login_url = self.instance_url + "/signin"
                    print(f"Navigating to: {login_url}")
                    await page.goto(login_url, wait_until='networkidle')
                    
                    # Wait for form to load
                    await page.wait_for_selector('input[name="emailOrLdapLoginId"]', timeout=10000)
                    
                    # Fill login form with correct selectors
                    print("Filling login form...")
                    await page.fill('input[name="emailOrLdapLoginId"]', self.username)
                    await page.fill('input[name="password"]', self.password)
                    
                    # Click sign in button
                    print("Clicking sign in button...")
                    await page.click('button[data-test-id="form-submit-button"]')
                    
                    # Wait for login to complete - looking for workflow or dashboard
                    print("Waiting for login to complete...")
                    try:
                        await page.wait_for_url('**/workflow**', timeout=15000)
                    except:
                        # Try alternative success indicators
                        try:
                            await page.wait_for_url('**/home**', timeout=5000)
                        except:
                            await page.wait_for_selector('[data-test-id="main-header"]', timeout=10000)
                    
                    print("Login successful, extracting credentials...")
                    
                    # Extract browser ID from localStorage
                    browser_id = await page.evaluate("localStorage.getItem('n8n-browserId')")
                    print(f"Extracted browser ID: {browser_id[:8] if browser_id else 'None'}...")
                    
                    # Extract auth token from cookies
                    cookies = await context.cookies()
                    n8n_auth = next((c['value'] for c in cookies if c['name'] == 'n8n-auth'), None)
                    print(f"Extracted auth token: {n8n_auth[:20] if n8n_auth else 'None'}...")
                    
                    if not browser_id:
                        raise Exception("Failed to extract browser ID from localStorage")
                    if not n8n_auth:
                        raise Exception("Failed to extract auth token from cookies")
                    
                    return {
                        "browser_id": browser_id,
                        "n8n_auth": n8n_auth,
                        "extracted_at": datetime.now().isoformat()
                    }
                    
                except Exception as e:
                    # Take screenshot for debugging
                    await page.screenshot(path='login_error.png')
                    print(f"Screenshot saved as login_error.png")
                    raise e
                    
                finally:
                    await browser.close()
        except Exception as e:
            print(f"Playwright error: {e}")
            raise e

async def main():
    # Get credentials from environment
    username = os.getenv('N8N_USERNAME')
    password = os.getenv('N8N_PASSWORD')
    instance_url = os.getenv('N8N_INSTANCE_URL')
    
    if not username or not password or not instance_url:
        print("Error: N8N_USERNAME, N8N_PASSWORD, and N8N_INSTANCE_URL must be set in environment variables")
        exit(1)
    
    print(f"Using instance URL: {instance_url}")
    
    extractor = N8NCredentialExtractor(username, password, instance_url)
    
    try:
        credentials = await extractor.extract_credentials()
        
        print("\n" + "="*60)
        print("🎉 EXTRACTION SUCCESSFUL!")
        print("="*60)
        print(f"BROWSER_ID = \"{credentials['browser_id']}\"")
        print(f"N8N_AUTH = \"{credentials['n8n_auth']}\"")
        print(f"Extracted at: {credentials['extracted_at']}")
        print("="*60)
        
        # Save to file
        with open('n8n_credentials.json', 'w') as f:
            json.dump(credentials, f, indent=2)
        print("✅ Credentials saved to n8n_credentials.json")
        
        # Generate environment variables
        env_content = f"""# N8N Credentials extracted on {credentials['extracted_at']}
export N8N_BROWSER_ID="{credentials['browser_id']}"
export N8N_AUTH="{credentials['n8n_auth']}"
"""
        
        with open('n8n_credentials.env', 'w') as f:
            f.write(env_content)
        print("✅ Environment variables saved to n8n_credentials.env")
        
        # Show usage instructions
        print(f"\n📋 Usage Instructions:")
        print(f"1. Source the env file: source n8n_credentials.env")
        print(f"2. Or update your mcp_router.py with these values:")
        print(f"   BROWSER_ID = \"{credentials['browser_id']}\"")
        print(f"   N8N_AUTH = \"{credentials['n8n_auth']}\"")
        
    except Exception as e:
        print(f"\n❌ EXTRACTION FAILED: {e}")
        print("Check login_error.png for debugging")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())