import streamlit as st
import os
import google.generativeai as genai
from pathlib import Path
import tempfile
from PIL import Image

# ✅ Set up Gemini API
os.environ["GENERATIVEAI_API_KEY"] = "AIzaSyBtiWaiaSSEMj_sqjPqCVdvBtr9BT54QnM"
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

# ✅ Streamlit Page Config
st.set_page_config(page_title="🌿 SISAGRO-AI", layout="centered")

# ✅ Header Styling + Embedded Logo
st.markdown("""
    <style>
    body {
        background-color: #e6f4ea; /* Plant-themed light green */
    }
    .main-header {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        color: #14532d; /* Dark green text */
        background-color: #bbf7d0; /* Soft green banner */
        padding: 10px 10px 5px 10px;
        border-radius: 12px 12px 0 0;
    }
    .main-header img {
        vertical-align: middle;
        width: 50px;
        height: 50px;
        margin-right: 10px;
        border-radius: 50%;
    }
    .sub-header {
        text-align: center;
        font-size: 18px;
        font-weight: 500;
        color: #064e3b;
        background-color: #bbf7d0;
        padding: 5px 10px;
        border-radius: 0 0 12px 12px;
    }
    </style>
""", unsafe_allow_html=True)

# ✅ Logo Path (ensure file exists at this path)
logo_path = "static/logo.png"
logo_html = f'<img src="data:image/png;base64,{Path(logo_path).read_bytes().hex()}" />' if os.path.exists(logo_path) else ''

