from datetime import datetime, timedelta, timezone
# IST Timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))
def format_timestamp(timestamp) -> str:
    """Format millisecond timestamp to IST"""
    if not timestamp:
        return "N/A"
    try:
        if isinstance(timestamp, (int, float)):
            if timestamp > 1e12:
                timestamp = timestamp / 1000
            dt_utc = datetime.utcfromtimestamp(timestamp)
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
            dt_ist = dt_utc.astimezone(IST)
            return dt_ist.strftime("%b %d, %Y %I:%M:%S %p IST")
        return str(timestamp)
    except:
        return "N/A"
def get_current_time_ist() -> str:
    """Get current time in IST"""
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc.astimezone(IST)
    return now_ist.strftime("%I:%M:%S %p IST")
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