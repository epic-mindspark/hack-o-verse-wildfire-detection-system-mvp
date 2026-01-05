"""
🔥 Wildfire Detection - Gradio App
Simulates ESP32 uploading image → YOLO Detection → Gemini Analysis → Firebase
"""

import os
import json
import time
import gradio as gr
import firebase_admin
from firebase_admin import credentials, db, storage
from PIL import Image
import io
import base64
from datetime import datetime
from ultralytics import YOLO
import google.generativeai as genai
import numpy as np

# ============ CONFIGURATION ============
FIREBASE_DB_URL = "https://gdg-wildfire-detection-mvp-default-rtdb.asia-southeast1.firebasedatabase.app"
FIREBASE_BUCKET = "gdg-wildfire-detection-mvp.firebasestorage.app"

# Default location - Pune, India
DEFAULT_LATITUDE = 18.4636
DEFAULT_LONGITUDE = 73.8682

# Demo sensor readings
DEFAULT_SENSORS = {
    "temperature": 47.5,
    "humidity": 18.2,
    "gas_level": 485,
    "flame_detected": True
}

# ============ INITIALIZE SERVICES ============

# Firebase
firebase_creds = json.loads(os.environ.get("FIREBASE_SERVICE_ACCOUNT", "{}"))
if firebase_creds and not firebase_admin._apps:
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {
        "databaseURL": FIREBASE_DB_URL,
        "storageBucket": FIREBASE_BUCKET
    })

# Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# YOLO Model
model = YOLO("fire_n.pt")  # Your trained wildfire model

# ============ CORE FUNCTIONS ============

def upload_image_to_storage(image: Image.Image, incident_id: str) -> tuple:
    """Upload original image to Firebase Storage and return URL"""
    try: 
        bucket = storage.bucket()
        
        # Convert PIL Image to bytes
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)
        
        # Upload original
        original_path = f"incidents/{incident_id}/original.jpg"
        blob = bucket.blob(original_path)
        blob.upload_from_file(buffer, content_type="image/jpeg")
        blob.make_public()
        original_url = blob.public_url
        
        return original_url
    except Exception as e:
        print(f"Storage upload error: {e}")
        return ""


def upload_annotated_image(image_array: np.ndarray, incident_id: str) -> str:
    """Upload annotated image to Firebase Storage"""
    try:
        bucket = storage.bucket()
        
        # Convert numpy array to PIL Image to bytes
        img = Image.fromarray(image_array)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)
        
        # Upload annotated
        annotated_path = f"incidents/{incident_id}/annotated.jpg"
        blob = bucket.blob(annotated_path)
        blob.upload_from_file(buffer, content_type="image/jpeg")
        blob.make_public()
        
        return blob.public_url
    except Exception as e:
        print(f"Annotated upload error: {e}")
        return ""


def run_yolo_detection(image: Image.Image) -> tuple:
    """Run YOLO detection on image"""
    results = model(image)
    
    detections = []
    fire_detected = False
    smoke_detected = False
    max_confidence = 0.0
    
    for result in results:
        boxes = result.boxes
        for box in boxes: 
            class_name = result.names[int(box.cls[0])].lower()
            confidence = float(box.conf[0])
            
            detection = {
                "class": class_name,
                "confidence": round(confidence, 3),
                "bbox": [round(x, 1) for x in box.xyxy[0].tolist()]
            }
            detections.append(detection)
            
            if "fire" in class_name: 
                fire_detected = True
            if "smoke" in class_name: 
                smoke_detected = True
            if confidence > max_confidence:
                max_confidence = confidence
    
    # Get annotated image
    annotated = results[0].plot()
    
    detection_result = {
        "fire_detected": fire_detected,
        "smoke_detected": smoke_detected,
        "confidence": round(max_confidence, 3),
        "detections": detections
    }
    
    return detection_result, annotated


