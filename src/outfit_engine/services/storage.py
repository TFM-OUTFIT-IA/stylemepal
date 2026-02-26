import json
import os
from threading import Lock
from typing import Optional, Dict, List

class StorageService:
    def __init__(self, file_path: str = "data/processed/mock_database.json"):
        self.file_path = file_path
        self.lock = Lock()
        
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w") as f:
                json.dump({}, f)
        
    def save_garment(self, item_id: str, metadata: dict) -> None:
        with self.lock:
            with open(self.file_path, "r") as f:
                data = json.load(f)
            data[item_id] = metadata
            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=4)
                
        print(f"Saved {item_id} to JSON storage.")

    def get_garment(self, item_id: str) -> Optional[Dict]:
        with self.lock:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                
        return data.get(item_id)

    def get_all_garments(self) -> Dict:
        with self.lock:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                
        return data
    
    def get_filtered_garments(self, style: str, weather: str, gender: str) -> List[Dict]:
        all_garments = self.get_all_garments()
        filtered_garments = []

        for item_id, garment in all_garments.items():
            if garment.get("style") == style and garment.get("weather") == weather and garment.get("gender") == gender:
                garment_data = garment.copy()
                garment_data["item_id"] = item_id
                filtered_garments.append(garment_data)
                
        return filtered_garments