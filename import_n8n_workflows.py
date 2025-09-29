#!/usr/bin/env python3
"""
Automated n8n workflow import script for Braid AI integration
"""
import requests
import json
import sys

# n8n configuration
N8N_URL = "https://primary-production-704b8.up.railway.app"
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5MzIyOWUzYy01NDM5LTRjZjItYjk1NS0yYWY3NGI5MTc1YzMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU5MTQ3NzYxfQ.qyXv5EAQ6bSSTw2k50BfSReAC0l1y7cAp3acHExmU6k"

def create_workflow(workflow_data):
    """Create a workflow in n8n via API."""
    headers = {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Content-Type": "application/json"
    }
    
    url = f"{N8N_URL}/api/v1/workflows"
    
    try:
        response = requests.post(url, headers=headers, json=workflow_data, timeout=30)
        if response.status_code in [200, 201]:
            return True, response.json()
        else:
            return False, f"Status {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def main():
    """Import Braid workflows into n8n."""
    print("🚀 Importing Braid AI workflows into n8n...")
    
    # Braid Chat Workflow
    chat_workflow = {
        "name": "Braid AI Chat",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "braid-chat",
                    "responseMode": "onReceived",
                    "options": {}
                },
                "id": "webhook-chat",
                "name": "Chat Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
                "webhookId": "braid-chat"
            },
            {
                "parameters": {
                    "url": "https://braid-production.up.railway.app/agents",
                    "sendHeaders": True,
                    "headerParameters": {
                        "parameters": [
                            {
                                "name": "Content-Type",
                                "value": "application/json"
                            }
                        ]
                    },
                    "sendBody": True,
                    "contentType": "json",
                    "jsonParameters": True,
                    "bodyParametersJson": "={{ {\n  \"agent_type\": $json.body.agent_type || \"chat\",\n  \"config\": {\n    \"model\": \"claude-4-sonnet-20250101\",\n    \"temperature\": 0.7\n  },\n  \"tools\": $json.body.tools || []\n} }}",
                    "options": {}
                },
                "id": "create-agent",
                "name": "Create Braid Agent",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "url": "={{ \"https://braid-production.up.railway.app/agents/\" + $('Create Braid Agent').item.json.agent_id + \"/workflows\" }}",
                    "sendHeaders": True,
                    "headerParameters": {
                        "parameters": [
                            {
                                "name": "Content-Type",
                                "value": "application/json"
                            }
                        ]
                    },
                    "sendBody": True,
                    "contentType": "json",
                    "jsonParameters": True,
                    "bodyParametersJson": "={{ {\n  \"agent_id\": $('Create Braid Agent').item.json.agent_id,\n  \"workflow_name\": \"chat_response\",\n  \"input_data\": {\n    \"message\": $('Chat Webhook').item.json.body.message,\n    \"user_id\": $('Chat Webhook').item.json.body.user_id || \"anonymous\"\n  }\n} }}",
                    "options": {}
                },
                "id": "execute-workflow",
                "name": "Execute Chat",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [680, 300]
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ {\n  \"status\": \"success\",\n  \"agent_id\": $('Create Braid Agent').item.json.agent_id,\n  \"execution_id\": $('Execute Chat').item.json.execution_id,\n  \"message\": \"Chat started with Braid AI agent\",\n  \"webhook_url\": \"https://primary-production-704b8.up.railway.app/webhook/braid-chat\"\n} }}"
                },
                "id": "respond",
                "name": "Respond",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 300]
            }
        ],
        "connections": {
            "Chat Webhook": {
                "main": [
                    [
                        {
                            "node": "Create Braid Agent",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Create Braid Agent": {
                "main": [
                    [
                        {
                            "node": "Execute Chat",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Execute Chat": {
                "main": [
                    [
                        {
                            "node": "Respond",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "settings": {
            "timezone": "America/New_York"
        }
    }
    
    # Agent Manager Workflow
    manager_workflow = {
        "name": "Braid Agent Manager",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "braid-manage",
                    "responseMode": "onReceived",
                    "options": {}
                },
                "id": "webhook-manage",
                "name": "Management Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
                "webhookId": "braid-manage"
            },
            {
                "parameters": {
                    "conditions": {
                        "options": {
                            "caseSensitive": True,
                            "leftValue": "",
                            "typeValidation": "strict"
                        },
                        "conditions": [
                            {
                                "id": "action-create",
                                "leftValue": "={{ $json.body.action }}",
                                "rightValue": "create",
                                "operator": {
                                    "type": "string",
                                    "operation": "equals"
                                }
                            }
                        ],
                        "combinator": "and"
                    },
                    "options": {}
                },
                "id": "check-action",
                "name": "Check Action",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "url": "https://braid-production.up.railway.app/agents",
                    "sendHeaders": True,
                    "headerParameters": {
                        "parameters": [
                            {
                                "name": "Content-Type",
                                "value": "application/json"
                            }
                        ]
                    },
                    "sendBody": True,
                    "contentType": "json",
                    "jsonParameters": True,
                    "bodyParametersJson": "={{ $('Management Webhook').item.json.body }}",
                    "options": {}
                },
                "id": "create-agent-node",
                "name": "Create Agent",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [680, 200]
            },
            {
                "parameters": {
                    "url": "={{ \"https://braid-production.up.railway.app/agents/\" + $('Management Webhook').item.json.body.agent_id }}",
                    "options": {}
                },
                "id": "get-agent-node",
                "name": "Get Agent",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [680, 400]
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ $json }}"
                },
                "id": "respond-create",
                "name": "Respond Create",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 200]
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ $json }}"
                },
                "id": "respond-get",
                "name": "Respond Get",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 400]
            }
        ],
        "connections": {
            "Management Webhook": {
                "main": [
                    [
                        {
                            "node": "Check Action",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Check Action": {
                "main": [
                    [
                        {
                            "node": "Create Agent",
                            "type": "main",
                            "index": 0
                        }
                    ],
                    [
                        {
                            "node": "Get Agent",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Create Agent": {
                "main": [
                    [
                        {
                            "node": "Respond Create",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Get Agent": {
                "main": [
                    [
                        {
                            "node": "Respond Get",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "settings": {
            "timezone": "America/New_York"
        }
    }
    
    # Import workflows
    workflows = [
        ("Braid AI Chat", chat_workflow),
        ("Braid Agent Manager", manager_workflow)
    ]
    
    success_count = 0
    webhook_urls = []
    
    for name, workflow in workflows:
        print(f"📝 Importing {name}...")
        success, result = create_workflow(workflow)
        
        if success:
            print(f"   ✅ {name} imported successfully!")
            print(f"   📋 Workflow ID: {result.get('id', 'N/A')}")
            
            # Extract webhook URL
            if 'braid-chat' in name.lower():
                webhook_urls.append(f"🔗 Chat Webhook: {N8N_URL}/webhook/braid-chat")
            elif 'manager' in name.lower():
                webhook_urls.append(f"🔗 Manager Webhook: {N8N_URL}/webhook/braid-manage")
            
            success_count += 1
        else:
            print(f"   ❌ Failed to import {name}: {result}")
    
    print(f"\n🎉 Import completed! ({success_count}/2 workflows imported)")
    
    if success_count > 0:
        print("\n📋 Your Braid AI n8n Integration is ready!")
        print("🌐 n8n Dashboard:", N8N_URL)
        print("🤖 Braid API:", "https://braid-production.up.railway.app")
        print("\n🔗 Webhook URLs:")
        for url in webhook_urls:
            print(f"   {url}")
        
        print("\n🧪 Test your chat integration:")
        print(f'''curl -X POST "{N8N_URL}/webhook/braid-chat" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "message": "Hello! Can you help me with research?",
    "user_id": "test_user",
    "agent_type": "research"
  }}' ''')
        
        print("\n✅ Integration complete! Your Braid AI agents are now accessible through n8n!")
        return True
    else:
        print("\n⚠️  No workflows were imported successfully.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
