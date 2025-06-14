import yfinance as yf
import json
from pathlib import Path
from langchain_core.tools import tool

@tool
def screen_stocks(sectors: list[str], risk_tolerance: str) -> str:
    """
    Screens stocks based on sector and risk tolerance.
    Fetches latest price and 7-day percentage change using yfinance.
    Ranks stocks by momentum (7-day change) and sector fit.
    Saves results to a JSON file in data/ and returns a summary.
    """
    # TODO: Replace with a more sophisticated screening logic, possibly RAG-based.
    # This is a simplified placeholder.
    print(f"Screening stocks for sectors: {sectors} and risk tolerance: {risk_tolerance}")

    # Placeholder tickers for demonstration
    tickers_by_sector = {
        'tech': ['AAPL', 'MSFT', 'GOOGL'],
        'energy': ['XOM', 'CVX', 'SHEL'],
        'finance': ['JPM', 'BAC', 'WFC'],
    }

    selected_tickers = []
    for sector in sectors:
        selected_tickers.extend(tickers_by_sector.get(sector.lower(), []))

    if not selected_tickers:
        return "No valid tickers found for the selected sectors."

    stock_data = []
    for ticker in selected_tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="8d")
        if not hist.empty:
            latest_price = hist['Close'].iloc[-1]
            seven_day_ago_price = hist['Close'].iloc[0]
            seven_day_change = ((latest_price - seven_day_ago_price) / seven_day_ago_price) * 100
            stock_data.append({
                'ticker': ticker,
                'latest_price': round(latest_price, 2),
                '7d_change_pct': round(seven_day_change, 2)
            })

    # Rank by momentum (7d_change_pct)
    stock_data.sort(key=lambda x: x['7d_change_pct'], reverse=True)

    # TODO: A real implementation would have a more complex risk assessment.
    if risk_tolerance == 'low':
        results = stock_data[len(stock_data)//2:] # Less volatile half
    elif risk_tolerance == 'high':
        results = stock_data[:len(stock_data)//2] # More volatile half
    else: # medium
        results = stock_data

    # Store results in data/
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    results_path = data_dir / 'screening_results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    summary = f"Found {len(results)} stocks. Top result: {results[0]['ticker']} with a 7-day change of {results[0]['7d_change_pct']}%. Results saved to {results_path}"
    return summary 