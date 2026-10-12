import streamlit as st
import requests
import base64

BACKEND_URL = "https://mdds-backend-tkbc.onrender.com/upload/"

st.title("MDDS - Deepfake Detection System")
st.write("Upload an image to check if it's Real or Fake (with AI Heatmap).")

uploaded_file = st.file_uploader("Choose a media file...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", width=300)
    
    if st.button("Analyze Media Now"):
        with st.spinner("AI is processing... Please wait."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            try:
                response = requests.post(BACKEND_URL, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Analysis Complete!")
                    
                    # Result Dikhana
                    st.subheader(f"Prediction: **{result.get('status', 'N/A')}**")
                    st.write(f"Confidence: **{result.get('confidence', 'N/A')}**")
                    
                    # Heatmap Dikhana (Fix ke sath)
                    if "heatmap_image" in result:
                        heatmap_data = result["heatmap_image"]
                        if "," in heatmap_data:
                            heatmap_data = heatmap_data.split(",")[1]
                        
                        image_bytes = base64.b64decode(heatmap_data)
                        st.image(image_bytes, caption="AI Analysis Heatmap (Red areas show focus)", use_container_width=True)
                    else:
                        st.error("Heatmap data nahi mila!")
                else:
                    st.error("Server mein koi masla aaya hai. Please try again.")
            except Exception as e:
                st.error(f"Connection error: {e}")