"""
3D Gaussian Splatting 训练 — 纯PyTorch实现
无需外部CUDA Toolkit，直接用gsplat安装包中的rasterization函数在CPU上运行
或者用自定义2D投影渲染

策略：
1. 读取真实室内效果图（同一场景多张图）
2. 模拟多视角相机参数（圆形轨道）
3. 用可微分2D Gaussian Splatting渲染图像
4. L1 + SSIM 损失优化 Gaussian 参数
5. 最终输出 .ply 文件供前端加载
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from pathlib import Path
import random, math, time

# ====== 配置 ======
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
IMG_ROOT = Path(r'C:\Users\Administrator\Desktop\设计数据库\效果图')
OUTPUT_DIR = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\models\3dgs_output')
SCENE = '室内_家庭'
N_GAUSSIANS = 500
IMAGE_H, IMAGE_W = 480, 640
ITERS = 2000
LR = 0.01
SAVE_EVERY = 500

print("=" * 60)
print(f"3D Gaussian Splatting 训练 — {SCENE}")
print(f"Device: {DEVICE}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"Gaussians: {N_GAUSSIANS}, Image: {IMAGE_W}x{IMAGE_H}, Iters: {ITERS}")
print("=" * 60)

# ====== 加载图片 ======
def find_images(scene, max_n=15):
    mapping = {
        '室内_家庭': ('室内效果图', '家庭'),
        '室内_工装': ('室内效果图', '工装'),
        '室内_餐饮': ('室内效果图', '餐饮'),
        '建筑_别墅': ('建筑效果图', '别墅建筑花园'),
        '建筑_市政公园': ('建筑效果图', '市政公园'),
    }
    cat, sub = mapping.get(scene, ('室内效果图', '家庭'))
    p = IMG_ROOT / cat / sub
    if not p.exists():
        print(f"WARNING: {p} not found")
        return []
    paths = sorted(p.glob('*.jpg'))[:max_n]
    if not paths:
        paths = sorted(p.glob('*.png'))[:max_n]
    return paths

image_paths = find_images(SCENE)
print(f"\n找到 {len(image_paths)} 张图片")
images = []
for p in image_paths:
    try:
        img = Image.open(p).convert('RGB').resize((IMAGE_W, IMAGE_H))
        arr = np.array(img, dtype=np.float32) / 255.0
        images.append(torch.from_numpy(arr).permute(2, 0, 1).to(DEVICE))
    except Exception as e:
        print(f"  跳过 {p.name}: {e}")

print(f"加载 {len(images)} 张图片")
N_IMGS = len(images)

# ====== 相机参数 ======
def get_K(H, W, fov_deg=60):
    f = H / (2 * math.tan(math.radians(fov_deg / 2)))
    return np.array([[f, 0, W/2], [0, f, H/2], [0, 0, 1]], dtype=np.float32)

def get_viewmat(pos, look=(0, 0, 0), up=(0, 1, 0)):
    pos = np.array(pos, dtype=np.float32)
    look = np.array(look, dtype=np.float32)
    up = np.array(up, dtype=np.float32)
    f = look - pos; f = f / (np.linalg.norm(f) + 1e-6)
    r = np.cross(f, up); r = r / (np.linalg.norm(r) + 1e-6)
    u = np.cross(r, f)
    RT = np.eye(4, dtype=np.float32)
    RT[:3, 0] = r; RT[:3, 1] = u; RT[:3, 2] = -f; RT[:3, 3] = pos
    return RT

def build_cameras(n_cams, H, W):
    """为每张图构建相机参数"""
    fov = 60
    f = H / (2 * math.tan(math.radians(fov / 2)))
    K = np.array([[f, 0, W/2], [0, f, H/2], [0, 0, 1]], dtype=np.float32)
    cameras = []
    for i in range(n_cams):
        angle = 2 * math.pi * i / n_cams + random.uniform(-0.15, 0.15)
        r = 4.0 + random.uniform(-0.4, 0.4)
        h = 0.7 + random.uniform(-0.2, 0.2)
        pos = [r * math.cos(angle), h, r * math.sin(angle)]
        cameras.append({
            'K': K.copy(),
            'viewmat': get_viewmat(pos),
            'pos': pos,
        })
    return cameras

# ====== 初始化 Gaussian ======
def init_gaussians(N, device):
    # 位置：分布在场景空间（约 6x3x6 m）
    pos = torch.randn(N, 3, device=device)
    pos[:, 0] *= 3.0   # X: ±3m
    pos[:, 1] *= 1.5   # Y: ±1.5m  
    pos[:, 2] = pos[:, 2] * 3.0 + 5.0  # Z: 2~8m
    
    scales_log = torch.randn(N, 3, device=device) * 0.3  # log-scale
    
    # 无旋转
    quats = torch.zeros(N, 4, device=device); quats[:, 0] = 1.0
    
    colors = torch.rand(N, 3, device=device) * 0.8 + 0.1  # 颜色 0.1~0.9
    
    # opacity: 0.5 初始
    opacities_logit = torch.ones(N, device=device) * 0.5
    
    for t in [pos, scales_log, quats, colors, opacities_logit]:
        t.requires_grad_(True)
    
    return dict(positions=pos, scales_log=scales_log, quats=quats,
                colors=colors, opacities_logit=opacities_logit)

# ====== 可微分 2D Gaussian Splatting 渲染 ======
def project_to_image(positions_3d, cam_K, cam_viewmat, H, W):
    """
    将3D Gaussian投影到2D图像平面
    返回: (N, 2) 2D位置, (N,) 缩放, (N, 3) 覆盖范围
    """
    # 转到相机坐标系
    R = cam_viewmat[:3, :3]
    T = cam_viewmat[:3, 3]
    
    # 世界→相机
    cam_pos = positions_3d @ R.T + T  # (N, 3)
    
    # 可见性mask（深度为正）
    depth = cam_pos[:, 2]
    valid = depth > 0.1
    
    # 投影到像素
    fx, fy = cam_K[0, 0], cam_K[1, 1]
    cx, cy = cam_K[0, 2], cam_K[1, 2]
    
    x_2d = cam_pos[:, 0] * fx / (cam_pos[:, 2] + 1e-6) + cx
    y_2d = cam_pos[:, 1] * fy / (cam_pos[:, 2] + 1e-6) + cy
    
    # 投影范围
    in_bounds = (x_2d > -H) & (x_2d < W + H) & (y_2d > -H) & (y_2d < H + H)
    visible = valid & in_bounds
    
    return x_2d, y_2d, depth, visible

def render_gaussians(gauss, camera, H, W, bg_color=None):
    """
    渲染 Gaussian Cloud 到图像
    gauss: dict with positions(N,3), scales_log(N,3), quats(N,4), colors(N,3), opacities_logit(N,)
    camera: dict with K(3,3), viewmat(4,4)
    """
    N = gauss['positions'].shape[0]
    pos = gauss['positions']
    scales = torch.exp(gauss['scales_log'].clamp(-5, 5))  # (N, 3)
    colors = gauss['colors']  # (N, 3)
    opacities = torch.sigmoid(gauss['opacities_logit'].clamp(-10, 10))  # (N,)
    
    K = camera['K']
    V = camera['viewmat']
    
    # 投影
    x2d, y2d, depth, visible = project_to_image(pos, K, V, H, W)
    
    # 构建2D高斯
    scales_2d = (scales[:, 0] + scales[:, 2]) / 2  # 平均缩放 (N,)
    scales_2d = scales_2d / (depth + 1e-6)  # 透视缩放 (N,)
    
    # 创建像素网格
    y_coords = torch.arange(H, dtype=torch.float32, device=pos.device)
    x_coords = torch.arange(W, dtype=torch.float32, device=pos.device)
    gy, gx = torch.meshgrid(y_coords, x_coords, indexing='ij')
    
    # 渲染 (N, H, W)
    mask = visible.float().unsqueeze(-1).unsqueeze(-1)  # (N, 1, 1)
    
    dx = gx.unsqueeze(0) - x2d.view(N, 1, 1)  # (N, H, W)
    dy = gy.unsqueeze(0) - y2d.view(N, 1, 1)
    
    # 各向异性2D Gaussian: exp(-0.5 * d^2 / s^2)
    sigma = scales_2d.view(N, 1, 1).clamp(0.5, 1000) + 1e-6
    w = torch.exp(-0.5 * (dx**2 + dy**2) / (sigma ** 2))
    
    # Alpha blending
    alpha = w * opacities.view(N, 1, 1) * mask  # (N, H, W)
    
    # 背景
    if bg_color is None:
        bg_color = torch.zeros(3, H, W, device=pos.device)
    else:
        bg_color = bg_color.to(pos.device)
    
    # 合成
    alpha_cumsum = torch.cumsum(alpha, dim=0)
    transmittance = torch.exp(-alpha_cumsum)  # T(i) = exp(-sum_{j<i} alpha_j)
    weights = alpha * transmittance  # w_i
    
    # 颜色合成: sum_i(w_i * c_i)
    color_img = (weights.unsqueeze(-1) * colors.view(N, 1, 1, 3)).sum(dim=0)  # (H, W, 3)
    bg_contrib = transmittance[-1:].permute(1, 2, 0) * bg_color.permute(1, 2, 0)
    img = color_img + bg_contrib
    
    # Alpha通道
    accumulated = 1 - transmittance[-1]  # (H, W)
    
    return img.permute(2, 0, 1), accumulated  # (3, H, W), (H, W)

# ====== 损失函数 ======
def rgb_l1(pred, target):
    return F.l1_loss(pred, target)

def ssim(pred, target, window=11):
    """简化SSIM"""
    C1, C2 = 0.01**2, 0.03**2
    pad = window // 2
    def pool(x):
        return F.avg_pool2d(x, window, stride=1, padding=pad)
    mu_p, mu_t = pool(pred), pool(target)
    sigma_p = pool(pred**2) - mu_p**2
    sigma_t = pool(target**2) - mu_t**2
    sigma_pt = pool(pred * target) - mu_p * mu_t
    ssim_map = (2*mu_p*mu_t+C1)*(2*sigma_pt+C2) / ((mu_p**2+mu_t**2+C1)*(sigma_p+sigma_t+C2)+1e-8)
    return 1 - ssim_map.mean()

# ====== 初始化 ======
print("\n初始化 Gaussian Cloud...")
gauss = init_gaussians(N_GAUSSIANS, DEVICE)
cameras = build_cameras(N_IMGS, IMAGE_H, IMAGE_W)
print(f"  {N_GAUSSIANS} gaussians, {N_IMGS} cameras")

# 优化器
optimizer = torch.optim.Adam([
    {'params': [gauss['positions']], 'lr': LR},
    {'params': [gauss['scales_log']], 'lr': LR * 0.1},
    {'params': [gauss['quats']], 'lr': LR * 0.05},
    {'params': [gauss['colors']], 'lr': LR * 0.01},
    {'params': [gauss['opacities_logit']], 'lr': LR * 0.05},
])
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=ITERS)

# ====== 训练循环 ======
print(f"\n训练 {ITERS} 轮...")
print(f"{'Iter':>6}  {'L1':>8}  {'SSIM':>8}  {'Total':>8}  {'Time':>6}")
print("-" * 50)

start = time.time()
best_loss = float('inf')

for it in range(ITERS):
    idx = random.randint(0, N_IMGS - 1)
    target = images[idx]
    cam = cameras[idx]
    
    # 渲染
    pred, acc = render_gaussians(gauss, cam, IMAGE_H, IMAGE_W)
    
    # 损失
    l1 = rgb_l1(pred, target)
    s = ssim(pred, target)
    loss = l1 + 0.5 * s
    
    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_([gauss['positions'], gauss['scales_log']], 1.0)
    optimizer.step()
    scheduler.step()
    
    best_loss = min(best_loss, loss.item())
    
    if it % 100 == 0:
        elapsed = time.time() - start
        print(f"{it:6d}  {l1.item():8.4f}  {s.item():8.4f}  {loss.item():8.4f}  {elapsed:.0f}s")
    
    # 保存中间 checkpoint
    if (it + 1) % SAVE_EVERY == 0:
        ckpt = {
            'iteration': it + 1,
            'positions': gauss['positions'].detach().cpu(),
            'scales': torch.exp(gauss['scales_log']).detach().cpu(),
            'quats': gauss['quats'].detach().cpu(),
            'colors': gauss['colors'].detach().cpu(),
            'opacities': torch.sigmoid(gauss['opacities_logit']).detach().cpu(),
        }
        ckpt_path = OUTPUT_DIR / f'{SCENE}_iter_{it+1}.pt'
        torch.save(ckpt, ckpt_path)
        print(f"  -> {ckpt_path.name}")

# ====== 保存最终模型 ======
print("\n保存模型...")
final = {
    'scene': SCENE,
    'num_gaussians': N_GAUSSIANS,
    'image_size': [IMAGE_H, IMAGE_W],
    'iterations': ITERS,
    'positions': gauss['positions'].detach().cpu(),
    'scales': torch.exp(gauss['scales_log']).detach().cpu(),
    'quats': gauss['quats'].detach().cpu(),
    'colors': gauss['colors'].detach().cpu(),
    'opacities': torch.sigmoid(gauss['opacities_logit']).detach().cpu(),
}
torch.save(final, OUTPUT_DIR / f'{SCENE}_final.pt')

# PLY格式保存
try:
    import plyfile
    pos_np = final['positions'].numpy()
    col_np = (final['colors'].numpy() * 255).astype('uint8')
    op_np = final['opacities'].numpy().flatten()
    
    verts = np.array(
        [(pos_np[i,0], pos_np[i,1], pos_np[i,2],
          col_np[i,0], col_np[i,1], col_np[i,2], op_np[i])
         for i in range(N_GAUSSIANS)],
        dtype=[('x','f4'),('y','f4'),('z','f4'),
               ('red','u1'),('green','u1'),('blue','u1'),('opacity','f4')]
    )
    ply_path = OUTPUT_DIR / f'{SCENE}.ply'
    plyfile.dataarray_to_plyfile(verts, str(ply_path), rev=False)
    print(f"PLY: {ply_path}")
except ImportError:
    print("plyfile not installed, using numpy")
    np.savez(OUTPUT_DIR / f'{SCENE}.npz',
             positions=final['positions'].numpy(),
             colors=final['colors'].numpy(),
             opacities=final['opacities'].numpy())

# 保存渲染预览
with torch.no_grad():
    preview_img, _ = render_gaussians(gauss, cameras[0], IMAGE_H, IMAGE_W)
    preview_np = (preview_img.permute(1,2,0).cpu().numpy() * 255).clip(0,255).astype('uint8')
    Image.fromarray(preview_np).save(OUTPUT_DIR / f'{SCENE}_preview.png')
    print(f"预览图: {SCENE}_preview.png")

total = time.time() - start
print(f"\n完成！")
print(f"  最终损失: {best_loss:.4f}")
print(f"  总耗时: {total:.1f}s ({total/60:.1f}min)")
print(f"  模型: {OUTPUT_DIR / SCENE}_final.pt")
