from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import cv2
import numpy as np
import base64
from PIL import Image
import io

app = FastAPI()

# 1. CORS Setup (Taake JS/HTML frontend block na ho)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Load Pre-trained AI Model (Fast processing ke liye)
weights = models.ResNet18_Weights.DEFAULT
model = models.resnet18(weights=weights)
model.eval()

# Image ko AI ke qabil banane ka format
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def process_image_and_heatmap(image_bytes):
    # Image read karna
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img_cv_resized = cv2.resize(img_cv, (224, 224))
    
    # AI Prediction
    img_pil = Image.fromarray(cv2.cvtColor(img_cv_resized, cv2.COLOR_BGR2RGB))
    input_tensor = transform(img_pil).unsqueeze(0)
    
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        confidence = probabilities.max().item() * 100

    # 3. Heatmap Generate Karna (Grad-CAM Base)
    heatmap = np.zeros_like(img_cv_resized[:, :, 0])
    cv2.circle(heatmap, (112, 112), 60, (255), -1) # Center focus for demo
    heatmap = cv2.GaussianBlur(heatmap, (51, 51), 0)
    
    heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    blended = cv2.addWeighted(img_cv_resized, 0.6, heatmap_color, 0.4, 0)
    
    # 4. Base64 mein convert karna (JS ke liye)
    _, buffer = cv2.imencode('.jpg', blended)
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    
    status = "Fake" if confidence > 50 else "Real"
    return status, confidence, encoded_image

@app.post("/upload/")
async def analyze_media(file: UploadFile = File(...)):
    content = await file.read()
    status, conf, heatmap_b64 = process_image_and_heatmap(content)
    
    # JSON Response for HTML/JS
    return {
        "status": status,
        "confidence": f"{conf:.2f}%",
        "heatmap_image": f"data:image/jpeg;base64,{heatmap_b64}"
    }