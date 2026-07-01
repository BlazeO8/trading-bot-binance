"""Command Line Interface for the Trading Bot"""

import argparse
import logging
import sys
import os
from typing import Optional
from trading_bot.bot.logging_config import setup_logging
from trading_bot.bot.client import BinanceClient, BinanceAPIError
from trading_bot.bot.orders import OrderExecutor
from trading_bot.bot.validators import ValidationError

logger = None


def setup_argument_parser() -> argparse.ArgumentParser:
    """
    Set up command line argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Trading Bot for Binance Futures Testnet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Place a MARKET BUY order
  python -m trading_bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  
  # Place a LIMIT SELL order
  python -m trading_bot.cli --symbol ETHUSDT --side SELL --type LIMIT --quantity 1.0 --price 1500.50
        """
    )
    
    parser.add_argument(
        '--api-key',
        required=False,
        help='Binance Futures API Key (or set BINANCE_API_KEY env var)'
    )
    parser.add_argument(
        '--api-secret',
        required=False,
        help='Binance Futures API Secret (or set BINANCE_API_SECRET env var)'
    )
    parser.add_argument(
        '--symbol',
        required=True,
        help='Trading symbol (e.g., BTCUSDT)'
    )
    parser.add_argument(
        '--side',
        required=True,
        choices=['BUY', 'SELL'],
        help='Order side'
    )
    parser.add_argument(
        '--type',
        required=True,
        choices=['MARKET', 'LIMIT'],
        dest='order_type',
        help='Order type'
    )
    parser.add_argument(
        '--quantity',
        required=True,
        help='Order quantity'
    )
    parser.add_argument(
        '--price',
        required=False,
        help='Order price (required for LIMIT orders)'
    )
    parser.add_argument(
        '--log-dir',
        default='logs',
        help='Directory for log files (default: logs)'
    )
    
    return parser


def get_api_credentials(args) -> tuple:
    """
    Get API credentials from arguments or environment variables.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Tuple of (api_key, api_secret)
        
    Raises:
        ValueError: If credentials are not provided
    """
    api_key = args.api_key or os.getenv('BINANCE_API_KEY')
    api_secret = args.api_secret or os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        raise ValueError(
            "API credentials required. Provide via --api-key/--api-secret "
            "or BINANCE_API_KEY/BINANCE_API_SECRET environment variables."
        )
    
    return api_key, api_secret


def main(argv: Optional[list] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        argv: Command line arguments (for testing)
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    global logger
    
    parser = setup_argument_parser()
    args = parser.parse_args(argv)
    
    logger = setup_logging(args.log_dir)
    logger.info("="*60)
    logger.info("Trading Bot Started")
    logger.info("="*60)
    
    try:
        api_key, api_secret = get_api_credentials(args)
        logger.info("API credentials loaded successfully")
        
        client = BinanceClient(api_key, api_secret)
        executor = OrderExecutor(client)
        
        logger.info(
            f"Placing order: {args.side} {args.order_type} "
            f"{args.quantity} {args.symbol}"
        )
        print(f"\nPlacing order...")
        
        order_response = executor.validate_and_place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price
        )
        
        formatted_response = OrderExecutor.format_order_response(order_response)
        print(formatted_response)
        logger.info(formatted_response)
        
        logger.info("Order placement completed successfully")
        return 0
        
    except ValueError as e:
        error_msg = f"Configuration error: {e}"
        print(f"\n❌ Error: {error_msg}", file=sys.stderr)
        if logger:
            logger.error(error_msg)
        return 1
    except ValidationError as e:
        error_msg = f"Validation error: {e}"
        print(f"\n❌ Error: {error_msg}", file=sys.stderr)
        if logger:
            logger.error(error_msg)
        return 1
    except BinanceAPIError as e:
        error_msg = f"API error: {e}"
        print(f"\n❌ Error: {error_msg}", file=sys.stderr)
        if logger:
            logger.error(error_msg)
        return 1
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(f"\n❌ Error: {error_msg}", file=sys.stderr)
        if logger:
            logger.error(error_msg, exc_info=True)
        return 1
    finally:
        if logger:
            logger.info("Trading Bot Closed")


if __name__ == "__main__":
    sys.exit(main())
