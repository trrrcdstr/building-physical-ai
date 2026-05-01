"""
建筑 CAD 解析服务
从 PDF 施工图中提取建筑结构、物理属性和空间规则
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pymupdf  # PyMuPDF
import json
import re

app = FastAPI(
    title="建筑物理 AI CAD 解析服务",
    description="从 CAD 施工图提取建筑结构、物理属性和空间规则",
    version="0.1.0"
)

# CORS 配置（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BuildingObject(BaseModel):
    """建筑对象"""
    id: str
    name: str
    type: str  # wall, door, window, floor, furniture, appliance
    position: List[float]
    rotation: List[float]
    dimensions: Dict[str, float]
    physics: Optional[Dict[str, Any]] = None
    function: Optional[Dict[str, Any]] = None


class ParseResult(BaseModel):
    """解析结果"""
    success: bool
    message: str
    objects: List[BuildingObject]
    metadata: Dict[str, Any]


# 物理属性规则库
PHYSICS_RULES = {
    'wall': {
        'default': {
            'mass': 2400,  # kg/m³
            'stiffness': 25000,  # MPa
            'friction': 0.5,
            'isStructural': True,
        },
        '承重墙': {
            'mass': 2500,
            'stiffness': 30000,
            'isStructural': True,
        },
        '隔墙': {
            'mass': 800,
            'stiffness': 5000,
            'isStructural': False,
        }
    },
    'door': {
        'default': {
            'mass': 25,
            'stiffness': 12000,
            'friction': 0.3,
        },
        '实木门': {'mass': 35, 'stiffness': 15000},
        '复合门': {'mass': 20, 'stiffness': 8000},
    },
    'window': {
        'default': {
            'mass': 15,
            'stiffness': 70000,
            'friction': 0.2,
        }
    }
}


def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """从 PDF 提取文本"""
    doc = pymupdf.open(pdf_path)
    texts = []
    for page in doc:
        text = page.get_text()
        texts.append(text)
    doc.close()
    return texts


def parse_construction_text(text: str) -> List[BuildingObject]:
    """解析施工图文本，提取建筑对象"""
    objects = []
    
    # 简化版解析规则（实际需要更复杂的规则引擎）
    # 检测墙体
    wall_pattern = r'墙体[：:]\s*(\d+)[×xX](\d+)'
    wall_matches = re.findall(wall_pattern, text)
    for i, (w, h) in enumerate(wall_matches):
        objects.append(BuildingObject(
            id=f'wall-{i}',
            name=f'墙体{i+1}',
            type='wall',
            position=[0, 0, 0],
            rotation=[0, 0, 0],
            dimensions={'width': float(w)/1000, 'height': float(h)/1000, 'depth': 0.24},
            physics=PHYSICS_RULES['wall']['default']
        ))
    
    return objects


@app.get("/")
def root():
    return {"message": "建筑物理 AI CAD 解析服务运行中"}


@app.post("/api/parse", response_model=ParseResult)
async def parse_cad_file(file: UploadFile = File(...)):
    """上传 CAD PDF 文件并解析"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")
    
    try:
        # 保存临时文件
        temp_path = f"/tmp/{file.filename}"
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # 提取文本
        texts = extract_text_from_pdf(temp_path)
        full_text = '\n'.join(texts)
        
        # 解析建筑对象
        objects = parse_construction_text(full_text)
        
        return ParseResult(
            success=True,
            message=f"成功解析 {len(objects)} 个建筑对象",
            objects=objects,
            metadata={
                'filename': file.filename,
                'pages': len(texts),
                'text_length': len(full_text)
            }
        )
        
    except Exception as e:
        return ParseResult(
            success=False,
            message=f"解析失败: {str(e)}",
            objects=[],
            metadata={}
        )


@app.post("/api/batch-parse")
async def batch_parse(files: List[UploadFile] = File(...)):
    """批量解析多个 CAD 文件"""
    results = []
    for file in files:
        result = await parse_cad_file(file)
        results.append(result)
    return results


@app.get("/api/physics-rules")
def get_physics_rules():
    """获取物理属性规则库"""
    return PHYSICS_RULES


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
