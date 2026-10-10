from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
import shutil
import os
import random

app = FastAPI()

# 📂 Folders setup
UPLOAD_DIR = "uploads"
HEATMAP_DIR = "heatmaps"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(HEATMAP_DIR, exist_ok=True)

app.mount("/heatmaps", StaticFiles(directory=HEATMAP_DIR), name="heatmaps")

# 🛡️ SECURITY SETTINGS
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB limit
ALLOWED_TYPES = ["image/jpeg", "image/png", "audio/mpeg", "audio/wav", "video/mp4"]

# --- 🧠 DUMMY AI FUNCTIONS ---

def analyze_image(file_path, filename):
    confidence = round(random.uniform(80.0, 99.9), 2)
    heatmap_url = f"http://127.0.0.1:8000/heatmaps/heatmap_ai_{filename}"
    return {"result": "Fake", "confidence": f"{confidence}%", "model": "CIFAKE", "heatmap_url": heatmap_url}

def analyze_audio(file_path, filename):
    confidence = round(random.uniform(80.0, 99.9), 2)
    heatmap_url = f"http://127.0.0.1:8000/heatmaps/spectrogram_ai_{filename}.png"
    return {"result": "Real", "confidence": f"{confidence}%", "model": "ASVspoof", "heatmap_url": heatmap_url}

def analyze_video(file_path, filename):
    confidence = round(random.uniform(80.0, 99.9), 2)
    heatmap_url = f"http://127.0.0.1:8000/heatmaps/heatmap_ai_{filename}.png"
    return {"result": "Fake", "confidence": f"{confidence}%", "model": "FaceForensics++", "heatmap_url": heatmap_url}

# --- 🌐 ROUTES ---

@app.get("/")
def home():
    return {"message": "Welcome to MDDS Backend! Setup successful."}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    
    # 🛑 1. FILE TYPE SECURITY CHECK
    if file.content_type not in ALLOWED_TYPES:
        # Agar file type allowed list mein nahi hai, toh error throw karein
        raise HTTPException(status_code=400, detail="Invalid File! Sirf JPG, PNG, MP3, WAV, aur MP4 allowed hain.")

    file_path = f"{UPLOAD_DIR}/{file.filename}"
    file_size = 0
    
    # 🛑 2. FILE SIZE SECURITY CHECK (Max 50MB)
    with open(file_path, "wb") as buffer:
        # File ko tukron mein read karein taake memory overload na ho
        for chunk in file.file:
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                # Agar limit cross ho jaye, toh ban rahi file delete kar do aur error de do
                buffer.close()
                os.remove(file_path)
                raise HTTPException(status_code=413, detail="File size too large! Maximum limit 50MB hai.")
            buffer.write(chunk)
        
    # --- 🤖 AI PROCESSING ---
    file_type = file.content_type
    analysis_result = {}
    
    if file_type.startswith("image/"):
        analysis_result = analyze_image(file_path, file.filename)
    elif file_type.startswith("audio/"):
        analysis_result = analyze_audio(file_path, file.filename)
    elif file_type.startswith("video/"):
        analysis_result = analyze_video(file_path, file.filename)

    return {
        "filename": file.filename,
        "status": "File processed successfully!",
        "ai_analysis": analysis_result
    }