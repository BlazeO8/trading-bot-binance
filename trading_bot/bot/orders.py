"""Order management and execution logic"""

import logging
from typing import Dict, Any, Optional
from .client import BinanceFuturesTestnetClient
from .validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
    ValidationError
)
from .logging_config import get_logger

logger = get_logger(__name__)


class OrderRequest:
    """Represents a validated trading order request."""
    
    def __init__(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ):
        self.symbol = symbol
        self.side = side
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.stop_price = stop_price
    
    @classmethod
    def build(
        cls,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: Optional[str] = None,
        stop_price: Optional[str] = None
    ) -> "OrderRequest":
        """Build and validate an order request from CLI inputs."""
        validated_symbol = validate_symbol(symbol)
        validated_side = validate_side(side)
        validated_order_type = validate_order_type(order_type)
        validated_quantity = validate_quantity(quantity)
        validated_price = validate_price(price, validated_order_type)
        validated_stop_price = validate_stop_price(stop_price, validated_order_type)
        
        logger.debug(
            f"Built order: {validated_symbol} {validated_side} "
            f"{validated_quantity} {validated_order_type}"
        )
        
        return cls(
            symbol=validated_symbol,
            side=validated_side,
            order_type=validated_order_type,
            quantity=validated_quantity,
            price=validated_price,
            stop_price=validated_stop_price
        )
    
    def summary(self) -> str:
        """Return a human-readable order summary."""
        parts = [
            f"{self.side} {self.quantity} {self.symbol} ({self.order_type})"
        ]
        if self.price:
            parts.append(f"price={self.price}")
        if self.stop_price:
            parts.append(f"stop_price={self.stop_price}")
        return " | ".join(parts)


class OrderService:
    """Service for placing orders on Binance Futures Testnet."""
    
    def __init__(self):
        self.client = BinanceFuturesTestnetClient()
    
    def place_order(self, order: OrderRequest) -> Dict[str, Any]:
        """Place an order on Binance Futures Testnet."""
        params = {
            'symbol': order.symbol,
            'side': order.side,
            'type': order.order_type,
            'quantity': order.quantity
        }
        
        if order.order_type == "LIMIT":
            params['price'] = order.price
            params['timeInForce'] = 'GTC'  # Good Till Cancel
        
        if order.order_type == "STOP_LIMIT":
            params['price'] = order.price
            params['stopPrice'] = order.stop_price
            params['timeInForce'] = 'GTC'
        
        logger.info(f"Placing order with params: {params}")
        response = self.client.create_order(**params)
        logger.info(f"Order placed successfully: {response}")
        return response
    
    @staticmethod
    def format_response(response: Dict[str, Any]) -> str:
        """Format the order response for display."""
        output = "\n" + "="*60 + "\n"
        output += f"Order ID:        {response.get('orderId', 'N/A')}\n"
        output += f"Symbol:          {response.get('symbol', 'N/A')}\n"
        output += f"Side:            {response.get('side', 'N/A')}\n"
        output += f"Order Type:      {response.get('type', 'N/A')}\n"
        output += f"Status:          {response.get('status', 'N/A')}\n"
        output += f"Quantity:        {response.get('origQty', 'N/A')}\n"
        output += f"Executed Qty:    {response.get('executedQty', 'N/A')}\n"
        
        if response.get('price'):
            output += f"Price:           {response.get('price', 'N/A')}\n"
        
        if response.get('stopPrice'):
            output += f"Stop Price:      {response.get('stopPrice', 'N/A')}\n"
        
        if response.get('avgPrice') and float(response.get('avgPrice', 0)) > 0:
            output += f"Average Price:   {response.get('avgPrice', 'N/A')}\n"
        
        output += f"Time in Force:   {response.get('timeInForce', 'N/A')}\n"
        output += f"Create Time:     {response.get('time', 'N/A')}\n"
        output += "="*60 + "\n"
        
        return output
