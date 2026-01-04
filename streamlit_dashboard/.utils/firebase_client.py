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

@st.cache_data(ttl=10)
def get_incidents():
    """Fetch all incidents from Firebase"""
    incidents = db.reference("incidents").get() or {}
    return list(incidents.values())

@st.cache_data(ttl=10)
def get_stats():
    """Fetch stats from Firebase"""
    return db.reference("stats").get() or {}

@st.cache_data(ttl=30)
def get_devices():
    """Fetch device status from Firebase"""
    return db.reference("devices").get() or {}

def update_incident_status(incident_id: str, status: str):
    """Update incident status"""
    db.reference(f"incidents/{incident_id}/status").set(status)