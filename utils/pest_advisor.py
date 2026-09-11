"""
utils/pest_advisor.py
----------------------
Two lightweight pest-control tools that need no trained model:

1. Environmental pest-risk scoring — turns your existing temperature /
   humidity / soil-moisture readings into a pest risk list, the same way
   your flood/drought alerts turn soil moisture into a hazard level.

2. Sticky-trap pest counting — counts dark insect blobs on a photo of a
   yellow sticky trap using plain color thresholding (no ML needed),
   and classifies the infestation level from the count.

Both are meant to sit next to utils/esp_client.py and
utils/recommendations.py, and follow the same "return a plain dict"
shape those already use.
"""

import numpy as np
from PIL import Image

# ---------------------------------------------------------------------
# 1. Environmental pest-risk scoring
# ---------------------------------------------------------------------
# Each rule: trigger condition on the live sensor readings, the pest it
# points to, a risk level, and an IPM-style recommendation (organic
# option first, chemical fallback second — same pattern as your disease
# treatment cards).

def _rule_aphids(temp, hum, soil):
    if temp >= 22 and hum <= 55:
        level = "HIGH" if temp >= 27 and hum <= 45 else "MODERATE"
        return {
            "pest": "Aphids",
            "risk_level": level,
            "reason": f"Warm, dry conditions ({temp}\u00b0C, {hum}% humidity) favor rapid aphid reproduction.",
            "organic_treatment": "Introduce ladybugs/lacewings, or spray neem oil (1-2 tbsp/gallon water + a drop of mild soap) in late afternoon.",
            "chemical_treatment": "Insecticidal soap or pyrethrin spray if infestation is severe.",
        }
    return None


def _rule_spider_mites(temp, hum, soil):
    if temp >= 25 and hum <= 50:
        level = "HIGH" if temp >= 30 and hum <= 35 else "MODERATE"
        return {
            "pest": "Spider mites",
            "risk_level": level,
            "reason": f"Hot, dry air ({temp}\u00b0C, {hum}% humidity) is prime spider-mite weather.",
            "organic_treatment": "Increase leaf humidity with a light overhead misting; spray diluted neem oil on leaf undersides.",
            "chemical_treatment": "Miticide (e.g. abamectin) if webbing is already visible.",
        }
    return None


def _rule_fungus_gnats(temp, hum, soil):
    if soil >= 65 and hum >= 60:
        level = "HIGH" if soil >= 80 else "MODERATE"
        return {
            "pest": "Fungus gnats",
            "risk_level": level,
            "reason": f"Waterlogged soil ({soil}%) and high humidity ({hum}%) let larvae thrive in the topsoil.",
            "organic_treatment": "Let the top inch of soil dry between waterings; apply yellow sticky traps near the base of plants.",
            "chemical_treatment": "Bti (Bacillus thuringiensis israelensis) soil drench.",
        }
    return None


def _rule_whiteflies(temp, hum, soil):
    if temp >= 21 and 40 <= hum <= 70:
        return {
            "pest": "Whiteflies",
            "risk_level": "MODERATE",
            "reason": f"Mild, humid conditions ({temp}\u00b0C, {hum}% humidity) suit whitefly breeding cycles.",
            "organic_treatment": "Yellow sticky traps, reflective mulch, or a strong water spray on leaf undersides.",
            "chemical_treatment": "Insecticidal soap or neem oil applied every 5-7 days until under control.",
        }
    return None


_RISK_RULES = [_rule_aphids, _rule_spider_mites, _rule_fungus_gnats, _rule_whiteflies]

_LEVEL_RANK = {"NORMAL": 0, "MODERATE": 1, "HIGH": 2}


def compute_pest_risks(sensor_data: dict) -> dict:
    """
    sensor_data: the same dict shape returned by utils.esp_client.get_sensor_data()
    / server.py's sensors_handler — expects temperature, humidity, soil_moisture.

    Returns: {"overall_level": ..., "risks": [ {pest, risk_level, reason,
    organic_treatment, chemical_treatment}, ... ]}
    """
    temp = float(sensor_data.get("temperature", 24.0))
    hum = float(sensor_data.get("humidity", 55.0))
    soil = float(sensor_data.get("soil_moisture", 45.0))

    risks = []
    for rule in _RISK_RULES:
        result = rule(temp, hum, soil)
        if result:
            risks.append(result)

    if not risks:
        overall = "NORMAL"
    else:
        overall = max((r["risk_level"] for r in risks), key=lambda lvl: _LEVEL_RANK[lvl])

    return {"overall_level": overall, "risks": risks}


# ---------------------------------------------------------------------
# 2. Sticky-trap pest counting (plain color thresholding, no ML)
# ---------------------------------------------------------------------

def count_trap_pests(image: Image.Image) -> dict:
    """
    Counts dark blobs (insects) against a yellow sticky-trap background.

    Approach: convert to RGB, flag pixels that are NOT yellow-ish
    (trap background) and are dark enough to be an insect body, then
    count connected components. No external CV library required beyond
    numpy + PIL, so it drops straight into requirements you already have.
    """
    # Kept small on purpose — this loop is pure Python, not vectorized,
    # so a smaller frame keeps it fast enough for a live Streamlit demo.
    img = image.convert("RGB").resize((300, 300))
    arr = np.asarray(img, dtype=np.float32)

    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    # Yellow trap background: high R, high G, low-ish B.
    is_yellowish = (r > 140) & (g > 120) & (b < 150) & (np.abs(r - g) < 60)
    # Insect bodies: notably darker than the bright trap background.
    brightness = (r + g + b) / 3.0
    is_dark = brightness < 110

    pest_mask = is_dark & (~is_yellowish)

    # Simple connected-component count via flood fill (small image, fine for a demo).
    visited = np.zeros_like(pest_mask, dtype=bool)
    h, w = pest_mask.shape
    blob_count = 0
    blob_pixel_min = 6  # ignore single-pixel noise

    stack_template = []
    for y in range(h):
        for x in range(w):
            if pest_mask[y, x] and not visited[y, x]:
                # flood fill this blob
                stack = [(y, x)]
                visited[y, x] = True
                size = 0
                while stack:
                    cy, cx = stack.pop()
                    size += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and pest_mask[ny, nx] and not visited[ny, nx]:
                            visited[ny, nx] = True
                            stack.append((ny, nx))
                if size >= blob_pixel_min:
                    blob_count += 1

    if blob_count == 0:
        density = "CLEAN"
    elif blob_count <= 8:
        density = "LOW"
    elif blob_count <= 25:
        density = "MODERATE"
    else:
        density = "HIGH"

    advice = {
        "CLEAN": "No pests detected on the trap. Keep monitoring weekly.",
        "LOW": "Light pest presence. Keep the trap up and recheck in a few days.",
        "MODERATE": "Noticeable pest pressure. Consider organic treatment (neem oil, beneficial insects) this week.",
        "HIGH": "High pest load. Treat promptly and consider adding more traps around the field to isolate the hotspot.",
    }[density]

    return {
        "pest_count": blob_count,
        "density": density,
        "advice": advice,
    }
