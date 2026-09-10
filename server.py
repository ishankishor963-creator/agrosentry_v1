"""
server.py
---------
High-performance asynchronous backend server for the AgroSentry Modern Web App.
Built with Starlette and Uvicorn.
Provides RESTful endpoints for:
- Leaf disease diagnosis via plant_model_v5.keras (55 PlantVillage classes)
- ESP32 / IoT telemetry relay and demo simulation
- Flood & drought risk alerting
- Agricultural AI chatbot
- Serving the modern glassmorphic web frontend
"""

import os
import io
import time
import base64
import random
import uvicorn
import numpy as np
from PIL import Image

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse, FileResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Import local project utilities
from utils.recommendations import get_recommendations
from utils.esp_client import get_sensor_data, set_base_url

# Model Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "plant_model_v5.keras")

CLASS_NAMES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Citrus_Canker",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Orange___Multiple_Diseases",
    "Orange___Nutrient_Deficiency",
    "Orange___healthy",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___Bacterial_Pustule",
    "Soybean___Brown_Spot",
    "Soybean___Crestamento",
    "Soybean___Ferrugen",
    "Soybean___Frogeye_Leaf_Spot",
    "Soybean___Mosaic_Virus",
    "Soybean___Powdery_Mildew",
    "Soybean___Rust",
    "Soybean___Septoria",
    "Soybean___Southern_Blight",
    "Soybean___Sudden_Death_Syndrome",
    "Soybean___Target_Leaf_Spot",
    "Soybean___Yellow_Mosaic",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

_model = None
_model_error = None

def get_model():
    global _model, _model_error
    if _model is None and _model_error is None:
        try:
            import tensorflow as tf
            if os.path.exists(MODEL_PATH):
                _model = tf.keras.models.load_model(MODEL_PATH)
                print(f"[AI Engine] Successfully loaded {MODEL_PATH}")
            else:
                _model_error = f"Model file not found at {MODEL_PATH}"
                print(f"[AI Engine Warning] {_model_error}")
        except Exception as e:
            _model_error = str(e)
            print(f"[AI Engine Error] Failed to load model: {_model_error}")
    return _model


# ----------------- Route Handlers -----------------

async def index_handler(request):
    """Serve the modern web frontend."""
    index_path = os.path.join(BASE_DIR, "web", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"message": "AgroSentry API is running. Web interface not found."})


async def status_handler(request):
    """Return backend and model status."""
    model = get_model()
    return JSONResponse({
        "status": "online",
        "model_loaded": model is not None,
        "model_path": MODEL_PATH,
        "num_classes": len(CLASS_NAMES),
        "error": _model_error,
        "timestamp": time.time()
    })


async def predict_handler(request):
    """
    Inference endpoint. Accepts:
    - multipart/form-data with 'file'
    - JSON payload with 'image_base64'
    """
    model = get_model()
    if model is None:
        return JSONResponse({
            "success": False,
            "error": f"Model is not loaded: {_model_error or 'Unknown error'}"
        }, status_code=500)

    image = None
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            data = await request.json()
            b64_str = data.get("image_base64", "")
            if "," in b64_str:
                b64_str = b64_str.split(",", 1)[1]
            image_data = base64.b64decode(b64_str)
            image = Image.open(io.BytesIO(image_data))
        else:
            form = await request.form()
            file = form.get("file")
            if not file:
                return JSONResponse({"success": False, "error": "No image file provided"}, status_code=400)
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Invalid image format: {str(e)}"}, status_code=400)

    try:
        # Preprocessing: 224x224 RGB, normalized to [0, 1]
        img_rgb = image.convert("RGB").resize((224, 224))
        arr = np.asarray(img_rgb, dtype=np.float32) / 255.0
        arr = np.expand_dims(arr, axis=0)

        # Run inference
        t0 = time.time()
        preds = model.predict(arr, verbose=0)[0]
        inference_time_ms = round((time.time() - t0) * 1000, 1)

        top_indices = np.argsort(preds)[::-1][:3]
        top_idx = int(top_indices[0])
        predicted_class = CLASS_NAMES[top_idx] if top_idx < len(CLASS_NAMES) else f"Class_{top_idx}"
        confidence = float(preds[top_idx])

        # Differential diagnoses ranking
        rankings = []
        for idx in top_indices:
            idx_int = int(idx)
            lbl = CLASS_NAMES[idx_int] if idx_int < len(CLASS_NAMES) else f"Class_{idx_int}"
            rankings.append({
                "class_name": lbl,
                "display_name": lbl.replace("___", " — ").replace("__", " ").replace("_", " "),
                "confidence": round(float(preds[idx_int]) * 100, 2)
            })

        # Fetch clinical info and treatment recommendations
        rec = get_recommendations(predicted_class)

        return JSONResponse({
            "success": True,
            "prediction": {
                "class_name": predicted_class,
                "display_name": rec["title"],
                "confidence": round(confidence * 100, 2),
                "is_healthy": rec["is_healthy"],
                "description": rec["description"],
                "treatment": rec["treatment"],
                "rankings": rankings,
                "inference_time_ms": inference_time_ms
            }
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Prediction failed: {str(e)}"}, status_code=500)


async def sensors_handler(request):
    """Return live or simulated telemetry data."""
    data = get_sensor_data()
    # Micro-fluctuations for realistic live dashboard dynamics
    temp = round(float(data.get("temperature", 24.5)) + random.uniform(-0.2, 0.2), 1)
    hum = round(float(data.get("humidity", 62.0)) + random.uniform(-0.5, 0.5), 1)
    soil = round(float(data.get("soil_moisture", 45.0)) + random.uniform(-0.3, 0.3), 1)
    raw_light = float(data.get("light_lux", 42500))
    light = int(raw_light + random.randint(-400, 400))

    # Evaluate status conditions
    soil_status = "optimal" if 40 <= soil <= 70 else ("low" if soil < 40 else "high")
    temp_status = "optimal" if 18 <= temp <= 30 else ("cold" if temp < 18 else "hot")

    # Light condition evaluation
    if light < 15000:
        light_status = "low"
        light_desc = "Low Irradiance — Sub-optimal photosynthesis"
    elif 15000 <= light <= 65000:
        light_status = "optimal"
        light_desc = "Optimal Photosynthetic Sunlight"
    else:
        light_status = "high"
        light_desc = "Intense Radiation — Shade net recommended"

    # Daily Light Integral (DLI) calculation: mol / m² / day (assuming ~12h photoperiod)
    ppfd = round(light * 0.0185, 1)
    dli = round(ppfd * 3600 * 12 / 1000000, 1)

    return JSONResponse({
        "temperature": temp,
        "humidity": hum,
        "soil_moisture": soil,
        "light_lux": light,
        "ppfd": ppfd,
        "dli": dli,
        "light_status": light_status,
        "light_desc": light_desc,
        "source": data.get("source", "demo"),
        "soil_status": soil_status,
        "temp_status": temp_status,
        "timestamp": time.strftime("%H:%M:%S")
    })


async def alerts_handler(request):
    """Calculate and return flood & drought hazard risks."""
    sensor_info = get_sensor_data()
    soil = float(sensor_info.get("soil_moisture", 45.0))

    # Determine drought risk based on soil moisture
    if soil < 25:
        drought_level = "CRITICAL"
        drought_desc = "Soil moisture is critically depleted (<25%). Immediate drip irrigation required."
    elif soil < 40:
        drought_level = "WARNING"
        drought_desc = "Soil moisture is declining below optimal threshold. Schedule watering cycle."
    else:
        drought_level = "NORMAL"
        drought_desc = "Soil hydration is adequate for transpiration and root uptake."

    # Determine flood risk
    if soil > 85:
        flood_level = "WARNING"
        flood_desc = "Soil saturation exceeds 85%. Standing water risk; inspect field drainage canals."
    else:
        flood_level = "NORMAL"
        flood_desc = "Drainage capacity optimal. No localized flooding threat detected."

    return JSONResponse({
        "drought": {
            "level": drought_level,
            "description": drought_desc,
            "soil_moisture": soil
        },
        "flood": {
            "level": flood_level,
            "description": flood_desc,
            "soil_moisture": soil
        },
        "forecast": [
            {"day": "Today", "rain_prob": 15, "temp": "28°C", "condition": "Partly Cloudy"},
            {"day": "Tomorrow", "rain_prob": 35, "temp": "26°C", "condition": "Scattered Clouds"},
            {"day": "Day 3", "rain_prob": 70, "temp": "23°C", "condition": "Rain Showers"},
            {"day": "Day 4", "rain_prob": 20, "temp": "27°C", "condition": "Clear Sky"}
        ]
    })


async def config_device_handler(request):
    """Configure ESP32/Pi IP address."""
    try:
        body = await request.json()
        base_url = body.get("base_url", "").strip()
        set_base_url(base_url)
        return JSONResponse({"success": True, "base_url": base_url})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)


async def chat_handler(request):
    """Agricultural AI advisory bot."""
    try:
        body = await request.json()
        user_message = body.get("message", "").strip().lower()

        # Knowledge base responses
        if any(w in user_message for w in ["blight", "fungus", "spot", "mildew"]):
            reply = (
                "For fungal issues like early/late blight or leaf spot: ensure drip irrigation rather than overhead "
                "watering, prune lower suckers to improve airflow, and apply copper fungicide or chlorothalonil. "
                "You can also use our **AI Disease Scanner** tab to analyze a photo of the affected leaf."
            )
        elif any(w in user_message for w in ["water", "irrigation", "dry", "moisture"]):
            reply = (
                "Target an optimal soil moisture between 45% and 65% for solanaceous crops (tomatoes, peppers, potatoes). "
                "Early morning watering minimizes evaporation and allows leaves to stay dry, reducing pathogen risk."
            )
        elif any(w in user_message for w in ["pest", "mite", "aphid", "insect", "bug"]):
            reply = (
                "For aphids and spider mites: introduce beneficial predatory insects like ladybugs, or spray diluted "
                "neem oil (1-2 tablespoons per gallon of water with a drop of mild soap) in the late afternoon."
            )
        elif any(w in user_message for w in ["fertilizer", "nutrient", "yellow", "nitrogen"]):
            reply = (
                "Interveinal yellowing on older leaves often signals nitrogen or magnesium deficiency. If young leaves "
                "are yellow with dark veins, suspect iron chlorosis. Check soil pH (aim for 6.0–6.8 for optimal nutrient availability)."
            )
        else:
            reply = (
                f"Hello! I am your AgroSentry AI farming assistant. You can ask me about plant disease treatments, "
                f"irrigation advice, soil moisture management, or field alerts. To diagnose a sick crop, switch to the "
                f"**Disease Scanner** tab and capture a leaf photo."
            )

        return JSONResponse({"reply": reply})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def esp_telemetry_handler(request):
    """
    Direct ingestion endpoint for ESP32 (192.168.31.57).
    Accepts:
    - JSON: {"soil_moisture": 48.5, "light_lux": 42000, "temperature": 26.2, "humidity": 65.0}
    - Form data
    - Query params: /api/update?soil=48.5&light=42000
    """
    try:
        payload = {}
        if request.method == "POST":
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                payload = await request.json()
            else:
                form = await request.form()
                payload = dict(form)

        # Merge query params if provided
        if request.query_params:
            for k, v in request.query_params.items():
                payload[k] = v

        if payload:
            from utils.esp_client import record_push_data
            result = record_push_data(payload)
            print(f"[ESP32 Telemetry Received] Soil: {result['soil_moisture']}%, Light: {result['light_lux']} Lux from {request.client.host if request.client else 'ESP32'}")
            return JSONResponse({"success": True, "recorded": result})
        return JSONResponse({"success": False, "error": "No sensor readings in request"}, status_code=400)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)


