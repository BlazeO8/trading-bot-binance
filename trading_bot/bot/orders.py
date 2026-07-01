"""Order management and execution logic"""

import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from trading_bot.bot.client import BinanceClient, BinanceAPIError
from trading_bot.bot.validators import InputValidator, ValidationError

logger = logging.getLogger("trading_bot")


class OrderExecutor:
    """
    Handles order execution logic with validation and error handling
    """
    
    def __init__(self, client: BinanceClient):
        """
        Initialize order executor.
        
        Args:
            client: BinanceClient instance
        """
        self.client = client
        self.validator = InputValidator()
    
    def validate_and_place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate inputs and place an order.
        
        Args:
            symbol: Trading pair
            side: Order side (BUY/SELL)
            order_type: Order type (MARKET/LIMIT)
            quantity: Order quantity as string
            price: Order price as string (optional)
            
        Returns:
            Order response from API
            
        Raises:
            ValidationError: If validation fails
            BinanceAPIError: If order placement fails
        """
        validated_symbol = self.validator.validate_symbol(symbol)
        validated_side = self.validator.validate_side(side)
        validated_order_type = self.validator.validate_order_type(order_type)
        validated_quantity = self.validator.validate_quantity(quantity)
        validated_price = self.validator.validate_price(price, validated_order_type)
        
        logger.info(
            f"Validated order: {validated_symbol} {validated_side} "
            f"{validated_quantity} {validated_order_type}"
        )
        
        try:
            response = self.client.place_order(
                symbol=validated_symbol,
                side=validated_side,
                order_type=validated_order_type,
                quantity=validated_quantity,
                price=validated_price
            )
            return response
        except BinanceAPIError as e:
            logger.error(f"Order placement failed: {e}")
            raise
    
    @staticmethod
    def format_order_response(order_response: Dict[str, Any]) -> str:
        """
        Format order response for display.
        
        Args:
            order_response: Order response from API
            
        Returns:
            Formatted string representation
        """
        output = "\n" + "="*60 + "\n"
        output += "ORDER PLACED SUCCESSFULLY\n"
        output += "="*60 + "\n"
        output += f"Order ID:        {order_response.get('orderId', 'N/A')}\n"
        output += f"Symbol:          {order_response.get('symbol', 'N/A')}\n"
        output += f"Side:            {order_response.get('side', 'N/A')}\n"
        output += f"Order Type:      {order_response.get('type', 'N/A')}\n"
        output += f"Status:          {order_response.get('status', 'N/A')}\n"
        output += f"Quantity:        {order_response.get('origQty', 'N/A')}\n"
        output += f"Executed Qty:    {order_response.get('executedQty', 'N/A')}\n"
        
        if order_response.get('price'):
            output += f"Price:           {order_response.get('price', 'N/A')}\n"
        
        if order_response.get('avgPrice'):
            output += f"Average Price:   {order_response.get('avgPrice', 'N/A')}\n"
        
        output += f"Time in Force:   {order_response.get('timeInForce', 'N/A')}\n"
        output += f"Create Time:     {order_response.get('time', 'N/A')}\n"
        output += "="*60 + "\n"
        
        return output
