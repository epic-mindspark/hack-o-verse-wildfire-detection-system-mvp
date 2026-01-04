from datetime import datetime, timedelta, timezone
# IST is UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))
def format_timestamp(timestamp) -> str:
    """Format millisecond timestamp to readable format in IST"""
    if not timestamp:
        return "N/A"
    try:
        if isinstance(timestamp, (int, float)):
            # Convert milliseconds to seconds
            if timestamp > 1e12:
                timestamp = timestamp / 1000
            # Create UTC datetime, then convert to IST
            dt_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            dt_ist = dt_utc.astimezone(IST)
            return dt_ist.strftime("%b %d, %Y %I:%M:%S %p IST")
        return str(timestamp)
    except:
        return "N/A"
def get_severity_color(severity: str) -> str:
    """Get color for severity level"""
    colors = {
        "CRITICAL": "#FF0000",
        "HIGH": "#FF6600",
        "MEDIUM": "#FFCC00",
        "LOW": "#00CC00"
    }
    return colors.get(severity.upper() if severity else "", "#888888")
def get_severity_emoji(severity: str) -> str:
    """Get emoji for severity level"""
    emojis = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🟢"
    }
    return emojis.get(severity.upper() if severity else "", "⚪")
def format_value(value, unit: str = "", decimals: int = 1) -> str:
    """Format sensor value with unit"""
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, float)):
        if decimals == 0:
            return f"{int(value)}{unit}"
        return f"{value:.{decimals}f}{unit}"
    return str(value)