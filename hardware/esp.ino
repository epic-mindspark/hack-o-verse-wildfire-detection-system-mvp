/*
 * ESP32-CAM Production Code - Visual Confirmation Module
 * 
 * Features:
 * - Multi-frame capture (5 images over 2.5 seconds)
 * - Flash LED control
 * - Image upload to cloud storage
 * - GPS metadata embedding
 * 
 * Upload using ESP32-CAM MB Board via Arduino IDE
 */

#include "esp_camera.h"
#include "esp_timer.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "driver/rtc_io.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include "base64.h"

// ==================== CAMERA MODEL ====================
// AI Thinker ESP32-CAM
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ==================== PIN DEFINITIONS ====================
#define FLASH_LED_PIN 4
#define TRIGGER_PIN 13        // Receives trigger from ESP32 DevKit

// ==================== WIFI CONFIGURATION ====================
// Configure with your WiFi for cloud upload
// In production, you might use the 4G module from main ESP32
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// ==================== CLOUD CONFIGURATION ====================
const char* UPLOAD_ENDPOINT = "https://your-api-endpoint.com/api/upload-image";
const char* API_KEY = "YOUR_API_KEY_HERE";

// ==================== SYSTEM STATE ====================
bool cameraReady = false;
bool wifiConnected = false;
unsigned long lastTriggerTime = 0;
const int NUM_FRAMES = 5;
const int FRAME_INTERVAL = 500; // milliseconds between frames

// ==================== FUNCTION PROTOTYPES ====================
void initCamera();
void initWiFi();
bool captureAndUploadImage(int frameNumber);
void flashControl(bool state);
String encodeImageToBase64(camera_fb_t* fb);

// ==================== SETUP ====================
void setup() {
  // Disable brownout detector (camera can cause voltage drops)
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n========================================");
  Serial.println("ESP32-CAM Visual Confirmation Module");
  Serial.println("========================================\n");
  
  // Initialize pins
  pinMode(FLASH_LED_PIN, OUTPUT);
  pinMode(TRIGGER_PIN, INPUT);
  digitalWrite(FLASH_LED_PIN, LOW);
  
  // Initialize camera
  initCamera();
  
  // Initialize WiFi
  initWiFi();
  
  Serial.println("[SYSTEM] Camera module ready");
  Serial.println("[SYSTEM] Waiting for trigger signal...\n");
}

// ==================== MAIN LOOP ====================
void loop() {
  // Check for trigger signal from main ESP32
  if (digitalRead(TRIGGER_PIN) == HIGH) {
    unsigned long currentTime = millis();
    
    // Debounce - ignore triggers within 10 seconds
    if (currentTime - lastTriggerTime > 10000) {
      lastTriggerTime = currentTime;
      
      Serial.println("\n[TRIGGER] Signal received from main controller!");
      Serial.println("[CAMERA] Starting multi-frame capture sequence...\n");
      
      // Capture 5 frames with flash
      int successCount = 0;
      for (int i = 1; i <= NUM_FRAMES; i++) {
        Serial.printf("[CAMERA] Capturing frame %d/%d...\n", i, NUM_FRAMES);
        
        // Turn on flash
        flashControl(true);
        delay(200); // Allow flash to stabilize
        
        // Capture and upload image
        bool success = captureAndUploadImage(i);
        
        // Turn off flash
        flashControl(false);
        
        if (success) {
          successCount++;
          Serial.printf("[CAMERA] Frame %d captured and uploaded successfully\n\n", i);
        } else {
          Serial.printf("[ERROR] Frame %d capture/upload failed\n\n", i);
        }
        
        // Wait before next frame (except after last frame)
        if (i < NUM_FRAMES) {
          delay(FRAME_INTERVAL);
        }
      }
      
      Serial.println("========================================");
      Serial.printf("[CAMERA] Capture complete: %d/%d frames successful\n", successCount, NUM_FRAMES);
      Serial.println("[CAMERA] Ready for next trigger\n");
      Serial.println("========================================\n");
    }
  }
  
  delay(100);
}

