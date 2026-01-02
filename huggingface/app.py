import gradio as gr
from ultralytics import YOLO
from PIL import Image
import json
import base64
import io

# Load model
model = YOLO('fire_n.pt')  # Your custom trained model
CLASS_NAMES = {0: "fire", 1: "smoke"}  # Adjust to your classes


def detect_fire_api(image):
    """
    API endpoint for Cloud Function to call. 
    Returns JSON with detections + annotated image.
    """
    
    if image is None: 
        return json.dumps({"error": "No image provided"})
    
    try:
        # Run detection
        results = model(image, conf=0.25)
        result = results[0]
        
        # Process detections
        detections = []
        fire_detected = False
        smoke_detected = False
        max_confidence = 0.0
        
        if result.boxes is not None:
            for box in result.boxes:
                conf = float(box.conf[0])
                cls = int(box. cls[0])
                class_name = CLASS_NAMES.get(cls, f"class_{cls}")
                
                x1, y1, x2, y2 = box. xyxy[0]. tolist()
                
                detections.append({
                    "class":  class_name,
                    "confidence":  round(conf, 4),
                    "bbox": [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]
                })
                
                if class_name == "fire":
                    fire_detected = True
                if class_name == "smoke":
                    smoke_detected = True
                max_confidence = max(max_confidence, conf)
        
        # Get annotated image as base64
        annotated = Image.fromarray(result.plot())
        buffer = io.BytesIO()
        annotated.save(buffer, format='JPEG', quality=70)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return json.dumps({
            "fire_detected": fire_detected,
            "smoke_detected": smoke_detected,
            "max_confidence": round(max_confidence, 4),
            "num_detections": len(detections),
            "detections":  detections,
            "annotated_image_base64": img_base64
        })
        
    except Exception as e: 
        return json.dumps({"error": str(e)})


def detect_fire_ui(image):
    """
    UI endpoint for testing in browser.
    Returns annotated image + JSON. 
    """
    
    if image is None:
        return None, "No image provided"
    
    result_json = detect_fire_api(image)
    result = json.loads(result_json)
    
    if "error" in result: 
        return image, f"Error: {result['error']}"
    
    # Decode annotated image for display
    img_bytes = base64.b64decode(result["annotated_image_base64"])
    annotated_image = Image.open(io.BytesIO(img_bytes))
    
    # Format result for display
    display_text = f"""
Fire Detected: {result['fire_detected']}
Smoke Detected: {result['smoke_detected']}
Max Confidence: {result['max_confidence'] * 100:.1f}%
Detections: {result['num_detections']}
    """
    
    return annotated_image, display_text


# Gradio Interface
with gr. Blocks(title="Wildfire Detection API") as demo:
    
    gr.Markdown("# 🔥 Wildfire Detection API")
    gr.Markdown("YOLOv8-based fire and smoke detection.  Upload image to test.")
    
    with gr.Tab("Test UI"):
        with gr.Row():
            input_image = gr. Image(type="pil", label="Upload Image")
            output_image = gr.Image(type="pil", label="Detection Result")
        
        result_text = gr. Textbox(label="Results", lines=5)
        detect_btn = gr.Button("🔍 Detect", variant="primary")
        
        detect_btn.click(
            fn=detect_fire_ui,
            inputs=input_image,
            outputs=[output_image, result_text]
        )
    
    with gr.Tab("API Info"):
        gr.Markdown("""
        ## API Endpoint
        
        ```python
        from gradio_client import Client
        
        client = Client("YOUR_USERNAME/wildfire-detection-api")
        result = client.predict(
            image="image. jpg",
            api_name="/detect_fire_api"
        )
        ```
        """)
        
demo.launch()