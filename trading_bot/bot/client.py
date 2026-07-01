"""Thin wrapper around python-binance's Client, scoped to Futures Testnet.

This is the only module that talks to the network. Keeping it isolated
means the CLI and order-building logic can be unit-tested by mocking
this class, and it's the single place that needs to change if the
underlying HTTP library or API version ever changes.
"""
import os
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from .logging_config import get_logger

logger = get_logger(__name__)


class BinanceFuturesTestnetClient:
    """Wraps python-binance's Client for USDT-M Futures Testnet order placement."""

    def __init__(self, api_key: str = None, api_secret: str = None):
        api_key = api_key or os.getenv("BINANCE_API_KEY")
        api_secret = api_secret or os.getenv("BINANCE_API_SECRET")

        if not api_key or not api_secret:
            raise RuntimeError(
                "Missing API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET "
                "as environment variables (or in a .env file) before running the bot."
            )

        # testnet=True routes python-binance's futures endpoints to
        # https://testnet.binancefuture.com/fapi instead of the live API.
        self._client = Client(api_key, api_secret, testnet=True)
        logger.info("Initialized Binance Futures Testnet client.")

    def create_order(self, **params) -> dict:
        """Send an order to Binance Futures Testnet and return the raw response."""
        logger.info("Sending order request: %s", params)
        try:
            response = self._client.futures_create_order(**params)
            logger.info("Order response: %s", response)
            return response
        except (BinanceAPIException, BinanceRequestException) as exc:
            logger.error("Binance API error while placing order: %s", exc)
            raise
        except Exception as exc:  # network errors, timeouts, DNS failures, etc.
            logger.error("Unexpected/network error while placing order: %s", exc)
            raise

    def get_symbol_price(self, symbol: str) -> float:
        """Convenience helper, useful for sanity-checking LIMIT prices."""
        try:
            ticker = self._client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker["price"])
            logger.info("Fetched mark price for %s: %s", symbol, price)
            return price
        except (BinanceAPIException, BinanceRequestException) as exc:
            logger.error("Failed to fetch price for %s: %s", symbol, exc)
            raise
