import numpy as np
import streamlit as st
from PIL import Image

from utils.theme import inject_theme, topnav
from utils.auth import logout_button

inject_theme()
with st.sidebar:
    logout_button()
topnav("disease")

st.title("🔬 AI Disease Detection")
st.caption(
    "Upload a leaf photo or capture one with your camera. Runs your "
    "trained MobileNetV2 model (plant_model_v5)."
)

MODEL_PATH = "model/plant_model_v5.keras"  # copy your trained .keras model here

# IMPORTANT: this model has 55 output classes (Dense(55, softmax)), but
# we've only confirmed 39 real class names so far (standard PlantVillage
# 38 classes + Background_without_leaves, alphabetically sorted). Indices
# 39-54 are UNKNOWN placeholders. If a prediction lands on one of those,
# predict() below shows a clear "unrecognized" message instead of a wrong
# disease name. Replace the placeholders as soon as you find the real list.
CLASS_NAMES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Background_without_leaves",
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
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
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
] + [f"UNKNOWN_class_{i}" for i in range(39, 55)]

# Prevention / treatment info per class. Keyed by the exact string in
# CLASS_NAMES. Fill these in as you confirm each class name — anything
# not in this dict falls back to a generic message below.
DISEASE_INFO = {
    # Example — replace "Tomato___Early_blight" with your real class names:
    # "Tomato___Early_blight": {
    #     "summary": "Fungal disease causing dark concentric-ring spots on lower leaves.",
    #     "prevention": [
    #         "Remove and destroy infected leaves promptly",
    #         "Avoid overhead watering; water at soil level",
    #         "Rotate crops yearly, avoid planting same family in same spot",
    #         "Apply copper-based or chlorothalonil fungicide for active outbreaks",
    #     ],
    # },
}

GENERIC_PREVENTION = [
    "Remove and isolate affected leaves to slow spread",
    "Avoid overhead watering; water at the base of the plant",
    "Ensure good airflow between plants",
    "Disinfect tools between plants",
    "Consult a local agricultural extension for a targeted treatment",
]


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
    return label, confidence, top_idx


def render_disease_info(label: str):
    info = DISEASE_INFO.get(label)
    if info:
        if info.get("summary"):
            st.markdown(f"**About this condition:** {info['summary']}")
        st.markdown("**Prevention & treatment:**")
        for tip in info["prevention"]:
            st.markdown(f"- {tip}")
    else:
        st.info(
            "No detailed prevention info saved yet for this class. "
            "Here are general leaf-disease best practices:"
        )
        for tip in GENERIC_PREVENTION:
            st.markdown(f"- {tip}")


model = load_model()
if model is None:
    st.warning(
        f"Model file not found at `{MODEL_PATH}`. Copy your trained model "
        "into the `model/` folder (and fill in `CLASS_NAMES` at the top of "
        "this file, in training order) to activate real predictions. The "
        "page still works below for testing the upload/camera flow.",
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
            label, confidence, top_idx = predict(image_to_predict, model)
        if label.startswith("UNKNOWN_class_"):
            st.error(
                f"Model predicted class index {top_idx}, which isn't in our "
                "confirmed 39-class list yet (this model has 55 total "
                "classes). We can't reliably name this disease until the "
                "remaining class names are found — please don't treat this "
                "as a confirmed diagnosis."
            )
        else:
            st.success(f"**Prediction:** {label}  \n**Confidence:** {confidence:.1%}")
            st.divider()
            render_disease_info(label)
