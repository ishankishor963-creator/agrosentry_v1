import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
import requests
import time
import random
from deep_translator import GoogleTranslator
from ddgs import DDGS

from recommendations import RECOMMENDATIONS

# ---------------------------------------------------------------------------
# Class names must be in the same order the model was trained on.
# v5 combines the original 38-class PlantVillage set with a 2nd dataset
# (Kaggle "Soybean Diseased Leaf Dataset") adding Orange disease variants
# and 13 new Soybean diseases — 55 classes total, confirmed against the
# training notebook's train_ds.class_names output.
# ---------------------------------------------------------------------------
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

SUPPORTED_CROPS = "apple, blueberry, cherry, corn, grape, orange, peach, pepper, potato, raspberry, soybean, squash, strawberry, tomato"
SUPPORTED_CROP_LIST = [
    "Apple", "Blueberry", "Cherry", "Corn", "Grape", "Orange", "Peach",
    "Pepper (bell)", "Potato", "Raspberry", "Soybean", "Squash", "Strawberry", "Tomato",
]


def get_class_display_name(index):
    """Safely map a predicted index to a class name, even if it falls outside
    the currently-named list (e.g. v5's classes 38-54, not yet added)."""
    if 0 <= index < len(CLASS_NAMES):
        return CLASS_NAMES[index], True
    return f"class_{index}", False


# ---------------------------------------------------------------------------
# Language support
# ---------------------------------------------------------------------------
LANGUAGES = {
    "English": "en",
    "हिंदी": "hi",
    "മലയാളം": "ml",
    "ಕನ್ನಡ": "kn",
    "தமிழ்": "ta",
}