# ----------------- App Construction -----------------

routes = [
    Route("/", endpoint=index_handler, methods=["GET"]),
    Route("/api/status", endpoint=status_handler, methods=["GET"]),
    Route("/api/predict", endpoint=predict_handler, methods=["POST"]),
    Route("/api/sensors", endpoint=sensors_handler, methods=["GET"]),
    Route("/api/alerts", endpoint=alerts_handler, methods=["GET"]),
    Route("/api/chat", endpoint=chat_handler, methods=["POST"]),
    Route("/api/config/device", endpoint=config_device_handler, methods=["POST"]),
    Route("/api/telemetry", endpoint=esp_telemetry_handler, methods=["GET", "POST"]),
    Route("/api/update", endpoint=esp_telemetry_handler, methods=["GET", "POST"]),
    Route("/update", endpoint=esp_telemetry_handler, methods=["GET", "POST"]),
    Mount("/static", app=StaticFiles(directory=os.path.join(BASE_DIR, "web")), name="static")
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
]

app = Starlette(debug=True, routes=routes, middleware=middleware)

if __name__ == "__main__":
    # Eager load the model on startup
    get_model()
    print("=" * 60)
    print("🌾 AgroSentry Modern Web Platform Starting...")
    print("🌐 Dashboard URL: http://localhost:8000")
    print("=" * 60)
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
