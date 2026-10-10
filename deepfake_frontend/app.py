import streamlit as st
import requests

# 🌟 Page Configuration (Browser tab icon aur wide layout)
st.set_page_config(page_title="MDDS Dashboard", page_icon="🛡️", layout="wide")

# --- 📱 SIDEBAR ---
with st.sidebar:
    st.title("🛡️ MDDS System")
    st.write("Multi-Modal Deepfake Detection System")
    st.info("**Allowed Files:** \n- 🖼️ Images: JPG, PNG\n- 🎵 Audio: MP3, WAV\n- 🎥 Video: MP4")
    st.write("---")
    st.write("🔒 Secure & Encrypted Analysis")

# --- 🖥️ MAIN CONTENT ---
st.title("Deepfake Detection AI 🔍")
st.markdown("Upload any media file below to verify its authenticity using our advanced AI models.")
st.divider()

BACKEND_URL = "https://mdds-backend-tkbc.onrender.com/upload"  # Backend API endpoint

# 🗂️ Layout ko 2 hisson (Columns) mein divide karna
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.subheader("📁 Upload Media")
    uploaded_file = st.file_uploader("Drag and drop your file here", type=["jpg", "png", "jpeg", "mp3", "wav", "mp4"])

with col2:
    st.subheader("🤖 AI Analysis Result")
    
    if uploaded_file is not None:
        st.success(f"File **{uploaded_file.name}** is ready!")
        
        # Khoobsurat bara button
        if st.button("🚀 Analyze Media Now", use_container_width=True, type="primary"):
            with st.spinner("🧠 AI is processing... Please wait."):
                
                # File backend ko bhejna
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = requests.post(BACKEND_URL, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    ai_result = data["ai_analysis"]
                    
                    st.write("### ✨ Final Verdict")
                    
                    # 📊 Professional Metrics Boxes
                    res_col1, res_col2, res_col3 = st.columns(3)
                    res_col1.metric(label="Prediction", value=ai_result['result'])
                    res_col2.metric(label="Confidence", value=ai_result['confidence'])
                    res_col3.metric(label="Model Used", value=ai_result['model'])
                    
                    st.divider()
                    
                    # 👁️ Dropdown/Expander for Heatmap
                    with st.expander("👁️ View Explainable AI (Heatmap)", expanded=True):
                        st.write("Below is the visual representation of where the AI detected manipulation:")
                        try:
                            # Streamlit direct URL se tasveer utha lega
                            st.image(ai_result['heatmap_url'], use_container_width=True)
                        except:
                            st.warning("Heatmap not found in backend 'heatmaps' folder.")
                            
                else:
                    error_msg = response.json().get('detail', 'Unknown error occurred!')
                    st.error(f"❌ Server Error: {error_msg}")
    else:
        st.info("👈 Please upload a file from the left panel to begin.")