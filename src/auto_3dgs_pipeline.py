"""
自动化3DGS训练管线 - src/auto_3dgs_pipeline.py
监听效果图目录，新增图片时自动触发训练→PLY导出→前端部署

用法:
  python src/auto_3dgs_pipeline.py --watch "C:\\...\\效果图" --interval 60
  python src/auto_3dgs_pipeline.py --once      # 一次性运行
  python src/auto_3dgs_pipeline.py --train "室内_家庭"  # 手动训练指定场景
  python src/auto_3dgs_pipeline.py --status    # 显示当前状态
"""

import os
import sys
import json
import time
import hashlib
import argparse
import urllib.parse
import subprocess
from pathlib import Path
from datetime import datetime

import torch  # noqa: E402

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
WATCH_DIR = Path(os.environ.get("WATCH_DIR", str(PROJECT_ROOT / "renderings_cache")))
GAUSSIAN_OUTPUT = PROJECT_ROOT / "models" / "3dgs_output"
FRONTEND_GAUSSIAN = PROJECT_ROOT / "web-app" / "public" / "gaussian"
GAUSSIAN_DATA_DIR = PROJECT_ROOT / "models" / "3dgs_training_data"

# ══════════════════════════════════════════════════════════════════
#  场景分类映射
# ══════════════════════════════════════════════════════════════════

SCENE_PATTERNS = {
    "室内_家庭":      ["室内/家庭", "室内\\家庭", "renderings/家庭", "interior/residence"],
    "室内_工装":      ["室内/工装", "室内\\工装", "renderings/工装"],
    "室内_酒店":      ["室内/酒店", "室内\\酒店", "renderings/酒店"],
    "室内_餐饮":      ["室内/餐饮", "室内\\餐饮", "renderings/餐饮"],
    "建筑_别墅":      ["建筑/别墅", "建筑\\别墅", "renderings/别墅", "architecture/villa"],
    "建筑_产业园":    ["建筑/产业园", "建筑\\产业园"],
    "建筑_商场":      ["建筑/商场", "建筑\\商场"],
    "建筑_小区":      ["建筑/小区", "建筑\\小区"],
    "建筑_市政公园":  ["建筑/市政公园", "建筑\\市政公园"],
    "园林":           ["园林", "landscape", "公园", "garden"],
}

def classify_scene(filepath: str) -> str:
    """从文件路径推断场景分类"""
    lower = filepath.lower()
    for scene, patterns in SCENE_PATTERNS.items():
        for p in patterns:
            if p.lower() in lower:
                return scene
    return "未知场景"

# ══════════════════════════════════════════════════════════════════
#  高斯模型训练（调用已有脚本）
# ══════════════════════════════════════════════════════════════════

def train_gaussian_scene(scene_name: str, image_dir: str, num_images: int = 15,
                          num_gaussians: int = 500, num_iterations: int = 300) -> dict:
    """
    训练单个场景的高斯模型
    image_dir: 包含该场景图片的目录
    返回: { status, output_dir, loss, time_s }
    """
    print(f"[GaussianTrainer] 开始训练: {scene_name} ({num_images}张图, {num_gaussians}高斯, {num_iterations}迭代)")

    # 查找图片
    from pathlib import Path as P
    img_dir = P(image_dir)
    if not img_dir.exists():
        return {"status": "error", "message": f"目录不存在: {image_dir}"}

    exts = {".jpg", ".jpeg", ".png", ".webp"}
    image_paths = [str(p) for p in img_dir.rglob("*") if p.suffix.lower() in exts]

    if len(image_paths) < 3:
        return {"status": "error", "message": f"图片不足: 仅找到{len(image_paths)}张，需要至少3张"}

    # 取前num_images张
    image_paths = sorted(image_paths)[:num_images]
    print(f"[GaussianTrainer] 找到 {len(image_paths)} 张图片")

    # 调用训练脚本（参考 tmp_train_multi.py 的流程）
    # 这里直接用纯PyTorch方式训练，不依赖gsplat
    output_dir = GAUSSIAN_OUTPUT / scene_name
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            [
                sys.executable, str(PROJECT_ROOT / "tmp_train_multi.py"),
                "--scene", scene_name,
                "--output", str(output_dir),
                "--images", str(num_images),
                "--gaussians", str(num_gaussians),
                "--iterations", str(num_iterations),
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode == 0:
            print(f"[GaussianTrainer] 训练完成: {scene_name}")
            return {
                "status": "success",
                "output_dir": str(output_dir),
                "loss": -1,  # 由子脚本输出
                "time_s": -1,
            }
        else:
            print(f"[GaussianTrainer] 训练失败: {result.stderr[:200]}")
            return {"status": "error", "message": result.stderr[:200]}
    except FileNotFoundError:
        # tmp_train_multi.py 不存在，使用内置训练
        return _train_with_pytorch(scene_name, image_paths, output_dir,
                                    num_gaussians, num_iterations)
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "训练超时（10分钟）"}
    except Exception as e:
        return {"status": "error", "message": str(e)[:200]}


