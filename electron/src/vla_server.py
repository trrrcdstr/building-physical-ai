"""
Psi-R2 VLA 推理服务 (端口 5004)
加载训练好的 vla_model.pt，提供指令分类 + 置信度 + 任务建议
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import torch
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path
import argparse
from datetime import datetime

# ─── Config ──────────────────────────────────────────────
ROOT = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai")
DEFAULT_PORT = 5004
VOCAB_SIZE = 12000
EMBED_DIM = 128
FEATURE_DIM = VOCAB_SIZE + 5

# ─── Model ──────────────────────────────────────────────
class VLAModel(nn.Module):
    def __init__(self, num_tasks=5):
        super().__init__()
        self.text_net = nn.Sequential(
            nn.Linear(FEATURE_DIM, 512), nn.LayerNorm(512), nn.GELU(), nn.Dropout(0.2),
            nn.Linear(512, 256), nn.LayerNorm(256), nn.GELU(), nn.Dropout(0.1),
            nn.Linear(256, EMBED_DIM),
        )
        self.scene_net = nn.Sequential(
            nn.Linear(64, 128), nn.LayerNorm(128), nn.GELU(),
            nn.Linear(128, EMBED_DIM),
        )
        self.fusion = nn.Sequential(
            nn.Linear(EMBED_DIM * 2, EMBED_DIM), nn.LayerNorm(EMBED_DIM), nn.GELU(), nn.Dropout(0.1),
            nn.Linear(EMBED_DIM, num_tasks),
        )
    
    def forward(self, feat, scene_emb):
        t = self.text_net(feat)
        s = self.scene_net(scene_emb)
        return self.fusion(torch.cat([t, s], dim=-1))
    
    def encode(self, feat, scene_emb):
        t = self.text_net(feat)
        s = self.scene_net(scene_emb)
        return torch.cat([t, s], dim=-1)


ACTION_KEYWORDS = {
    'drill': ['钻', '孔', '挂', '安装', '打孔', '膨胀', '螺栓', '螺丝', '冲击钻', '孔眼', '墙孔'],
    'clean': ['清洁', '打扫', '擦', '拖', '洗', '除尘', '清理', '擦拭', '刷洗', '抛光', '清扫'],
    'move': ['搬', '移', '运输', '移动', '抬起', '放下', '抓取', '夹取', '搬运', '推', '拉'],
    'navigate': ['路径', '路线', '导航', '走向', '通往', '最短', '距离', '怎么走', '怎么去', '路线'],
    'inspect': ['检查', '查看', '巡视', '巡查', '测量', '检测', '确认', '识别', '评估', '看'],
}

TASK_KEYWORDS = {
    'drill': {
        'safe': ['在东墙', '在北墙（非承重）', '在西墙', '在南墙', '墙面钻孔', '墙上打孔', '膨胀螺栓'],
        'unsafe': ['北墙（承重墙）', '承重墙钻孔', '梁上钻孔'],
        'steps_template': [
            '① 用水平仪确认位置（建议离地150cm）',
            '② 用铅笔标记打孔位置',
            '③ 贴美纹纸保护周围墙面',
            '④ 低速预钻（6mm钻头）',
            '⑤ 插入膨胀螺栓',
            '⑥ 安装并确认牢固',
        ],
    },
    'clean': {
        'glass': ['玻璃', '隔断', '淋浴房'],
        'floor': ['地板', '地面', '地砖'],
        'counter': ['台面', '厨房', '餐桌'],
        'steps_template': [
            '【安全准备】轻柔模式，移动速度限制0.2m/s，力度<5N',
            '【材质识别】识别表面材质类型',
            '【清洁作业】顺纹理/纹路单向擦拭',
            '【干燥检测】气流干燥5分钟',
            '【完成确认】拍照记录',
        ],
    },
    'move': {
        'steps_template': [
            '① 深度相机识别物体边界和重心',
            '② 规划抓取点（重心偏移10%）',
            '③ 夹爪力度逐步增加至安全力度',
            '④ 抬起至安全高度（30cm）',
            '⑤ 沿最短路径搬运',
            '⑥ 放置并确认稳定',
        ],
    },
    'navigate': {
        'steps_template': [
            '① 构建空间图谱',
            '② Dijkstra路径规划',
            '③ 障碍物检测',
            '④ 路径执行',
        ],
    },
    'inspect': {
        'steps_template': [
            '① 视觉扫描目标区域',
            '② 传感器数据采集',
            '③ 异常检测与标注',
            '④ 生成检查报告',
        ],
    },
}


def extract_features(text: str):
    bow = torch.zeros(VOCAB_SIZE)
    for w in text.split():
        idx = abs(hash(w)) % VOCAB_SIZE
        bow[idx] += 1.0
    if bow.sum() > 0:
        bow = bow / bow.sum()
    
    action_vec = torch.zeros(5)
    task_order = ['drill', 'clean', 'move', 'navigate', 'inspect']
    for i, task in enumerate(task_order):
        for kw in ACTION_KEYWORDS[task]:
            if kw in text:
                action_vec[i] += 1
    if action_vec.sum() > 0:
        action_vec = action_vec / action_vec.sum()
    
    return torch.cat([bow, action_vec])


def get_scene_emb(sid: str):
    h = hash(sid)
    return torch.tensor([((h >> (i*7)) & 0x3F) / 63.0 - 0.5 for i in range(64)], dtype=torch.float32)


def generate_steps(task_type: str, instruction: str) -> list:
    """根据任务类型生成步骤"""
    if task_type == 'drill':
        steps = list(TASK_KEYWORDS['drill']['steps_template'])
        # 检查是否是承重墙
        if '北墙' in instruction:
            steps = ['⚠️ 北墙为结构承重墙，钻孔会破坏结构安全！'] + steps[:0] + ['建议改用免钉胶或落地支架']
        return steps
    
    if task_type == 'clean':
        steps = []
        if any(kw in instruction for kw in TASK_KEYWORDS['clean']['glass']):
            steps.append('【玻璃清洁】使用橡胶刮刀自上而下，力度<5N')
        if any(kw in instruction for kw in TASK_KEYWORDS['clean']['floor']):
            steps.append('【地面清洁】从内向外倒退清洁，禁止来回摩擦')
        if any(kw in instruction for kw in TASK_KEYWORDS['clean']['counter']):
            steps.append('【台面清洁】顺纹理单向擦拭，及时擦干水渍')
        return steps + list(TASK_KEYWORDS['clean']['steps_template'][1:])
    
    return list(TASK_KEYWORDS.get(task_type, {}).get('steps_template', []))


def generate_warnings(task_type: str, instruction: str) -> list:
    """生成安全警告"""
    warnings = []
    if task_type == 'drill':
        warnings = ['避开窗框50cm范围', '避开墙角30cm范围', '确认墙内无水管电线']
        if '北墙' in instruction:
            warnings = ['⚠️ 承重墙禁止钻孔！', '建议改用免钉胶']
    elif task_type == 'clean':
        if any(kw in instruction for kw in ['玻璃', '淋浴']):
            warnings.append('玻璃表面力度<5N，禁止硬质工具接触')
        if any(kw in instruction for kw in ['厨房', '卫生间']):
            warnings.append('湿区操作，地面湿滑，速度限制0.3m/s')
    return warnings


# ─── Load model ─────────────────────────────────────────
def load_model():
    ckpt_path = ROOT / "data/processed/checkpoints/vla_model.pt"
    if not ckpt_path.exists():
        print(f"[WARN] VLA checkpoint not found: {ckpt_path}")
        return None, None, None
    
    ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=True)
    TASK_LIST = ckpt.get('task_types', ['drill','clean','move','navigate','inspect'])
    model = VLAModel(len(TASK_LIST))
    model.load_state_dict(ckpt['model_state'], strict=False)
    model.eval()
    val_acc = ckpt.get('val_acc', 0)
    print(f"[INFO] VLA model loaded: {TASK_LIST}, val_acc={val_acc:.3f}")
    return model, TASK_LIST, val_acc


# ─── Inference ──────────────────────────────────────────
def infer(instruction: str, room_id: str = 'room_00', model=None, TASK_LIST=None):
    if model is None or TASK_LIST is None:
        return {
            'task_type': 'inspect',
            'confidence': 0.5,
            'all_probs': {},
            'steps': ['系统模拟中...'],
            'warnings': [],
        }
    
    with torch.no_grad():
        feat = extract_features(instruction).unsqueeze(0)
        emb = get_scene_emb(room_id).unsqueeze(0)
        logits = model(feat, emb)
        probs = F.softmax(logits, dim=-1)[0]
        
        pred_idx = logits.argmax(dim=-1).item()
        pred_task = TASK_LIST[pred_idx]
        conf = probs[pred_idx].item()
        
        all_probs = {TASK_LIST[i]: round(probs[i].item(), 4) for i in range(len(TASK_LIST))}
        
        steps = generate_steps(pred_task, instruction)
        warnings = generate_warnings(pred_task, instruction)
        
        # Determine success/failure
        success = True
        if pred_task == 'drill' and '北墙（承重墙）' in instruction:
            success = False
            steps = ['⚠️ 承重墙禁止钻孔！'] + steps[:1]
        
        return {
            'task_type': pred_task,
            'confidence': round(conf, 4),
            'all_probs': all_probs,
            'steps': steps,
            'warnings': warnings,
            'success': success,
            'model_info': {
                'name': 'Psi-R2 VLA',
                'val_acc': 0.684,
                'version': 'v3-balanced',
            },
        }


# ─── FastAPI server ────────────────────────────────────
def create_vla_server(port=DEFAULT_PORT):
    model, TASK_LIST, val_acc = load_model()
    
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        import uvicorn
    except ImportError:
        print("[ERROR] fastapi/uvicorn not installed. Try: pip install fastapi uvicorn")
        return
    
    app = FastAPI(title="Psi-R2 VLA Server", version="v3")
    
    class VLARequest(BaseModel):
        instruction: str
        room_id: str = 'room_00'
    
    class VLAResponse(BaseModel):
        task_type: str
        confidence: float
        all_probs: dict
        steps: list
        warnings: list
        success: bool
        model_info: dict
    
    @app.get("/api/health")
    async def health():
        return {
            "status": "ok",
            "model": "Psi-R2 VLA",
            "version": "v3-balanced",
            "val_acc": val_acc if val_acc else 0,
            "tasks": TASK_LIST if TASK_LIST else [],
            "ready": model is not None,
        }
    
    @app.post("/api/classify", response_model=VLAResponse)
    async def classify(req: VLARequest):
        result = infer(req.instruction, req.room_id, model, TASK_LIST)
        return result
    
    @app.get("/api/tasks")
    async def list_tasks():
        """列出所有支持的任务类型"""
        return {
            "tasks": TASK_LIST if TASK_LIST else [],
            "keywords": ACTION_KEYWORDS,
        }
    
    @app.get("/api/demo")
    async def demo():
        """内置演示测试"""
        demos = [
            ("在东墙钻孔挂画", "drill"),
            ("清洁淋浴房的玻璃隔断", "clean"),
            ("把茶几移到窗边", "move"),
            ("规划去洗手间的最短路径", "navigate"),
            ("检查厨房烟雾报警器", "inspect"),
        ]
        results = []
        for instr, expected in demos:
            r = infer(instr, 'room_00', model, TASK_LIST)
            r['expected'] = expected
            r['correct'] = r['task_type'] == expected
            results.append(r)
        return {"demo_results": results}
    
    print(f"[INFO] Starting VLA server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    create_vla_server(port=args.port)
