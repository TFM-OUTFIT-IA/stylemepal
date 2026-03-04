from torch import nn
from torch_geometric.nn import RGCNConv
import torch.nn.functional as F


class FashionRGCN(nn.Module):
    def __init__(self, num_relations, in_channels=512, hidden_channels=256, out_channels=128, num_bases=30):
        super(FashionRGCN, self).__init__()
        
        # The Graph Layers parately
        self.conv1 = RGCNConv(in_channels, hidden_channels, num_relations, num_bases)
        self.conv2 = RGCNConv(hidden_channels, out_channels, num_relations, num_bases)
        
        # Prevent overfitting
        self.dropout = nn.Dropout(0.5)

    def forward(self, x, edge_index, edge_type):
        # Layer 1: Compress 512 -> 256
        x = self.conv1(x, edge_index, edge_type)
        x = F.relu(x)
        x = self.dropout(x)
        
        # Layer 2: Compress 256 -> 128 
        x = self.conv2(x, edge_index, edge_type)
        
        # L2 Normalize the output (Crucial for Cosine Similarity later)
        x = F.normalize(x, p=2, dim=-1, eps=1e-6)
        
        return x