# ✅ Header Content with Logo
if os.path.exists(logo_path):
    import base64
    with open(logo_path, "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <div class="main-header">
            <img src="data:image/png;base64,{logo_data}" alt="Logo" />
            SISAGRO-AI
        </div>
        <div class="sub-header">
            AI-Powered Diagnosis & Fertilizer Suggestions for Healthy Crops
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="main-header">🌿 SISAGRO-AI</div>
        <div class="sub-header">
    The Best Doctor for your Plant Health  — Get instant analysis, detect diseases and deficiencies, and receive tailored treatment advice.<br></div>
    <br>""", unsafe_allow_html=True)

# ✅ Prompts
auto_description_prompt = """
Analyze the entire plant from top to bottom. Identify and correctly name the plant. 
Provide a short and accurate description, including details of all visible parts 
(leaves, stem, flowers, fruits, and roots if visible). Assess the overall health and 
condition of the plant, including any signs of disease, pests, or deficiencies. 
Additionally, examine and describe the nature and condition of the surrounding soil.
"""

disease_analysis_template = """
The following is a description of the plant image:

"{description}"

Now, carefully examine the plant for any signs of disease, stress, or deficiency. 
Determine whether the plant is lacking water or experiencing overwatering. 
Assess whether the plant currently requires fertilizer based on its condition. 
If fertilizer is needed, recommend the specific type and formulation suitable 
for the plant's current growth stage.

Only report a problem if you clearly see one. If the plant looks healthy, say so clearly.

**Instructions:**
1. If you see a disease or deficiency, name it and explain the symptoms you observe.
2. Describe the likely cause.
3. Suggest what to do next (treatment or care tips), and specifically:
   - Mention **popular brand names or generic names of insecticides, fungicides, or fertilizers** commonly used for the issue.
   - If the disease is fungal, recommend at least one fungicide.
   - If it's a pest, suggest an insecticide.
   - For nutrient deficiencies, suggest specific types of fertilizer.

4. If the plant looks healthy, just say it is healthy and no treatment is needed.

Use clear and simple language.
"""

hausa_auto_description_prompt = """
You are a plant expert. Summarize what you observe in the image in one short, clear, plain English paragraph. Focus on:
- General appearance of the plant
- Health condition
- Basic visible parts (e.g., leaves, stem, soil)
Keep the paragraph short and easy to translate into Hausa. Do not use technical terms.
"""

hausa_disease_analysis_prompt = """
You are a plant doctor. Based on the description:

"{description}"

Write two short and clear paragraphs in simple English.

1. First paragraph: Mention if the plant is healthy or if there are any signs of stress, disease, pest, or nutrient issues.
2. Second paragraph: Give one or two care suggestions like water needs, fertilizer type, or treatment if needed.

Avoid complex words. Keep it easy for rural farmers or general audience to understand.
"""

# ✅ Translation
def translate_to_hausa(text):
    try:
        translation_prompt = f"""
        Translate the following English text to Hausa language:

        "{text}"

        Provide ONLY the Hausa translation with no additional text or explanations.
        """
        translation_response = model.generate_content(translation_prompt)
        return translation_response.text.strip()
    except Exception as e:
        st.warning(f"Translation service temporarily unavailable. Showing English version.")
        return text

# ✅ Core functions
def read_image_data(file_path):
    path = Path(file_path)
    return {"mime_type": "image/jpeg", "data": path.read_bytes()}

def generate_auto_description(image_path, lang="English"):
    image_data = read_image_data(image_path)
    prompt = hausa_auto_description_prompt if lang == "Hausa" else auto_description_prompt
    response = model.generate_content([prompt, image_data])
    return response.text.strip()

def generate_disease_diagnosis(image_path, description, lang="English"):
    image_data = read_image_data(image_path)
    prompt = (
        hausa_disease_analysis_prompt.replace("{description}", description)
        if lang == "Hausa"
        else disease_analysis_template.replace("{description}", description)
    )
    response = model.generate_content([prompt, image_data])
    return response.text.strip()

# ✅ Language and UI
lang = st.sidebar.radio("🌐 Choose Language / Zaɓi Harshe", ["English", "Hausa"])

image_path = None
plant_description = None



    # Instruction Section


# UI Labels and Instruction Block
if lang == "English":
    st.markdown("""
    ### How to Use
    Upload or snap the plant image to get:
    - Instant analysis
    - Disease, deficiency, or abnormality detection
    - Growth-stage fertilizer recommendations
    """)

    upload_method = st.radio("Choose image input method", ["📷 Camera", "🖼 Upload Image"])
    capture_label = "Capture plant image"
    upload_label = "Upload plant image"
    summary_label = "📋 Plant Summary"
    analysis_button = "🔬 Analyze the Plant Abnormalities"
    result_label = "🧪 Abnormality Analysis Result"
    summary_generated = "✅ Summary generated"
    generating_summary = "🔍 Generating plant summary..."
    analysis_complete = "✅ Analysis Complete"

else:
    st.markdown("""
    ### Yadda Ake Amfani
    Ɗora ko ɗauki hoton shuka domin:
    - Samun bayani kai tsaye
    - Gano cuta, matsaloli, ko rashin gina jiki
    - Shawarar takin zamani da ya dace da matakin girma
    """)

    upload_method = st.radio("Zaɓi hanyar ɗora hoto", ["📷 Dauki Hoto", "🖼 Ɗora Hoto"])
    capture_label = "Dauki hoton shuka"
    upload_label = "Ɗora hoton shuka"
    summary_label = "📋 Bayanin Shuka"
    analysis_button = "🔬 Binciken Matsalolin Shuka"
    result_label = "🧪 Sakamakon Nazari"
    summary_generated = "✅ An gama fitar da bayani"
    generating_summary = "🔍 Ana fitar da bayanin shuka..."
    analysis_complete = "✅ An gama bincike"

    # Hausa Instructions
    


# ✅ Image Input
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

# ✅ Auto Summary
if image_path:
    with st.spinner(generating_summary):
        try:
            plant_description = generate_auto_description(image_path, lang=lang)
            st.success(summary_generated)
            st.markdown(f"### {summary_label}")
            st.write(translate_to_hausa(plant_description) if lang == "Hausa" else plant_description)
        except Exception as e:
            st.error(f"⚠️ Error: {e}")


# ✅ Disease Analysis
if plant_description:
    if st.button(analysis_button):
        with st.spinner("🔎 Analyzing plant health..."):
            try:
                diagnosis = generate_disease_diagnosis(image_path, plant_description, lang=lang)
                st.success(analysis_complete)
                st.markdown(f"### {result_label}")
                st.write(translate_to_hausa(diagnosis) if lang == "Hausa" else diagnosis)
            except Exception as e:
                st.error(f"⚠️ Error: {e}")

