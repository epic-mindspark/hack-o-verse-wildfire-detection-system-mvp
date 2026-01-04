import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json
@st.cache_resource
def init_firebase():
    """Initialize Firebase connection"""
    if not firebase_admin._apps:
        cred_dict = json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://gdg-wildfire-detection-mvp-default-rtdb.asia-southeast1.firebasedatabase.app"
        })
    return True
def safe_get(data, *keys, default=None):
    """Safely get nested dictionary values"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return default
        if data is None:
            return default
    return data
@st.cache_data(ttl=5)
def get_incidents():
    """Fetch all incidents from Firebase"""
    raw_incidents = db.reference("incidents").get() or {}
    
    incidents = []
    for incident_id, data in raw_incidents.items():
        # Skip placeholder and template entries
        if incident_id.startswith("_") or incident_id.startswith("{"):
            continue
        
        incident = {
            "id": incident_id,
            "device_id": data.get("device_id", "Unknown"),
            "timestamp": data.get("timestamp", 0),
            "status": data.get("status", "unknown"),
            
            # Location
            "latitude": safe_get(data, "location", "latitude", default=0),
            "longitude": safe_get(data, "location", "longitude", default=0),
            
            # Sensors
            "temperature": safe_get(data, "sensors", "temperature"),
            "humidity": safe_get(data, "sensors", "humidity"),
            "gas_level": safe_get(data, "sensors", "gas_level"),
            "flame_detected": safe_get(data, "sensors", "flame_detected", default=False),
            
            # Detection
            "fire_detected": safe_get(data, "detection", "fire_detected", default=False),
            "smoke_detected": safe_get(data, "detection", "smoke_detected", default=False),
            "confidence": safe_get(data, "detection", "confidence", default=0),
            "detections": safe_get(data, "detection", "detections", default=[]),
            
            # Analysis
            "severity": safe_get(data, "analysis", "severity", default="UNKNOWN"),
            "summary": safe_get(data, "analysis", "summary", default=""),
            "action": safe_get(data, "analysis", "action", default=""),
            
            # Images
            "original_url": safe_get(data, "images", "original_url", default=""),
            "annotated_url": safe_get(data, "images", "annotated_url", default=""),
        }
        incidents.append(incident)
    
    # Sort by timestamp descending
    incidents.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    return incidents
@st.cache_data(ttl=5)
def get_stats():
    """Get stats from Firebase"""
    return db.reference("stats").get() or {
        "total_incidents": 0,
        "critical_count": 0,
        "high_count": 0,
        "medium_count": 0,
        "low_count": 0,
        "last_detection": None
    }
@st.cache_data(ttl=10)
def get_devices():
    """Get devices from Firebase"""
    raw_devices = db.reference("devices").get() or {}
    
    devices = {}
    for device_id, data in raw_devices.items():
        devices[device_id] = {
            "name": data.get("name", device_id),
            "status": data.get("status", "unknown"),
            "last_seen": data.get("last_seen", 0),
            "latitude": safe_get(data, "location", "latitude", default=0),
            "longitude": safe_get(data, "location", "longitude", default=0),
            "battery": data.get("battery_percent"),
            "solar_charging": data.get("solar_charging"),
            "signal_strength": data.get("signal_strength"),
        }
    
    return devices