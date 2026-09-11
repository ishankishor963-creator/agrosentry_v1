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
    "Strawberry___healthy": "No disease detected. Keep monitoring regularly.",
    "Tomato___Bacterial_spot": "Use disease-free seed, avoid overhead watering, apply copper bactericide.",
    "Tomato___Early_blight": "Remove infected leaves, rotate crops, apply copper or chlorothalonil fungicide.",
    "Tomato___Late_blight": "Destroy infected plants immediately, avoid overhead irrigation, apply fungicide preventively.",
    "Tomato___Leaf_Mold": "Improve ventilation, avoid overhead watering, apply fungicide if needed.",
    "Tomato___Septoria_leaf_spot": "Remove infected leaves, mulch to prevent soil splash, apply fungicide.",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Spray with water, use insecticidal soap or miticide for heavy infestation.",
    "Tomato___Target_Spot": "Remove infected leaves and debris, improve airflow, apply fungicide in wet conditions.",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Control whiteflies, remove infected plants, use resistant varieties.",
    "Tomato___Tomato_mosaic_virus": "Remove infected plants, disinfect tools between plants, use resistant varieties.",
    "Tomato___healthy": "No disease detected. Keep monitoring regularly.",
}


@st.cache_resource
def load_model():
    try:
        import tensorflow as tf
        return tf.keras.models.load_model(MODEL_PATH)
    except Exception as e:
        st.session_state["model_load_error"] = str(e)
        return None


def predict(image: Image.Image, model):
    img = image.convert("RGB").resize((224, 224))
    arr = np.asarray(img) / 255.0
    arr = np.expand_dims(arr, axis=0)
    preds = model.predict(arr, verbose=0)[0]
    top_idx = int(np.argmax(preds))
    label = CLASS_NAMES[top_idx] if top_idx < len(CLASS_NAMES) else f"class_{top_idx}"
    confidence = float(preds[top_idx])
    return label, confidence


model = load_model()
if model is None:
    real_error = st.session_state.get("model_load_error", "Unknown error")
    st.warning(
        f"Couldn't load the model at `model/plant_model_v4.keras`.\n\n"
        f"**Actual error:** `{real_error}`\n\n"
        "The page still works below for testing the upload/camera flow.",
        icon="⚠️",
    )

st.divider()
tab_upload, tab_camera = st.tabs(["📁 Upload File", "📷 Use Camera"])

image_to_predict = None

with tab_upload:
    uploaded = st.file_uploader("Upload a leaf photo", type=["jpg", "jpeg", "png"])
    if uploaded:
        image_to_predict = Image.open(uploaded)
        st.image(image_to_predict, caption="Uploaded image", width=400)

with tab_camera:
    captured = st.camera_input("Take a photo of the leaf")
    if captured:
        image_to_predict = Image.open(captured)

if image_to_predict and st.button("🔍 Detect Disease", type="primary"):
    if model is None:
        st.error("Add your model file to `model/` first (see warning above).")
    else:
        with st.spinner("Analyzing..."):
            label, confidence = predict(image_to_predict, model)
        st.success(f"**Prediction:** {label}  \n**Confidence:** {confidence:.1%}")
        cure = CURE_INFO.get(label, "No cure info available for this class yet.")
        st.info(f"**How to treat/prevent:** {cure}")
