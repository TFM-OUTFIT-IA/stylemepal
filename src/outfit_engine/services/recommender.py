import random
from ..core.config import settings
import torch
from .fashionrgcn import FashionRGCN

class OutfitRecommender:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.gnn_model = FashionRGCN(
            num_relations=110, 
            in_channels=512, 
            hidden_channels=256,
            out_channels=128
        ).to(self.device)
        self.gnn_model.load_state_dict(torch.load(settings.RGCN_WEIGHTS_PATH, map_location=self.device))
        self.gnn_model.eval()
        self.is_loaded = True
        
    def generate_outfit(self, closet_items: list, anchor_category: str) -> list:
        outfit_list = []
        anchors = [item for item in closet_items if item['category'] == anchor_category]
        if not anchors:
            return {"error": f"No {anchor_category} found in closet to build around."}
            
        query_item = anchors[random.randint(0, len(anchors) - 1)]
        query_vec = torch.tensor([query_item['embedding']], dtype=torch.float32).to(self.device)
        
        if anchor_category == 'tops': targets = ['bottoms', 'shoes', 'outerwear']
        elif anchor_category == 'bottoms': targets = ['tops', 'shoes', 'outerwear']
        else: targets = ['tops', 'bottoms', 'shoes']
        
        outfit = {"anchor": query_item}
        
        for target_cat in targets:
            candidates = [item for item in closet_items if item['category'] == target_cat]
            if not candidates:
                print(f"Wardrobe Gap: No {target_cat} found in user's closet.")
                continue

            cand_vecs = torch.tensor([c['embedding'] for c in candidates], dtype=torch.float32).to(self.device)
         
            # Calculate distances
            dists = torch.cdist(query_vec, cand_vecs, p=2)
            best_idx = dists.argmin().item()
            best_distance = dists.min().item()
            
            best_candidate = candidates[best_idx]
            mock_score = 1.0 / (1.0 + best_distance)
            
            outfit_list.append({
                "item_id": best_candidate["item_id"],
                "category": best_candidate["category"],
                "compatibility_score": round(mock_score, 4)
            })
            
        return outfit_list