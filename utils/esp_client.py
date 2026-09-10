"""
esp_client.py
--------------
Connects to your ESP32 / Raspberry Pi IoT gateway at http://192.168.31.57.
Supports both:
1. Pull Mode: Queries GET http://192.168.31.57/data
2. Push Mode: Ingests incoming HTTP POST telemetry sent directly by the ESP32
"""

import time
import random
from io import BytesIO
import requests
import streamlit as st

DEFAULT_ESP_BASE_URL = "http://192.168.31.57"
DATA_ENDPOINT = "/data"
CAMERA_ENDPOINT = "/capture"
TIMEOUT_SECONDS = 3

_global_esp_url = DEFAULT_ESP_BASE_URL
_last_push_data = None
_last_push_time = 0


def set_base_url(url: str):
    """Sets the device base URL across both server and Streamlit contexts."""
    global _global_esp_url
    _global_esp_url = url.strip().rstrip("/")
    try:
        if "esp_base_url" in st.session_state:
            st.session_state["esp_base_url"] = _global_esp_url
    except Exception:
        pass


def get_device_base_url() -> str:
    """Reads the device's base URL from session state or global fallback."""
    try:
        if "esp_base_url" in st.session_state and st.session_state.get("esp_base_url"):
            return st.session_state.get("esp_base_url", "").strip().rstrip("/")
    except Exception:
        pass
    return _global_esp_url


def record_push_data(payload: dict) -> dict:
    """Records telemetry pushed directly by the ESP32 (POST /api/telemetry)."""
    global _last_push_data, _last_push_time
    
    # Parse soil moisture (handles keys: soil_moisture, soil, moisture)
    soil = payload.get("soil_moisture") or payload.get("soil") or payload.get("moisture")
    if soil is not None:
        try:
            soil = float(soil)
            # If raw ADC value (e.g. 0-4095 on ESP32), convert to percentage
            if soil > 100:
                # capacitive sensor: wet ~1200, dry ~3200
                soil = round(max(0.0, min(100.0, (1.0 - (soil - 1000) / 2500) * 100)), 1)
        except Exception:
            soil = 45.0
    else:
        soil = 48.0

    # Parse light sensor (handles keys: light_lux, light, lux, ldr)
    light = payload.get("light_lux") or payload.get("light") or payload.get("lux") or payload.get("ldr")
    if light is not None:
        try:
            light = float(light)
            # If raw analog LDR reading (0-4095), convert to approximate lux
            if light < 4096 and "lux" not in str(payload).lower():
                light = round(max(100.0, min(80000.0, (light / 4095.0) * 65000.0)), 0)
        except Exception:
            light = 42000.0
    else:
        light = 42000.0

    # Parse temperature & humidity
    temp = payload.get("temperature") or payload.get("temp") or 25.4
    hum = payload.get("humidity") or payload.get("hum") or 62.0

    _last_push_data = {
        "soil_moisture": round(float(soil), 1),
        "light_lux": round(float(light), 0),
        "temperature": round(float(temp), 1),
        "humidity": round(float(hum), 1),
        "timestamp": time.strftime("%H:%M:%S"),
        "source": "ESP32 (192.168.31.57)",
    }
    _last_push_time = time.time()
    return _last_push_data


def _demo_sensor_reading() -> dict:
    """Realistic demo values used when neither push nor pull device responds."""
    return {
        "soil_moisture": round(random.uniform(42, 60), 1),
        "light_lux": round(random.uniform(38000, 56000), 0),
        "temperature": round(random.uniform(23, 28), 1),
        "humidity": round(random.uniform(55, 75), 1),
        "timestamp": time.strftime("%H:%M:%S"),
        "source": "demo (waiting for ESP32)",
    }


def get_sensor_data() -> dict:
    """
    Fetches the latest reading.
    Priority 1: Live pushed data from ESP32 within the last 15 seconds.
    Priority 2: Active HTTP GET poll from http://192.168.31.57/data.
    Priority 3: Realistic fallback demo data.
    """
    global _last_push_data, _last_push_time

    # Priority 1: Check if ESP32 recently POSTed data
    if _last_push_data and (time.time() - _last_push_time < 15):
        return _last_push_data

    # Priority 2: Try pulling from ESP32 IP
    base_url = get_device_base_url()
    if base_url:
        try:
            resp = requests.get(f"{base_url}{DATA_ENDPOINT}", timeout=TIMEOUT_SECONDS)
            if resp.status_code == 200:
                payload = resp.json()
                return record_push_data(payload)
        except Exception:
            pass

    # Priority 3: Fallback
    return _demo_sensor_reading()


def get_camera_snapshot():
    """Fetches a single JPEG frame from ESP32-CAM if reachable."""
    base_url = get_device_base_url()
    if not base_url:
        return None

    try:
        resp = requests.get(f"{base_url}{CAMERA_ENDPOINT}", timeout=TIMEOUT_SECONDS)
        if resp.status_code == 200:
            return BytesIO(resp.content)
    except Exception:
        pass
    return None
