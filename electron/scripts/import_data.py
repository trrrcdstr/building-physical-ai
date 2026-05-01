"""
建筑数据导入脚本 v2.0
====================
从桌面建筑数据库导入所有类型数据：
- CAD施工图
- 效果图
- 结构图纸
- 电气图纸
- 景观图纸
"""

import os
import re
import json
import fitz  # PyMuPDF
from PIL import Image
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

# 数据路径
DESKTOP_DATA_PATH = Path(os.path.expanduser("~/Desktop/建筑数据库"))
PROJECT_DATA_PATH = Path(__file__).parent.parent / "data"
PROCESSED_DATA_PATH = PROJECT_DATA_PATH / "processed"


# ============================================================
# 项目类型分类
# ============================================================

PROJECT_TYPES = {
    "residential": "住宅",
    "villa": "别墅",
    "commercial": "商业",
    "landscape": "景观",
    "structure": "结构"
}


def get_project_type(dir_name: str) -> str:
    """根据目录名判断项目类型"""
    name_lower = dir_name.lower()
    
    if "翠微" in name_lower or "旧村" in name_lower:
        return "urban_renovation"
    elif "别墅" in name_lower or "villa" in name_lower or "黄" in name_lower:
        return "villa"
    elif "景观" in name_lower or "园林" in name_lower or "花园" in name_lower:
        return "landscape"
    elif "结构" in name_lower or "施工" in name_lower or "图纸" in name_lower:
        return "structure"
    elif "商业" in name_lower or "办公" in name_lower:
        return "commercial"
    else:
        return "residential"


def classify_pdf(pdf_path: Path) -> str:
    """根据PDF文件名分类"""
    name_lower = pdf_path.stem.lower()
    
    if "结构" in name_lower or "梁" in name_lower or "柱" in name_lower or "楼" in name_lower:
        return "structure"
    elif "电气" in name_lower or "电" in name_lower or "配电" in name_lower:
        return "electrical"
    elif "景观" in name_lower or "园林" in name_lower or "方案" in name_lower:
        return "landscape"
    elif "给排水" in name_lower or "水暖" in name_lower:
        return "plumbing"
    elif "暖通" in name_lower or "空调" in name_lower:
        return "hvac"
    else:
        return "cad"


# ============================================================
# 解析函数
# ============================================================

def extract_text_from_pdf(pdf_path: Path) -> str:
    """从 PDF 提取文本"""
    try:
        doc = fitz.open(str(pdf_path))
        texts = []
        for page in doc:
            text = page.get_text()
            texts.append(text)
        doc.close()
        return "\n".join(texts)
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""