def analyze_with_gemini(detection_result: dict, sensors: dict) -> dict:
    """Get Gemini analysis of the situation"""
    
    # If no fire/smoke detected, return low severity
    if not detection_result["fire_detected"] and not detection_result["smoke_detected"]:
        return {
            "severity": "LOW",
            "summary": "No fire or smoke detected in the image. Area appears safe.",
            "action": "Continue routine monitoring. No immediate action required."
        }
    
    prompt = f"""
    You are a wildfire emergency assessment AI. Analyze this detection data and provide an emergency assessment. 
    
    DETECTION RESULTS:
    - Fire Detected: {detection_result['fire_detected']}
    - Smoke Detected: {detection_result['smoke_detected']}
    - Detection Confidence: {detection_result['confidence'] * 100:.1f}%
    - Number of detections: {len(detection_result['detections'])}
    
    SENSOR DATA:
    - Temperature: {sensors.get('temperature', 'N/A')}°C
    - Humidity: {sensors.get('humidity', 'N/A')}%
    - Gas Level: {sensors.get('gas_level', 'N/A')} ppm
    - Flame Sensor: {'Triggered' if sensors.get('flame_detected') else 'Normal'}
    
    Based on this data, provide: 
    1. Severity level: Must be exactly one of: LOW, MEDIUM, HIGH, CRITICAL
    2. Summary: 2-3 sentence assessment of the situation
    3. Action: Specific recommended action for emergency responders
    
    Respond ONLY with valid JSON in this exact format:
    {{"severity": "HIGH", "summary": "Your assessment here", "action": "Your recommended action here"}}
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        text = response.text.strip()
        
        # Extract JSON from response
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        result = json.loads(text.strip())
        
        # Validate severity
        if result.get("severity") not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            result["severity"] = "MEDIUM"
        
        return result
    except Exception as e:
        print(f"Gemini error: {e}")
        # Default response based on detection
        severity = "HIGH" if detection_result["fire_detected"] else "MEDIUM"
        return {
            "severity": severity,
            "summary": f"{'Fire' if detection_result['fire_detected'] else 'Smoke'} detected with {detection_result['confidence']*100:.1f}% confidence. Manual review recommended.",
            "action": "Dispatch emergency response team for visual confirmation and assessment."
        }


def update_stats(severity: str):
    """Update global stats in Firebase"""
    try:
        stats_ref = db.reference("stats")
        stats = stats_ref.get() or {}
        
        stats["total_incidents"] = stats.get("total_incidents", 0) + 1
        stats["last_detection"] = int(datetime.now().timestamp() * 1000)
        
        severity_key = f"{severity.lower()}_count"
        stats[severity_key] = stats.get(severity_key, 0) + 1
        
        stats_ref.set(stats)
    except Exception as e:
        print(f"Stats update error: {e}")


def save_incident_to_firebase(
    detection_result: dict,
    analysis: dict,
    sensors: dict,
    latitude: float,
    longitude: float,
    original_url: str,
    annotated_url: str
) -> str:
    """Save complete incident to Firebase"""
    
    # Generate incident ID
    incident_ref = db.reference("incidents").push()
    incident_id = incident_ref.key
    
    # Determine status
    if not detection_result["fire_detected"] and not detection_result["smoke_detected"]:
        status = "false_alarm"
    else: 
        status = "confirmed"
    
    incident = {
        "id": incident_id,
        "timestamp": int(datetime.now().timestamp() * 1000),
        "device_id": "demo-upload",
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "sensors": sensors,
        "detection": detection_result,
        "analysis": analysis,
        "images": {
            "original_url": original_url,
            "annotated_url": annotated_url
        },
        "status": status
    }
    
    # Save to Firebase
    incident_ref.set(incident)
    
    # Update device last_seen
    db.reference("devices/demo-upload/last_seen").set(int(datetime.now().timestamp() * 1000))
    db.reference("devices/demo-upload/status").set("online")
    
    # Update stats
    update_stats(analysis.get("severity", "MEDIUM"))
    
    return incident_id


# ============ MAIN DETECTION FUNCTION ============

def process_image(
    image: Image.Image,
    latitude: float,
    longitude: float,
    temperature: float,
    humidity: float,
    gas_level: int,
    flame_detected: bool
):
    """Main function to process uploaded image"""
    
    if image is None:
        return None, "❌ Please upload an image", "", "", ""
    
    try:
        # Prepare sensor data
        sensors = {
            "temperature": temperature,
            "humidity": humidity,
            "gas_level": gas_level,
            "flame_detected": flame_detected
        }
        
        # Step 1: Run YOLO Detection
        detection_result, annotated_image = run_yolo_detection(image)
        
        # Step 2: Gemini Analysis
        analysis = analyze_with_gemini(detection_result, sensors)
        
        # Step 3: Generate temp incident ID for storage
        temp_id = f"temp_{int(datetime.now().timestamp() * 1000)}"
        
        # Step 4: Upload images to Firebase Storage
        original_url = upload_image_to_storage(image, temp_id)
        annotated_url = upload_annotated_image(annotated_image, temp_id)
        
        # Step 5: Save to Firebase
        incident_id = save_incident_to_firebase(
            detection_result=detection_result,
            analysis=analysis,
            sensors=sensors,
            latitude=latitude,
            longitude=longitude,
            original_url=original_url,
            annotated_url=annotated_url
        )
        
        # Prepare output
        severity = analysis.get("severity", "UNKNOWN")
        severity_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(severity, "⚪")
        
        detection_text = f"""
