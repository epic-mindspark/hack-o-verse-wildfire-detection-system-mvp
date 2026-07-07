# 🔥 Wildfire Detection System - MVP

An AI-powered early wildfire detection and alert system that combines IoT sensors, computer vision, and intelligent analysis to detect wildfires in real-time. 

![Python](https://img.shields.io/badge/Python-76.5%25-3776AB?style=flat-square&logo=python&logoColor=white)
![C++](https://img.shields.io/badge/C++-23.5%25-00599C?style=flat-square&logo=cplusplus&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat-square&logo=firebase&logoColor=black)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Fire%20Detection-00FFFF?style=flat-square)
![Gemini AI](https://img.shields.io/badge/Gemini%20AI-Analysis-8E75B2?style=flat-square&logo=google&logoColor=white)

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Our Solution](#-our-solution)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Hardware Components](#-hardware-components)
- [Demo & Live Links](#-demo--live-links)
- [Setup & Installation](#-setup--installation)
- [How It Works](#-how-it-works)
- [Important Note on Demo](#-important-note-on-demo)
- [Future Scope](#-future-scope)
- [Team](#-team)

---

## 🎯 Problem Statement

Wildfires cause devastating damage to ecosystems, wildlife, property, and human lives every year. Traditional detection methods rely on manual observation or satellite imagery, which often result in delayed responses.  **Early detection is critical** — the first few minutes after a fire starts are crucial for containment. 

---

## 💡 Our Solution

We've built an **end-to-end IoT-based wildfire detection system** that: 

1. **Monitors** forest areas using ESP32-CAM modules with environmental sensors
2. **Detects** fire and smoke in real-time using a custom-trained YOLOv8 model
3. **Analyzes** the situation using Google's Gemini AI for severity assessment
4. **Alerts** authorities with precise location data and recommended actions
5. **Visualizes** all incidents on a real-time dashboard with analytics

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          WILDFIRE DETECTION SYSTEM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐      │
│  │   ESP32-CAM     │      │   Cloud Layer   │      │   Dashboard     │      │
│  │   + Sensors     │────▶│   Processing     │────▶│   Monitoring    │      │
│  └─────────────────┘      └─────────────────┘      └─────────────────┘      │
│         │                        │                       │                  │
│         ▼                        ▼                       ▼                  │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐            │
│  │ • Camera    │         │ • YOLOv8    │         │ • Streamlit │            │
│  │ • DHT22     │         │ • Gemini AI │         │ • Google    │            │
│  │ • MQ-2 Gas  │         │ • Firebase  │         │   Maps      │            │
│  │ • Flame IR  │         │   RTDB      │         │ • Analytics │            │
│  │ • GPS       │         │ • Storage   │         │ • Alerts    │            │
│  └─────────────┘         └─────────────┘         └─────────────┘            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Hardware
| Component | Purpose |
|-----------|---------|
| ESP32-CAM | Image capture with onboard flash |
| DHT22 | Temperature & Humidity sensing |
| MQ-2 | Gas/Smoke detection |
| Flame Sensor | Infrared flame detection |
| GPS Module | Location tracking |

### Software
| Technology | Purpose |
|------------|---------|
| **Python** | Backend processing |
| **C++ (Arduino)** | ESP32 firmware |
| **YOLOv8 (Ultralytics)** | Fire & smoke detection model |
| **Google Gemini AI** | Intelligent situation analysis |
| **Firebase RTDB** | Real-time database |
| **Firebase Storage** | Image storage |
| **Gradio** | ML demo interface |
| **Streamlit** | Dashboard & visualization |
| **Plotly** | Interactive charts |
| **Google Maps API** | Incident mapping |

---

## ✨ Features

### 🔍 Detection Capabilities
- **Multi-frame capture** — Captures 5 images over 2. 5 seconds for accuracy
- **Fire detection** — Custom YOLOv8 model trained on wildfire datasets
- **Smoke detection** — Early warning before flames are visible
- **Confidence scoring** — Detection confidence percentage

### 📊 Environmental Monitoring
- Real-time temperature readings
- Humidity level monitoring
- Gas/smoke concentration (ppm)
- Infrared flame detection

### 🤖 AI-Powered Analysis
- **Severity Classification**:  CRITICAL, HIGH, MEDIUM, LOW
- Situational assessment summary
- Recommended actions for responders
- Combines sensor data + visual detection

### 📍 Dashboard Features
- Real-time incident map with Google Maps
- Severity distribution analytics
- Incident timeline visualization
- Device status monitoring
- Filter by severity and status
- Original vs annotated image comparison

---

## 📁 Project Structure

```
hack-o-verse-wildfire-detection-system-mvp/
│
├── hardware/
│   └── esp. ino                 # ESP32-CAM firmware (C++)
│
├── huggingface/
│   ├── app.py                  # Gradio demo app
│   ├── fire_n. pt               # Trained YOLOv8 model
│   └── requirements.txt        # Gradio app dependencies
│
├── streamlit_dashboard/
│   ├── app.py                  # Main dashboard application
│   ├── requirements.txt        # Dashboard dependencies
│   ├── . streamlit/             # Streamlit configuration
│   ├── assets/                 # Static assets
│   └── utils/
│       ├── firebase_client.py  # Firebase integration
│       └── helpers. py          # Utility functions
│
├── schema. json                 # Firebase database schema
└── README.md
```

---

## 🔧 Hardware Components

### ESP32-CAM Module
```cpp
// Pin Configuration
#define FLASH_LED_PIN 4       // Onboard flash LED
#define TRIGGER_PIN 13        // Trigger from sensor ESP32

// Camera Settings
- Resolution:  VGA (640 x 480) 
```

### Sensor Integration
| Sensor | Reading | Threshold |
|--------|---------|-----------|
| DHT22 | Temperature | > 45°C |
| DHT22 | Humidity | < 20% |
| MQ-2 | Gas Level | > 400 ppm |
| Flame IR | Detection | Digital trigger |

---

## 🌐 Demo & Live Links

| Platform | Link | Description |
|----------|------|-------------|
| **Streamlit Dashboard** | [Live Dashboard](https://hack-o-verse-wildfire-detection-system-mvp.streamlit.app/) | Real-time monitoring dashboard |
| **Gradio Demo** | [Hugging Face Space](https://huggingface.co/spaces/) | Detection demo interface |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- Firebase project with Realtime Database & Storage
- Google Gemini API key
- Google Maps API key (for dashboard)

### 1. Clone the Repository
```bash
git clone https://github.com/epic-mindspark/hack-o-verse-wildfire-detection-system-mvp. git
cd hack-o-verse-wildfire-detection-system-mvp
```

### 2. Gradio App (Hugging Face)
```bash
cd huggingface
pip install -r requirements.txt

# Set environment variables
export FIREBASE_SERVICE_ACCOUNT='{"your":  "service-account-json"}'
export GEMINI_API_KEY='your-gemini-api-key'

python app.py
```

### 3.  Streamlit Dashboard
```bash
cd streamlit_dashboard
pip install -r requirements.txt

# Configure secrets in .streamlit/secrets.toml
streamlit run app.py
```

### 4. ESP32 Firmware
1. Open `hardware/esp. ino` in Arduino IDE
2. Install required libraries:  `esp_camera`, `WiFi`, `HTTPClient`
3. Configure WiFi credentials and API endpoint
4. Upload to ESP32-CAM board

---

## 🔄 How It Works

### Detection Pipeline

```
1️⃣ TRIGGER
   ESP32 sensors detect anomaly (high temp, gas, flame)
         ↓
2️⃣ CAPTURE
   ESP32-CAM captures 5 images with flash
         ↓
3️⃣ UPLOAD
   Images uploaded to Firebase Storage
         ↓
4️⃣ DETECT
   YOLOv8 model analyzes for fire/smoke
         ↓
5️⃣ ANALYZE
   Gemini AI assesses severity & recommends action
         ↓
6️⃣ STORE
   Incident saved to Firebase RTDB
         ↓
7️⃣ ALERT
   Dashboard updates in real-time
```

### Data Schema
```json
{
  "incidents": {
    "incident_id": {
      "id": "unique_id",
      "timestamp": 1704067200000,
      "device_id": "esp32-001",
      "location": { "latitude": 18.4636, "longitude": 73.8682 },
      "sensors": {
        "temperature": 47.5,
        "humidity": 18.2,
        "gas_level": 485,
        "flame_detected": true
      },
      "detection":  {
        "fire_detected": true,
        "smoke_detected": false,
        "confidence": 0.87,
        "detections": [...]
      },
      "analysis": {
        "severity": "HIGH",
        "summary": "Active fire detected.. .",
        "action":  "Deploy response team..."
      },
      "images": {
        "original_url": "https://...",
        "annotated_url": "https://..."
      },
      "status": "confirmed"
    }
  }
}
```

---

## ⚠️ Important Note on Demo

> **🎮 Simulated Sensor Readings**
> 
> The **Gradio app UI is created solely for demonstration purposes**.  Since hardware readings cannot be made available online without the complete physical setup, the sensor values (temperature, humidity, gas level, flame detection) in the demo are **simulated inputs**. 
 
> The demo allows evaluators to test the **core AI capabilities** (YOLO detection + Gemini analysis) without requiring physical hardware.

---

<div align="center">

*Protecting forests, one detection at a time*

</div>