def _train_with_pytorch(scene_name: str, image_paths: list, output_dir: Path,
                         num_gaussians: int, num_iterations: int) -> dict:
    """
    内置纯PyTorch 2D Gaussian Splatting训练
    """
    import numpy as np
    from PIL import Image

    print(f"[GaussianTrainer(PyTorch)] 内置训练模式: {scene_name}")
    start_time = time.time()

    device = torch.device("cpu")
    num_views = min(len(image_paths), 15)

    # 加载图片
    images = []
    for path in image_paths[:num_views]:
        try:
            img = Image.open(path).convert("RGB").resize((640, 480))
            images.append(np.array(img, dtype=np.float32) / 255.0)
        except Exception:
            continue

    if len(images) < 3:
        return {"status": "error", "message": f"成功加载{len(images)}张图，需要至少3张"}

    H, W = images[0].shape[:2]
    images = np.stack(images, axis=0)  # (N, H, W, 3)
    images_t = torch.from_numpy(images).permute(0, 3, 1, 2).to(device)  # (N, 3, H, W)

    # 随机初始化高斯参数
    positions = torch.rand(num_gaussians, 2, device=device)  # 2D 归一化坐标
    colors = torch.rand(num_gaussians, 3, device=device)
    scales = torch.ones(num_gaussians, 2, device=device) * 0.02
    opacity = torch.rand(num_gaussians, 1, device=device).sigmoid()

    # 相机位姿（简化：15个视角围绕中心）
    angles = torch.linspace(0, 2 * 3.14159, num_views)
    view_mats = []
    for a in angles:
        c, s = a.cos(), a.sin()
        # 简化的3x3旋转矩阵 + 平移
        view_mat = torch.tensor([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, -2],
        ], dtype=torch.float32, device=device)
        view_mats.append(view_mat)

    optimizer = torch.optim.Adam([positions, colors, scales, opacity], lr=0.05)

    for iteration in range(num_iterations):
        optimizer.zero_grad()
        total_loss = torch.tensor(0.0, device=device)

        # 随机选一个视角
        view_idx = iteration % len(images_t)
        target = images_t[view_idx]  # (3, H, W)
        view_mat = view_mats[view_idx]

        # 将高斯投影到2D图像平面
        pts_3d = torch.cat([
            positions * torch.tensor([W, H], device=device).float(),
            torch.zeros(num_gaussians, 1, device=device),
        ], dim=1)  # (N, 3)

        # 简化的投影
        pts_2d = pts_3d[:, :2] / (pts_3d[:, 2:3] + 1)  # 透视投影

        # 渲染
        rendered = torch.zeros(3, H, W, device=device)
        rendered = rendered + 0.1  # 背景

        for g in range(num_gaussians):
            x, y = int(pts_2d[g, 0].item()), int(pts_2d[g, 1].item())
            if 0 <= x < W and 0 <= y < H:
                sigma = (opacity[g].item() * 10)
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < W and 0 <= ny < H:
                            weight = sigma * torch.exp(torch.tensor(-(dx*dx + dy*dy) * 2.0))
                            for c in range(3):
                                rendered[c, ny, nx] += weight * colors[g, c].item()

        # MSE损失
        loss = ((rendered - target) ** 2).mean()
        loss.backward()
        optimizer.step()

        if iteration % 100 == 0:
            print(f"  iter {iteration}/{num_iterations}, loss={loss.item():.4f}")

    # 导出PLY
    ply_path = output_dir / f"{scene_name}.ply"
    write_ply(ply_path, positions, colors, opacity, W, H)

    # 生成前端JSON
    model_json = convert_ply_to_json(ply_path, scene_name, output_dir)

    elapsed = time.time() - start_time
    print(f"[GaussianTrainer(PyTorch)] 完成: {scene_name}, {elapsed:.1f}s")
    return {"status": "success", "output_dir": str(output_dir), "loss": -1, "time_s": elapsed}