def parse_wall_dimensions(text: str) -> List[Dict]:
    """解析墙体尺寸标注"""
    walls = []
    
    # 常见墙体标注格式
    patterns = [
        r'(\d+)[×xX](\d+)\s*墙',
        r'墙厚[：:]\s*(\d+)',
        r'(\d+)mm\s*厚',
        r'承重墙[：:]?\s*(\d+)[×xX](\d+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) == 2:
                walls.append({
                    "thickness": int(match[0]),
                    "height": int(match[1]),
                    "is_structural": "承重" in text
                })
            elif len(match) == 1:
                walls.append({
                    "thickness": int(match[0]),
                    "height": 3000,
                    "is_structural": False
                })
    
    return walls


def parse_room_labels(text: str) -> List[Dict]:
    """解析房间标注"""
    rooms = []
    
    room_patterns = [
        (r'客厅', '客厅'),
        (r'卧室', '卧室'),
        (r'厨房', '厨房'),
        (r'卫生间', '卫生间'),
        (r'阳台', '阳台'),
        (r'书房', '书房'),
        (r'餐厅', '餐厅'),
        (r'走廊', '走廊'),
        (r'玄关', '玄关'),
        (r'车库', '车库'),
        (r'储藏', '储藏室'),
        (r'影音', '影音室'),
        (r'花园', '花园'),
        (r'庭院', '庭院'),
    ]
    
    for pattern, room_type in room_patterns:
        if re.search(pattern, text):
            rooms.append({"type": room_type, "found": True})
    
    return rooms


def parse_cad_pdf(pdf_path: Path) -> Dict[str, Any]:
    """解析 CAD 施工图 PDF"""
    result = {
        "filename": pdf_path.name,
        "pdf_type": classify_pdf(pdf_path),
        "pages": 0,
        "walls": [],
        "doors_windows": [],
        "rooms": [],
        "structures": [],  # 结构元素
        "electrical": [],   # 电气元素
        "landscape": [],    # 景观元素
        "dimensions": {},
        "raw_text": ""
    }
    
    try:
        doc = fitz.open(str(pdf_path))
        result["pages"] = len(doc)
        
        # 提取文本
        texts = []
        for page in doc:
            text = page.get_text()
            texts.append(text)
        full_text = "\n".join(texts)
        result["raw_text"] = full_text[:2000]
        
        # 根据类型解析
        pdf_type = result["pdf_type"]
        
        if pdf_type == "structure":
            # 结构图纸解析
            result["structures"] = parse_structure_elements(full_text)
        elif pdf_type == "electrical":
            # 电气图纸解析
            result["electrical"] = parse_electrical_elements(full_text)
        elif pdf_type == "landscape":
            # 景观图纸解析
            result["landscape"] = parse_landscape_elements(full_text)
        else:
            # 标准CAD解析
            result["walls"] = parse_wall_dimensions(full_text)
            result["rooms"] = parse_room_labels(full_text)
        
        # 提取尺寸
        dimensions = re.findall(r'(\d{3,5})\s*(?:mm|m)?', full_text)
        if dimensions:
            result["dimensions"] = {
                "values": [int(d) for d in dimensions[:20]],
                "max": max([int(d) for d in dimensions]) if dimensions else 0,
                "min": min([int(d) for d in dimensions]) if dimensions else 0
            }
        
        doc.close()
        
    except Exception as e:
        print(f"  Error: {e}")
    
    return result


def parse_structure_elements(text: str) -> List[Dict]:
    """解析结构元素"""
    elements = []
    
    patterns = [
        (r'梁[：:]?\s*(\d+)[×xX](\d+)', 'beam'),
        (r'柱[：:]?\s*(\d+)', 'column'),
        (r'板[：:]?\s*(\d+)[×xX](\d+)', 'slab'),
        (r'基础[：:]?\s*(\d+)', 'foundation'),
        (r'楼梯', 'stair'),
    ]
    
    for pattern, elem_type in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            elements.append({
                "type": elem_type,
                "dimensions": [int(match[0]), int(match[1]) if len(match) > 1 else 3000]
            })
    
    return elements


def parse_electrical_elements(text: str) -> List[Dict]:
    """解析电气元素"""
    elements = []
    
    patterns = [
        (r'配电箱', 'distribution_board'),
        (r'开关[：:]?\s*(\d+)', 'switch'),
        (r'插座[：:]?\s*(\d+)', 'outlet'),
        (r'灯具', 'lighting'),
        (r'回路[：:]?\s*(\d+)', 'circuit'),
    ]
    
    for pattern, elem_type in patterns:
        if re.search(pattern, text):
            elements.append({"type": elem_type, "found": True})
    
    return elements


def parse_landscape_elements(text: str) -> List[Dict]:
    """解析景观元素"""
    elements = []
    
    patterns = [
        (r'锦鲤池', 'koi_pond'),
        (r'假山', 'rockery'),
        (r'跌水', 'waterfall'),
        (r'烧烤区', 'bbq_area'),
        (r'亭子', 'pavilion'),
        (r'景墙', 'feature_wall'),
        (r'台阶', 'steps'),
        (r'廊架', 'pergola'),
        (r'乔木', 'tree'),
        (r'灌木', 'shrub'),
        (r'草坪', 'lawn'),
    ]
    
    for pattern, elem_type in patterns:
        if re.search(pattern, text):
            elements.append({"type": elem_type, "found": True})
    
    return elements


def load_render_images(client_dir: Path) -> List[Path]:
    """加载效果图"""
    images = []
    if client_dir.exists():
        for file in client_dir.iterdir():
            if file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                images.append(file)
    return images


# ============================================================
# 主导入函数
# ============================================================

def import_project_data():
    """导入所有项目数据"""
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 60)
    print("Building Data Import v2.0")
    print("=" * 60)
    
    if not DESKTOP_DATA_PATH.exists():
        print(f"Data path not found: {DESKTOP_DATA_PATH}")
        return None
    
    # 创建输出目录
    PROJECT_DATA_PATH.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)
    
    projects = []
    
    # 遍历客户目录
    for client_dir in DESKTOP_DATA_PATH.iterdir():
        if not client_dir.is_dir():
            continue
        
        client_name = client_dir.name
        project_type = get_project_type(client_name)
        print(f"\nProject: {client_name} ({project_type})")
        
        project = {
            "name": client_name,
            "type": project_type,
            "path": str(client_dir),
            "cad_files": [],
            "render_images": [],
            "structure_files": [],
            "electrical_files": [],
            "landscape_files": [],
            "plumbing_files": [],
            "hvac_files": [],
            "parsed_data": []
        }
        
        # 分类查找 PDF 文件
        for pdf_file in client_dir.glob("*.pdf"):
            pdf_type = classify_pdf(pdf_file)
            print(f"  PDF: {pdf_file.name} ({pdf_type})")
            
            if pdf_type == "structure":
                project["structure_files"].append(str(pdf_file))
            elif pdf_type == "electrical":
                project["electrical_files"].append(str(pdf_file))
            elif pdf_type == "landscape":
                project["landscape_files"].append(str(pdf_file))
            elif pdf_type == "plumbing":
                project["plumbing_files"].append(str(pdf_file))
            elif pdf_type == "hvac":
                project["hvac_files"].append(str(pdf_file))
            else:
                project["cad_files"].append(str(pdf_file))
            
            # 解析 CAD
            parsed = parse_cad_pdf(pdf_file)
            project["parsed_data"].append(parsed)
        
        # 查找效果图
        render_images = load_render_images(client_dir)
        print(f"  Images: {len(render_images)}")
        for img in render_images:
            project["render_images"].append(str(img))
        
        # 统计对象数量
        total_objects = 0
        for parsed in project["parsed_data"]:
            total_objects += len(parsed.get("walls", []))
            total_objects += len(parsed.get("structures", []))
            total_objects += len(parsed.get("electrical", []))
            total_objects += len(parsed.get("landscape", []))
        project["object_count"] = total_objects
        
        if project["cad_files"] or project["render_images"] or project["structure_files"]:
            projects.append(project)
    
    # 保存处理结果
    output_path = PROCESSED_DATA_PATH / "projects.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)
    
    # 打印统计
    print("\n" + "=" * 60)
    print("Import Summary:")
    print("=" * 60)
    print(f"Total projects: {len(projects)}")
    
    for p in projects:
        print(f"\n  {p['name']} ({p['type']})")
        print(f"    CAD: {len(p['cad_files'])}")
        print(f"    Structure: {len(p['structure_files'])}")
        print(f"    Electrical: {len(p['electrical_files'])}")
        print(f"    Landscape: {len(p['landscape_files'])}")
        print(f"    Images: {len(p['render_images'])}")
    
    print(f"\nOutput: {output_path}")
    print("Done!")
    
    return projects


# ============================================================
# 快速测试
# ============================================================

if __name__ == "__main__":
    import_project_data()
