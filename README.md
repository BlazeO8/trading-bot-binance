# Trading Bot - Binance Futures Testnet

A simplified Python trading bot for placing market and limit orders on Binance Futures Testnet (USDT-M) with proper logging, error handling, and clean code structure.

## Features

✅ **Order Types**: MARKET and LIMIT orders  
✅ **Order Sides**: BUY and SELL  
✅ **Input Validation**: Comprehensive validation for all parameters  
✅ **Error Handling**: Network, API, and input validation errors  
✅ **Logging**: Detailed logging to file and console  
✅ **Clean Architecture**: Separated client, orders, validators, and CLI layers  
✅ **Testnet Support**: Uses Binance Futures Testnet for safe testing  

## Setup

### Prerequisites

- Python 3.8 or higher
- pip or conda
- Binance Futures Testnet account

### 1. Clone Repository

```bash
git clone https://github.com/BlazeO8/trading-bot-binance.git
cd trading-bot-binance
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Binance Futures Testnet Credentials

1. Go to [Binance Testnet](https://testnet.binancefuture.com/)
2. Register a new account
3. Navigate to API Management
4. Create a new API key and secret
5. Enable trading permissions

### 5. Set Environment Variables

Create a `.env` file in the project root:

```bash
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

Or set them directly:

```bash
export BINANCE_API_KEY="your_api_key"
export BINANCE_API_SECRET="your_api_secret"
```

## Usage

### Market Order (BUY)

```bash
python -m trading_bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Limit Order (SELL)

```bash
python -m trading_bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 50000
```

### With Inline Credentials

```bash
python -m trading_bot.cli \
  --api-key your_key \
  --api-secret your_secret \
  --symbol ETHUSDT \
  --side BUY \
  --type MARKET \
  --quantity 1.0
```

### Custom Log Directory

```bash
python -m trading_bot.cli \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.001 \
  --log-dir ./my_logs
```

## Command Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--api-key` | No | Binance API Key (or use BINANCE_API_KEY env var) |
| `--api-secret` | No | Binance API Secret (or use BINANCE_API_SECRET env var) |
| `--symbol` | **Yes** | Trading pair (e.g., BTCUSDT, ETHUSDT) |
| `--side` | **Yes** | BUY or SELL |
| `--type` | **Yes** | MARKET or LIMIT |
| `--quantity` | **Yes** | Order quantity |
| `--price` | No | Order price (required for LIMIT orders) |
| `--log-dir` | No | Directory for log files (default: logs) |

## Project Structure

```
trading-bot-binance/
├── trading_bot/
│   ├── __init__.py
│   ├── cli.py                 # CLI entry point
│   └── bot/
│       ├── __init__.py
│       ├── client.py          # Binance API client wrapper
│       ├── orders.py          # Order execution logic
│       ├── validators.py      # Input validation
│       └── logging_config.py  # Logging configuration
├── logs/                      # Log files directory
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore file
└── LICENSE                    # MIT License
```

## Log Files

Logs are stored in the `logs/` directory with timestamps:

```
logs/
├── trading_bot_20240101_120000.log  # MARKET order example
└── trading_bot_20240101_121500.log  # LIMIT order example
```

Each log file contains:
- API request details
- Parameter validation logs
- Order placement responses
- Error messages with full stack traces

## Examples

### Example 1: Place a MARKET BUY Order

```bash
python -m trading_bot.cli \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.001
```

**Output:**
```
Placing order...
============================================================
ORDER PLACED SUCCESSFULLY
============================================================
Order ID:        1234567890
Symbol:          BTCUSDT
Side:            BUY
Order Type:      MARKET
Status:          FILLED
Quantity:        0.001
Executed Qty:    0.001
Average Price:   42500.50
Time in Force:   GTC
Create Time:     1704110400000
============================================================
```

### Example 2: Place a LIMIT SELL Order

```bash
python -m trading_bot.cli \
  --symbol ETHUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 1.0 \
  --price 2500.00
```

