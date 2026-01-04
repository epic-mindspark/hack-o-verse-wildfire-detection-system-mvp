from datetime import datetime

def format_timestamp(timestamp_str: str) -> str:
    """Format ISO timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y %H:%M")
    except: 
        return timestamp_str

def get_severity_color(severity: str) -> str:
    """Get color code for severity level"""
    colors = {
        "CRITICAL": "#FF0000",
        "HIGH": "#FF6600",
        "MEDIUM": "#FFCC00",
        "LOW": "#00CC00"
    }
    return colors.get(severity, "#888888")

def get_severity_emoji(severity: str) -> str:
    """Get emoji for severity level"""
    emojis = {
        "CRITICAL":  "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🟢"
    }
    return emojis.get(severity, "⚪")