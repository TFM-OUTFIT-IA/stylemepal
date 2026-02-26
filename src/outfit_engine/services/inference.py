import torch
import torch.nn as nn
from PIL import Image
import numpy as np
import joblib
from transformers import CLIPProcessor, CLIPModel
from ..core.config import settings

class InferenceEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.clip_model = CLIPModel.from_pretrained(settings.CLIP_MODEL_NAME).to(self.device)
        self.clip_processor = CLIPProcessor.from_pretrained(settings.CLIP_MODEL_NAME)
        self.clip_model.eval()

        # Label Encoder
        self.label_encoder = joblib.load(settings.LABEL_ENCODER_PATH)
        num_classes = len(self.label_encoder.classes_)

        self.probe = nn.Sequential(
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        ).to(self.device)
        self.probe.load_state_dict(torch.load(settings.PROBE_WEIGHTS_PATH, map_location=self.device))
        self.probe.eval()

        # Zero-Shot Prompts
        self.style_prompts = ["Casual", "Formal", "Streetwear", "Bohemian", "Sporty", "Elegant", "Vintage", "Minimalist"]
        self.weather_prompts = ["Summer", "Winter", "Transitional"]
        self.gender_prompts = ["Men's", "Women's", "Unisex"]
        
        self.style_features = self._get_text_features([f"a photo of {s.lower()} clothing" for s in self.style_prompts])
        self.weather_features = self._get_text_features([f"a photo of {w.lower()} weather clothing" for w in self.weather_prompts])
        self.gender_features = self._get_text_features([
            "a photo of men's clothing", 
            "a photo of women's clothing", 
            "a photo of unisex clothing"
        ])

    def _get_text_features(self, prompts):
        inputs = self.clip_processor(text=prompts, return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            features = self.clip_model.get_text_features(**inputs)
        if not isinstance(features, torch.Tensor):
            features = features.pooler_output if hasattr(features, 'pooler_output') else features[0]
        return features / features.norm(p=2, dim=-1, keepdim=True)

    def process_image(self, image: Image.Image) -> dict:
        inputs = self.clip_processor(images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            img_features = self.clip_model.get_image_features(**inputs)
            if not isinstance(img_features, torch.Tensor):
                img_features = img_features.pooler_output if hasattr(img_features, 'pooler_output') else img_features[0]
            img_features_norm = img_features / img_features.norm(p=2, dim=-1, keepdim=True)
            
            # Category Prediction
            probe_out = self.probe(img_features)
            cat_idx = torch.argmax(probe_out, dim=1).item()
            category = self.label_encoder.inverse_transform([cat_idx])[0]
            
            # Zero-Shot Style, Weather, & Gender
            style_sim = (img_features_norm @ self.style_features.T)
            weather_sim = (img_features_norm @ self.weather_features.T)
            gender_sim = (img_features_norm @ self.gender_features.T)
            
            style = self.style_prompts[torch.argmax(style_sim, dim=-1).item()]
            weather = self.weather_prompts[torch.argmax(weather_sim, dim=-1).item()]
            gender = self.gender_prompts[torch.argmax(gender_sim, dim=-1).item()]

        return {
            "category": category,
            "style": style,
            "weather": weather,
            "gender": gender,
            "embedding": img_features.cpu().numpy().tolist()[0]
        }