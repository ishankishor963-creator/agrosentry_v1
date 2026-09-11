"""
AgroSentry - Local AI Farm Assistant

No external AI API is used.

The assistant generates answers from:
- ESP32 sensor readings
- soil moisture
- temperature
- humidity
- water level
- sensor status

The module intentionally keeps the public `ai_reply()` function so the
existing AgroSentry UI can continue using it.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

SOIL_DRY = 30.0
SOIL_LOW = 45.0
SOIL_GOOD = 75.0

TEMP_HIGH = 35.0
TEMP_LOW = 15.0

HUMIDITY_HIGH = 80.0
HUMIDITY_LOW = 30.0

WATER_LOW = 25.0


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _number(value: Any) -> float | None:
    """Safely convert a sensor value to float."""
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _get_value(data: dict[str, Any], *names: str) -> float | None:
    """Find the first available numeric value using multiple possible keys."""
    for name in names:
        if name in data:
            value = _number(data[name])
            if value is not None:
                return value

    return None


def _normalise_sensor_data(data: Any) -> dict[str, Any]:
    """
    Convert different possible ESP32/sensor response formats into one
    dictionary.

    Supports dictionaries and simple objects/dataclasses.
    """

    if data is None:
        return {}

    if isinstance(data, dict):
        source = data
    else:
        source = {}

        # Common sensor attribute names used by Streamlit/ESP projects.
        for name in (
            "soil_moisture",
            "soil",
            "moisture",
            "temperature",
            "temp",
            "humidity",
            "water_level",
            "water",
            "battery",
            "status",
            "online",
            "timestamp",
        ):
            if hasattr(data, name):
                source[name] = getattr(data, name)

        # Some sensor clients expose a to_dict() method.
        if not source and hasattr(data, "to_dict"):
            try:
                converted = data.to_dict()
                if isinstance(converted, dict):
                    source = converted
            except Exception:
                pass

    return source


def _sensor_summary(data: dict[str, Any]) -> dict[str, Any]:
    """Extract the important farm measurements."""

    return {
        "soil_moisture": _get_value(
            data,
            "soil_moisture",
            "soilMoisture",
            "soil_moisture_percent",
            "moisture",
            "soil",
        ),
        "temperature": _get_value(
            data,
            "temperature",
            "temp",
            "temperature_c",
            "temp_c",
        ),
        "humidity": _get_value(
            data,
            "humidity",
            "humidity_percent",
            "relative_humidity",
        ),
        "water_level": _get_value(
            data,
            "water_level",
            "waterLevel",
            "water_level_percent",
            "tank_level",
            "tank",
        ),
        "battery": _get_value(
            data,
            "battery",
            "battery_level",
            "battery_percent",
        ),
        "status": data.get("status"),
        "online": data.get("online"),
        "timestamp": data.get("timestamp"),
    }


# ---------------------------------------------------------------------
# Sensor acquisition
# ---------------------------------------------------------------------

def get_sensor_data() -> dict[str, Any]:
    """
    Get the latest AgroSentry sensor data.

    The function tries the existing ESP client without requiring any API.
    If the ESP client is unavailable/offline, an empty dictionary is
    returned instead of inventing sensor values.
    """

    try:
        from utils import esp_client
    except Exception:
        return {}

    # Try common function names used by ESP32 clients.
    possible_functions = (
        "get_sensor_data",
        "get_latest_sensor_data",
        "get_latest_readings",
        "read_sensor_data",
        "fetch_sensor_data",
        "get_data",
    )

    for function_name in possible_functions:
        function = getattr(esp_client, function_name, None)

        if not callable(function):
            continue

        try:
            result = function()

            if result is None:
                continue

            return _normalise_sensor_data(result)

        except Exception:
            continue

    return {}


# ---------------------------------------------------------------------
# Farm analysis
# ---------------------------------------------------------------------

def analyze_farm(sensor_data: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze sensor readings using deterministic agriculture rules.

    No AI API is involved.
    """

    data = _sensor_summary(sensor_data)

    soil = data["soil_moisture"]
    temperature = data["temperature"]
    humidity = data["humidity"]
    water = data["water_level"]

    issues: list[str] = []
    recommendations: list[str] = []
    positive: list[str] = []

    irrigation_needed = False

    # -------------------------------------------------------------
    # Soil moisture
    # -------------------------------------------------------------

    if soil is None:
        issues.append("Soil moisture data is unavailable.")
    elif soil < SOIL_DRY:
        irrigation_needed = True
        issues.append(f"Soil moisture is very low at {soil:.1f}%.")
        recommendations.append(
            "Irrigation is recommended because the soil is dry."
        )
    elif soil < SOIL_LOW:
        irrigation_needed = True
        issues.append(f"Soil moisture is low at {soil:.1f}%.")
        recommendations.append(
            "Consider irrigation soon and monitor soil moisture."
        )
    elif soil <= SOIL_GOOD:
        positive.append(f"Soil moisture is in a suitable range at {soil:.1f}%.")
    else:
        positive.append(
            f"Soil moisture is high at {soil:.1f}%; avoid unnecessary irrigation."
        )
        recommendations.append(
            "Avoid additional irrigation unless the crop specifically requires it."
        )

    # -------------------------------------------------------------
    # Temperature
    # -------------------------------------------------------------

    if temperature is None:
        issues.append("Temperature data is unavailable.")
    elif temperature >= TEMP_HIGH:
        issues.append(f"High temperature detected: {temperature:.1f}°C.")
        recommendations.append(
            "Monitor crops for heat stress and maintain adequate soil moisture."
        )
    elif temperature <= TEMP_LOW:
        issues.append(f"Low temperature detected: {temperature:.1f}°C.")
        recommendations.append(
            "Monitor the crop for cold stress."
        )
    else:
        positive.append(
            f"Temperature is currently {temperature:.1f}°C."
        )

    # -------------------------------------------------------------
    # Humidity
    # -------------------------------------------------------------

    if humidity is None:
        issues.append("Humidity data is unavailable.")
    elif humidity >= HUMIDITY_HIGH:
        issues.append(f"Humidity is high at {humidity:.1f}%.")
        recommendations.append(
            "High humidity can increase fungal-disease risk; inspect leaves regularly."
        )
    elif humidity <= HUMIDITY_LOW:
        issues.append(f"Humidity is low at {humidity:.1f}%.")
        recommendations.append(
            "Low humidity may increase plant water stress; monitor the crop and soil."
        )
    else:
        positive.append(
            f"Humidity is {humidity:.1f}%."
        )

    # -------------------------------------------------------------
    # Water tank
    # -------------------------------------------------------------

    if water is not None:
        if water <= WATER_LOW:
            issues.append(f"Water level is low at {water:.1f}%.")
            recommendations.append(
                "Refill the water source before running extended irrigation."
            )
        else:
            positive.append(
                f"Available water level is {water:.1f}%."
            )

    # -------------------------------------------------------------
    # Overall status
    # -------------------------------------------------------------

    if irrigation_needed:
        overall = "IRRIGATION RECOMMENDED"
    elif issues:
        overall = "ATTENTION REQUIRED"
    else:
        overall = "FARM CONDITIONS LOOK GOOD"

    return {
        "overall": overall,
        "soil_moisture": soil,
        "temperature": temperature,
        "humidity": humidity,
        "water_level": water,
        "issues": issues,
        "recommendations": recommendations,
        "positive": positive,
        "irrigation_needed": irrigation_needed,
    }


