import streamlit as st
import os
import google.generativeai as genai
from pathlib import Path
import tempfile
import platform

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

# SISAGROAI Welcome Message
st.markdown("""
# 👋 Welcome to **SISAGRO-AI**
### 🧑‍🌾 The Best Doctor for Your Plant 

Please **snap the picture** or **upload the plant image** to get a summary and expert diagnosis.

SISAGRO-AI helps you to:
- Analyze your plant's condition instantly
- Detect diseases or nutrient issues
- Get treatment advice with real product names

Note: We are always improving our system to keep you upto date
""")

# ✅ Detect device type (simple fallback: mobile = Android or iOS)
user_agent = st.session_state.get("user_agent", platform.platform().lower())
mobile_device = any(x in user_agent for x in ["android", "iphone", "ipad"])

image_path = None
plant_description = None

if mobile_device:
    st.info("📱 Mobile device detected: using back camera with zoom.")
    st.components.v1.html("""
    <video id=\"video\" autoplay playsinline style=\"width:100%; max-width: 100%; border: 2px solid green; border-radius: 8px;\"></video><br>
    <input type=\"range\" id=\"zoom\" min=\"1\" max=\"3\" step=\"0.1\" value=\"1\" onchange=\"setZoom(this.value)\" style=\"width: 100%\"><br>
    <button onclick=\"takePhoto()\" style=\"padding: 10px 20px; font-size: 16px;\">\ud83d\udcf8 Take Photo</button>
    <canvas id=\"canvas\" style=\"display: none;\"></canvas>
    <script>
      let stream;
      const video = document.getElementById('video');
      const canvas = document.getElementById('canvas');
      const context = canvas.getContext('2d');
      const zoomControl = document.getElementById('zoom');

      async function initCamera() {
        try {
          stream = await navigator.mediaDevices.getUserMedia({
            video: {
              facingMode: { exact: 'environment' },
              zoom: { ideal: 2 }
            },
            audio: false
          });
          video.srcObject = stream;
        } catch (err) {
          alert("Error accessing camera: " + err.message);
        }
      }

      function setZoom(zoomLevel) {
        const [track] = stream.getVideoTracks();
        const capabilities = track.getCapabilities();
        if (capabilities.zoom) {
          track.applyConstraints({ advanced: [{ zoom: zoomLevel }] });
        }
      }

      function takePhoto() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL("image/jpeg");
        const pyMsg = {'imageData': dataUrl};
        window.parent.postMessage(pyMsg, '*');
      }

      initCamera();
    </script>
    """, height=600)
    st.warning("⚠️ Captured image not saved because Streamlit HTML component lacks image bridge. Use desktop for full analysis.")
else:
    upload_method = st.radio("Choose image input method", ["📷 Camera", "🖼 Upload Image"])

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

    if image_path:
        with st.spinner("🔍 Generating plant summary..."):
            try:
                plant_description = generate_auto_description(image_path)
                st.success("✅ Summary generated")
                st.markdown("### 📋 Plant Summary")
                st.write(plant_description)
            except Exception as e:
                st.error(f"Error generating plant description: {e}")

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
