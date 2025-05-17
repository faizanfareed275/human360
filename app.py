import streamlit as st
import google.generativeai as genai
import os
import PIL.Image
import base64
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="Human360",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon="🕵️"
)

# Custom CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .gradient-header {
        background: linear-gradient(45deg, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .attribute-card {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .confidence-bar {
        height: 8px;
        border-radius: 4px;
        background: #e2e8f0;
        margin: 0.5rem 0;
    }
    
    .confidence-fill {
        height: 100%;
        border-radius: 4px;
        background: #4f46e5;
        transition: width 0.5s ease;
    }
    
    .uploader-section {
        border: 2px dashed #94a3b8;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Set Google Gemini API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyBzn2Z420Ex2U6MvuTOs8Zh5_H_-jGVxOY"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Load the Gemini model
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Helper: Convert image to base64
def pil_image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# Function to parse response into dictionary
def parse_response(response_text):
    attributes = {}
    lines = [line.strip() for line in response_text.split('\n') if line.strip()]
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            attributes[key.strip()] = value.strip()
    return attributes

# Function to analyze human attributes
def analyze_human_attributes(image):
    base64_image = pil_image_to_base64(image)
    image_part = {
        "mime_type": "image/jpeg",
        "data": base64_image
    }

    prompt = """
    Analyze this human portrait and provide detailed attributes in the following format:
    Gender: [Male/Female/Non-binary]
    Age Estimate: [number] years
    Ethnicity: [specific ethnicity]
    Mood: [primary mood]
    Facial Expression: [specific expression]
    Glasses: [Yes/No]
    Beard: [Yes/No]
    Hair Color: [specific color]
    Eye Color: [specific color]
    Headwear: [Yes/No with type if applicable]
    Emotions Detected: [comma-separated list]
    Confidence Level: [percentage]%

    Include only these attributes and values. Be precise and specific.
    """

    response = model.generate_content([prompt, image_part])
    return parse_response(response.text.strip())

# UI Layout
st.markdown("<h1 class='gradient-header' style='font-size: 2.5rem;'>🕵️ Human Attribute Analyzer Pro</h1>", unsafe_allow_html=True)

# Hero Section
col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/1862/1862357.png", width=150)
with col2:
    st.markdown("""
    <div style='border-left: 4px solid #6366f1; padding-left: 1rem;'>
    <h3 style='color: #1e293b; margin-bottom: 0.5rem;'>AI-Powered Portrait Analysis</h3>
    <p style='color: #64748b;'>Upload a clear frontal portrait to detect demographic, 
    appearance, and emotional characteristics with advanced computer vision.</p>
    </div>
    """, unsafe_allow_html=True)

# File uploader with enhanced UI
with st.container():
    st.markdown("<div class='uploader-section'>", unsafe_allow_html=True)
    uploaded_image = st.file_uploader(
        "DRAG & DROP PORTRAIT HERE",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Supported formats: JPEG, PNG • Max size: 5MB • Ideal ratio: 3:4")

if uploaded_image:
    img = PIL.Image.open(uploaded_image)

    with st.spinner("🔍 Analyzing portrait features..."):
        try:
            person_info = analyze_human_attributes(img)

            # Display results
            col1, col2 = st.columns(2, gap="large")

            with col1:
                st.image(img, caption="Uploaded Portrait", use_container_width=True)
                
                # Add image controls
                with st.expander("Image Tools"):
                    st.slider("Zoom Level", 1, 3, 1)
                    st.checkbox("Show facial landmarks", value=False)
                    st.button("Compare with previous analysis")

            with col2:
                st.markdown("### Analysis Report")
                
                # Demographic Section
                with st.expander("**Demographic Profile**", expanded=True):
                    cols = st.columns(2)
                    cols[0].metric("Gender", person_info.get("Gender", "N/A"))
                    cols[1].metric("Age Estimate", person_info.get("Age Estimate", "N/A"))
                    st.write(f"**Ethnicity:** {person_info.get('Ethnicity', 'N/A')}")
                
                # Appearance Section
                with st.expander("Physical Characteristics", expanded=True):
                    cols = st.columns(2)
                    cols[0].write(f"**Hair Color:** {person_info.get('Hair Color', 'N/A')}")
                    cols[1].write(f"**Eye Color:** {person_info.get('Eye Color', 'N/A')}")
                    cols[0].write(f"**Glasses:** {person_info.get('Glasses', 'N/A')}")
                    cols[1].write(f"**Headwear:** {person_info.get('Headwear', 'N/A')}")
                
                # Emotional Analysis
                with st.expander("Emotional Profile", expanded=True):
                    cols = st.columns(2)
                    cols[0].write(f"**Primary Mood:** {person_info.get('Mood', 'N/A')}")
                    cols[1].write(f"**Facial Expression:** {person_info.get('Facial Expression', 'N/A')}")
                    st.write(f"**Detected Emotions:** {person_info.get('Emotions Detected', 'N/A')}")
                    
                    # Confidence visualization
                    confidence = int(person_info.get("Confidence Level", "0%").strip('%'))
                    st.markdown(f"**Analysis Confidence:** {confidence}%")
                    st.markdown(f"""
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: {confidence}%"></div>
                    </div>
                    """, unsafe_allow_html=True)

                # Raw data export
                with st.expander("Technical Details"):
                    st.json(person_info)
                    st.download_button(
                        label="Download Report",
                        data=str(person_info),
                        file_name="attribute_analysis.json"
                    )

        except Exception as e:
            st.error(f"""
            ## ⚠️ Analysis Failed
            **Possible reasons:**
            - Low image quality
            - No clear face detected
            - Unsupported image format
            
            Error details: `{str(e)}`
            """)
else:
    st.info("📌 Tip: For best results, use a well-lit frontal portrait with neutral expression")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 1rem;'>
    <div>© 2025 Human360 Analyzer • Built with ❤️ by Faizan Abbasi</div>
</div>
""", unsafe_allow_html=True)