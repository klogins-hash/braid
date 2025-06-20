"""Tools for conducting market research using Perplexity API."""

import os
import logging
from typing import Dict, Any
import requests

logger = logging.getLogger(__name__)

class PerplexityTools:
    """Tools for conducting market research using Perplexity."""
    
    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY', '').strip()
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def conduct_market_research(self, industry: str, location: str) -> str:
        """
        Conduct market research for a specific industry and location.
        
        Args:
            industry: Industry to research
            location: Geographic location
            
        Returns:
            Market research insights as a string
        """
        try:
            if not self.api_key:
                logger.warning("⚠️ No Perplexity API key, using mock data")
                return self._get_mock_research(industry, location)
            
            logger.info(f"🔍 Conducting market research for {industry} in {location}...")
            
            # Construct research query
            query = f"""Provide a comprehensive market analysis for the {industry} industry in {location}, focusing on:
1. Market size and growth projections (next 5 years)
2. Key industry trends and drivers
3. Competitive landscape
4. Regulatory environment
5. Economic factors affecting the industry
6. Technology trends impacting the sector
7. Key risks and opportunities"""
            
            # Call Perplexity API
            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers=self.headers,
                json={
                    'model': 'llama-3.1-sonar-small-128k-online',
                    'messages': [{'role': 'user', 'content': query}],
                    'max_tokens': 1000
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                research = data['choices'][0]['message']['content']
                logger.info("✅ Market research completed successfully")
                return research
            else:
                logger.warning(f"⚠️ Perplexity API error: {response.status_code}")
                return self._get_mock_research(industry, location)
                
        except Exception as e:
            logger.error(f"❌ Market research error: {e}")
            return self._get_mock_research(industry, location)
    
    def _get_mock_research(self, industry: str, location: str) -> str:
        """Get mock market research data for testing."""
        return f"""Market Analysis: {industry} in {location}

Market Size & Growth:
- Current market size: $50B
- Projected CAGR: 12% over next 5 years
- Expected market size by 2028: $88B

Key Industry Trends:
1. Digital transformation driving operational efficiency
2. Increasing focus on sustainability
3. Rising demand for personalized solutions
4. Growing adoption of AI and automation

Competitive Landscape:
- Market is moderately fragmented
- Top 5 players hold 40% market share
- High barriers to entry due to technology requirements
- Increasing M&A activity

Regulatory Environment:
- Strict data privacy regulations
- Environmental compliance requirements
- Industry-specific certifications needed
- Regular regulatory audits required

Economic Factors:
- Strong correlation with GDP growth
- Interest rates affecting capital investments
- Labor market remains tight
- Supply chain stabilizing post-pandemic

Technology Trends:
1. Cloud computing adoption accelerating
2. AI/ML implementation growing
3. IoT integration becoming standard
4. Cybersecurity investments increasing

Risks and Opportunities:
Risks:
- Cybersecurity threats
- Regulatory changes
- Talent shortage
- Economic uncertainty

Opportunities:
- Market expansion
- Technology innovation
- Strategic partnerships
- Green initiatives

Overall Outlook: Positive growth trajectory with strong digital transformation trends driving innovation and market expansion.

Note: This is simulated market research data for demonstration purposes.""" 