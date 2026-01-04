"""
🔥 Wildfire Detection Dashboard
"""

import streamlit as st
from utils.firebase_client import init_firebase, get_incidents, get_stats, get_devices
from utils.helpers import format_timestamp, get_severity_emoji, format_value, get_current_time_ist
import pandas as pd
import plotly.express as px

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="🔥 Wildfire Detection Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ INIT ============
init_firebase()

# ============ LOAD DATA ============
incidents = get_incidents()
stats = get_stats()
devices = get_devices()

# ============ SIDEBAR ============
with st.sidebar:
    st.title("🔥 Wildfire Detection")
    st.caption("Real-time Monitoring System")
    
    st.markdown("---")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    st.subheader("🔍 Filters")
    severity_filter = st.multiselect(
        "Severity Level",
        ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        default=["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    )
    
    status_filter = st.selectbox(
        "Status",
        ["All", "Confirmed", "False Alarm"]
    )
    
    st.markdown("---")
    
    st.subheader("📊 Quick Stats")
    st.metric("Total Incidents", stats.get("total_incidents", 0))
    
    last_det = stats.get("last_detection")
    st.caption(f"Last: {format_timestamp(last_det) if last_det else 'Never'}")

# ============ HEADER ============
st.title("🔥 Wildfire Detection Dashboard")
st.markdown("Real-time monitoring and incident management")

# ============ METRICS ROW ============
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📊 Total", stats.get("total_incidents", 0))
with col2:
    st.metric("🔴 Critical", stats.get("critical_count", 0))
with col3:
    st.metric("🟠 High", stats.get("high_count", 0))
with col4:
    st.metric("🟡 Medium", stats.get("medium_count", 0))
with col5:
    st.metric("🟢 Low", stats.get("low_count", 0))

st.markdown("---")

# ============ FILTER INCIDENTS ============
filtered_incidents = incidents

if severity_filter:
    filtered_incidents = [i for i in filtered_incidents if i.get("severity", "").upper() in severity_filter]

if status_filter == "Confirmed":
    filtered_incidents = [i for i in filtered_incidents if i.get("status") == "confirmed"]
elif status_filter == "False Alarm":
    filtered_incidents = [i for i in filtered_incidents if i.get("status") == "false_alarm"]

# ============ MAP & RECENT INCIDENTS ============
map_col, list_col = st.columns([3, 2])

with map_col:
    st.subheader("🗺️ Incident Map")
    
    # Get valid incidents with coordinates
    valid_incidents = [
        i for i in filtered_incidents 
        if i.get("latitude", 0) != 0 and i.get("longitude", 0) != 0
    ]
    
    if valid_incidents:
        # Use first incident as center, or default to Pune
        center_lat = valid_incidents[0]["latitude"]
        center_lng = valid_incidents[0]["longitude"]
        
        # Build markers parameter for Google Maps Static/Embed
        # Using Google Maps Embed API with place
        api_key = st.secrets.get("GOOGLE_MAPS_API_KEY", "")
        
        if api_key:
            # Create markers string for all incidents
            markers_param = ""
            for inc in valid_incidents:
                severity = inc.get("severity", "UNKNOWN")
                color_map = {"CRITICAL": "red", "HIGH": "orange", "MEDIUM": "yellow", "LOW": "green"}
                color = color_map.get(severity, "red")
                lat = inc.get("latitude")
                lng = inc.get("longitude")
                markers_param += f"&markers=color:{color}%7C{lat},{lng}"
            
            # Google Maps Static API URL
            map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={center_lat},{center_lng}&zoom=13&size=600x400&maptype=terrain{markers_param}&key={api_key}"
            
            # Display static map image
            st.image(map_url, use_container_width=True)
            
            # Add clickable link to open in Google Maps
            google_maps_link = f"https://www.google.com/maps?q={center_lat},{center_lng}&z=13"
            st.markdown(f"[🔗 Open in Google Maps]({google_maps_link})")
            
            # Legend
            st.markdown("""
            **Legend:** 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low
            """)
        else:
            st.error("⚠️ Google Maps API key not found in secrets!")
    else:
        st.info("📍 No incidents with valid coordinates to display")

with list_col:
    st.subheader("📋 Recent Incidents")
    
    if filtered_incidents:
        for inc in filtered_incidents[:5]:
            severity = inc.get("severity", "UNKNOWN")
            emoji = get_severity_emoji(severity)
            status = inc.get("status", "unknown")
            status_icon = "🔥" if status == "confirmed" else "✅"
            
            with st.expander(f"{emoji} {format_timestamp(inc.get('timestamp'))} - {severity}"):
                st.markdown(f"""
**Status:** {status_icon} {status.replace("_", " ").title()}

**🔍 Detection:**
- Fire: {"✅" if inc.get("fire_detected") else "❌"} | Smoke: {"✅" if inc.get("smoke_detected") else "❌"}
- Confidence: {format_value(inc.get("confidence", 0) * 100, "%")}

**🌡️ Sensors:**
- Temp: {format_value(inc.get("temperature"), "°C")} | Humidity: {format_value(inc.get("humidity"), "%")}
- Gas: {format_value(inc.get("gas_level"), " ppm", 0)}

**🤖 AI Assessment:**
{inc.get("summary", "N/A")}

**⚡ Action:**
{inc.get("action", "N/A")}
""")
                
                if inc.get("annotated_url"):
                    st.image(inc["annotated_url"], caption="Detection Result", use_container_width=True)
    else:
        st.info("No incidents match the current filters")

st.markdown("---")

# ============ CHARTS ============
st.subheader("📈 Analytics")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### Severity Distribution")
    
    severity_data = {
        "CRITICAL": stats.get("critical_count", 0),
        "HIGH": stats.get("high_count", 0),
        "MEDIUM": stats.get("medium_count", 0),
        "LOW": stats.get("low_count", 0)
    }
    
    severity_data = {k: v for k, v in severity_data.items() if v > 0}
    
    if severity_data:
        fig = px.pie(
            values=list(severity_data.values()),
            names=list(severity_data.keys()),
            color=list(severity_data.keys()),
            color_discrete_map={
                "CRITICAL": "#FF0000",
                "HIGH": "#FF6600",
                "MEDIUM": "#FFCC00",
                "LOW": "#00CC00"
            },
            hole=0.4
        )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for severity chart")

with chart_col2:
    st.markdown("#### Incidents Timeline")
    
    if incidents:
        df = pd.DataFrame(incidents)
        if "timestamp" in df.columns and len(df) > 0:
            df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date
            daily_counts = df.groupby("date").size().reset_index(name="count")
            
            if len(daily_counts) > 0:
                fig = px.bar(
                    daily_counts,
                    x="date",
                    y="count",
                    color_discrete_sequence=["#FF6B35"]
                )
                fig.update_layout(
                    margin={"r": 0, "t": 0, "l": 0, "b": 0},
                    height=300,
                    xaxis_title="Date",
                    yaxis_title="Incidents"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data for timeline")
        else:
            st.info("No timestamp data")
    else:
        st.info("No data for timeline chart")

st.markdown("---")

# ============ LATEST DETECTION DETAIL ============
if filtered_incidents:
    st.subheader("🔥 Latest Detection Details")
    
    latest = filtered_incidents[0]
    
    detail_col1, detail_col2, detail_col3 = st.columns([1, 1, 1])
    
    with detail_col1:
        st.markdown("#### 📍 Location & Time")
        st.write(f"**Coordinates:** {latest.get('latitude', 0):.4f}°N, {latest.get('longitude', 0):.4f}°E")
        st.write(f"**Time:** {format_timestamp(latest.get('timestamp'))}")
        st.write(f"**Device:** {latest.get('device_id', 'Unknown')}")
        st.write(f"**Status:** {latest.get('status', 'Unknown').replace('_', ' ').title()}")
    
    with detail_col2:
        st.markdown("#### 🌡️ Sensor Data")
        st.write(f"**Temperature:** {format_value(latest.get('temperature'), '°C')}")
        st.write(f"**Humidity:** {format_value(latest.get('humidity'), '%')}")
        st.write(f"**Gas Level:** {format_value(latest.get('gas_level'), ' ppm', 0)}")
        st.write(f"**Flame Sensor:** {format_value(latest.get('flame_detected'))}")
    
    with detail_col3:
        st.markdown("#### 🤖 AI Analysis")
        severity = latest.get("severity", "UNKNOWN")
        emoji = get_severity_emoji(severity)
        st.write(f"**Severity:** {emoji} {severity}")
        st.write(f"**Confidence:** {format_value(latest.get('confidence', 0) * 100, '%')}")
    
    # Images
    img_col1, img_col2 = st.columns(2)
    
    with img_col1:
        if latest.get("original_url"):
            st.markdown("#### 📷 Original Image")
            st.image(latest["original_url"], use_container_width=True)
    
    with img_col2:
        if latest.get("annotated_url"):
            st.markdown("#### 🎯 Detection Result")
            st.image(latest["annotated_url"], use_container_width=True)
    
    # Full Analysis
    st.markdown("#### 📝 Full Analysis")
    st.info(f"**Summary:** {latest.get('summary', 'N/A')}")
    st.warning(f"**Recommended Action:** {latest.get('action', 'N/A')}")

st.markdown("---")

# ============ DEVICES ============
st.subheader("📡 Device Status")

if devices:
    device_cols = st.columns(min(len(devices), 4))
    
    for idx, (device_id, device) in enumerate(devices.items()):
        with device_cols[idx % 4]:
            status = device.get("status", "unknown")
            status_color = "🟢" if status == "online" else "🔴"
            
            st.markdown(f"""
**{status_color} {device.get('name', device_id)}**
- Status: {status.title()}
- Last Seen: {format_timestamp(device.get('last_seen'))}
- Location: {device.get('latitude', 0):.2f}°N, {device.get('longitude', 0):.2f}°E
""")
            
            if device.get("battery"):
                st.progress(device["battery"] / 100, text=f"🔋 {device['battery']}%")
else:
    st.info("No devices registered")

# ============ FOOTER ============
st.markdown("---")
st.caption(f"🔥 Wildfire Detection System | Last refreshed: {get_current_time_ist()} | GDG Hack-O-Verse MVP")