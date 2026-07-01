"""Input validation helpers for order requests.

Kept separate from the CLI and the API client so validation rules can be
unit-tested in isolation and reused if a different front-end (e.g. a UI)
is added later.
"""
import re

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


class ValidationError(ValueError):
    """Raised when CLI input fails validation."""


def validate_symbol(symbol: str) -> str:
    if symbol is None:
        raise ValidationError("Symbol is required.")
    symbol = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Expected a format like 'BTCUSDT'."
        )
    return symbol


def validate_side(side: str) -> str:
    if side is None:
        raise ValidationError("Side is required.")
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be one of {sorted(VALID_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    if order_type is None:
        raise ValidationError("Order type is required.")
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of {sorted(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity) -> float:
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than 0.")
    return quantity


def validate_price(price, order_type: str):
    """Price is required for LIMIT and STOP_LIMIT orders, must be > 0.

    Returns None for MARKET orders (price is not applicable).
    """
    if order_type not in ("LIMIT", "STOP_LIMIT"):
        return None
    if price is None:
        raise ValidationError(f"price is required for {order_type} orders.")
    try:
        price = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"price must be a number, got '{price}'.")
    if price <= 0:
        raise ValidationError("price must be greater than 0.")
    return price


def validate_stop_price(stop_price, order_type: str):
    """stop_price is required only for STOP_LIMIT orders, must be > 0."""
    if order_type != "STOP_LIMIT":
        return None
    if stop_price is None:
        raise ValidationError("stop_price is required for STOP_LIMIT orders.")
    try:
        stop_price = float(stop_price)
    except (TypeError, ValueError):
        raise ValidationError(f"stop_price must be a number, got '{stop_price}'.")
    if stop_price <= 0:
        raise ValidationError("stop_price must be greater than 0.")
    return stop_price
