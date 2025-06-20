# AlphaVantage MCP Server

AlphaVantage MCP provides comprehensive financial market data including real-time stock quotes, historical time series, forex rates, cryptocurrency data, and technical indicators through the Model Context Protocol.

## Overview

AlphaVantage is a leading provider of financial market data APIs. This MCP server enables AI agents to access real-time and historical financial data for stocks, forex, cryptocurrencies, and technical analysis indicators.

## Capabilities

### Core Financial Data Tools

- **`av_get_stock_quote`**: Get real-time stock price quotes
  - Input: Stock symbol (e.g., "AAPL", "GOOGL")
  - Output: Current price, volume, change, and market data
  
- **`av_get_time_series_daily`**: Daily historical stock data
  - Input: Symbol, output size (compact/full)
  - Output: Daily OHLCV data for up to 20+ years
  
- **`av_get_time_series_intraday`**: Intraday stock data
  - Input: Symbol, interval (1min, 5min, 15min, 30min, 60min)
  - Output: Real-time and historical intraday price movements

- **`av_get_company_overview`**: Fundamental company data
  - Input: Stock symbol
  - Output: Financial ratios, market cap, P/E, dividend yield, etc.

### Foreign Exchange & Crypto

- **`av_get_forex_rate`**: Real-time forex exchange rates
  - Input: From currency, to currency (e.g., USD to EUR)
  - Output: Current exchange rate and bid/ask prices

- **`av_get_crypto_quote`**: Cryptocurrency market data
  - Input: Crypto symbol, market (e.g., BTC, ETH)
  - Output: Current price, market cap, volume in multiple currencies

### Technical Analysis

- **`av_get_technical_indicator`**: Technical analysis indicators
  - Input: Symbol, indicator function, interval, time period
  - Output: Technical indicators like SMA, EMA, RSI, MACD, Bollinger Bands
  - Supports 30+ technical indicators

## Setup Instructions

### 1. Get AlphaVantage API Key

1. Visit [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)
2. Sign up for a free account
3. Your API key will be provided immediately
4. Note: Free tier includes 25 requests per day, 5 per minute

### 2. Environment Configuration

Add to your `.env` file:

```bash
ALPHAVANTAGE_API_KEY=your-alphavantage-api-key-here
```

### 3. Installation

The MCP server is automatically installed when using Braid's Docker orchestration:

```bash
braid package --production
docker compose up --build
```

For manual installation:
```bash
git clone https://github.com/calvernaz/alphavantage.git
cd alphavantage
pip install -e .
```

## Usage Examples

### Stock Market Analysis

```python
# Get real-time stock quote
quote = agent.av_get_stock_quote(symbol="AAPL")
print(f"Apple stock: ${quote['price']} ({quote['change']})")

# Get historical data
historical = agent.av_get_time_series_daily(
    symbol="AAPL",
    outputsize="compact"  # Last 100 days
)

# Get company fundamentals
fundamentals = agent.av_get_company_overview(symbol="AAPL")
print(f"P/E Ratio: {fundamentals['PE_ratio']}")
print(f"Market Cap: {fundamentals['market_cap']}")
```

### Portfolio Tracking

```python
# Track multiple stocks
portfolio = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
portfolio_data = []

for symbol in portfolio:
    quote = agent.av_get_stock_quote(symbol=symbol)
    portfolio_data.append({
        "symbol": symbol,
        "price": quote["price"],
        "change_percent": quote["change_percent"]
    })

# Analyze portfolio performance
total_change = sum(stock["change_percent"] for stock in portfolio_data)
print(f"Portfolio daily change: {total_change:.2f}%")
```

### Currency Exchange

```python
# Get current exchange rates
usd_to_eur = agent.av_get_forex_rate(
    from_currency="USD",
    to_currency="EUR"
)

# Track multiple currencies
currencies = [("USD", "EUR"), ("USD", "GBP"), ("USD", "JPY")]
for from_curr, to_curr in currencies:
    rate = agent.av_get_forex_rate(from_curr, to_curr)
    print(f"{from_curr}/{to_curr}: {rate['exchange_rate']}")
```

### Technical Analysis

```python
# Get moving averages
sma_20 = agent.av_get_technical_indicator(
    symbol="AAPL",
    function="SMA",
    interval="daily",
    time_period=20
)

# Get RSI for momentum analysis
rsi = agent.av_get_technical_indicator(
    symbol="AAPL",
    function="RSI",
    interval="daily",
    time_period=14
)

# Bollinger Bands for volatility
bbands = agent.av_get_technical_indicator(
    symbol="AAPL",
    function="BBANDS",
    interval="daily",
    time_period=20
)
```

### Cryptocurrency Monitoring

