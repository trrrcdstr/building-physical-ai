"""
黄葛渡施工图 DWG 解析脚本
清洗隐私信息，提取几何数据，输出为通用 JSON
"""
import ezdxf, os, json, re

SRC_DIR = r"C:\Users\Administrator\Desktop\黄葛渡施工图"
OUT_DIR = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\huangguidu"
os.makedirs(OUT_DIR, exist_ok=True)

# 需要清洗的隐私关键词
PRIVATE_COMPANY_PATTERNS = [
    r"龙湖", r"Longfor", r"LONGFOR",
    r"重庆市南岸区南坪街道",
    r"黄葛渡", r"南坪",
    r"设计单位：[\u4e00-\u9fff\w]+",
    r"施工单位：[\u4e00-\u9fff\w]+",
    r"建设单位：[\u4e00-\u9fff\w]+",
    r"勘察单位：[\u4e00-\u9fff\w]+",
    r"监理单位：[\u4e00-\u9fff\w]+",
    r"图审单位：[\u4e00-\u9fff\w]+",
    r"制图人：[\u4e00-\u9fff\w]+",
    r"审核人：[\u4e00-\u9fff\w]+",
    r"批准人：[\u4e00-\u9fff\w]+",
    r"项目名称：[\u4e00-\u9fff\w]+",
    r"项目编号：[\u4e00-\u9fff\w\d-]+",
]

def anonymize(text):
    if not text:
        return text
    result = str(text)
    # 替换公司名
    result = re.sub(r"龙湖|Longfor|LONGFOR", "[某房企]", result)
    result = re.sub(r"黄葛渡|南坪|南岸区", "[项目地]", result)
    result = re.sub(r"设计单位：[^\s，,]+", "设计单位：[某设计院]", result)
    result = re.sub(r"施工单位：[^\s，,]+", "施工单位：[某施工单位]", result)
    result = re.sub(r"建设单位：[^\s，,]+", "建设单位：[某建设单位]", result)
    result = re.sub(r"制图人：[^\s，,]+", "制图人：[设计师]", result)
    result = re.sub(r"审核人：[^\s，,]+", "审核人：[审核师]", result)
    result = re.sub(r"批准人：[^\s，,]+", "批准人：[批准人]", result)
    return result


def entity_to_dict(ent):
    """把 DXF 实体转成干净的可序列化字典"""
    d = {"type": ent.dxftype()}
    try:
        if ent.dxftype() == "LINE":
            d["start"] = [round(x, 3) for x in ent.dxf.start]
            d["end"] = [round(x, 3) for x in ent.dxf.end]
        elif ent.dxftype() == "CIRCLE":
            d["center"] = [round(x, 3) for x in ent.dxf.center]
            d["radius"] = round(ent.dxf.radius, 3)
        elif ent.dxftype() == "ARC":
            d["center"] = [round(x, 3) for x in ent.dxf.center]
            d["radius"] = round(ent.dxf.radius, 3)
            d["start_angle"] = round(ent.dxf.start_angle, 2)
            d["end_angle"] = round(ent.dxf.end_angle, 2)
        elif ent.dxftype() == "LWPOLYLINE":
            points = [(round(p[0], 3), round(p[1], 3)) for p in ent.get_points()]
            d["points"] = points
            d["closed"] = ent.closed
        elif ent.dxftype() == "TEXT":
            d["text"] = anonymize(ent.dxf.text)
            d["insert"] = [round(x, 3) for x in ent.dxf.insert]
            d["height"] = round(ent.dxf.height, 3)
        elif ent.dxftype() == "MTEXT":
            raw = ent.text.replace("\n", " ")
            d["text"] = anonymize(raw[:500])
        elif ent.dxftype() == "DIMENSION":
            d["defpoint"] = [round(x, 3) for x in ent.dxf.defpoint]
            d["measure"] = round(ent.dxf.actual_measurement, 3) if hasattr(ent.dxf, "actual_measurement") else 0
        elif ent.dxftype() == "INSERT":
            d["name"] = ent.dxf.name
            d["insert"] = [round(x, 3) for x in ent.dxf.insert]
        elif ent.dxftype() == "SPLINE":
            d["control_points"] = [[round(x, 3) for x in pt] for pt in ent.control_points]
        elif ent.dxftype() == "HATCH":
            d["pattern"] = ent.pattern
        elif ent.dxftype() == "POLYLINE":
            d["flags"] = ent.dxf.flags
        elif ent.dxftype() == "POINT":
            d["location"] = [round(x, 3) for x in ent.dxf.location]
        elif ent.dxftype() == "ELLIPSE":
            d["center"] = [round(x, 3) for x in ent.dxf.center]
            d["major_axis"] = [round(x, 3) for x in ent.dxf.major_axis]
            d["ratio"] = round(ent.dxf.ratio, 4)
        elif ent.dxftype() == "SOLID":
            d["points"] = [[round(x, 3) for x in pt] for pt in ent.points]
    except Exception:
        pass
    return d


