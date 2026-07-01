"""Binance Futures Testnet API Client"""

import logging
import hashlib
import hmac
import time
from typing import Dict, Any, Optional
from decimal import Decimal
import requests
from urllib.parse import urlencode

logger = logging.getLogger("trading_bot")


class BinanceAPIError(Exception):
    """Custom exception for Binance API errors"""
    pass


class BinanceClient:
    """
    Binance Futures Testnet API Client
    
    Handles authentication and API requests to Binance Futures Testnet
    """
    
    BASE_URL = "https://testnet.binancefuture.com"
    TIMEOUT = 10
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize Binance client.
        
        Args:
            api_key: Binance Futures API key
            api_secret: Binance Futures API secret
            
        Raises:
            ValueError: If API credentials are empty
        """
        if not api_key or not api_secret:
            raise ValueError("API key and secret are required")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        
        logger.info("Binance client initialized successfully")
    
    def _generate_signature(self, data: Dict[str, Any]) -> str:
        """
        Generate HMAC SHA256 signature for API request.
        
        Args:
            data: Request parameters
            
        Returns:
            Signature string
        """
        query_string = urlencode(data)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = True
    ) -> Dict[str, Any]:
        """
        Make a request to Binance API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Request parameters
            signed: Whether to sign the request
            
        Returns:
            JSON response from API
            
        Raises:
            BinanceAPIError: If request fails
        """
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            logger.debug(f"Making {method} request to {endpoint}")
            
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=self.TIMEOUT)
            elif method.upper() == "POST":
                response = self.session.post(url, data=params, timeout=self.TIMEOUT)
            else:
                raise BinanceAPIError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            response_data = response.json()
            
            logger.debug(f"Response from {endpoint}: {response_data}")
            return response_data
            
        except requests.exceptions.Timeout:
            error_msg = f"Request timeout: {endpoint}"
            logger.error(error_msg)
            raise BinanceAPIError(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = f"Connection error: {endpoint}"
            logger.error(error_msg)
            raise BinanceAPIError(error_msg)
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise BinanceAPIError(error_msg)
        except ValueError as e:
            error_msg = f"Invalid JSON response: {e}"
            logger.error(error_msg)
            raise BinanceAPIError(error_msg)
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Place an order on Binance Futures Testnet.
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: Order side (BUY/SELL)
            order_type: Order type (MARKET/LIMIT)
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            
        Returns:
            Order response from API
            
        Raises:
            BinanceAPIError: If order placement fails
            ValueError: If required parameters are missing
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': str(quantity)
        }
        
        if order_type == "LIMIT":
            if price is None:
                raise ValueError("Price is required for LIMIT orders")
            params['price'] = str(price)
            params['timeInForce'] = 'GTC'
        
        logger.info(f"Placing {side} {order_type} order for {quantity} {symbol}")
        
        try:
            response = self._make_request("POST", "/fapi/v1/order", params, signed=True)
            logger.info(f"Order placed successfully: {response}")
            return response
        except BinanceAPIError as e:
            logger.error(f"Failed to place order: {e}")
            raise
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance and position information.
        
        Returns:
            Account information from API
            
        Raises:
            BinanceAPIError: If request fails
        """
        logger.info("Fetching account balance")
        try:
            response = self._make_request("GET", "/fapi/v2/account", {}, signed=True)
            logger.info("Account balance retrieved successfully")
            return response
        except BinanceAPIError as e:
            logger.error(f"Failed to get account balance: {e}")
            raise
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Get status of a specific order.
        
        Args:
            symbol: Trading pair
            order_id: Order ID
            
        Returns:
            Order status from API
            
        Raises:
            BinanceAPIError: If request fails
        """
        params = {'symbol': symbol, 'orderId': order_id}
        logger.info(f"Fetching order status for {symbol} order {order_id}")
        try:
            response = self._make_request("GET", "/fapi/v1/order", params, signed=True)
            logger.info(f"Order status retrieved")
            return response
        except BinanceAPIError as e:
            logger.error(f"Failed to get order status: {e}")
            raise
