import yfinance as yf
import pandas as pd
from tavily import TavilyClient
from langchain_core.tools import tool
import os

# A list of popular, highly-traded stocks to check
# In a real-world scenario, this list would be much larger or dynamically sourced.
CANDIDATE_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM", "JNJ", "V",
    "PG", "UNH", "HD", "MA", "BAC", "DIS", "PFE", "XOM", "CSCO", "PEP"
]

@tool
def get_top_gainer() -> dict:
    """
    Fetches data for a list of candidate stocks and identifies the one with the highest
    percentage gain over the past day. FOR TESTING, THIS IS HARDCODED TO RETURN NVDA.

    Returns:
        dict: A dictionary containing the top gainer's data,
              or an error message if the operation fails.
    """
    print("--- (TESTING) Forcing tool to return NVDA to test RAG. ---")
    try:
        # Hardcode to NVDA for this test
        ticker_symbol = "NVDA"
        
        # Download data for just NVDA, silencing the warning
        data = yf.download(ticker_symbol, period="2d", progress=False, auto_adjust=True)
        if data.empty:
            return {"error": "Could not download stock data for NVDA from yfinance."}

        # Get the latest entry
        latest_data = data.iloc[-1]
        previous_data = data.iloc[-2]

        # Explicitly cast to float/int before formatting
        price_val = float(latest_data['Close'])
        change_val = float(latest_data['Close'] - previous_data['Close'])
        change_percentage_val = float((change_val / previous_data['Close']) * 100)
        volume_val = int(latest_data['Volume'])
        
        gainer_info = yf.Ticker(ticker_symbol).info

        return {
            "ticker": ticker_symbol,
            "company_name": gainer_info.get('longName', ticker_symbol),
            "price": f"{price_val:.2f}",
            "change_amount": f"{change_val:.2f}",
            "change_percentage": f"{change_percentage_val:.2f}%",
            "volume": f"{volume_val:,}"
        }

    except Exception as e:
        return {"error": f"An unexpected error occurred with yfinance: {e}"}


@tool
def search_gainer_news(ticker: str, company_name: str) -> str:
    """
    Searches for news and analysis about a specific stock using Tavily.

    Args:
        ticker (str): The stock ticker.
        company_name (str): The name of the company.

    Returns:
        str: A summary of the search results, or an error message.
    """
    query = f"Why did the stock for {company_name} ({ticker}) gain value recently? Summarize the top 3 reasons."
    try:
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        # Using qna_search for a direct answer based on search results
        response = tavily_client.qna_search(query, search_depth="advanced")
        return response
    except Exception as e:
        return f"Error searching for news with Tavily: {e}"