UI_STRINGS = {
    "en": {
        "eyebrow_system": "Field Diagnostics System",
        "hero_desc": "Upload a photo of a crop leaf to detect disease and get treatment advice.",
        "current_condition": "Current Condition",
        "location_placeholder": "Enter your city/location",
        "no_location_msg": "Enter your location above to see live weather, irrigation tips, and the matching theme.",
        "soil_eyebrow": "Soil Moisture",
        "moisture_label": "Moisture Level",
        "soil_error": "Couldn't fetch soil moisture data — check the sensor and ThingSpeak connection.",
        "weather_eyebrow": "Irrigation Tip",
        "weather_not_configured": "Weather feature not configured — add an OpenWeatherMap API key in app secrets to enable this.",
        "weather_error": "Couldn't fetch weather for that location — check the spelling or try a nearby larger city/town name.",
        "upload_label": "Upload a leaf image",
        "uploaded_caption": "Uploaded image",
        "analyzing_eyebrow": "Analyzing Sample",
        "scan_line1": "Extracting visual features...",
        "scan_line2": "Cross-referencing crop-disease profiles...",
        "scan_line3": "Computing confidence score...",
        "diagnosis_eyebrow": "Diagnosis",
        "not_recognized_label": "⚠ Crop Not Recognized",
        "not_recognized_msg": "This doesn't look like any of the 14 supported crops ({crops}). Try a photo of one of these crops for a reliable result.",
        "unlabeled_class_msg": "This looks like a newer disease class that hasn't been named in the app yet (index {idx}). The model detected something with {conf:.1f}% confidence, but no description is available until this class is labeled.",
        "confidence_label": "Confidence",
        "confidence_note": "Confidence is moderate — a clearer, well-lit photo of a single leaf may improve accuracy.",
        "treatment_eyebrow": "Treatment Protocol",
        "what_means_header": "What This Means",
        "recommended_action_header": "Recommended Action",
        "web_searching": "Searching the web for more information...",
        "web_info_eyebrow": "More Info from the Web",
        "web_no_results": "No web results found — try again in a moment.",
        "footer": "Agro Edge // Crop Intelligence System // Team Cyberpunk",
        "last_updated": "Last updated:",
        "my_farms": "🌾 My Farms",
        "add_farm": "+ Add Farm",
        "farm_name_label": "Farm Name",
        "crop_label": "Crop",
        "remove_farm": "Remove",
        "active_farm_label": "Active Farm",
        "other_crop_option": "Other (not yet supported)",
        "other_crop_placeholder": "Type your crop name",
        "crop_not_supported_note": "Automated diagnosis isn't available yet for {crop}. Currently supported crops: {crops}.",
    },
    "hi": {
        "eyebrow_system": "फील्ड डायग्नोस्टिक्स सिस्टम",
        "hero_desc": "रोग की पहचान करने और उपचार सलाह पाने के लिए फसल की पत्ती की फोटो अपलोड करें।",
        "current_condition": "वर्तमान स्थिति",
        "location_placeholder": "अपना शहर/स्थान दर्ज करें",
        "no_location_msg": "लाइव मौसम, सिंचाई सुझाव और संबंधित थीम देखने के लिए ऊपर अपना स्थान दर्ज करें।",
        "soil_eyebrow": "मिट्टी की नमी",
        "moisture_label": "नमी स्तर",
        "soil_error": "मिट्टी की नमी का डेटा नहीं मिल सका — सेंसर और थिंगस्पीक कनेक्शन जांचें।",
        "weather_eyebrow": "सिंचाई सुझाव",
        "weather_not_configured": "मौसम सुविधा कॉन्फ़िगर नहीं है — इसे सक्षम करने के लिए ऐप सीक्रेट्स में OpenWeatherMap API कुंजी जोड़ें।",
        "weather_error": "उस स्थान का मौसम नहीं मिल सका — वर्तनी जांचें या किसी नज़दीकी बड़े शहर का नाम आज़माएं।",
        "upload_label": "पत्ती की फोटो अपलोड करें",
        "uploaded_caption": "अपलोड की गई फोटो",
        "analyzing_eyebrow": "नमूने का विश्लेषण हो रहा है",
        "scan_line1": "दृश्य विशेषताएं निकाली जा रही हैं...",
        "scan_line2": "फसल-रोग प्रोफाइल से तुलना हो रही है...",
        "scan_line3": "विश्वास स्कोर की गणना हो रही है...",
        "diagnosis_eyebrow": "निदान",
        "not_recognized_label": "⚠ फसल पहचानी नहीं गई",
        "not_recognized_msg": "यह समर्थित 14 फसलों ({crops}) में से किसी जैसी नहीं दिखती। विश्वसनीय परिणाम के लिए इनमें से किसी एक फसल की फोटो आज़माएं।",
        "unlabeled_class_msg": "यह एक नई रोग श्रेणी लग रही है जिसे अभी ऐप में नाम नहीं दिया गया है (इंडेक्स {idx})। मॉडल ने {conf:.1f}% विश्वास के साथ कुछ पहचाना, लेकिन इस श्रेणी के लेबल होने तक कोई विवरण उपलब्ध नहीं है।",
        "confidence_label": "विश्वास स्तर",
        "confidence_note": "विश्वास स्तर मध्यम है — एक स्पष्ट, अच्छी रोशनी वाली एकल पत्ती की फोटो सटीकता बढ़ा सकती है।",
        "treatment_eyebrow": "उपचार प्रोटोकॉल",
        "what_means_header": "इसका क्या अर्थ है",
        "recommended_action_header": "अनुशंसित कार्रवाई",
        "web_searching": "अधिक जानकारी के लिए वेब खोजी जा रही है...",
        "web_info_eyebrow": "वेब से अधिक जानकारी",
        "web_no_results": "कोई वेब परिणाम नहीं मिला — कुछ देर बाद पुनः प्रयास करें।",
        "footer": "एग्रो एज // क्रॉप इंटेलिजेंस सिस्टम // टीम साइबरपंक",
        "last_updated": "आखिरी बार अपडेट किया गया:",
        "my_farms": "🌾 मेरे खेत",
        "add_farm": "+ खेत जोड़ें",
        "farm_name_label": "खेत का नाम",
        "crop_label": "फसल",
        "remove_farm": "हटाएं",
        "active_farm_label": "सक्रिय खेत",
        "other_crop_option": "अन्य (अभी समर्थित नहीं)",
        "other_crop_placeholder": "अपनी फसल का नाम लिखें",
        "crop_not_supported_note": "{crop} के लिए स्वचालित निदान अभी उपलब्ध नहीं है। वर्तमान में समर्थित फसलें: {crops}।",
    },
    "ml": {
        "eyebrow_system": "ഫീൽഡ് ഡയഗ്നോസ്റ്റിക്സ് സിസ്റ്റം",
        "hero_desc": "രോഗം കണ്ടെത്താനും ചികിത്സാ നിർദ്ദേശം ലഭിക്കാനും വിളയുടെ ഇലയുടെ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക.",
        "current_condition": "നിലവിലെ അവസ്ഥ",
        "location_placeholder": "നിങ്ങളുടെ നഗരം/സ്ഥലം നൽകുക",
        "no_location_msg": "തത്സമയ കാലാവസ്ഥ, ജലസേചന നിർദ്ദേശങ്ങൾ, അനുബന്ധ തീം എന്നിവ കാണാൻ മുകളിൽ നിങ്ങളുടെ സ്ഥലം നൽകുക.",
        "soil_eyebrow": "മണ്ണിലെ ഈർപ്പം",
        "moisture_label": "ഈർപ്പ നില",
        "soil_error": "മണ്ണിലെ ഈർപ്പ ഡാറ്റ ലഭിച്ചില്ല — സെൻസറും ThingSpeak കണക്ഷനും പരിശോധിക്കുക.",
        "weather_eyebrow": "ജലസേചന നിർദ്ദേശം",
        "weather_not_configured": "കാലാവസ്ഥാ സവിശേഷത കോൺഫിഗർ ചെയ്തിട്ടില്ല — ഇത് സജീവമാക്കാൻ ആപ്പ് സീക്രട്ടുകളിൽ OpenWeatherMap API കീ ചേർക്കുക.",
        "weather_error": "ആ സ്ഥലത്തെ കാലാവസ്ഥ ലഭിച്ചില്ല — അക്ഷരവിന്യാസം പരിശോധിക്കുക അല്ലെങ്കിൽ അടുത്തുള്ള വലിയ നഗരത്തിന്റെ പേര് ശ്രമിക്കുക.",
        "upload_label": "ഇലയുടെ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക",
        "uploaded_caption": "അപ്‌ലോഡ് ചെയ്ത ഫോട്ടോ",
        "analyzing_eyebrow": "സാമ്പിൾ വിശകലനം ചെയ്യുന്നു",
        "scan_line1": "ദൃശ്യ സവിശേഷതകൾ എടുക്കുന്നു...",
        "scan_line2": "വിള-രോഗ പ്രൊഫൈലുകളുമായി താരതമ്യം ചെയ്യുന്നു...",
        "scan_line3": "വിശ്വാസ്യതാ സ്കോർ കണക്കാക്കുന്നു...",
        "diagnosis_eyebrow": "രോഗനിർണയം",
        "not_recognized_label": "⚠ വിള തിരിച്ചറിഞ്ഞില്ല",
        "not_recognized_msg": "ഇത് പിന്തുണയ്ക്കുന്ന 14 വിളകളിൽ ({crops}) ഏതെങ്കിലുമായി പൊരുത്തപ്പെടുന്നില്ല. വിശ്വസനീയമായ ഫലത്തിനായി ഈ വിളകളിൽ ഒന്നിന്റെ ഫോട്ടോ ശ്രമിക്കുക.",
        "unlabeled_class_msg": "ഇത് ആപ്പിൽ ഇതുവരെ പേരിടാത്ത ഒരു പുതിയ രോഗ വിഭാഗമായി തോന്നുന്നു (ഇൻഡെക്സ് {idx}). മോഡൽ {conf:.1f}% വിശ്വാസ്യതയോടെ എന്തോ കണ്ടെത്തി, പക്ഷേ ഈ വിഭാഗം ലേബൽ ചെയ്യുന്നത് വരെ വിവരണം ലഭ്യമല്ല.",
        "confidence_label": "വിശ്വാസ്യത",
        "confidence_note": "വിശ്വാസ്യത മിതമായ നിലയിലാണ് — വ്യക്തവും നല്ല വെളിച്ചമുള്ളതുമായ ഒറ്റ ഇലയുടെ ഫോട്ടോ കൃത്യത മെച്ചപ്പെടുത്തിയേക്കാം.",
        "treatment_eyebrow": "ചികിത്സാ പ്രോട്ടോക്കോൾ",
        "what_means_header": "ഇതിന്റെ അർത്ഥം",
        "recommended_action_header": "ശുപാർശ ചെയ്യുന്ന നടപടി",
        "web_searching": "കൂടുതൽ വിവരങ്ങൾക്കായി വെബ് തിരയുന്നു...",
        "web_info_eyebrow": "വെബിൽ നിന്നുള്ള കൂടുതൽ വിവരങ്ങൾ",
        "web_no_results": "വെബ് ഫലങ്ങളൊന്നും കണ്ടെത്തിയില്ല — അൽപ്പസമയം കഴിഞ്ഞ് വീണ്ടും ശ്രമിക്കുക.",
        "footer": "അഗ്രോ എഡ്ജ് // ക്രോപ്പ് ഇന്റലിജൻസ് സിസ്റ്റം // ടീം സൈബർപങ്ക്",
        "last_updated": "അവസാനം അപ്ഡേറ്റ് ചെയ്തത്:",
        "my_farms": "🌾 എന്റെ കൃഷിയിടങ്ങൾ",
        "add_farm": "+ കൃഷിയിടം ചേർക്കുക",
        "farm_name_label": "കൃഷിയിടത്തിന്റെ പേര്",
        "crop_label": "വിള",
        "remove_farm": "നീക്കം ചെയ്യുക",
        "active_farm_label": "സജീവ കൃഷിയിടം",
        "other_crop_option": "മറ്റുള്ളവ (ഇതുവരെ പിന്തുണയ്ക്കുന്നില്ല)",
        "other_crop_placeholder": "നിങ്ങളുടെ വിളയുടെ പേര് നൽകുക",
        "crop_not_supported_note": "{crop}-ന് സ്വയമേവയുള്ള രോഗനിർണയം ഇതുവരെ ലഭ്യമല്ല. നിലവിൽ പിന്തുണയ്ക്കുന്ന വിളകൾ: {crops}.",
    },
    "kn": {
        "eyebrow_system": "ಫೀಲ್ಡ್ ಡಯಾಗ್ನೋಸ್ಟಿಕ್ಸ್ ಸಿಸ್ಟಮ್",
        "hero_desc": "ರೋಗ ಪತ್ತೆ ಮಾಡಲು ಮತ್ತು ಚಿಕಿತ್ಸಾ ಸಲಹೆ ಪಡೆಯಲು ಬೆಳೆಯ ಎಲೆಯ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
        "current_condition": "ಪ್ರಸ್ತುತ ಸ್ಥಿತಿ",
        "location_placeholder": "ನಿಮ್ಮ ನಗರ/ಸ್ಥಳ ನಮೂದಿಸಿ",
        "no_location_msg": "ಲೈವ್ ಹವಾಮಾನ, ನೀರಾವರಿ ಸಲಹೆಗಳು ಮತ್ತು ಸಂಬಂಧಿತ ಥೀಮ್ ನೋಡಲು ಮೇಲೆ ನಿಮ್ಮ ಸ್ಥಳವನ್ನು ನಮೂದಿಸಿ.",
        "soil_eyebrow": "ಮಣ್ಣಿನ ತೇವಾಂಶ",
        "moisture_label": "ತೇವಾಂಶ ಮಟ್ಟ",
        "soil_error": "ಮಣ್ಣಿನ ತೇವಾಂಶ ಡೇಟಾ ಸಿಗಲಿಲ್ಲ — ಸೆನ್ಸಾರ್ ಮತ್ತು ThingSpeak ಸಂಪರ್ಕವನ್ನು ಪರಿಶೀಲಿಸಿ.",
        "weather_eyebrow": "ನೀರಾವರಿ ಸಲಹೆ",
        "weather_not_configured": "ಹವಾಮಾನ ವೈಶಿಷ್ಟ್ಯ ಕಾನ್ಫಿಗರ್ ಆಗಿಲ್ಲ — ಇದನ್ನು ಸಕ್ರಿಯಗೊಳಿಸಲು ಆ್ಯಪ್ ಸೀಕ್ರೆಟ್ಸ್‌ನಲ್ಲಿ OpenWeatherMap API ಕೀ ಸೇರಿಸಿ.",
        "weather_error": "ಆ ಸ್ಥಳದ ಹವಾಮಾನ ಸಿಗಲಿಲ್ಲ — ಕಾಗುಣಿತ ಪರಿಶೀಲಿಸಿ ಅಥವಾ ಹತ್ತಿರದ ದೊಡ್ಡ ನಗರದ ಹೆಸರನ್ನು ಪ್ರಯತ್ನಿಸಿ.",
        "upload_label": "ಎಲೆಯ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "uploaded_caption": "ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಫೋಟೋ",
        "analyzing_eyebrow": "ಮಾದರಿ ವಿಶ್ಲೇಷಣೆ ನಡೆಯುತ್ತಿದೆ",
        "scan_line1": "ದೃಶ್ಯ ಲಕ್ಷಣಗಳನ್ನು ಹೊರತೆಗೆಯಲಾಗುತ್ತಿದೆ...",
        "scan_line2": "ಬೆಳೆ-ರೋಗ ಪ್ರೊಫೈಲ್‌ಗಳೊಂದಿಗೆ ಹೋಲಿಸಲಾಗುತ್ತಿದೆ...",
        "scan_line3": "ವಿಶ್ವಾಸ ಅಂಕವನ್ನು ಲೆಕ್ಕಹಾಕಲಾಗುತ್ತಿದೆ...",
        "diagnosis_eyebrow": "ರೋಗ ನಿರ್ಣಯ",
        "not_recognized_label": "⚠ ಬೆಳೆ ಗುರುತಿಸಲಾಗಲಿಲ್ಲ",
        "not_recognized_msg": "ಇದು ಬೆಂಬಲಿತ 14 ಬೆಳೆಗಳಲ್ಲಿ ({crops}) ಯಾವುದನ್ನೂ ಹೋಲುತ್ತಿಲ್ಲ. ವಿಶ್ವಾಸಾರ್ಹ ಫಲಿತಾಂಶಕ್ಕಾಗಿ ಈ ಬೆಳೆಗಳಲ್ಲಿ ಒಂದರ ಫೋಟೋ ಪ್ರಯತ್ನಿಸಿ.",
        "unlabeled_class_msg": "ಇದು ಆ್ಯಪ್‌ನಲ್ಲಿ ಇನ್ನೂ ಹೆಸರಿಸದ ಹೊಸ ರೋಗ ವರ್ಗದಂತೆ ಕಾಣುತ್ತದೆ (ಇಂಡೆಕ್ಸ್ {idx}). ಮಾದರಿ {conf:.1f}% ವಿಶ್ವಾಸದೊಂದಿಗೆ ಏನನ್ನೋ ಪತ್ತೆ ಮಾಡಿದೆ, ಆದರೆ ಈ ವರ್ಗವನ್ನು ಲೇಬಲ್ ಮಾಡುವವರೆಗೆ ಯಾವುದೇ ವಿವರಣೆ ಲಭ್ಯವಿಲ್ಲ.",
        "confidence_label": "ವಿಶ್ವಾಸ ಮಟ್ಟ",
        "confidence_note": "ವಿಶ್ವಾಸ ಮಟ್ಟ ಮಧ್ಯಮವಾಗಿದೆ — ಸ್ಪಷ್ಟವಾದ, ಚೆನ್ನಾಗಿ ಬೆಳಗಿದ ಒಂದೇ ಎಲೆಯ ಫೋಟೋ ನಿಖರತೆಯನ್ನು ಸುಧಾರಿಸಬಹುದು.",
        "treatment_eyebrow": "ಚಿಕಿತ್ಸಾ ಪ್ರೋಟೋಕಾಲ್",
        "what_means_header": "ಇದರ ಅರ್ಥವೇನು",
        "recommended_action_header": "ಶಿಫಾರಸು ಮಾಡಿದ ಕ್ರಮ",
        "web_searching": "ಹೆಚ್ಚಿನ ಮಾಹಿತಿಗಾಗಿ ವೆಬ್ ಹುಡುಕಲಾಗುತ್ತಿದೆ...",
        "web_info_eyebrow": "ವೆಬ್‌ನಿಂದ ಹೆಚ್ಚಿನ ಮಾಹಿತಿ",
        "web_no_results": "ಯಾವುದೇ ವೆಬ್ ಫಲಿತಾಂಶಗಳು ಕಂಡುಬಂದಿಲ್ಲ — ಸ್ವಲ್ಪ ಸಮಯದ ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
        "footer": "ಅಗ್ರೋ ಎಡ್ಜ್ // ಕ್ರಾಪ್ ಇಂಟೆಲಿಜೆನ್ಸ್ ಸಿಸ್ಟಮ್ // ಟೀಂ ಸೈಬರ್‌ಪಂಕ್",
        "last_updated": "ಕೊನೆಯದಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ:",
        "my_farms": "🌾 ನನ್ನ ಜಮೀನುಗಳು",
        "add_farm": "+ ಜಮೀನು ಸೇರಿಸಿ",
        "farm_name_label": "ಜಮೀನಿನ ಹೆಸರು",
        "crop_label": "ಬೆಳೆ",
        "remove_farm": "ತೆಗೆದುಹಾಕಿ",
        "active_farm_label": "ಸಕ್ರಿಯ ಜಮೀನು",
        "other_crop_option": "ಇತರೆ (ಇನ್ನೂ ಬೆಂಬಲಿತವಲ್ಲ)",
        "other_crop_placeholder": "ನಿಮ್ಮ ಬೆಳೆಯ ಹೆಸರನ್ನು ಬರೆಯಿರಿ",
        "crop_not_supported_note": "{crop} ಗಾಗಿ ಸ್ವಯಂಚಾಲಿತ ರೋಗ ನಿರ್ಣಯ ಇನ್ನೂ ಲಭ್ಯವಿಲ್ಲ. ಪ್ರಸ್ತುತ ಬೆಂಬಲಿತ ಬೆಳೆಗಳು: {crops}.",
    },
    "ta": {
        "eyebrow_system": "களக் கண்டறிதல் அமைப்பு",
        "hero_desc": "நோயைக் கண்டறிந்து சிகிச்சை ஆலோசனை பெற பயிர் இலையின் புகைப்படத்தை பதிவேற்றவும்.",
        "current_condition": "தற்போதைய நிலை",
        "location_placeholder": "உங்கள் நகரம்/இடத்தை உள்ளிடவும்",
        "no_location_msg": "நேரடி வானிலை, பாசன ஆலோசனைகள் மற்றும் பொருந்தும் தீமைக் காண மேலே உங்கள் இடத்தை உள்ளிடவும்.",
        "soil_eyebrow": "மண் ஈரப்பதம்",
        "moisture_label": "ஈரப்பத நிலை",
        "soil_error": "மண் ஈரப்பத தரவு கிடைக்கவில்லை — சென்சார் மற்றும் ThingSpeak இணைப்பை சரிபார்க்கவும்.",
        "weather_eyebrow": "பாசன ஆலோசனை",
        "weather_not_configured": "வானிலை அம்சம் கட்டமைக்கப்படவில்லை — இதை இயக்க ஆப் சீக்ரெட்டுகளில் OpenWeatherMap API கீயைச் சேர்க்கவும்.",
        "weather_error": "அந்த இடத்திற்கான வானிலை கிடைக்கவில்லை — எழுத்துப்பிழையை சரிபார்க்கவும் அல்லது அருகிலுள்ள பெரிய நகரத்தின் பெயரை முயற்சிக்கவும்.",
        "upload_label": "இலையின் புகைப்படத்தை பதிவேற்றவும்",
        "uploaded_caption": "பதிவேற்றப்பட்ட புகைப்படம்",
        "analyzing_eyebrow": "மாதிரி பகுப்பாய்வு செய்யப்படுகிறது",
        "scan_line1": "காட்சி அம்சங்கள் பிரித்தெடுக்கப்படுகின்றன...",
        "scan_line2": "பயிர்-நோய் விவரக்குறிப்புகளுடன் ஒப்பிடப்படுகிறது...",
        "scan_line3": "நம்பகத்தன்மை மதிப்பெண் கணக்கிடப்படுகிறது...",
        "diagnosis_eyebrow": "நோய் கண்டறிதல்",
        "not_recognized_label": "⚠ பயிர் அடையாளம் காணப்படவில்லை",
        "not_recognized_msg": "இது ஆதரிக்கப்படும் 14 பயிர்களில் ({crops}) எதையும் ஒத்திருக்கவில்லை. நம்பகமான முடிவுக்கு இந்த பயிர்களில் ஒன்றின் புகைப்படத்தை முயற்சிக்கவும்.",
        "unlabeled_class_msg": "இது ஆப்பில் இன்னும் பெயரிடப்படாத ஒரு புதிய நோய் வகையாகத் தெரிகிறது (இன்டெக்ஸ் {idx}). மாடல் {conf:.1f}% நம்பகத்தன்மையுடன் ஏதோ கண்டறிந்தது, ஆனால் இந்த வகை லேபிள் செய்யப்படும் வரை விவரம் இல்லை.",
        "confidence_label": "நம்பகத்தன்மை",
        "confidence_note": "நம்பகத்தன்மை மிதமான அளவில் உள்ளது — தெளிவான, நல்ல வெளிச்சமுள்ள ஒரு இலையின் புகைப்படம் துல்லியத்தை மேம்படுத்தலாம்.",
        "treatment_eyebrow": "சிகிச்சை நெறிமுறை",
        "what_means_header": "இதன் பொருள் என்ன",
        "recommended_action_header": "பரிந்துரைக்கப்படும் நடவடிக்கை",
        "web_searching": "மேலும் தகவலுக்காக இணையத்தில் தேடுகிறது...",
        "web_info_eyebrow": "இணையத்திலிருந்து கூடுதல் தகவல்",
        "web_no_results": "இணைய முடிவுகள் எதுவும் கிடைக்கவில்லை — சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்.",
        "footer": "அக்ரோ எட்ஜ் // பயிர் நுண்ணறிவு அமைப்பு // டீம் சைபர்பங்க்",
        "last_updated": "கடைசியாக புதுப்பிக்கப்பட்டது:",
        "my_farms": "🌾 எனது பண்ணைகள்",
        "add_farm": "+ பண்ணை சேர்க்க",
        "farm_name_label": "பண்ணையின் பெயர்",
        "crop_label": "பயிர்",
        "remove_farm": "அகற்று",
        "active_farm_label": "செயலில் உள்ள பண்ணை",
        "other_crop_option": "மற்றவை (இன்னும் ஆதரிக்கப்படவில்லை)",
        "other_crop_placeholder": "உங்கள் பயிரின் பெயரை உள்ளிடவும்",
        "crop_not_supported_note": "{crop}-க்கான தானியங்கி நோய் கண்டறிதல் இன்னும் கிடைக்கவில்லை. தற்போது ஆதரிக்கப்படும் பயிர்கள்: {crops}.",
    },
}


