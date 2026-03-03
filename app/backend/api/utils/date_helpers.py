"""
Date and time helper utilities.
"""

from datetime import date, datetime, timedelta


def get_date_range(period="month", start_date=None, end_date=None):
    """
    Get date range for analysis.

    Args:
        period: 'week', 'month', 'quarter', 'year', or 'custom'
        start_date: Custom start date (for 'custom' period)
        end_date: Custom end date (for 'custom' period)

    Returns:
        Tuple of (start_date, end_date)
    """
    today = date.today()

    if period == "custom":
        if not start_date or not end_date:
            raise ValueError("start_date and end_date required for custom period")
        return (start_date, end_date)

    elif period == "week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return (start, end)

    elif period == "month":
        start = date(today.year, today.month, 1)
        if today.month == 12:
            end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        return (start, end)

    elif period == "quarter":
        quarter = (today.month - 1) // 3 + 1
        start = date(today.year, (quarter - 1) * 3 + 1, 1)
        end_month = quarter * 3
        if end_month == 12:
            end = date(today.year, 12, 31)
        else:
            end = date(today.year, end_month + 1, 1) - timedelta(days=1)
        return (start, end)

    elif period == "year":
        start = date(today.year, 1, 1)
        end = date(today.year, 12, 31)
        return (start, end)

    else:
        raise ValueError(f"Invalid period: {period}")


def get_previous_period(start_date, end_date):
    """
    Get the previous period with same duration.

    Args:
        start_date: Current period start
        end_date: Current period end

    Returns:
        Tuple of (previous_start, previous_end)
    """
    duration = (end_date - start_date).days
    previous_end = start_date - timedelta(days=1)
    previous_start = previous_end - timedelta(days=duration)
    return (previous_start, previous_end)


def parse_date_param(date_string):
    """
    Parse date string from API parameter.

    Args:
        date_string: Date string (YYYY-MM-DD)

    Returns:
        date object
    """
    if not date_string:
        return None

    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_string}. Use YYYY-MM-DD")


def format_period_label(date_obj, period="month"):
    """
    Format a date as a period label.

    Args:
        date_obj: Date to format
        period: 'day', 'week', 'month', 'year'

    Returns:
        Formatted string
    """
    if period == "day":
        return date_obj.strftime("%Y-%m-%d")
    elif period == "week":
        return date_obj.strftime("%Y-W%W")
    elif period == "month":
        return date_obj.strftime("%Y-%m")
    elif period == "year":
        return date_obj.strftime("%Y")
    else:
        return str(date_obj)
