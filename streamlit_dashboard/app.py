"""
🔥 Wildfire Detection Dashboard - Main Page
"""
import streamlit as st
from utils import init_firebase, get_incidents, get_stats, get_devices
from utils.helpers import get_severity_emoji, format_timestamp
import pandas as pd
import plotly.express as px
# Page config
st.set_page_config(
    page_title="🔥 Wildfire Detection",
    page_icon="🔥",
    layout="wide"
)
# Initialize Firebase
init_firebase()
# Load data
incidents = get_incidents()
stats = get_stats()
devices = get_devices()
# ========== HEADER ==========
st.title("🔥 Wildfire Detection Dashboard")
st.markdown("Real-time monitoring and incident management")
# ========== METRICS ==========
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Incidents", stats.get("total_incidents", 0))
with col2:
    critical = len([i for i in incidents if i.get("severity") == "CRITICAL"])
    st.metric("🚨 Critical", critical)
with col3:
    active = len([i for i in incidents if i.get("status") == "active"])
    st.metric("🔴 Active", active)
with col4:
    st.metric("📡 Devices", len(devices))
st.markdown("---")
# ========== MAP ==========
st.subheader("🗺️ Incident Map")
if incidents:
    map_data = pd.DataFrame([
        {
            "lat": i.get("latitude", 0),
            "lon": i.get("longitude", 0),
            "severity": i.get("severity", "UNKNOWN")
        }
        for i in incidents
        if i.get("latitude") and i.get("longitude")
    ])
    
    if not map_data.empty:
        fig = px.scatter_mapbox(
            map_data,
            lat="lat",
            lon="lon",
            color="severity",
            color_discrete_map={
                "CRITICAL": "#FF0000",
                "HIGH": "#FF6600",
                "MEDIUM": "#FFCC00",
                "LOW": "#00CC00"
            },
            zoom=5,
            height=500
        )
        fig.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No incidents to display")
# ========== RECENT INCIDENTS ==========
st.subheader("📋 Recent Incidents")
if incidents:
    sorted_incidents = sorted(incidents, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]
    
    for inc in sorted_incidents: 
        emoji = get_severity_emoji(inc.get("severity", ""))
        with st.expander(f"{emoji} {inc.get('id', 'Unknown')[:12]}... - {inc.get('severity')}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Time:** {format_timestamp(inc.get('timestamp', ''))}")
                st.write(f"**Location:** {inc.get('latitude', 0):.4f}, {inc.get('longitude', 0):.4f}")
                st.write(f"**Device:** {inc.get('device_id', 'Unknown')}")
            with col2:
                st.write(f"**Temperature:** {inc.get('temperature', 'N/A')}°C")
                st.write(f"**Smoke Level:** {inc.get('smoke_level', 'N/A')}")
                st.write(f"**Status:** {inc.get('status', 'Unknown')}")
            
            st.markdown(f"**AI Assessment:** {inc.get('ai_assessment', 'N/A')}")
            
            if inc.get("annotated_image"):
                st.image(inc["annotated_image"], caption="Detection", width=400)
else:
    st.info("No incidents recorded yet")
# ========== SIDEBAR ==========
with st.sidebar:
    st.title("🔥 Wildfire Detection")
    st.markdown("---")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Quick Stats**")
    st.write(f"Last detection: {stats.get('last_detection', 'Never')[:10] if stats.get('last_detection') else 'Never'}")