@st.cache_data(show_spinner=False)
def translate_text(text, lang_code):
    """Translate dynamic model output (disease names, descriptions, treatments) into the target language."""
    if lang_code == "en" or not text:
        return text
    try:
        return GoogleTranslator(source="en", target=lang_code).translate(text)
    except Exception:
        return text


st.set_page_config(page_title="Agro Edge", page_icon="🌱", layout="centered")

# ---------------------------------------------------------------------------
# Design system — AgriPulse-inspired glassmorphism, ported for Agro Edge
# ---------------------------------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@500;600&family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">

<style>
:root {
    --bg: #111410;
    --accent: #7DBE6F;
    --accent-2: #a1d494;
    --glow: rgba(125,190,111,0.22);
    --sky-tint: #E0F2F1;
    --harvest-gold: #F2C94C;
    --soil-brown: #4B3621;
    --secondary: #e9c349;
    --text: #e2e3dc;
    --text-muted: #c2c9bb;
    --border: rgba(224,242,241,0.15);
    --surface-highest: #333631;
    --error: #ffb4ab;
    --error-glow: rgba(255,180,171,0.35);
    transition: background-color 0.8s ease;
}

#MainMenu, footer, header { visibility: hidden; }

.material-symbols-outlined {
    font-family: 'Material Symbols Outlined';
    font-weight: normal;
    font-style: normal;
    vertical-align: middle;
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.stApp {
    background:
        linear-gradient(to bottom, rgba(17,20,16,0.4), transparent 40%, rgba(17,20,16,0.85)),
        radial-gradient(circle at top left, color-mix(in srgb, var(--accent) 14%, #14180F) 0%, var(--bg) 60%);
    transition: background-color 0.8s ease;
}
body, [class*="css"] { font-family: 'Hanken Grotesk', sans-serif; color: var(--text); }

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes pulseGlow {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.55; }
}
@keyframes scanSweep {
    0% { left: -30%; }
    100% { left: 110%; }
}
@keyframes growFill {
    from { width: 0%; }
}

/* Glass panel — the core AgriPulse component */
.glass-card {
    background: rgba(255,255,255,0.045);
    backdrop-filter: blur(14px) saturate(150%);
    -webkit-backdrop-filter: blur(14px) saturate(150%);
    border: 1px solid var(--border);
    border-top: 1px solid rgba(255,255,255,0.25);
    border-radius: 16px;
    padding: 1.5rem 1.6rem;
    margin-bottom: 1.1rem;
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.45s ease both;
}

/* Header */
.app-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 0 1.2rem 0;
}
.app-header .material-symbols-outlined { color: var(--accent); font-size: 26px; }
.app-header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent);
    margin: 0;
    font-family: 'Hanken Grotesk', sans-serif;
}