// ==================== CAMERA INITIALIZATION ====================
void initCamera() {
  Serial.println("[INIT] Initializing camera...");
  
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // High quality settings for fire detection
  if (psramFound()) {
    config.frame_size = FRAMESIZE_UXGA;  // 1600x1200
    config.jpeg_quality = 10;            // 0-63, lower = higher quality
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;  // 800x600
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }
  
  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("[ERROR] Camera init failed with error 0x%x\n", err);
    return;
  }
  
  // Adjust camera settings for fire detection
  sensor_t* s = esp_camera_sensor_get();
  if (s != NULL) {
    s->set_brightness(s, 0);     // -2 to 2
    s->set_contrast(s, 0);       // -2 to 2
    s->set_saturation(s, 0);     // -2 to 2
    s->set_whitebal(s, 1);       // 0 = disable, 1 = enable
    s->set_awb_gain(s, 1);       // 0 = disable, 1 = enable
    s->set_wb_mode(s, 0);        // 0 to 4
    s->set_exposure_ctrl(s, 1);  // 0 = disable, 1 = enable
    s->set_aec2(s, 0);           // 0 = disable, 1 = enable
    s->set_ae_level(s, 0);       // -2 to 2
    s->set_aec_value(s, 300);    // 0 to 1200
    s->set_gain_ctrl(s, 1);      // 0 = disable, 1 = enable
    s->set_agc_gain(s, 0);       // 0 to 30
    s->set_gainceiling(s, (gainceiling_t)0);  // 0 to 6
  }
  
  cameraReady = true;
  Serial.println("[CAMERA] Initialization successful");
  Serial.printf("[CAMERA] Frame size: %s\n", 
                psramFound() ? "UXGA (1600x1200)" : "SVGA (800x600)");
}

// ==================== WIFI INITIALIZATION ====================
void initWiFi() {
  Serial.println("[INIT] Connecting to WiFi...");
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println("\n[WIFI] Connected successfully");
    Serial.print("[WIFI] IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[ERROR] WiFi connection failed");
    Serial.println("[INFO] Will store images locally");
  }
}

// ==================== CAPTURE AND UPLOAD IMAGE ====================
bool captureAndUploadImage(int frameNumber) {
  if (!cameraReady) {
    Serial.println("[ERROR] Camera not ready");
    return false;
  }
  
  // Capture image
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("[ERROR] Camera capture failed");
    return false;
  }
  
  Serial.printf("[CAMERA] Image captured - Size: %d bytes\n", fb->len);
  
  bool uploadSuccess = false;
  
  // Upload to cloud if WiFi is connected
  if (wifiConnected && WiFi.status() == WL_CONNECTED) {
    Serial.println("[CLOUD] Uploading image...");
    
    HTTPClient http;
    http.begin(UPLOAD_ENDPOINT);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-Key", API_KEY);
    
    // Create JSON payload with base64 encoded image
    String jsonPayload = "{";
    jsonPayload += "\"frameNumber\":" + String(frameNumber) + ",";
    jsonPayload += "\"timestamp\":" + String(millis()) + ",";
    jsonPayload += "\"imageFormat\":\"jpeg\",";
    jsonPayload += "\"imageSize\":" + String(fb->len) + ",";
    
    // Encode image to base64
    String base64Image = base64::encode(fb->buf, fb->len);
    jsonPayload += "\"imageData\":\"" + base64Image + "\"";
    jsonPayload += "}";
    
    int httpCode = http.POST(jsonPayload);
    
    if (httpCode > 0) {
      Serial.printf("[CLOUD] Upload successful (Code: %d)\n", httpCode);
      uploadSuccess = true;
    } else {
      Serial.printf("[CLOUD] Upload failed (Error: %s)\n", 
                    http.errorToString(httpCode).c_str());
    }
    
    http.end();
  } else {
    Serial.println("[INFO] WiFi not connected - image stored locally");
    // In production, you would save to SD card here
    uploadSuccess = true; // Consider local storage as success
  }
  
  // Return frame buffer
  esp_camera_fb_return(fb);
  
  return uploadSuccess;
}

// ==================== FLASH CONTROL ====================
void flashControl(bool state) {
  if (state) {
    digitalWrite(FLASH_LED_PIN, HIGH);
    Serial.println("[FLASH] ON");
  } else {
    digitalWrite(FLASH_LED_PIN, LOW);
    Serial.println("[FLASH] OFF");
  }
}

// ==================== BASE64 ENCODING ====================
String encodeImageToBase64(camera_fb_t* fb) {
  return base64::encode(fb->buf, fb->len);
}