```python
# Track major cryptocurrencies
crypto_portfolio = ["BTC", "ETH", "ADA", "DOT"]

for crypto in crypto_portfolio:
    data = agent.av_get_crypto_quote(
        symbol=crypto,
        market="USD"
    )
    print(f"{crypto}: ${data['price']} ({data['change_24h']}%)")
```

## Use Cases

### Investment Research
- **Stock Screening**: Filter stocks by P/E ratio, market cap, dividend yield
- **Fundamental Analysis**: Compare financial metrics across companies
- **Sector Analysis**: Track performance of industry groups

### Algorithmic Trading
- **Signal Generation**: Use technical indicators for buy/sell signals
- **Backtesting**: Historical data for strategy validation
- **Risk Management**: Real-time monitoring of position values

### Market Monitoring
- **Watchlists**: Track favorite stocks and their performance
- **News Impact**: Monitor price reactions to events
- **Volatility Tracking**: Identify high-volatility opportunities

### Financial Reporting
- **Portfolio Valuation**: Real-time portfolio worth calculation
- **Performance Analytics**: Compare against benchmarks
- **Risk Assessment**: Calculate portfolio beta and correlation

## Rate Limiting & Best Practices

### API Limits (Free Tier)
- **Daily Limit**: 25 requests per day
- **Rate Limit**: 5 requests per minute
- **Premium Plans**: Available for higher limits

### Optimization Tips
1. **Cache Results**: Store frequently accessed data locally
2. **Batch Requests**: Combine related queries when possible
3. **Use Appropriate Intervals**: Daily data for long-term analysis, intraday for active trading
4. **Monitor Usage**: Track API calls to stay within limits

### Error Handling
```python
try:
    quote = agent.av_get_stock_quote(symbol="INVALID")
except Exception as e:
    print(f"Error fetching data: {e}")
    # Implement fallback or retry logic
```

## Technical Indicators Available

### Trend Indicators
- **SMA/EMA**: Simple and Exponential Moving Averages
- **MACD**: Moving Average Convergence Divergence
- **ADX**: Average Directional Index

### Momentum Indicators
- **RSI**: Relative Strength Index
- **Stochastic**: %K and %D oscillators
- **Williams %R**: Williams Percent Range

### Volatility Indicators
- **Bollinger Bands**: Price envelope bands
- **ATR**: Average True Range
- **Standard Deviation**: Price volatility measure

### Volume Indicators
- **OBV**: On-Balance Volume
- **AD**: Accumulation/Distribution
- **Chaikin A/D**: Chaikin Accumulation/Distribution Line

## Troubleshooting

### Common Issues

**Invalid API Key**
- Verify the key is correctly set in your `.env` file
- Check that the API key hasn't expired
- Ensure you're using the correct key format

**Rate Limit Exceeded**
- AlphaVantage enforces strict rate limits
- Implement delays between requests
- Consider upgrading to a premium plan for higher limits

**Symbol Not Found**
- Verify the stock symbol is correct (e.g., "AAPL" not "Apple")
- Check if the symbol exists on the target exchange
- Some international symbols may require specific formatting

**Network Issues**
- Ensure the container has internet access
- Check firewall settings for outbound HTTPS connections
- Verify DNS resolution for alphavantage.co

### Debug Mode

To enable detailed logging:

```bash
# Set debug environment variable
DEBUG=1 python -m alphavantage_mcp_server
```

## Integration with Braid

When using AlphaVantage MCP with Braid agents, the tools are automatically available with the `av_` prefix:

- `av_get_stock_quote()` - Real-time stock quotes
- `av_get_time_series_daily()` - Daily historical data
- `av_get_company_overview()` - Fundamental analysis
- And all other financial data tools

The MCP runs in a separate Docker container with proper networking and caching configured automatically.

## Security & Compliance

- **API Keys**: Securely stored in environment variables
- **Data Privacy**: No sensitive data stored locally
- **HTTPS Only**: All API communications encrypted
- **Rate Limiting**: Built-in respect for API limits
- **Audit Trail**: Request logging for compliance

## Premium Features

Consider upgrading to AlphaVantage Premium for:
- **Higher Rate Limits**: Up to 1,200 requests per minute
- **Extended History**: 20+ years of historical data
- **Real-time Data**: Live market feeds
- **Additional Datasets**: Earnings, news, sentiment data
- **Priority Support**: Faster response times

## Support

- **AlphaVantage Documentation**: [https://www.alphavantage.co/documentation/](https://www.alphavantage.co/documentation/)
- **MCP Repository**: [https://github.com/calvernaz/alphavantage](https://github.com/calvernaz/alphavantage)
- **API Support**: Contact AlphaVantage through their support portal