# ---------------------------------------------------------------------
# Question understanding
# ---------------------------------------------------------------------

def _contains_any(text: str, words: tuple[str, ...]) -> bool:
    return any(word in text for word in words)


def _format_value(value: float | None, unit: str) -> str:
    if value is None:
        return "unavailable"

    return f"{value:.1f}{unit}"


# ---------------------------------------------------------------------
# Main local assistant
# ---------------------------------------------------------------------

def ai_reply(
    question: str,
    history: list[dict[str, Any]] | None = None,
) -> str:
    """
    Generate a farming answer entirely from local sensor data.

    `history` is accepted for compatibility with the existing AgroSentry
    Assistant page, but no external AI model is called.
    """

    del history  # Compatibility only.

    question = (question or "").strip()

    if not question:
        return "Please ask me about your farm, soil, temperature, humidity, water level, or irrigation."

    sensor_data = get_sensor_data()

    if not sensor_data:
        return (
            "I cannot give a sensor-based recommendation right now because "
            "the AgroSentry sensor data is unavailable.\n\n"
            "Please check that the ESP32 is powered on and connected."
        )

    analysis = analyze_farm(sensor_data)

    soil = analysis["soil_moisture"]
    temperature = analysis["temperature"]
    humidity = analysis["humidity"]
    water = analysis["water_level"]

    q = question.lower()

    # -------------------------------------------------------------
    # Soil questions
    # -------------------------------------------------------------

    if _contains_any(
        q,
        (
            "soil",
            "moisture",
            "dry",
            "wet",
        ),
    ):
        if soil is None:
            return "Soil moisture data is currently unavailable."

        if soil < SOIL_DRY:
            return (
                f"🌱 Soil moisture is {_format_value(soil, '%')}.\n\n"
                "The soil is dry. Irrigation is recommended."
            )

        if soil < SOIL_LOW:
            return (
                f"🌱 Soil moisture is {_format_value(soil, '%')}.\n\n"
                "The soil moisture is getting low. Consider irrigation soon."
            )

        if soil <= SOIL_GOOD:
            return (
                f"🌱 Soil moisture is {_format_value(soil, '%')}.\n\n"
                "The soil moisture is currently in a suitable range."
            )

        return (
            f"🌱 Soil moisture is {_format_value(soil, '%')}.\n\n"
            "The soil is already quite wet. Avoid unnecessary irrigation."
        )

    # -------------------------------------------------------------
    # Temperature questions
    # -------------------------------------------------------------

    if _contains_any(
        q,
        (
            "temperature",
            "hot",
            "heat",
            "cold",
        ),
    ):
        if temperature is None:
            return "Temperature data is currently unavailable."

        if temperature >= TEMP_HIGH:
            return (
                f"🌡️ Temperature is {_format_value(temperature, '°C')}.\n\n"
                "This is high. Monitor the crop for heat stress and make sure "
                "soil moisture is adequate."
            )

        if temperature <= TEMP_LOW:
            return (
                f"🌡️ Temperature is {_format_value(temperature, '°C')}.\n\n"
                "This is relatively low. Monitor the crop for cold stress."
            )

        return (
            f"🌡️ Temperature is {_format_value(temperature, '°C')}.\n\n"
            "The temperature is not currently triggering a high-temperature alert."
        )

    # -------------------------------------------------------------
    # Humidity questions
    # -------------------------------------------------------------

    if _contains_any(
        q,
        (
            "humidity",
            "humid",
            "fungus",
            "fungal",
        ),
    ):
        if humidity is None:
            return "Humidity data is currently unavailable."

        if humidity >= HUMIDITY_HIGH:
            return (
                f"💧 Humidity is {_format_value(humidity, '%')}.\n\n"
                "Humidity is high. Monitor the crop for fungal-disease symptoms "
                "and avoid unnecessary leaf wetness."
            )

        if humidity <= HUMIDITY_LOW:
            return (
                f"💧 Humidity is {_format_value(humidity, '%')}.\n\n"
                "Humidity is low. Monitor the crop for water stress."
            )

        return (
            f"💧 Humidity is {_format_value(humidity, '%')}.\n\n"
            "Humidity is currently within the normal monitoring range."
        )

    # -------------------------------------------------------------
    # Water questions
    # -------------------------------------------------------------

    if _contains_any(
        q,
        (
            "water level",
            "tank",
            "water available",
            "water source",
        ),
    ):
        if water is None:
            return "Water-level data is currently unavailable."

        if water <= WATER_LOW:
            return (
                f"🚰 Water level is {_format_value(water, '%')}.\n\n"
                "The water level is low. Refill the water source before "
                "running extended irrigation."
            )

        return (
            f"🚰 Water level is {_format_value(water, '%')}.\n\n"
            "The available water level is currently above the low-water threshold."
        )

    # -------------------------------------------------------------
    # Irrigation questions
    # -------------------------------------------------------------

    if _contains_any(
        q,
        (
            "irrigate",
            "irrigation",
            "water my crop",
            "water the crop",
            "should i water",
            "need water",
        ),
    ):
        if soil is None:
            return (
                "I cannot safely recommend irrigation because soil-moisture "
                "data is unavailable."
            )

        if soil < SOIL_DRY:
            if water is not None and water <= WATER_LOW:
                return (
                    f"🚨 Soil moisture is only {soil:.1f}%, but the water level "
                    f"is also low at {water:.1f}%.\n\n"
                    "The crop needs water, but the water source should be refilled."
                )

            return (
                f"💧 Yes. Soil moisture is only {soil:.1f}%.\n\n"
                "Irrigation is recommended."
            )

        if soil < SOIL_LOW:
            return (
                f"💧 Soil moisture is {soil:.1f}%.\n\n"
                "Irrigation may be needed soon. Monitor the soil and crop."
            )

        if soil <= SOIL_GOOD:
            return (
                f"✅ Soil moisture is {soil:.1f}%.\n\n"
                "Irrigation is not urgently required based on the current reading."
            )

        return (
            f"⚠️ Soil moisture is {soil:.1f}%.\n\n"
            "The soil is already wet. Avoid unnecessary irrigation."
        )

    # -------------------------------------------------------------
    # General farm status
    # -------------------------------------------------------------

    if _contains_any(
        q,
        (
            "how is my farm",
            "farm status",
            "farm condition",
            "status",
            "what should i do",
            "what do i do",
            "recommendation",
            "recommend",
            "summary",
        ),
    ):
        lines = [
            f"🌾 **{analysis['overall']}**",
            "",
        ]

        if soil is not None:
            lines.append(f"🌱 Soil moisture: {soil:.1f}%")
        else:
            lines.append("🌱 Soil moisture: unavailable")

        if temperature is not None:
            lines.append(f"🌡️ Temperature: {temperature:.1f}°C")
        else:
            lines.append("🌡️ Temperature: unavailable")

        if humidity is not None:
            lines.append(f"💧 Humidity: {humidity:.1f}%")
        else:
            lines.append("💧 Humidity: unavailable")

        if water is not None:
            lines.append(f"🚰 Water level: {water:.1f}%")

        if analysis["recommendations"]:
            lines.extend(["", "### Recommended action"])

            for recommendation in analysis["recommendations"][:4]:
                lines.append(f"- {recommendation}")

        return "\n".join(lines)

    # -------------------------------------------------------------
    # Generic sensor report
    # -------------------------------------------------------------

    return (
        "I am AgroSentry's local farm intelligence assistant.\n\n"
        "I currently use the sensor data available from the farm system. "
        "You can ask me:\n\n"
        "- What is my soil moisture?\n"
        "- Do I need irrigation?\n"
        "- What is the temperature?\n"
        "- What is the humidity?\n"
        "- What is my water level?\n"
        "- How is my farm?\n"
        "- What should I do now?"
    )


# ---------------------------------------------------------------------
# Optional compatibility function
# ---------------------------------------------------------------------

def rule_based_reply(question: str) -> str:
    """
    Backwards-compatible wrapper.

    Older AgroSentry code may import this function.
    """

    return ai_reply(question)