.label-mono {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.label-mono .material-symbols-outlined { font-size: 16px; color: var(--accent-2); }

.data-viz { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: var(--text); }

/* Hero condition card */
.hero-temp {
    font-size: 2.6rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
    margin: 0;
}
.hero-condition {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text-muted);
    margin-left: 0.6rem;
}
.hero-desc-text {
    color: var(--text-muted);
    font-size: 0.95rem;
    margin-top: 0.5rem;
    max-width: 32rem;
    line-height: 1.5;
}

/* Metric tiles (bento) */
.metric-tile { min-height: 128px; display: flex; flex-direction: column; justify-content: space-between; }
.metric-value { font-size: 1.5rem; font-weight: 700; color: var(--text); margin: 0.4rem 0; }
.progress-track {
    width: 100%; height: 8px; background: var(--surface-highest);
    border-radius: 999px; overflow: hidden; border: 1px solid var(--border);
}
.progress-fill { height: 100%; border-radius: 999px; animation: growFill 1s cubic-bezier(0.22,1,0.36,1) both; }

/* Result title (diagnosis) */
.result-title {
    font-family: 'Hanken Grotesk', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 1rem 0;
}

/* Rec grid */
.rec-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.9rem; margin-top: 0.3rem; }
@media (max-width: 640px) { .rec-grid { grid-template-columns: 1fr; } }
.rec-tile {
    padding: 1rem 1.1rem; border-radius: 12px;
    background: rgba(255,255,255,0.03); border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
}
.rec-tile.treatment { border-left-color: var(--accent-2); }
.rec-tile h4 {
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--text-muted); margin: 0 0 0.5rem 0;
}
.rec-tile p { margin: 0; font-size: 0.92rem; line-height: 1.5; color: var(--text); }