### 🔍 Detection Results
- **Fire Detected:** {"✅ Yes" if detection_result["fire_detected"] else "❌ No"}
- **Smoke Detected:** {"✅ Yes" if detection_result["smoke_detected"] else "❌ No"}
- **Confidence:** {detection_result["confidence"] * 100:.1f}%
- **Objects Found:** {len(detection_result["detections"])}
"""
        
        analysis_text = f"""
### {severity_emoji} Severity: {severity}

**Assessment:**
{analysis.get("summary", "N/A")}

**Recommended Action:**
{analysis.get("action", "N/A")}
"""
        
        status_text = f"""
### ✅ Saved to Firebase
- **Incident ID:** `{incident_id}`
- **Location:** {latitude}°N, {longitude}°E
- **Status:** {"🔥 Confirmed" if detection_result["fire_detected"] or detection_result["smoke_detected"] else "✅ False Alarm"}

📊 **View on Dashboard:** Check Streamlit dashboard to see this incident on the map!
"""
        
        # Convert annotated image for display
        annotated_pil = Image.fromarray(annotated_image)
        
        return annotated_pil, detection_text, analysis_text, status_text, ""
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return None, error_msg, "", "", str(e)


# ============ GRADIO INTERFACE ============

with gr.Blocks(
    title="🔥 Wildfire Detection System",
    theme=gr.themes.Soft()
) as demo:
    
    gr.Markdown("""
    # 🔥 Wildfire Detection System
    ### Upload an image to detect fire/smoke, analyze with AI, and save to dashboard
    
    This simulates an ESP32 camera module sending images for wildfire detection.
    """)
    
    with gr.Row():
        # Left Column - Input
        with gr.Column(scale=1):
            gr.Markdown("### 📤 Upload Image")
            input_image = gr.Image(
                label="Upload Image",
                type="pil",
                height=300
            )
            
            gr.Markdown("### 📍 Location (Pune, India)")
            with gr.Row():
                latitude = gr.Number(
                    label="Latitude",
                    value=DEFAULT_LATITUDE,
                    precision=4
                )
                longitude = gr.Number(
                    label="Longitude",
                    value=DEFAULT_LONGITUDE,
                    precision=4
                )
            
            gr.Markdown("### 🌡️ Sensor Readings")
            with gr.Row():
                temperature = gr.Number(
                    label="Temperature (°C)",
                    value=DEFAULT_SENSORS["temperature"],
                    precision=1
                )
                humidity = gr.Number(
                    label="Humidity (%)",
                    value=DEFAULT_SENSORS["humidity"],
                    precision=1
                )
            with gr.Row():
                gas_level = gr.Number(
                    label="Gas Level (ppm)",
                    value=DEFAULT_SENSORS["gas_level"],
                    precision=0
                )
                flame_detected = gr.Checkbox(
                    label="Flame Sensor Triggered",
                    value=DEFAULT_SENSORS["flame_detected"]
                )
            
            detect_btn = gr.Button(
                "🔍 Detect & Analyze",
                variant="primary",
                size="lg"
            )
        
        # Right Column - Output
        with gr.Column(scale=1):
            gr.Markdown("### 📸 Detection Result")
            output_image = gr.Image(
                label="Annotated Image",
                height=300
            )
            
            detection_output = gr.Markdown(label="Detection")
            analysis_output = gr.Markdown(label="Analysis")
            status_output = gr.Markdown(label="Status")
            error_output = gr.Textbox(label="Errors", visible=False)
    
    # Footer
    gr.Markdown("""
    ---
    ### 📋 How It Works
    1. **Upload** an image (or use sample wildfire image)
    2. **Adjust** location and sensor readings if needed
    3. **Click** "Detect & Analyze"
    4. **View** results here and on the Streamlit dashboard
    
    🔗 **Dashboard:** [Open Streamlit Dashboard](https://hack-o-verse-wildfire-detection-system-mvp.streamlit.app/#incident-map)
    """)
    
    # Connect button to function
    detect_btn.click(
        fn=process_image,
        inputs=[
            input_image,
            latitude,
            longitude,
            temperature,
            humidity,
            gas_level,
            flame_detected
        ],
        outputs=[
            output_image,
            detection_output,
            analysis_output,
            status_output,
            error_output
        ]
    )

# Launch
if __name__ == "__main__":
    demo.launch()