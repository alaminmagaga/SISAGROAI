import streamlit as st
import os
import google.generativeai as genai
from pathlib import Path
from PIL import Image
import tempfile

# ✅ Set Gemini API key
os.environ["GENERATIVEAI_API_KEY"] = "AIzaSyA9d_mJIx2gxeBS-4wJi766eukWD8Q3MXk"
genai.configure(api_key=os.environ["GENERATIVEAI_API_KEY"])

# ✅ Configure Gemini Model
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {"category": f"HARM_CATEGORY_{category}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    for category in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# ✅ Prompt
input_prompt = """
As a highly skilled plant pathologist, your expertise is indispensable in our pursuit of maintaining optimal plant health. You will be provided with information or samples related to plant diseases, and your role involves conducting a detailed analysis to identify the specific issues, propose solutions, and offer recommendations.

**Analysis Guidelines:**

1. **Disease Identification:** Examine the provided information or samples to identify and characterize plant diseases accurately.

2. **Detailed Findings:** Provide in-depth findings on the nature and extent of the identified plant diseases, including affected plant parts, symptoms, and potential causes.

3. **Next Steps:** Outline the recommended course of action for managing and controlling the identified plant diseases. This may involve treatment options, preventive measures, or further investigations.

4. **Recommendations:** Offer informed recommendations for maintaining plant health, preventing disease spread, and optimizing overall plant well-being.

5. **Important Note:** As a plant pathologist, your insights are vital for informed decision-making in agriculture and plant management. Your response should be thorough, concise, and focused on plant health.

**Disclaimer:**
*"Please note that the information provided is based on plant pathology analysis and should not replace professional agricultural advice. Consult with qualified agricultural experts before implementing any strategies or treatments."*

Your role is pivotal in ensuring the health and productivity of plants. Proceed to analyze the provided information or samples, adhering to the structured. Do not mention any Plant Pathologist Name, Date or References Id etc. Try to mention the disease name.
"""

# ✅ Read image
def read_image_data(file_path):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {file_path}")
    return {"mime_type": "image/jpeg", "data": path.read_bytes()}

# ✅ Gemini Response Function
def generate_gemini_response(image_path):
    image_data = read_image_data(image_path)
    response = model.generate_content([input_prompt, image_data])
    return response.text

# ✅ Streamlit UI
st.set_page_config(page_title="Plant Disease Diagnosis", layout="centered")
st.title("🌿 Plant Disease Diagnosis using Gemini Pro Vision")
st.markdown("Upload a photo of a plant leaf to detect possible diseases.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    if st.button("🔍 Analyze Plant Health"):
        with st.spinner("Processing image with Gemini Pro Vision..."):
            try:
                result = generate_gemini_response(tmp_path)
                st.success("✅ Analysis Complete!")
                st.markdown("### 🧪 Diagnosis Result")
                st.write(result)
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
