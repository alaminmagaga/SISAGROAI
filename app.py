import streamlit as st
import os
import google.generativeai as genai
from pathlib import Path
from PIL import Image
import tempfile

# ✅ Configure Gemini API
os.environ["GENERATIVEAI_API_KEY"] = "AIzaSyA9d_mJIx2gxeBS-4wJi766eukWD8Q3MXk"
genai.configure(api_key=os.environ["GENERATIVEAI_API_KEY"])

# ✅ Gemini model setup
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

# ✅ Plant analysis prompt
input_prompt = """
As a highly skilled plant pathologist, your expertise is indispensable...
(keep your existing prompt content here)
"""

# ✅ Read image helper
def read_image_data(file_path):
    path = Path(file_path)
    return {"mime_type": "image/jpeg", "data": path.read_bytes()}

# ✅ Generate response
def generate_gemini_response(image_path):
    image_data = read_image_data(image_path)
    response = model.generate_content([input_prompt, image_data])
    return response.text

# ✅ Streamlit UI
st.set_page_config(page_title="Plant Disease Diagnosis", layout="centered")
st.title("🌿 Plant Disease Diagnosis")
st.markdown("Upload a photo or take one with your camera to detect plant diseases.")

# ✅ Upload or use camera
upload_option = st.radio("Choose input method:", ["📷 Take Photo (Camera)", "🖼 Upload Image"])

image_path = None

if upload_option == "📷 Take Photo (Camera)":
    camera_img = st.camera_input("Take a photo of the plant leaf")
    if camera_img:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(camera_img.getvalue())
            image_path = f.name

elif upload_option == "🖼 Upload Image":
    uploaded_img = st.file_uploader("Upload an image of the leaf", type=["jpg", "jpeg", "png"])
    if uploaded_img:
        st.image(uploaded_img, caption="Uploaded Image", use_column_width=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(uploaded_img.read())
            image_path = f.name

# ✅ Trigger analysis
if image_path and st.button("🔍 Analyze Plant Health"):
    with st.spinner("Analyzing with Gemini Pro Vision..."):
        try:
            result = generate_gemini_response(image_path)
            st.success("✅ Analysis Complete!")
            st.markdown("### 🧪 Diagnosis Result")
            st.write(result)
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
