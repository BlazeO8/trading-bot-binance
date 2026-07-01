"""Input validation for trading bot"""

import logging
from typing import Optional
from decimal import Decimal, InvalidOperation

logger = logging.getLogger("trading_bot")


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class InputValidator:
    """Validates user input for trading orders"""
    
    VALID_SIDES = ["BUY", "SELL"]
    VALID_ORDER_TYPES = ["MARKET", "LIMIT"]
    
    @staticmethod
    def validate_symbol(symbol: str) -> str:
        """
        Validate trading symbol format.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            
        Returns:
            Validated symbol in uppercase
            
        Raises:
            ValidationError: If symbol is invalid
        """
        if not symbol:
            raise ValidationError("Symbol cannot be empty")
        
        symbol = symbol.upper().strip()
        
        if len(symbol) < 6:
            raise ValidationError(f"Symbol '{symbol}' is too short (minimum 6 characters)")
        
        if not symbol.isalnum():
            raise ValidationError(f"Symbol '{symbol}' contains invalid characters")
        
        logger.debug(f"Symbol validated: {symbol}")
        return symbol
    
    @staticmethod
    def validate_side(side: str) -> str:
        """
        Validate order side (BUY/SELL).
        
        Args:
            side: Order side
            
        Returns:
            Validated side in uppercase
            
        Raises:
            ValidationError: If side is invalid
        """
        if not side:
            raise ValidationError("Side cannot be empty")
        
        side = side.upper().strip()
        
        if side not in InputValidator.VALID_SIDES:
            raise ValidationError(
                f"Invalid side '{side}'. Must be one of: {', '.join(InputValidator.VALID_SIDES)}"
            )
        
        logger.debug(f"Side validated: {side}")
        return side
    
    @staticmethod
    def validate_order_type(order_type: str) -> str:
        """
        Validate order type (MARKET/LIMIT).
        
        Args:
            order_type: Order type
            
        Returns:
            Validated order type in uppercase
            
        Raises:
            ValidationError: If order type is invalid
        """
        if not order_type:
            raise ValidationError("Order type cannot be empty")
        
        order_type = order_type.upper().strip()
        
        if order_type not in InputValidator.VALID_ORDER_TYPES:
            raise ValidationError(
                f"Invalid order type '{order_type}'. Must be one of: {', '.join(InputValidator.VALID_ORDER_TYPES)}"
            )
        
        logger.debug(f"Order type validated: {order_type}")
        return order_type
    
    @staticmethod
    def validate_quantity(quantity: str) -> Decimal:
        """
        Validate order quantity.
        
        Args:
            quantity: Order quantity as string
            
        Returns:
            Validated quantity as Decimal
            
        Raises:
            ValidationError: If quantity is invalid
        """
        if not quantity:
            raise ValidationError("Quantity cannot be empty")
        
        try:
            qty = Decimal(quantity.strip())
        except InvalidOperation:
            raise ValidationError(f"Quantity '{quantity}' is not a valid number")
        
        if qty <= 0:
            raise ValidationError(f"Quantity must be greater than 0, got {qty}")
        
        logger.debug(f"Quantity validated: {qty}")
        return qty
    
    @staticmethod
    def validate_price(price: Optional[str], order_type: str) -> Optional[Decimal]:
        """
        Validate order price.
        
        Args:
            price: Order price as string (required for LIMIT orders)
            order_type: Order type (MARKET/LIMIT)
            
        Returns:
            price_decimal for LIMIT or None for MARKET
            
        Raises:
            ValidationError: If price validation fails
        """
        if order_type == "MARKET":
            logger.debug("MARKET order - price not required")
            return None
        
        if not price:
            raise ValidationError("Price is required for LIMIT orders")
        
        try:
            price_decimal = Decimal(price.strip())
        except InvalidOperation:
            raise ValidationError(f"Price '{price}' is not a valid number")
        
        if price_decimal <= 0:
            raise ValidationError(f"Price must be greater than 0, got {price_decimal}")
        
        logger.debug(f"Price validated: {price_decimal}")
        return price_decimal
