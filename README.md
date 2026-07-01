# Simplified Trading Bot — Binance Futures Testnet (USDT-M)

A small CLI application that places MARKET, LIMIT, and (bonus) STOP_LIMIT orders on Binance Futures Testnet, with input validation, structured error handling, and request/response logging.

## Project Structure

```
trading_bot/
  bot/
    __init__.py
    client.py              # Binance client wrapper
    orders.py              # order placement logic
    validators.py          # input validation
    logging_config.py      # logging configuration
  cli.py                   # CLI entry point
  README.md
  requirements.txt
  .env.example
  .gitignore
  LICENSE
```

## Setup

### 1. Create a Binance Futures Testnet Account

Go to [Binance Testnet](https://testnet.binancefuture.com) and register a new account. Generate an API key and secret from the testnet dashboard with trading permissions enabled.

### 2. Clone/Install the Project

```bash
git clone https://github.com/BlazeO8/trading-bot-binance.git
cd trading_bot
pip install -r requirements.txt
```

### 3. Configure Credentials

Copy `.env.example` to `.env` and fill in your testnet API credentials:

```bash
cp .env.example .env
```

```
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

Alternatively, set them as environment variables:

```bash
export BINANCE_API_KEY="your_key"
export BINANCE_API_SECRET="your_secret"
```

## Running It

### Market Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Limit Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 61000
```

### Bonus: Stop-Limit Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.01 --price 58000 --stop-price 58500
```

Each run prints:
- The validated order request summary
- The raw order response (order ID, status, executed quantity, average price when available)
- A clear success/failure message

All requests, responses, and errors are logged to `logs/trading_bot_YYYYMMDD_HHMMSS.log` (created automatically on first run, rotated at 2MB).

## CLI Arguments

| Flag           | Required        | Notes                                   |
|----------------|-----------------|-----------------------------------------|
| `--symbol`     | yes             | e.g. `BTCUSDT`                          |
| `--side`       | yes             | `BUY` or `SELL`                         |
| `--type`       | yes             | `MARKET`, `LIMIT`, or `STOP_LIMIT`      |
| `--quantity`   | yes             | must be > 0                             |
| `--price`      | LIMIT/STOP_LIMIT| required for those two order types      |
| `--stop-price` | STOP_LIMIT      | required only for STOP_LIMIT            |

Invalid input (bad symbol format, unsupported side/type, missing price, non-positive quantity, etc.) is rejected before any network call is made, with a specific error message and an entry in the log file.

## Error Handling

- **Input validation errors** (`bot/validators.py`) are caught in `cli.py` and reported without ever touching the network.
- **Binance API errors** (e.g. invalid symbol, LOT_SIZE filter failures, insufficient testnet balance) are caught in `bot/client.py`, logged with the full exception, and re-raised so the CLI can print a clean `[FAILED]` message.
- **Network/connectivity errors** (timeouts, DNS failures, etc.) are caught the same way as API errors, since both are just "the order didn't go through" from the user's perspective.

## Design Notes / Assumptions

- Uses the `python-binance` library with `Client(api_key, api_secret, testnet=True)`, which points the futures endpoints at `https://testnet.binancefuture.com/fapi` instead of the live API — no manual URL wiring needed.
- STOP_LIMIT is implemented as Binance Futures' `STOP` order type (price + stopPrice), chosen as the bonus feature over OCO/TWAP/Grid for simplicity and because it maps directly onto the existing LIMIT code path.
- `timeInForce` defaults to `GTC` (Good Till Cancel) for LIMIT/STOP_LIMIT orders since the task didn't specify one.
- Quantities/prices are taken as-is from the CLI (as floats); this project does not attempt to auto-round to each symbol's exchange filter precision — if you hit a `LOT_SIZE` or `PRICE_FILTER` error, adjust the quantity/price to match the symbol's step size on the testnet.
- The client class only ever talks to the Futures Testnet base URL; it is not configured to accidentally hit the live Binance API.

## Logging

The bot provides two levels of logging:

### Console Output
- Shows order summaries and errors
- Log level: INFO and above

### File Output
- Detailed logs including debug information
- Location: `logs/trading_bot_YYYYMMDD_HHMMSS.log`
- Log level: DEBUG and above
- Rotating files (max 2MB per file, 5 backups)

### Log Format

```
2026-07-01 10:28:10 - bot.client - INFO - Initialized Binance Futures Testnet client.
2026-07-01 10:28:11 - bot.orders - DEBUG - Built order: BTCUSDT BUY 0.01 MARKET
2026-07-01 10:28:12 - bot.client - INFO - Sending order request: {...}
2026-07-01 10:28:13 - bot.client - INFO - Order response: {...}
```

## Module Overview

### `bot/client.py`
Thin wrapper around `python-binance`'s Client, scoped to Futures Testnet. This is the only module that talks to the network. Keeping it isolated means the CLI and order-building logic can be unit-tested by mocking this class.

**Key class:** `BinanceFuturesTestnetClient`
- `create_order(**params)` - Send an order and return the raw response
- `get_symbol_price(symbol)` - Convenience helper for sanity-checking LIMIT prices

### `bot/orders.py`
Builds, validates, and places OrderRequest objects.

**Key classes:**
- `OrderRequest` - Represents a validated trading order
  - `build()` - Factory method to validate CLI inputs
  - `summary()` - Human-readable order summary
- `OrderService` - Service for placing orders
  - `place_order(order)` - Place an order on testnet
  - `format_response(response)` - Format response for display

### `bot/validators.py`
Pure input-validation functions, kept separate so they can be unit-tested in isolation and reused if a different front-end (e.g. a UI) is added later.

**Functions:**
- `validate_symbol(symbol)` - Validate symbol format (e.g., BTCUSDT)
- `validate_side(side)` - Validate BUY/SELL
- `validate_order_type(order_type)` - Validate MARKET/LIMIT/STOP_LIMIT
- `validate_quantity(quantity)` - Validate quantity > 0
- `validate_price(price, order_type)` - Validate price for LIMIT/STOP_LIMIT
- `validate_stop_price(stop_price, order_type)` - Validate stop price for STOP_LIMIT

### `bot/logging_config.py`
Rotating file + console logger configuration.

**Functions:**
- `get_logger(name)` - Configure and return a logger instance

### `cli.py`
argparse CLI entry point.

**Functions:**
- `build_parser()` - Set up argument parser
- `main(argv)` - Main entry point (returns exit code 0 for success, 1 for failure)

## Examples

### Example 1: Place a Market BUY Order

```bash
$ python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
Order Request Summary:
  BUY 0.01 BTCUSDT (MARKET)

Order Response:
============================================================
Order ID:        1234567890
Symbol:          BTCUSDT
Side:            BUY
Order Type:      MARKET
Status:          FILLED
Quantity:        0.01
Executed Qty:    0.01
Average Price:   42500.50
Time in Force:   GTC
Create Time:     1704110400000
============================================================

[SUCCESS] Order placed successfully.
```

### Example 2: Place a Limit SELL Order

```bash
$ python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 61000
Order Request Summary:
  SELL 0.01 BTCUSDT (LIMIT) | price=61000

Order Response:
============================================================
Order ID:        1234567891
Symbol:          BTCUSDT
Side:            SELL
Order Type:      LIMIT
Status:          NEW
Quantity:        0.01
Executed Qty:    0.0
Price:           61000
Time in Force:   GTC
Create Time:     1704110415000
============================================================

[SUCCESS] Order placed successfully.
```

### Example 3: Place a Stop-Limit Order

```bash
$ python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.01 --price 58000 --stop-price 58500
Order Request Summary:
  SELL 0.01 BTCUSDT (STOP_LIMIT) | price=58000 | stop_price=58500

Order Response:
============================================================
Order ID:        1234567892
Symbol:          BTCUSDT
Side:            SELL
Order Type:      STOP
Status:          NEW
Quantity:        0.01
Executed Qty:    0.0
Price:           58000
Stop Price:      58500
Time in Force:   GTC
Create Time:     1704110430000
============================================================

[SUCCESS] Order placed successfully.
```

## Error Examples

### Invalid Symbol

```bash
$ python cli.py --symbol BTC --side BUY --type MARKET --quantity 0.01
[INPUT ERROR] Invalid symbol 'BTC'. Expected a format like 'BTCUSDT'.
```

### Missing Price for LIMIT Order

```bash
$ python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01
[INPUT ERROR] price is required for LIMIT orders.
```

### Invalid Quantity

```bash
$ python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity -1
[INPUT ERROR] Quantity must be greater than 0.
```

### API/Network Error

```bash
$ python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
[FAILED] Order could not be placed: 1000 [MIN_NOTIONAL_FILTER] Order value does not meet minimum quantity requirement.
```

## Troubleshooting

### "Missing API credentials"

Ensure you have set the environment variables or `.env` file:
```bash
export BINANCE_API_KEY="your_key"
export BINANCE_API_SECRET="your_secret"
```

### "Connection error"

Check your internet connection and verify the Binance Testnet URL is accessible.

### "Invalid signature"

Ensure your API credentials are correct and your system time is synchronized.

### "Symbol not found" / "Invalid symbol"

Verify the symbol exists on Binance Futures Testnet (USDT-M markets). Common symbols: BTCUSDT, ETHUSDT, BNBUSDT, ADAUSDT.

## Possible Future Improvements

- Query `exchangeInfo` to auto-validate/round quantity and price against each symbol's LOT_SIZE and PRICE_FILTER before submitting.
- Add `--dry-run` to print the constructed order without sending it.
- Add unit tests for `bot/validators.py` and `bot/orders.py` (both are pure functions with no network dependency, so they're easy to test in isolation).
- Add a lightweight web UI dashboard.

## Security

⚠️ **Important**: Never commit API credentials to version control. Always use:
- Environment variables
- `.env` files (add to `.gitignore`)
- Secure credential management systems

## License

MIT License - See LICENSE file for details

## Disclaimer

This trading bot is provided for educational purposes only. Trading cryptocurrencies carries risk. Always:
- Test thoroughly on testnet
- Start with small amounts
- Implement proper risk management
- Never invest more than you can afford to lose

The authors are not responsible for any financial losses incurred through use of this bot.