/* Unrecognized / error box */
.unrecognized {
    border: 1px solid var(--error-glow);
    background: rgba(255,180,171,0.06);
    border-radius: 12px; padding: 1rem 1.2rem; font-size: 0.92rem; color: var(--text);
}
.unrecognized-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--error); margin-bottom: 0.5rem; font-weight: 600;
}

/* Scan sequence */
.scan-track { position: relative; width: 100%; height: 3px; background: var(--surface-highest);
    border-radius: 2px; overflow: hidden; margin: 0.9rem 0 1rem 0; }
.scan-bar { position: absolute; top: 0; height: 100%; width: 30%;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    animation: scanSweep 1.3s linear infinite; }
.scan-line { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--text-muted);
    margin: 0.3rem 0; animation: pulseGlow 1.6s ease-in-out infinite; }
.scan-line span { color: var(--accent-2); }

/* File uploader */
[data-testid="stFileUploader"] section {
    border: 2px dashed rgba(125,190,111,0.4); border-radius: 14px;
    background: rgba(255,255,255,0.03);
}
[data-testid="stFileUploader"] label p { color: var(--text-muted) !important; }

/* Location input styling */
.loc-wrap input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}

/* Web info links */
.web-link-title { color: var(--accent-2); font-weight: 600; text-decoration: none; font-size: 0.95rem; }
.web-link-body { margin: 0.3rem 0 0 0; font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; }

/* Footer */
.sys-footer {
    font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--text-muted); text-align: center;
    padding: 1.2rem 0 0.5rem 0; border-top: 1px solid var(--border); margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    return tf.keras.models.load_model("plant_model_v5.keras")


