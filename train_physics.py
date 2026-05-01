"""快速重新训练 + 保存 PhysicsMLP"""
import sys
sys.path.insert(0, r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\src')

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np
from pathlib import Path

from neural.physics_mlp import PhysicsMLP, generate_physics_training_data

output_dir = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\checkpoints')
output_dir.mkdir(parents=True, exist_ok=True)

device = torch.device('cpu')
n_samples = 2000

# 生成数据（44维特征）
data = generate_physics_training_data(n_samples)
X = torch.tensor(data['X'], dtype=torch.float32)
y_mass = torch.tensor(data['y_mass'], dtype=torch.float32)
y_fric = torch.tensor(data['y_fric_s'], dtype=torch.float32)
y_cond = torch.tensor(data['y_stiff'], dtype=torch.float32)  # 用y_stiff作为第三个属性

print(f"Data: {X.shape}")
print(f"Mass range: [{y_mass.min():.2f}, {y_mass.max():.2f}] kg")
print(f"Fric range: [{y_fric.min():.3f}, {y_fric.max():.3f}]")

class PData(Dataset):
    def __init__(self, X, y_mass, y_fric, y_cond):
        self.X = X
        self.y_mass = y_mass
        self.y_fric = y_fric
        self.y_cond = y_cond
    def __len__(self): return len(self.X)
    def __getitem__(self, i):
        return {'x': self.X[i], 'mass': self.y_mass[i], 'fric': self.y_fric[i], 'cond': self.y_cond[i]}

ds = PData(X, y_mass, y_fric, y_cond)
loader = DataLoader(ds, batch_size=64, shuffle=True)

# 模型（用 embed_dim=64 让它更轻量）
model = PhysicsMLP(embed_dim=64).to(device)

opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
criterion = nn.MSELoss()

best_loss = float('inf')
for epoch in range(1, 101):
    model.train()
    total = 0
    for batch in loader:
        x = batch['x'].to(device)
        m = batch['mass'].to(device)
        f = batch['fric'].to(device)
        c = batch['cond'].to(device)
        
        out = model(geometry_features=x)
        loss = criterion(out['mass_kg'], m) + criterion(out['friction_static'], f) + criterion(out['stiffness_Nm'], c)
        
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        total += loss.item() * len(x)
    
    avg = total / len(ds)
    if epoch % 20 == 0:
        print(f"Epoch {epoch:3d}: loss={avg:.6f}")
    
    if avg < best_loss:
        best_loss = avg

print(f"Best loss: {best_loss:.6f}")

# 保存
torch.save({
    'model_state': model.state_dict(),
    'loss': best_loss,
    'feature_dim': 44,
}, output_dir / 'physics_mlp_best.pt')
print(f"[OK] physics_mlp_best.pt saved")

# 测试推理
model.eval()
with torch.no_grad():
    # 门锁 44维特征
    feat = torch.zeros(1, 44, dtype=torch.float32)
    feat[0, 0] = 0.15   # bbox_w
    feat[0, 1] = 0.08   # bbox_h
    feat[0, 2] = 0.04   # bbox_d
    feat[0, 6] = 1.0    # material_metal
    feat[0, 7] = 0.9    # material_wood_proxy
    
    out = model(geometry_features=feat)
    print(f"\nInference: 智能门锁")
    print(f"  mass={out['mass_kg'].item():.3f}kg (expected ~1.5kg)")
    print(f"  friction={out['friction_static'].item():.3f} (expected ~0.3)")
    print(f"  stiffness={out['stiffness_Nm'].item():.1f}Nm")