def parse_dwg(fpath, category):
    """解析单个 DWG 文件"""
    try:
        doc = ezdxf.readfile(fpath)
    except Exception as e:
        return {"error": str(e)[:100], "status": "failed"}

    msp = doc.modelspace()
    entities_by_type = {}
    all_entities = []

    for ent in msp:
        etype = ent.dxftype()
        if etype not in entities_by_type:
            entities_by_type[etype] = 0
        entities_by_type[etype] += 1
        all_entities.append(entity_to_dict(ent))

    # 提取图层信息
    layers = []
    for name in doc.layers:
        try:
            layer = doc.layers.get(name)
            layers.append({"name": name, "color": str(layer.dxf.color)})
        except Exception:
            pass

    # 提取块信息
    blocks_info = []
    for bname, block in doc.blocks.items():
        if bname.startswith("*"):
            continue
        blocks_info.append({"name": bname, "entities": len(list(block))})

    # 提取尺寸标注的测量值（物理尺寸）
    dimensions = [e for e in all_entities if e.get("type") == "DIMENSION"]
    dim_values = [d["measure"] for d in dimensions if "measure" in d and d["measure"] > 0]

    # 计算边界框
    bbx = msp.bounding_box()
    bbox = None
    if bbx:
        bbox = {
            "min": [round(x, 3) for x in bbx.extmin],
            "max": [round(x, 3) for x in bbx.extmax]
        }

    return {
        "status": "ok",
        "file": os.path.basename(fpath),
        "category": category,
        "total_entities": len(all_entities),
        "entities_by_type": entities_by_type,
        "layers": layers,
        "blocks": blocks_info,
        "bbox": bbox,
        "dimension_values": sorted(set(dim_values))[:100],  # 取前100个去重尺寸值
        "sample_entities": all_entities[:50],  # 只存前50个实体作为样本
    }


