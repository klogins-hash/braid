#!/usr/bin/env python3
"""
Activate n8n workflows for Braid AI integration
"""
import requests
import json

# n8n configuration
N8N_URL = "https://primary-production-704b8.up.railway.app"
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5MzIyOWUzYy01NDM5LTRjZjItYjk1NS0yYWY3NGI5MTc1YzMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU5MTQ3NzYxfQ.qyXv5EAQ6bSSTw2k50BfSReAC0l1y7cAp3acHExmU6k"

def get_workflows():
    """Get all workflows."""
    headers = {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Content-Type": "application/json"
    }
    
    url = f"{N8N_URL}/api/v1/workflows"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def activate_workflow(workflow_id):
    """Activate a workflow."""
    headers = {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Content-Type": "application/json"
    }
    
    url = f"{N8N_URL}/api/v1/workflows/{workflow_id}/activate"
    
    try:
        response = requests.post(url, headers=headers, timeout=30)
        if response.status_code in [200, 201]:
            return True, response.json()
        else:
            return False, f"Status {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def main():
    """Activate Braid workflows."""
    print("🚀 Activating Braid AI workflows in n8n...")
    
    # Get all workflows
    print("📋 Getting workflows...")
    success, workflows = get_workflows()
    
    if not success:
        print(f"❌ Failed to get workflows: {workflows}")
        return False
    
    # Find Braid workflows
    braid_workflows = []
    for workflow in workflows.get('data', []):
        if 'braid' in workflow.get('name', '').lower():
            braid_workflows.append(workflow)
    
    print(f"🔍 Found {len(braid_workflows)} Braid workflows")
    
    # Activate each workflow
    activated_count = 0
    webhook_urls = []
    
    for workflow in braid_workflows:
        workflow_id = workflow.get('id')
        workflow_name = workflow.get('name')
        
        print(f"⚡ Activating {workflow_name} (ID: {workflow_id})...")
        
        success, result = activate_workflow(workflow_id)
        
        if success:
            print(f"   ✅ {workflow_name} activated successfully!")
            activated_count += 1
            
            # Extract webhook URLs
            if 'chat' in workflow_name.lower():
                webhook_urls.append(f"💬 Chat: {N8N_URL}/webhook/braid-chat")
            elif 'manager' in workflow_name.lower():
                webhook_urls.append(f"🔧 Manager: {N8N_URL}/webhook/braid-manage")
        else:
            print(f"   ❌ Failed to activate {workflow_name}: {result}")
    
    print(f"\n🎉 Activation completed! ({activated_count}/{len(braid_workflows)} workflows activated)")
    
    if activated_count > 0:
        print("\n🔗 Active Webhook URLs:")
        for url in webhook_urls:
            print(f"   {url}")
        
        print("\n🧪 Test your integration:")
        print(f'''curl -X POST "{N8N_URL}/webhook/braid-chat" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "message": "Hello! Test message from Braid AI",
    "user_id": "test_user",
    "agent_type": "chat"
  }}' ''')
        
        print("\n✅ Your Braid AI chat interface is now live!")
        return True
    else:
        print("\n⚠️  No workflows were activated.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
