import streamlit as st
import os
import google.generativeai as genai
from pathlib import Path
import tempfile

# ✅ Set up Gemini API
os.environ["GENERATIVEAI_API_KEY"] = "AIzaSyA9d_mJIx2gxeBS-4wJi766eukWD8Q3MXk"
genai.configure(api_key=os.environ["GENERATIVEAI_API_KEY"])


# ✅ Gemini configuration
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

# ✅ Prompts
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

Keep the language clear and easy to understand for farmers or plant owners. Do not include scientific jargon or advanced terminology.
"""


# ✅ Helper functions
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

st.set_page_config(page_title="🌿 SISAGROAI: Plant Doctor", layout="centered")

# 🌱 SISAGROAI Welcome Message
st.markdown("""
# 👋 Welcome to **SISAGRO-AI**
### 🧑‍🌾 The Best Doctor for Your Plant 🌿

Please **snap a picture** or **upload a plant leaf image** to get a summary and expert diagnosis.

SISAGROAI helps you:
- 📷 Analyze your plant's condition instantly
- 🪴 Detect diseases or nutrient issues
- 💊 Get treatment advice with real product names
""")

# st.title("📸 Plant Summary & Disease Diagnosis")

# ✅ Streamlit app
# st.set_page_config(page_title="🌿 Plant Diagnosis", layout="centered")
# st.title("🌿 Plant Summary & Disease Diagnosis")
# st.markdown("Upload or capture a photo of a plant to receive a summary and health analysis.")

upload_method = st.radio("Choose image input method", ["📷 Camera", "🖼 Upload Image"])

image_path = None
plant_description = None

if upload_method == "📷 Camera":
    image = st.camera_input("Capture plant image")
    if image:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(image.getvalue())
            image_path = f.name

elif upload_method == "🖼 Upload Image":
    uploaded = st.file_uploader("Upload plant image", type=["jpg", "jpeg", "png"])
    if uploaded:
        st.image(uploaded, caption="Uploaded Image", use_column_width=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(uploaded.read())
            image_path = f.name

# ✅ Auto description
if image_path:
    with st.spinner("🔍 Generating plant summary..."):
        try:
            plant_description = generate_auto_description(image_path)
            st.success("✅ Summary generated")
            st.markdown("### 📋 Plant Summary")
            st.write(plant_description)
        except Exception as e:
            st.error(f"Error generating plant description: {e}")

# ✅ Disease analysis button
if plant_description:
    if st.button("🔬 Analyze for Plant Diseases"):
        with st.spinner("Analyzing image for plant health..."):
            try:
                diagnosis = generate_disease_diagnosis(image_path, plant_description)
                st.success("✅ Detailed Diagnosis Complete!")
                st.markdown("### 🧪 Disease Analysis Result")
                st.write(diagnosis)
            except Exception as e:
                st.error(f"Error during analysis: {e}")
