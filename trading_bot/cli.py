"""Command-line entry point for the Trading Bot.

Example:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
    python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.01 --price 58000 --stop-price 58500
"""
import argparse
import sys
import os
from dotenv import load_dotenv
from bot.logging_config import get_logger
from bot.orders import OrderRequest, OrderService
from bot.validators import ValidationError

logger = get_logger("cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Place MARKET / LIMIT / STOP orders on Binance Futures Testnet (USDT-M).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Market order
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
  
  # Limit order
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 61000
  
  # Stop order (formerly Stop-Limit)
  python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.01 --price 58000 --stop-price 58500
        """
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument(
        "--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="Order side"
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP", "STOP_LIMIT", "market", "limit", "stop", "stop_limit"],
        help="Order type",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", help="Required for LIMIT and STOP orders")
    parser.add_argument(
        "--stop-price", dest="stop_price", help="Required for STOP orders"
    )
    return parser


def main(argv=None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        order = OrderRequest.build(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        print(f"[INPUT ERROR] {exc}")
        logger.warning("Rejected invalid input: %s", exc)
        return 1

    print("Order Request Summary:")
    print(f"  {order.summary()}\n")

    try:
        service = OrderService()
        response = service.place_order(order)
    except Exception as exc:  # surfaces validation, API, and network failures alike
        print(f"[FAILED] Order could not be placed: {exc}")
        logger.error("Order failed: %s", exc)
        return 1

    print("Order Response:")
    print(OrderService.format_response(response))
    print("\n[SUCCESS] Order placed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
