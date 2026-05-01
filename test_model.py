import sys
sys.path.insert(0, r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\src')

import torch
from neural.physics_mlp import PhysicsMLP, generate_physics_training_data

# Test data generation
data = generate_physics_training_data(100)
X = torch.tensor(data['X'], dtype=torch.float32)
print(f'X shape: {X.shape}')

# Test forward
model = PhysicsMLP(embed_dim=64)
out = model(geometry_features=X[:3])
print(f'Forward OK: mass={out["mass_kg"]}')
