"""
🔥 Wildfire Detection Dashboard
"""

import streamlit as st
from utils.firebase_client import init_firebase, get_incidents, get_stats, get_devices
from utils.helpers import format_timestamp, get_severity_emoji, get_severity_color, format_value
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="🔥 Wildfire Detection Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ GOOGLE MAPS API KEY ============
GOOGLE_MAPS_API_KEY = st.secrets.get("GOOGLE_MAPS_API_KEY", "")

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
    
    # Filters
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
    
    # Quick Stats
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

# ============ GOOGLE MAPS FUNCTION ============
def create_google_map(incidents_list, api_key, height=450):
    """Create Google Map with incident markers"""
    
    # Filter incidents with valid coordinates
    valid_incidents = [i for i in incidents_list if i.get("latitude", 0) != 0 and i.get("longitude", 0) != 0]
    
    if not valid_incidents:
        return None
    
    # Center map on first incident or default location
    center_lat = valid_incidents[0]["latitude"] if valid_incidents else 18.4636
    center_lng = valid_incidents[0]["longitude"] if valid_incidents else 73.8682
    
    # Marker colors based on severity
    severity_colors = {
        "CRITICAL": "red",
        "HIGH": "orange", 
        "MEDIUM": "yellow",
        "LOW": "green"
    }
    
    # Create markers JavaScript
    markers_js = ""
    for inc in valid_incidents:
        lat = inc.get("latitude", 0)
        lng = inc.get("longitude", 0)
        severity = inc.get("severity", "UNKNOWN")
        color = severity_colors.get(severity, "blue")
        device = inc.get("device_id", "Unknown")
        time = format_timestamp(inc.get("timestamp"))
        status = inc.get("status", "unknown").replace("_", " ").title()
        
        # Icon URL based on severity
        icon_url = f"http://maps.google.com/mapfiles/ms/icons/{color}-dot.png"
        
        markers_js += f"""
        new google.maps.Marker({{
            position: {{ lat: {lat}, lng: {lng} }},
            map: map,
            icon: "{icon_url}",
            title: "{severity} - {device}"
        }}).addListener('click', function() {{
            new google.maps.InfoWindow({{
                content: `
                    <div style="font-family: Arial; padding: 5px;">
                        <h3 style="color: {color}; margin: 0 0 10px 0;">🔥 {severity} Alert</h3>
                        <p><b>Device:</b> {device}</p>
                        <p><b>Time:</b> {time}</p>
                        <p><b>Status:</b> {status}</p>
                        <p><b>Location:</b> {lat:.4f}°N, {lng:.4f}°E</p>
                    </div>
                `
            }}).open(map, this);
        }});
        """
    
    # Complete HTML with Google Maps
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            #map {{
                height: {height}px;
                width: 100%;
                border-radius: 10px;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            function initMap() {{
                const map = new google.maps.Map(document.getElementById("map"), {{
                    zoom: 12,
                    center: {{ lat: {center_lat}, lng: {center_lng} }},
                    mapTypeId: "terrain",
                    styles: [
                        {{
                            featureType: "poi",
                            elementType: "labels",
                            stylers: [{{ visibility: "off" }}]
                        }}
                    ]
                }});
                
                {markers_js}
                
                // Add legend
                const legend = document.createElement('div');
                legend.innerHTML = `
                    <div style="background: white; padding: 10px; margin: 10px; border-radius: 5px; box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
                        <b>Severity</b><br>
                        <span style="color: red;">●</span> Critical<br>
                        <span style="color: orange;">●</span> High<br>
                        <span style="color: yellow;">●</span> Medium<br>
                        <span style="color: green;">●</span> Low
                    </div>
                `;
                map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(legend);
            }}
        </script>
        <script async defer src="https://maps.googleapis.com/maps/api/js?key={api_key}&callback=initMap"></script>
    </body>
    </html>
    """
    return html

# ============ MAP & RECENT INCIDENTS ============
map_col, list_col = st.columns([3, 2])

with map_col:
    st.subheader("🗺️ Incident Map")
    
    if GOOGLE_MAPS_API_KEY:
        map_html = create_google_map(filtered_incidents, GOOGLE_MAPS_API_KEY)
        if map_html:
            st.components.v1.html(map_html, height=470)
        else:
            st.info("📍 No incidents with valid coordinates to display")
    else:
        st.warning("⚠️ Google Maps API key not found. Add GOOGLE_MAPS_API_KEY to secrets.")
        
        # Fallback to simple map display
        map_incidents = [i for i in filtered_incidents if i.get("latitude", 0) != 0]
        if map_incidents:
            st.markdown("**Incident Locations:**")
            for inc in map_incidents[:5]:
                emoji = get_severity_emoji(inc.get("severity", ""))
                st.write(f"{emoji} {inc.get('latitude', 0):.4f}°N, {inc.get('longitude', 0):.4f}°E - {inc.get('severity', 'Unknown')}")

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
        st.info("No data for chart")

with chart_col2:
    st.markdown("#### Incidents Timeline")
    
    if incidents:
        df = pd.DataFrame(incidents)
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
        st.info("No data for chart")

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
    device_cols = st.columns(len(devices))
    
    for idx, (device_id, device) in enumerate(devices.items()):
        with device_cols[idx]:
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
st.caption(f"🔥 Wildfire Detection System | Last refreshed: {datetime.now().strftime('%I:%M:%S %p IST')} | GDG Hack-O-Verse MVP")