def get_weather(city_name, api_key):
    """Fetch current weather for a city using OpenWeatherMap. Returns dict or None on failure."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "appid": api_key, "units": "metric"}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None


def get_irrigation_tip(weather_data):
    """Simple rule-based irrigation advice based on current conditions."""
    condition = weather_data["weather"][0]["main"].lower()
    temp = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"]

    if "rain" in condition or "drizzle" in condition or "thunderstorm" in condition:
        return "🌧️ Rain detected — delay watering to avoid overwatering and root issues."
    elif temp > 32 and humidity < 40:
        return "☀️ Hot and dry conditions — consider watering soon, ideally early morning or evening to reduce evaporation."
    elif humidity > 80:
        return "💧 High humidity — go easy on watering, and monitor for fungal disease risk (many crop diseases spread faster in humid conditions)."
    else:
        return "🌤️ Conditions look moderate — water as per your crop's normal schedule."


def get_soil_moisture():
    """Fetch latest soil moisture reading from ThingSpeak."""
    channel_id = "3467712"
    read_api_key = "GV82FOVOEX7A2MQU"
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json"
    params = {"api_key": read_api_key, "results": 1}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("feeds"):
                return data["feeds"][0]
        return None
    except requests.exceptions.RequestException:
        return None


def gauge_color(pct):
    if pct >= 85:
        return "#7DBE6F"  # sapling green — confident
    elif pct >= 70:
        return "#F2C94C"  # harvest gold — moderate
    else:
        return "#ffb4ab"  # error red — low


def get_weather_theme(condition_main):
    """Map an OpenWeatherMap 'main' condition to a color palette + background effect."""
    c = (condition_main or "").lower()
    if c in ("rain", "drizzle"):
        return {"accent": "#8ED1E8", "accent2": "#E0F2F1", "glow": "rgba(224,242,241,0.22)", "effect": "rain"}
    if c == "thunderstorm":
        return {"accent": "#B39DDB", "accent2": "#9575CD", "glow": "rgba(126,87,194,0.3)", "effect": "thunder"}
    if c == "snow":
        return {"accent": "#E0F2F1", "accent2": "#B8E6E0", "glow": "rgba(224,247,250,0.25)", "effect": "snow"}
    if c == "clear":
        return {"accent": "#F2C94C", "accent2": "#e9c349", "glow": "rgba(242,201,76,0.3)", "effect": "sun"}
    if c == "clouds":
        return {"accent": "#B0BEC5", "accent2": "#90A4AE", "glow": "rgba(176,190,197,0.2)", "effect": "clouds"}
    if c in ("mist", "fog", "haze", "smoke"):
        return {"accent": "#CFD8DC", "accent2": "#B0BEC5", "glow": "rgba(207,216,220,0.18)", "effect": "fog"}
    return None


def render_weather_theme(theme):
    """Override accent CSS variables and add an animated background effect matching the weather."""
    if not theme:
        return

    st.markdown(f"""
    <style>
    :root {{
        --accent: {theme['accent']};
        --accent-2: {theme['accent2']};
        --glow: {theme['glow']};
    }}
    </style>
    """, unsafe_allow_html=True)

    effect = theme["effect"]

    if effect in ("rain", "thunder"):
        drops = ""
        for _ in range(28):
            left = random.uniform(0, 100)
            delay = random.uniform(0, 2)
            duration = random.uniform(0.6, 1.3)
            height = random.uniform(40, 80)
            drops += (f'<div class="raindrop" style="left:{left:.1f}%; height:{height:.0f}px; '
                      f'animation-delay:{delay:.2f}s; animation-duration:{duration:.2f}s;"></div>')
        flash_html = '<div class="lightning-flash"></div>' if effect == "thunder" else ""
        st.markdown(f"""
        <style>
        .weather-overlay {{ position: fixed; top:0; left:0; width:100%; height:100%;
            overflow:hidden; pointer-events:none; z-index:-1; }}
        .raindrop {{ position:absolute; top:-10%; width:1px;
            background:linear-gradient(to bottom, transparent, {theme['accent']});
            animation-name: rainFall; animation-timing-function: linear;
            animation-iteration-count: infinite; opacity:0.5; }}
        @keyframes rainFall {{ from {{ transform: translateY(-10vh); }} to {{ transform: translateY(110vh); }} }}
        .lightning-flash {{ position:fixed; top:0; left:0; width:100%; height:100%;
            background:#fff; opacity:0; animation: flash 7s infinite; pointer-events:none; z-index:999; }}
        @keyframes flash {{ 0%, 95%, 100% {{ opacity:0; }} 96% {{ opacity:0.5; }} 97% {{ opacity:0; }} 98% {{ opacity:0.28; }} }}
        </style>
        <div class="weather-overlay">{drops}</div>
        {flash_html}
        """, unsafe_allow_html=True)

    elif effect == "snow":
        flakes = ""
        for _ in range(22):
            left = random.uniform(0, 100)
            delay = random.uniform(0, 5)
            duration = random.uniform(4, 8)
            size = random.uniform(3, 7)
            flakes += (f'<div class="snowflake" style="left:{left:.1f}%; width:{size:.1f}px; height:{size:.1f}px; '
                       f'animation-delay:{delay:.2f}s; animation-duration:{duration:.2f}s;"></div>')
        st.markdown(f"""
        <style>
        .weather-overlay {{ position: fixed; top:0; left:0; width:100%; height:100%;
            overflow:hidden; pointer-events:none; z-index:-1; }}
        .snowflake {{ position:absolute; top:-5%; border-radius:50%; background:{theme['accent']};
            opacity:0.75; animation-name: snowFall; animation-timing-function: linear;
            animation-iteration-count: infinite; }}
        @keyframes snowFall {{ from {{ transform: translate(0, -10vh); }} to {{ transform: translate(24px, 110vh); }} }}
        </style>
        <div class="weather-overlay">{flakes}</div>
        """, unsafe_allow_html=True)

    elif effect == "sun":
        st.markdown(f"""
        <style>
        .weather-overlay {{ position: fixed; top:-25%; right:-15%; width:60vw; height:60vw;
            pointer-events:none; z-index:-1; border-radius:50%;
            background: radial-gradient(circle, {theme['glow']} 0%, transparent 70%);
            animation: sunPulse 4s ease-in-out infinite; }}
        @keyframes sunPulse {{ 0%,100% {{ opacity:0.75; }} 50% {{ opacity:1; }} }}
        </style>
        <div class="weather-overlay"></div>
        """, unsafe_allow_html=True)

    elif effect in ("clouds", "fog"):
        st.markdown(f"""
        <style>
        .weather-overlay {{ position: fixed; top:0; left:0; width:100%; height:100%;
            overflow:hidden; pointer-events:none; z-index:-1; }}
        .cloud-blob {{ position:absolute; border-radius:50%; background:{theme['glow']};
            filter: blur(30px); animation-name: cloudDrift; animation-timing-function: linear;
            animation-iteration-count: infinite; }}
        @keyframes cloudDrift {{ from {{ transform: translateX(-25vw); }} to {{ transform: translateX(125vw); }} }}
        </style>
        <div class="weather-overlay">
            <div class="cloud-blob" style="top:8%; width:220px; height:80px; animation-duration:38s;"></div>
            <div class="cloud-blob" style="top:28%; width:160px; height:60px; animation-duration:28s; animation-delay:-10s;"></div>
            <div class="cloud-blob" style="top:52%; width:260px; height:90px; animation-duration:45s; animation-delay:-20s;"></div>
        </div>
        """, unsafe_allow_html=True)


WEATHER_ICON_MAP = {
    "rain": "rainy", "drizzle": "rainy", "thunderstorm": "thunderstorm",
    "snow": "ac_unit", "clear": "sunny", "clouds": "cloud",
    "mist": "foggy", "fog": "foggy", "haze": "foggy", "smoke": "foggy",
}


@st.cache_data(show_spinner=False, ttl=3600)
def search_disease_info(query, max_results=3):
    """Search the web for extra info on a detected disease, biased toward plant/agriculture sources."""
    TRUSTED_PLANT_DOMAINS = [
        "extension.org", "apsnet.org", "plantvillage.psu.edu", "ipm.ucanr.edu",
        "rhs.org.uk", "gardeningknowhow.com", "planetnatural.com", "growveg.com",
        "cabi.org", "fao.org", "agriculture.com", "britannica.com", "wikipedia.org",
        "agrilinks.org", "agric.wa.gov.au", "almanac.com", "gardenia.net",
        "missouribotanicalgarden.org", "epicgardening.com", ".edu", ".gov", ".ac.in", ".edu.in",
    ]
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results * 5))
        trusted = [r for r in raw_results if any(d in r.get("href", "").lower() for d in TRUSTED_PLANT_DOMAINS)]
        results = trusted[:max_results] if trusted else raw_results[:max_results]
        return results
    except Exception:
        return []


model = load_model()

# ---------------------------------------------------------------------------
# Language selector
# ---------------------------------------------------------------------------
lang_col, _ = st.columns([1, 2.5])
with lang_col:
    selected_lang_name = st.selectbox("Language", list(LANGUAGES.keys()), label_visibility="collapsed")
lang = LANGUAGES[selected_lang_name]
T = UI_STRINGS[lang]

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="app-header">
    <span class="material-symbols-outlined">eco</span>
    <h1>Agro Edge</h1>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Multi-farm management — lets a user set up separate farms/plots, each
# with its own name, crop, and saved location. Session-based for now
# (resets on page reload); ask about persistent storage if this needs to
# survive across visits.
# ---------------------------------------------------------------------------
if "farms" not in st.session_state:
    st.session_state.farms = [{"id": 0, "name": "Farm 1", "crop": "Tomato", "location": ""}]
    st.session_state.next_farm_id = 1
if "active_farm_id" not in st.session_state:
    st.session_state.active_farm_id = 0

farm_tab_labels = [f["name"] for f in st.session_state.farms]
active_index = next(
    (i for i, f in enumerate(st.session_state.farms) if f["id"] == st.session_state.active_farm_id), 0
)

st.markdown(f'<div class="label-mono">{T["active_farm_label"]}</div>', unsafe_allow_html=True)
tab_cols = st.columns(len(farm_tab_labels) + 1)
for i, farm in enumerate(st.session_state.farms):
    with tab_cols[i]:
        is_active = farm["id"] == st.session_state.active_farm_id
        if st.button(
            farm["name"], key=f"farm_tab_{farm['id']}",
            type="primary" if is_active else "secondary", use_container_width=True,
        ):
            st.session_state.active_farm_id = farm["id"]
            st.rerun()
with tab_cols[-1]:
    if st.button(T["add_farm"], key="add_farm_btn", use_container_width=True):
        new_id = st.session_state.next_farm_id
        st.session_state.farms.append({
            "id": new_id, "name": f"Farm {len(st.session_state.farms) + 1}",
            "crop": "Tomato", "location": "",
        })
        st.session_state.next_farm_id += 1
        st.session_state.active_farm_id = new_id
        st.rerun()

active_farm = st.session_state.farms[active_index]

with st.expander(f"⚙️ {T['my_farms']}", expanded=False):
    crop_options = SUPPORTED_CROP_LIST + [T["other_crop_option"]]
    new_name = st.text_input(T["farm_name_label"], value=active_farm["name"], key=f"farm_name_{active_farm['id']}")
    current_crop_is_custom = active_farm["crop"] not in SUPPORTED_CROP_LIST
    default_crop_index = len(SUPPORTED_CROP_LIST) if current_crop_is_custom else SUPPORTED_CROP_LIST.index(active_farm["crop"])
    selected_crop = st.selectbox(T["crop_label"], crop_options, index=default_crop_index, key=f"farm_crop_{active_farm['id']}")
    if selected_crop == T["other_crop_option"]:
        custom_crop = st.text_input(
            T["other_crop_placeholder"],
            value=active_farm["crop"] if current_crop_is_custom else "",
            key=f"farm_custom_crop_{active_farm['id']}",
        )
        active_farm["crop"] = custom_crop if custom_crop else active_farm["crop"]
    else:
        active_farm["crop"] = selected_crop
    active_farm["name"] = new_name

    if len(st.session_state.farms) > 1:
        if st.button(f"🗑️ {T['remove_farm']}", key=f"remove_farm_{active_farm['id']}"):
            st.session_state.farms = [f for f in st.session_state.farms if f["id"] != active_farm["id"]]
            st.session_state.active_farm_id = st.session_state.farms[0]["id"]
            st.rerun()

# ---------------------------------------------------------------------------
# Location input — drives both the weather theme and the irrigation tip.
# Pre-filled from (and saved back to) the active farm.
# ---------------------------------------------------------------------------
st.markdown('<div class="loc-wrap">', unsafe_allow_html=True)
city = st.text_input(
    "Location", value=active_farm["location"],
    placeholder=f"📍 {T['location_placeholder']}", label_visibility="collapsed",
    key=f"location_input_{active_farm['id']}",
)
active_farm["location"] = city
st.markdown('</div>', unsafe_allow_html=True)

weather_data = None
weather_configured = True
if city:
    api_key = st.secrets.get("OPENWEATHER_API_KEY", None)
    if not api_key:
        weather_configured = False
    else:
        weather_data = get_weather(city, api_key)
        if weather_data:
            theme = get_weather_theme(weather_data["weather"][0]["main"])
            render_weather_theme(theme)

# ---------------------------------------------------------------------------
# Hero condition card
# ---------------------------------------------------------------------------
if weather_data:
    temp = weather_data["main"]["temp"]
    condition_raw = weather_data["weather"][0]["main"]
    condition_desc = weather_data["weather"][0]["description"].title()
    icon = WEATHER_ICON_MAP.get(condition_raw.lower(), "eco")
    condition_t = translate_text(condition_desc, lang)
    st.markdown(f"""
    <div class="glass-card">
        <div class="label-mono"><span class="material-symbols-outlined">location_on</span>{city}</div>
        <div style="display:flex; align-items:center; gap:0.8rem;">
            <span class="material-symbols-outlined" style="font-size:44px; color:var(--accent);">{icon}</span>
            <span class="hero-temp">{temp:.0f}°C</span>
            <span class="hero-condition">{condition_t}</span>
        </div>
        <p class="hero-desc-text">{T['hero_desc']}</p>
    </div>
    """, unsafe_allow_html=True)
elif city and not weather_configured:
    st.markdown(f"""
    <div class="glass-card">
        <p class="hero-desc-text">{T['weather_not_configured']}</p>
    </div>
    """, unsafe_allow_html=True)
elif city:
    st.markdown(f"""
    <div class="glass-card">
        <p class="hero-desc-text">{T['weather_error']}</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="glass-card">
        <div class="label-mono"><span class="material-symbols-outlined">eco</span>{T['eyebrow_system']}</div>
        <p class="hero-desc-text">{T['hero_desc']} {T['no_location_msg']}</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Bento tiles — Soil Moisture + Irrigation Tip (real data only, no mock metrics)
# ---------------------------------------------------------------------------
tile1, tile2 = st.columns(2)

with tile1:
    soil_data = get_soil_moisture()
    if soil_data and soil_data.get("field1") is not None:
        moisture = float(soil_data["field1"])
        timestamp = soil_data["created_at"]
        color = gauge_color(moisture)
        st.markdown(f"""
        <div class="glass-card metric-tile">
            <div class="label-mono"><span class="material-symbols-outlined">water_drop</span>{T['soil_eyebrow']}</div>
            <div class="metric-value">{moisture:.0f}%</div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{moisture:.0f}%; background:{color};"></div>
            </div>
            <p class="label-mono" style="margin-top:0.6rem; margin-bottom:0;">{T['last_updated']} {timestamp}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="glass-card metric-tile">
            <div class="label-mono"><span class="material-symbols-outlined">water_drop</span>{T['soil_eyebrow']}</div>
            <p class="hero-desc-text" style="margin-top:0.4rem;">{T['soil_error']}</p>
        </div>
        """, unsafe_allow_html=True)

with tile2:
    if not city:
        tip_body = T["no_location_msg"]
    elif not weather_configured:
        tip_body = T["weather_not_configured"]
    elif weather_data:
        tip_raw = get_irrigation_tip(weather_data)
        tip_body = translate_text(tip_raw, lang)
    else:
        tip_body = T["weather_error"]
    st.markdown(f"""
    <div class="glass-card metric-tile">
        <div class="label-mono"><span class="material-symbols-outlined">agriculture</span>{T['weather_eyebrow']}</div>
        <p class="hero-desc-text" style="margin-top:0.4rem;">{tip_body}</p>
    </div>
    """, unsafe_allow_html=True)


if active_farm["crop"] not in SUPPORTED_CROP_LIST:
    st.info(T["crop_not_supported_note"].format(crop=active_farm["crop"], crops=SUPPORTED_CROPS))

uploaded_file = st.file_uploader(T["upload_label"], type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption=T["uploaded_caption"], use_container_width=True)

    # Preprocess exactly like training: resize to 224x224
    img_resized = image.resize((224, 224))
    img_array = np.array(img_resized)
    img_array = np.expand_dims(img_array, axis=0)  # add batch dimension

    scan_placeholder = st.empty()
    scan_placeholder.markdown(f"""
    <div class="glass-card">
        <div class="label-mono"><span class="material-symbols-outlined">search</span>{T['analyzing_eyebrow']}</div>
        <div class="scan-track"><div class="scan-bar"></div></div>
        <div class="scan-line">&gt; <span>{T['scan_line1']}</span></div>
        <div class="scan-line">&gt; <span>{T['scan_line2']}</span></div>
        <div class="scan-line">&gt; <span>{T['scan_line3']}</span></div>
    </div>
    """, unsafe_allow_html=True)

    predictions = model.predict(img_array)
    predicted_index = int(np.argmax(predictions[0]))
    confidence = 100 * float(np.max(predictions[0]))
    predicted_class, is_named = get_class_display_name(predicted_index)

    time.sleep(0.4)  # let the scan animation register before revealing the result
    scan_placeholder.empty()

    if not is_named:
        # Model predicted a class outside the currently-named list (e.g. v5's 38-54)
        st.markdown(f"""
        <div class="glass-card">
            <div class="label-mono"><span class="material-symbols-outlined">warning</span>{T['diagnosis_eyebrow']}</div>
            <div class="unrecognized">
                {T['unlabeled_class_msg'].format(idx=predicted_index, conf=confidence)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        display_name = predicted_class.replace("___", " - ").replace("__", " ").replace("_", " ")
        display_name_t = translate_text(display_name, lang)

        if confidence < 70:
            not_recognized_msg_t = T["not_recognized_msg"].format(crops=SUPPORTED_CROPS)
            st.markdown(f"""
            <div class="glass-card">
                <div class="label-mono"><span class="material-symbols-outlined">warning</span>{T['diagnosis_eyebrow']}</div>
                <div class="unrecognized">
                    <div class="unrecognized-label">{T['not_recognized_label']}</div>
                    {not_recognized_msg_t}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            color = gauge_color(confidence)
            confidence_note = "" if confidence >= 85 else f'<p class="hero-desc-text" style="margin-top:0.8rem;">{T["confidence_note"]}</p>'

            st.markdown(f"""
            <div class="glass-card">
                <div class="label-mono"><span class="material-symbols-outlined">biotech</span>{T['diagnosis_eyebrow']}</div>
                <div class="result-title">{display_name_t}</div>
                <div class="label-mono" style="justify-content:space-between; margin-bottom:0.4rem;">
                    <span>{T['confidence_label']}</span><span class="data-viz">{confidence:.1f}%</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:{confidence:.1f}%; background:{color};"></div>
                </div>
                {confidence_note}
            </div>
            """, unsafe_allow_html=True)

            info = RECOMMENDATIONS.get(predicted_class)
            if info:
                description_t = translate_text(info["description"], lang)
                treatment_t = translate_text(info["treatment"], lang)
                st.markdown(f"""
                <div class="glass-card">
                    <div class="label-mono"><span class="material-symbols-outlined">medical_information</span>{T['treatment_eyebrow']}</div>
                    <div class="rec-grid">
                        <div class="rec-tile">
                            <h4>{T['what_means_header']}</h4>
                            <p>{description_t}</p>
                        </div>
                        <div class="rec-tile treatment">
                            <h4>{T['recommended_action_header']}</h4>
                            <p>{treatment_t}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with st.spinner(T["web_searching"]):
                search_query = f"{display_name} plant disease symptoms causes treatment agriculture botany -software -app -company"
                web_results = search_disease_info(search_query)
            if web_results:
                st.markdown(f'<div class="glass-card"><div class="label-mono"><span class="material-symbols-outlined">travel_explore</span>{T["web_info_eyebrow"]}</div>', unsafe_allow_html=True)
                for r in web_results:
                    title = r.get("title", "")
                    link = r.get("href", "")
                    body = r.get("body", "")[:200]
                    title_t = translate_text(title, lang)
                    body_t = translate_text(body, lang)
                    st.markdown(f"""
                    <div style="margin-bottom:0.9rem; padding-bottom:0.9rem; border-bottom:1px solid var(--border);">
                        <a href="{link}" target="_blank" class="web-link-title">{title_t}</a>
                        <p class="web-link-body">{body_t}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning(T["web_no_results"])

st.markdown(f'<div class="sys-footer">{T["footer"]}</div>', unsafe_allow_html=True)