def write_ply(ply_path: Path, positions: torch.Tensor, colors: torch.Tensor,
               opacity: torch.Tensor, W: int, H: int) -> None:
    """将高斯数据写入PLY文件"""
    n = positions.shape[0]
    # 将2D位置映射到3D空间（用于前端展示）
    x = (positions[:, 0] * W).cpu().numpy().astype(float)
    y = (positions[:, 1] * H).cpu().numpy().astype(float)
    z = torch.zeros(n).cpu().numpy()
    r = (colors[:, 0].clamp(0, 1) * 255).cpu().numpy().astype(int)
    g = (colors[:, 1].clamp(0, 1) * 255).cpu().numpy().astype(int)
    b = (colors[:, 2].clamp(0, 1) * 255).cpu().numpy().astype(int)

    header = (
        "ply\n"
        "format ascii 1.0\n"
        f"element vertex {n}\n"
        "property float x\nproperty float y\nproperty float z\n"
        "property uchar red\nproperty uchar green\nproperty uchar blue\n"
        "property float scale\n"
        "end_header\n"
    )

    with open(ply_path, "w") as f:
        f.write(header)
        for i in range(n):
            f.write(f"{x[i]:.2f} {y[i]:.2f} {z[i]:.2f} "
                    f"{r[i]} {g[i]} {b[i]} 2.0\n")

    print(f"[PLY] 已生成: {ply_path} ({n}个高斯)")


def convert_ply_to_json(ply_path: Path, scene_name: str, output_dir: Path) -> dict:
    """将PLY转换为前端GaussianScene可用的JSON"""
    # 读取PLY
    positions_2d = []
    colors = []
    scales = []

    with open(ply_path) as f:
        for line in f:
            if line.startswith("element"):
                continue
            if line.startswith("property") or line.startswith("ply") or line.startswith("end"):
                continue
            parts = line.strip().split()
            if len(parts) >= 6:
                positions_2d.append([float(parts[0]), float(parts[1])])
                colors.append([int(parts[3]) / 255, int(parts[4]) / 255, int(parts[5]) / 255])
                scales.append(float(parts[6]) if len(parts) > 6 else 2.0)

    model = {
        "scene": scene_name,
        "num_gaussians": len(positions_2d),
        "gaussians": {
            "positions": positions_2d,
            "colors": colors,
            "scales": scales,
        }
    }

    json_path = output_dir / f"{scene_name}_model.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(model, f, ensure_ascii=False)

    print(f"[JSON] 已生成: {json_path}")

    # 复制到前端部署目录
    FRONTEND_GAUSSIAN.mkdir(parents=True, exist_ok=True)
    deployed_path = FRONTEND_GAUSSIAN / f"{scene_name}_model.json"
    import shutil
    shutil.copy(json_path, deployed_path)
    print(f"[Deploy] 已部署到前端: {deployed_path}")

    return model


# ══════════════════════════════════════════════════════════════════
#  文件监控
# ══════════════════════════════════════════════════════════════════

class FileWatcher:
    """监控目录变化，检测新增图片"""

    def __init__(self, watch_dir: str):
        self.watch_dir = Path(watch_dir)
        self.known_files: dict[str, str] = {}  # path -> sha256
        self._scan()

    def _scan(self) -> list[Path]:
        """扫描目录，返回所有图片文件"""
        if not self.watch_dir.exists():
            return []
        exts = {".jpg", ".jpeg", ".png", ".webp"}
        files = []
        for root, dirs, filenames in os.walk(self.watch_dir):
            # 忽略子目录
            dirs[:] = []  # 不递归子目录
            for fn in filenames:
                if Path(fn).suffix.lower() in exts:
                    files.append(Path(root) / fn)
        return files

    def _sha256(self, path: Path) -> str:
        h = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def has_new(self) -> list[Path]:
        """返回新增文件（相对于上次扫描）"""
        current = self._scan()
        new_files = []
        for f in current:
            key = str(f)
            sha = self._sha256(f)
            if key not in self.known_files or self.known_files[key] != sha:
                new_files.append(f)
                self.known_files[key] = sha
        return new_files

    def get_scene_from_path(self, filepath: Path) -> str:
        return classify_scene(str(filepath))

    def status(self) -> dict:
        """返回当前状态摘要"""
        files = self._scan()
        scenes: dict[str, int] = {}
        for f in files:
            scene = self.get_scene_from_path(f)
            scenes[scene] = scenes.get(scene, 0) + 1
        return {
            "watch_dir": str(self.watch_dir),
            "total_files": len(files),
            "by_scene": scenes,
            "known_hashes": len(self.known_files),
        }


# ══════════════════════════════════════════════════════════════════
#  主流程
# ══════════════════════════════════════════════════════════════════

