#!/usr/bin/env python3
"""
Configure LibreChat to use Braid AI via Railway internal networking
"""
import requests
import json
import os

def main():
    """Configure LibreChat integration with Braid."""
    print("🚀 Configuring LibreChat integration with Braid AI...")
    
    # Configuration for LibreChat
    librechat_config = {
        "name": "Braid AI",
        "baseURL": "http://braid:8000/v1",
        "apiKey": "braid-api-key",  # This will be set as environment variable
        "models": {
            "default": [
                "claude-4-sonnet-20250101",
                "claude-4-opus-20250101", 
                "claude-4-haiku-20250101"
            ],
            "fetch": False
        },
        "titleConvo": True,
        "titleModel": "claude-4-sonnet-20250101",
        "summarize": False,
        "summaryModel": "claude-4-haiku-20250101",
        "forcePrompt": False,
        "modelDisplayLabel": "Braid AI",
        "iconURL": "https://cdn-icons-png.flaticon.com/512/8943/8943377.png"
    }
    
    print("📋 LibreChat Configuration:")
    print(f"   🔗 Braid API URL: http://braid:8000/v1")
    print(f"   🤖 Available Models:")
    for model in librechat_config["models"]["default"]:
        print(f"      - {model}")
    
    print("\n🔧 Required Environment Variables for LibreChat:")
    print("   BRAID_API_KEY=your-braid-api-key")
    print("   ENDPOINTS=braid")
    
    print("\n📝 LibreChat Custom Endpoint Configuration:")
    print("Add this to your LibreChat librechat.yaml:")
    print("""
endpoints:
  custom:
    - name: "Braid AI"
      apiKey: "${BRAID_API_KEY}"
      baseURL: "http://braid:8000/v1"
      models:
        default: [
          "claude-4-sonnet-20250101",
          "claude-4-opus-20250101", 
          "claude-4-haiku-20250101"
        ]
        fetch: false
      titleConvo: true
      titleModel: "claude-4-sonnet-20250101"
      modelDisplayLabel: "Braid AI"
      iconURL: "https://cdn-icons-png.flaticon.com/512/8943/8943377.png"
""")
    
    print("\n🚀 Next Steps:")
    print("1. Copy librechat-config/librechat.yaml to your LibreChat service")
    print("2. Set BRAID_API_KEY environment variable in LibreChat service")
    print("3. Restart LibreChat service")
    print("4. Select 'Braid AI' from the model dropdown in LibreChat")
    
    print("\n✅ Configuration complete!")
    print("🌐 LibreChat will now use Braid AI agents via Railway internal networking")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