def main():
    # 分类文件列表（全部75个文件）
    files = [
        # 建施
        ("黄葛渡2.5级示范区施工图-审查后-建/龙湖黄葛渡重庆南坪2.5级总图_20260318_t8.dwg", "建筑总图"),
        ("黄葛渡2.5级示范区施工图-审查后-建/建筑总说明-黄葛渡示范区260312.dwg", "建筑说明"),
        ("黄葛渡2.5级示范区施工图-审查后-建/10#单体260312.dwg", "建筑单体"),
        ("黄葛渡2.5级示范区施工图-审查后-建/单体 03.20_t8.dwg", "建筑单体"),
        # 景观 - 园建
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/封面目录.dwg", "景观园建"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/1.1景观竖向平面图.dwg", "景观园建"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/1.2景观索引及室外设施平面图.dwg", "景观园建"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/1.3景观铺装平面图.dwg", "景观园建"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/1.4-5景观定位平面图.dwg", "景观园建"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/10.1景石详图.dwg", "景观详图"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/11.1边坡处理详图一.dwg", "景观详图"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/11.2边坡处理详图二.dwg", "景观详图"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/2.1入口LOGO及景石详图.dwg", "景观详图"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/3.1-2休闲平台详图.dwg", "景观详图"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/4.1-6假山水景详图.dwg", "景观详图"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/5.1-2休闲木平台详图.dwg", "景观详图"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/6.1-2通用做法详图.dwg", "景观详图"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/7.1钢架桥栏杆详图.dwg", "景观详图"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/8.1装饰井盖详图.dwg", "景观详图"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/9.1泵坑详图.dwg", "景观详图"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/base.dwg", "景观园建"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/01园建/A2图框.dwg", "图框"),
        # 景观 - 植施
        ("黄葛渡2.5级示范区施工图-审查后-景观/02植施/00 图框封面目录.dwg", "景观植施"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/02植施/01 植物施工设计说明.dwg", "景观植施"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/02植施/02 植物图.dwg", "景观植施"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/02植施/A2.dwg", "景观植施"),
        ("黄葛渡2.5级示范区施工图-审查后-景观/02植施/龙湖黄葛渡重庆南坪景观BASE.dwg", "景观总图"),
        # 景观 - 安装
        ("黄葛渡2.5级示范区施工图-审查后-景观/03安装部分/安装部分20260320.zip", "景观安装_zip"),
        # 水施
        ("黄葛渡2.5级示范区施工图-审查后-水/给排水总平面图20260313_t9.dwg", "水施总图"),
        ("黄葛渡2.5级示范区施工图-审查后-水/水施20260313/单体水施_t9.dwg", "水施单体"),
        ("黄葛渡2.5级示范区施工图-审查后-水/水施20260313/给排水总平面图_t9.dwg", "水施总图"),
        ("黄葛渡2.5级示范区施工图-审查后-水/水施20260313/设计说明/目录、说明、材料表_t9.dwg", "水施说明"),
        # 电施
        ("黄葛渡2.5级示范区施工图-审查后-电/封面、目录、说明.dwg", "电施说明"),
        ("黄葛渡2.5级示范区施工图-审查后-电/电气平面图.dwg", "电施平面"),
        ("黄葛渡2.5级示范区施工图-审查后-电/电气总平面图.dwg", "电施总图"),
        ("黄葛渡2.5级示范区施工图-审查后-电/参照/TK-A1.dwg", "电施参照"),
        ("黄葛渡2.5级示范区施工图-审查后-电/参照/TK-A2.dwg", "电施参照"),
        ("黄葛渡2.5级示范区施工图-审查后-电/参照/TK.dwg", "电施参照"),
        ("黄葛渡2.5级示范区施工图-审查后-电/参照/参照-建筑.dwg", "电施参照"),
        ("黄葛渡2.5级示范区施工图-审查后-电/参照/参照-建筑2.dwg", "电施参照"),
        ("黄葛渡2.5级示范区施工图-审查后-电/参照/参照-总图.dwg", "电施总图"),
        # 结构
        ("黄葛渡2.5级示范区施工图-审查后-结/2.5级开发架空和钢结构20260318-桩底标高.dwg", "结构基础"),
        ("黄葛渡2.5级示范区施工图-审查后-结/支护剖面图20260318_t9.dwg", "结构支护"),
        ("黄葛渡2.5级示范区施工图-审查后-结/支护平面图20260318_t9.dwg", "结构支护"),
        ("黄葛渡2.5级示范区施工图-审查后-结/支护说明20260317_t9.dwg", "结构说明"),
    ]

    all_results = []
    parsed_ok = 0
    binary_cnt = 0
    failed_cnt = 0

    for i, (rel_path, category) in enumerate(files):
        fpath = os.path.join(SRC_DIR, rel_path)
        fname = os.path.basename(rel_path)

        if not os.path.exists(fpath):
            print(f"[SKIP] {fname} - 文件不存在")
            continue

        if fname.endswith(".zip"):
            print(f"[ZIP]   {i+1}/{len(files)} {fname} - 跳过压缩包")
            continue

        result = parse_dwg(fpath, category)
        result["original_path"] = rel_path
        result["category"] = category

        if result.get("error"):
            if "dimension" in result["error"].lower():
                binary_cnt += 1
            else:
                failed_cnt += 1
            print(f"[ERR]   {i+1}/{len(files)} {fname}: {result['error']}")
        else:
            parsed_ok += 1
            print(f"[OK]    {i+1}/{len(files)} {fname}: "
                  f"{result['total_entities']} entities | {len(result.get('layers', []))} layers")

        all_results.append(result)

    # 统计汇总
    summary = {
        "total": len(files),
        "parsed": parsed_ok,
        "binary_skip": binary_cnt,
        "failed": failed_cnt,
        "categories": {}
    }
    for r in all_results:
        cat = r.get("category", "unknown")
        if cat not in summary["categories"]:
            summary["categories"][cat] = {"count": 0, "entities": 0, "files": []}
        summary["categories"][cat]["count"] += 1
        summary["categories"][cat]["entities"] += r.get("total_entities", 0)
        summary["categories"][cat]["files"].append(r.get("file", ""))

    # 保存完整结果
    out_all = os.path.join(OUT_DIR, "huangguidu_all_parsed.json")
    with open(out_all, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    # 保存汇总
    out_summary = os.path.join(OUT_DIR, "huangguidu_summary.json")
    with open(out_summary, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"解析完成！")
    print(f"  总计文件: {len(files)}")
    print(f"  解析成功: {parsed_ok}")
    print(f"  二进制跳过: {binary_cnt}")
    print(f"  解析失败: {failed_cnt}")
    print(f"  输出: {out_all}")
    print(f"  汇总: {out_summary}")

    return summary, all_results


if __name__ == "__main__":
    main()