def process_once(watch_dir: str) -> dict:
    """一次性检测并处理新增图片"""
    print(f"\n[{timestamp()}] === 一次性3DGS处理 ===")
    watcher = FileWatcher(watch_dir)
    new_files = watcher.has_new()

    if not new_files:
        print(f"[{timestamp()}] 无新增图片")
        return {"status": "no_new_files", "new_count": 0}

    # 按场景分组
    scenes: dict[str, list[Path]] = {}
    for f in new_files:
        scene = watcher.get_scene_from_path(f)
        if scene not in scenes:
            scenes[scene] = []
        scenes[scene].append(f)

    print(f"[{timestamp()}] 发现 {len(new_files)} 张新增图片，分布在 {len(scenes)} 个场景")

    results = []
    for scene, files in scenes.items():
        # 查找该场景的已有图片目录
        scene_dir = watcher.watch_dir / scene
        if not scene_dir.exists():
            # 用父目录
            scene_dir = watcher.watch_dir

        result = train_gaussian_scene(scene, str(scene_dir), num_images=15)
        results.append({"scene": scene, "result": result})

    return {"status": "done", "results": results}


def train_specific_scene(scene_name: str) -> dict:
    """手动训练指定场景"""
    print(f"\n[{timestamp()}] === 手动训练: {scene_name} ===")

    # 查找图片目录
    candidates = [
        PROJECT_ROOT / "renderings_cache" / scene_name,
        GAUSSIAN_DATA_DIR / scene_name,
        PROJECT_ROOT / "models" / "3dgs_training_data" / scene_name,
    ]

    for candidate in candidates:
        if candidate.exists():
            result = train_gaussian_scene(scene_name, str(candidate))
            return result

    return {"status": "error", "message": f"场景目录不存在: {candidates}"}


def run_continuous(watch_dir: str, interval: int = 60) -> None:
    """持续监控模式"""
    print(f"\n[{timestamp()}] === 启动自动3DGS管线 ===")
    print(f"[{timestamp()}] 监控目录: {watch_dir}")
    print(f"[{timestamp()}] 检查间隔: {interval}秒")
    print(f"[{timestamp()}] 按 Ctrl+C 停止\n")

    watcher = FileWatcher(watch_dir)
    status = watcher.status()
    print(f"[{timestamp()}] 当前状态: {status['total_files']} 张图片")
    for scene, count in status.get("by_scene", {}).items():
        print(f"  - {scene}: {count}张")

    while True:
        try:
            result = process_once(watch_dir)
            if result.get("status") == "done":
                for r in result.get("results", []):
                    if r["result"]["status"] == "success":
                        print(f"[{timestamp()}] ✅ {r['scene']} 训练+部署完成")
            time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n[{timestamp()}] 停止监控")
            break


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ══════════════════════════════════════════════════════════════════
#  命令行入口
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自动化3DGS训练管线")
    parser.add_argument("--watch", type=str, default=None,
                        help="监控的目录路径")
    parser.add_argument("--interval", type=int, default=60,
                        help="检查间隔（秒），默认60")
    parser.add_argument("--once", action="store_true",
                        help="一次性运行，不持续监控")
    parser.add_argument("--train", type=str, default=None,
                        help="手动训练指定场景")
    parser.add_argument("--status", action="store_true",
                        help="显示当前监控状态")
    args = parser.parse_args()

    # 默认监控目录
    watch_dir = args.watch or str(WATCH_DIR)

    if args.status:
        watcher = FileWatcher(watch_dir)
        s = watcher.status()
        print(f"监控目录: {s['watch_dir']}")
        print(f"总图片数: {s['total_files']}")
        for scene, count in s.get("by_scene", {}).items():
            print(f"  {scene}: {count}张")
        print(f"已记录哈希: {s['known_hashes']}")
    elif args.train:
        result = train_specific_scene(args.train)
        if result["status"] == "success":
            print(f"\n✅ 训练完成: {result}")
        else:
            print(f"\n❌ 训练失败: {result.get('message', '未知错误')}")
    elif args.once:
        result = process_once(watch_dir)
        print(f"\n结果: {result}")
    elif args.watch:
        run_continuous(watch_dir, args.interval)
    else:
        parser.print_help()
        print("\n示例:")
        print("  python src/auto_3dgs_pipeline.py --status")
        print("  python src/auto_3dgs_pipeline.py --once")
        print("  python src/auto_3dgs_pipeline.py --train 室内_家庭")
        print("  python src/auto_3dgs_pipeline.py --watch \"C:\\...\\效果图\" --interval 60")