**Output:**
```
Placing order...
============================================================
ORDER PLACED SUCCESSFULLY
============================================================
Order ID:        1234567891
Symbol:          ETHUSDT
Side:            SELL
Order Type:      LIMIT
Status:          NEW
Quantity:        1.0
Executed Qty:    0.0
Price:           2500.00
Time in Force:   GTC
Create Time:     1704110415000
============================================================
```

## Error Handling

The bot handles multiple error scenarios:

### Input Validation Errors

```bash
$ python -m trading_bot.cli --symbol BTC --side BUY --type MARKET --quantity 0.001
Error: Symbol 'BTC' is too short (minimum 6 characters)
```

### API Errors

```bash
$ python -m trading_bot.cli --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001
Error: Price is required for LIMIT orders
```

### Network Errors

```bash
Error: Connection error: /fapi/v1/order
```

All errors are logged to the log file for debugging.

## Configuration

### Binance Testnet URL

The bot uses the official Binance Futures Testnet:
```
https://testnet.binancefuture.com
```

### Supported Symbols

Any USDT-M perpetual futures pair:
- BTCUSDT
- ETHUSDT
- BNBUSDT
- ADAUSDT
- etc.

### API Rate Limits

Binance Testnet has generous rate limits. The bot includes:
- Request timeout: 10 seconds
- Automatic logging of all requests
- Error handling for timeouts

## Assumptions

1. **Testnet Only**: This bot is designed for Binance Futures Testnet and should NOT be used with mainnet without review
2. **USDT-M Futures**: Only USDT-M perpetual futures are supported
3. **Good Till Cancel (GTC)**: LIMIT orders use GTC time in force
4. **No Position Management**: This is a simple order placement bot, not a full trading system
5. **No Risk Management**: User is responsible for position sizing and risk
6. **API Credentials**: Store credentials securely in environment variables or .env files

## Logging

The bot provides two levels of logging:

### Console Output
- Shows order summaries and errors
- Log level: INFO and above

### File Output
- Detailed logs including debug information
- Location: `logs/trading_bot_YYYYMMDD_HHMMSS.log`
- Log level: DEBUG and above
- Rotating files (max 10MB per file, 5 backups)

### Log Format
```
2024-01-01 12:00:00 - trading_bot - INFO - Binance client initialized successfully
2024-01-01 12:00:01 - trading_bot - DEBUG - Making POST request to /fapi/v1/order
2024-01-01 12:00:02 - trading_bot - INFO - Order placed successfully
```

## Troubleshooting

### "API credentials required"

Ensure you have set the environment variables:
```bash
export BINANCE_API_KEY="your_key"
export BINANCE_API_SECRET="your_secret"
```

Or use command line arguments:
```bash
python -m trading_bot.cli --api-key "your_key" --api-secret "your_secret" ...
```

### "Connection error"

Check your internet connection and verify the Binance Testnet URL is accessible.

### "Invalid signature"

Ensure your API credentials are correct and your system time is synchronized.

### "Symbol not found"

Verify the symbol exists on Binance Futures Testnet (USDT-M markets).

## Development

### Running Tests (Future)

```bash
python -m pytest tests/
```

### Code Style

The project follows PEP 8 conventions. Format code with:

```bash
pip install black
black trading_bot/
```

## Future Enhancements

- [ ] Stop-Limit and OCO orders
- [ ] Position management
- [ ] Portfolio monitoring
- [ ] Automated trading strategies
- [ ] WebSocket support for real-time data
- [ ] Unit tests
- [ ] Web UI dashboard

## Security

⚠️ **Important**: Never commit API credentials to version control. Always use:
- Environment variables
- `.env` files (add to `.gitignore`)
- Secure credential management systems

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the log files in `logs/` directory
2. Review error messages in console output
3. Verify API credentials and permissions
4. Check Binance Testnet status

## Disclaimer

This trading bot is provided for educational purposes only. Trading cryptocurrencies carries risk. Always:
- Test thoroughly on testnet
- Start with small amounts
- Implement proper risk management
- Never invest more than you can afford to lose

The authors are not responsible for any financial losses incurred through use of this bot.
