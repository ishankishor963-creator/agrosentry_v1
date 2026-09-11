import numpy as np
import streamlit as st
from PIL import Image

st.set_page_config(page_title="AI Disease Detection", page_icon="🔬", layout="wide")
st.title("🔬 AI Disease Detection")
st.caption(
    "Upload a leaf photo or capture one with your camera. Runs your "
    "existing MobileNetV2 model from the plant_disease_modal project."
)

MODEL_PATH = "model/plant_model_v4.keras"

CLASS_NAMES = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Blueberry___healthy", "Cherry_(including_sour)___Powdery_mildew", "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy", "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot", "Peach___healthy",
    "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy", "Potato___Early_blight",
    "Potato___Late_blight", "Potato___healthy", "Raspberry___healthy", "Soybean___healthy",
    "Squash___Powdery_mildew", "Strawberry___Leaf_scorch", "Strawberry___healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite", "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus", "Tomato___healthy",
]

CURE_INFO = {
    "Apple___Apple_scab": "Remove fallen leaves, prune for airflow, apply captan or myclobutanil fungicide.",
    "Apple___Black_rot": "Prune out dead/cankered wood, remove mummified fruit, apply fungicide during season.",
    "Apple___Cedar_apple_rust": "Remove nearby cedar/juniper trees, apply fungicide in early spring, plant resistant varieties.",
    "Apple___healthy": "No disease detected. Keep monitoring regularly.",
    "Blueberry___healthy": "No disease detected. Keep monitoring regularly.",
    "Cherry_(including_sour)___Powdery_mildew": "Improve air circulation, avoid excess nitrogen, apply sulfur-based fungicide.",
    "Cherry_(including_sour)___healthy": "No disease detected. Keep monitoring regularly.",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Rotate crops, remove crop debris, plant resistant hybrids.",
    "Corn_(maize)___Common_rust_": "Plant rust-resistant hybrids, apply fungicide early if seen before tasseling.",
    "Corn_(maize)___Northern_Leaf_Blight": "Rotate crops, use resistant hybrids, manage residue after harvest.",
    "Corn_(maize)___healthy": "No disease detected. Keep monitoring regularly.",
    "Grape___Black_rot": "Remove mummified berries and infected canes, improve airflow, apply fungicide.",
    "Grape___Esca_(Black_Measles)": "Prune out infected wood, avoid pruning in wet weather, protect wounds with sealant.",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Remove infected leaves, improve airflow, apply protectant fungicide.",
    "Grape___healthy": "No disease detected. Keep monitoring regularly.",
    "Orange___Haunglongbing_(Citrus_greening)": "No cure. Remove infected trees, control psyllid insects, use certified disease-free stock.",
    "Peach___Bacterial_spot": "Plant resistant varieties, apply copper bactericide, avoid overhead irrigation.",
    "Peach___healthy": "No disease detected. Keep monitoring regularly.",
    "Pepper,_bell___Bacterial_spot": "Use disease-free seed, avoid overhead watering, apply copper bactericide.",
    "Pepper,_bell___healthy": "No disease detected. Keep monitoring regularly.",
    "Potato___Early_blight": "Rotate crops, remove infected foliage, apply fungicide preventively.",
    "Potato___Late_blight": "Destroy infected plants immediately, avoid overhead watering, apply fungicide preventively.",
    "Potato___healthy": "No disease detected. Keep monitoring regularly.",
    "Raspberry___healthy": "No disease detected. Keep monitoring regularly.",
    "Soybean___healthy": "No disease detected. Keep monitoring regularly.",
    "Squash___Powdery_mildew": "Space plants for airflow, avoid wetting leaves, apply sulfur fungicide.",
    "Strawberry___Leaf_scorch": "Remove infected leaves after harvest, avoid overhead irrigation, apply fungicide if needed.",
    "Strawberry___healthy": "No disease detected. Keep
