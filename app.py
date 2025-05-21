import streamlit as st
import os
import google.generativeai as genai
from pathlib import Path
import tempfile
from deep_translator import GoogleTranslator

# ✅ Set up Gemini API
os.environ["GENERATIVEAI_API_KEY"] = "AIzaSyA9d_mJIx2gxeBS-4wJi766eukWD8Q3MXk"
genai.configure(api_key=os.environ["GENERATIVEAI_API_KEY"])

generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {"category": f"HARM_CATEGORY_{cat}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    for cat in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# ✅ English Prompts
auto_description_prompt = """
You are a plant expert. Look at the image and write a short, clear paragraph to describe what you see.

In your description, include (if visible):
- The name or type of the plant
- What the plant looks like (size, shape, color, health)
- What the soil looks like (dry, wet, cracked, etc.)
- Whether the soil looks rich or poor

Only write one simple paragraph. Use plain English.
"""

disease_analysis_template = """
The following is a description of the plant image:

"{description}"

Now, examine the image again and analyze it for any plant diseases or nutrient deficiencies.

Only report a problem if you clearly see one. If the plant looks healthy, say so clearly.

**Instructions:**
1. If you see a disease or deficiency, name it and explain the symptoms you observe.
2. Describe the likely cause.
3. Suggest what to do next (treatment or care tips), and specifically:
   - Mention **popular brand names or generic names of insecticides, fungicides, or fertilizers** commonly used for the issue.
   - If the disease is fungal, recommend at least one fungicide (e.g., **Ridomil, Mancozeb, Copper-based fungicide**).
   - If it's a pest, suggest an insecticide (e.g., **Cypermethrin, Confidor, Lambda-Cyhalothrin**).
   - For nutrient deficiencies, suggest specific types of fertilizer (e.g., **urea for nitrogen, NPK 15:15:15**, etc.)

4. If the plant looks healthy, just say it is healthy and no treatment is needed.

Use clear and simple language.
"""

# ✅ Helper Functions
def read_image_data(file_path):
    path = Path(file_path)
    return {"mime_type": "image/jpeg", "data": path.read_bytes()}

def generate_auto_description(image_path):
    image_data = read_image_data(image_path)
    response = model.generate_content([auto_description_prompt, image_data])
    return response.text.strip()

def generate_disease_diagnosis(image_path, description):
    image_data = read_image_data(image_path)
    combined_prompt = disease_analysis_template.replace("{description}", description)
    response = model.generate_content([combined_prompt, image_data])
    return response.text.strip()

def translate_to_hausa(text):
    try:
        return GoogleTranslator(source='auto', target='ha').translate(text)
    except Exception as e:
        return f"⚠️ Failed to translate: {e}"

# ✅ Streamlit App
st.set_page_config(page_title="🌿 SISAGROAI", layout="centered")
lang = st.sidebar.radio("🌐 Choose Language / Zaɓi Harshe", ["English", "Hausa"])

image_path = None
plant_description = None

# UI Layout by Language
if lang == "English":
    st.markdown("""
    # 👋 Welcome to **SISAGRO-AI**
    ### 🧑‍🌾 The Best Doctor for Your Plant

    Upload or snap a plant image to get:
    - Instant analysis
    - Disease or deficiency detection
    - Treatment suggestions with real product names
    """)

    upload_method = st.radio("Choose image input method", ["📷 Camera", "🖼 Upload Image"])
    capture_label = "Capture plant image"
    upload_label = "Upload plant image"
    summary_label = "📋 Plant Summary"
    analysis_button = "🔬 Analyze for Plant Diseases"
    result_label = "🧪 Disease Analysis Result"

else:
    st.markdown("""
    # 👋 Maraba da zuwa **SISAGRO-AI**
    ### 🧑‍🌾 Likitan Shuka Mafi Inganci

    Ɗora ko ɗauki hoton shuka domin:
    - Nazarin lafiyar shuka
    - Gano cuta ko rashin sinadaran gina jiki
    - Samun shawarwarin magani da sunan kaya
    """)

    upload_method = st.radio("Zaɓi hanyar ɗora hoto", ["📷 Dauki Hoto", "🖼 Ɗora Hoto"])
    capture_label = "Dauki hoton shuka"
    upload_label = "Ɗora hoton shuka"
    summary_label = "📋 Bayanin Shuka"
    analysis_button = "🔬 Binciken Cutar Shuka"
    result_label = "🧪 Sakamakon Nazari"

# Image Upload Handling
if upload_method.startswith("📷"):
    image = st.camera_input(capture_label)
    if image:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(image.getvalue())
            image_path = f.name
else:
    uploaded = st.file_uploader(upload_label, type=["jpg", "jpeg", "png"])
    if uploaded:
        st.image(uploaded, caption="🖼 Uploaded Image", use_column_width=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(uploaded.read())
            image_path = f.name

# ✅ Generate Description
if image_path:
    with st.spinner("🔍 Generating plant summary..."):
        try:
            plant_description = generate_auto_description(image_path)
            st.success("✅ Summary generated")
            st.markdown(f"### {summary_label}")
            st.write(translate_to_hausa(plant_description) if lang == "Hausa" else plant_description)
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# ✅ Analyze Disease
if plant_description:
    if st.button(analysis_button):
        with st.spinner("🔎 Analyzing plant health..."):
            try:
                diagnosis = generate_disease_diagnosis(image_path, plant_description)
                st.success("✅ Analysis Complete")
                st.markdown(f"### {result_label}")
                st.write(translate_to_hausa(diagnosis) if lang == "Hausa" else diagnosis)
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
