#!/usr/bin/env python3
"""
Test Perplexity API directly
"""

import logging
from agent import conduct_market_research

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_perplexity_api():
    """Test direct Perplexity API call"""
    print("🧪 Testing Perplexity API Direct Call")
    print("=" * 50)
    
    try:
        # Test market research
        print("🔍 Testing market research...")
        result = conduct_market_research.func("Software Development", "San Francisco, CA")
        print(f"✅ Market Research Result:")
        print(f"{result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Perplexity API test failed: {e}")
        return False

if __name__ == "__main__":
    test_perplexity_api()