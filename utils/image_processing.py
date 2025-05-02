import requests
from PIL import Image
from io import BytesIO
from transformers import CLIPProcessor, CLIPModel
from huggingface_hub import login
import torch
import os
from dotenv import load_dotenv

# Disable symlinks warning
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

# Initialize environment
load_dotenv()

# Authenticate with Hugging Face
login(token=os.getenv("HUGGINGFACE_TOKEN"))

# Load model with new token parameter
model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32",
    token=os.getenv("HUGGINGFACE_TOKEN")
)
processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32",
    token=os.getenv("HUGGINGFACE_TOKEN")
)

ISSUE_CATEGORIES = [
    "water leak plumbing",
    "electrical wiring problem",
    "broken furniture carpentry",
    "wall crack painting",
    "appliance repair",
    "roof damage"
]

def analyze_telegram_photo(photo_url):
    """Analyze home service issues from photos"""
    try:
        response = requests.get(photo_url, timeout=10)
        img = Image.open(BytesIO(response.content))
        
        inputs = processor(
            text=ISSUE_CATEGORIES,
            images=img,
            return_tensors="pt",
            padding=True,
            truncation=True
        )
        
        with torch.no_grad():
            outputs = model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)
            top_prob, top_idx = torch.max(probs, dim=1)
        
        return {
            "issue_type": ISSUE_CATEGORIES[top_idx],
            "confidence": float(top_prob) * 100,
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }