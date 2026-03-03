"""
Formatting utilities for financial data.
"""


def format_currency(amount, currency_symbol="$", decimal_places=2):
    """
    Format amount as currency.

    Args:
        amount: Numeric amount
        currency_symbol: Currency symbol to use
        decimal_places: Number of decimal places

    Returns:
        Formatted string (e.g., "$1,234.56")
    """
    formatted = f"{abs(float(amount)):,.{decimal_places}f}"

    if amount < 0:
        return f"-{currency_symbol}{formatted}"
    else:
        return f"{currency_symbol}{formatted}"


def format_percentage(value, decimal_places=2):
    """
    Format value as percentage.

    Args:
        value: Numeric value (0-100)
        decimal_places: Number of decimal places

    Returns:
        Formatted string (e.g., "45.67%")
    """
    return f"{float(value):.{decimal_places}f}%"


def format_change(current, previous):
    """
    Calculate and format change between two values.

    Args:
        current: Current value
        previous: Previous value

    Returns:
        Dictionary with change amount, percentage, and direction
    """
    if previous == 0:
        return {
            "amount": current,
            "percentage": None,
            "direction": "up" if current > 0 else "down" if current < 0 else "same",
        }

    change = current - previous
    percentage = (change / abs(previous)) * 100

    return {
        "amount": change,
        "percentage": percentage,
        "direction": "up" if change > 0 else "down" if change < 0 else "same",
    }


def format_number_abbreviated(number):
    """
    Format large numbers with abbreviations.

    Args:
        number: Numeric value

    Returns:
        Abbreviated string (e.g., "1.2K", "3.4M")
    """
    number = abs(float(number))

    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return f"{number:.0f}"
