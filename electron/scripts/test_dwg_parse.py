"""黄葛渡 DWG 解析测试 - 用 Python 原生路径"""
import ezdxf, os, glob, json

# 直接 glob 扫描目录
SRC = r"C:\Users\Administrator\Desktop\黄葛渡施工图"

def find_dwg_files():
    """递归找所有 DWG 文件"""
    pattern = os.path.join(SRC, "**", "*.dwg")
    files = glob.glob(pattern, recursive=True)
    return files

def check_dwg_version(fpath):
    """读 DWG 文件头判断版本"""
    with open(fpath, "rb") as f:
        header = f.read(20)
    # AC1027 = AutoCAD 2021, AC1024 = 2010, AC1021 = 2007, AC1018 = 2004
    for ver in [b"AC1027", b"AC1024", b"AC1021", b"AC1020", b"AC1018", b"AC1015"]:
        if header.startswith(ver):
            return ver.decode()
    return "unknown"

def try_parse(fpath, version):
    """尝试用 ezdxf 解析"""
    try:
        doc = ezdxf.readfile(fpath)
        msp = doc.modelspace()
        entities = list(msp)
        layers = [ln.dxf.name for ln in doc.layers]
        blocks = [bn for bn in doc.blocks.keys() if not bn.startswith("*")]
        
        # 提取几何统计
        etype_counts = {}
        lines, circles, arcs, polylines, texts = [], [], [], [], []
        
        for e in msp:
            t = e.dxftype()
            etype_counts[t] = etype_counts.get(t, 0) + 1
            if t == "LINE":
                lines.append({"start": [round(x, 3) for x in e.dxf.start],
                              "end": [round(x, 3) for x in e.dxf.end]})
            elif t == "CIRCLE":
                circles.append({"center": [round(x, 3) for x in e.dxf.center],
                                 "r": round(e.dxf.radius, 3)})
            elif t == "ARC":
                arcs.append({"center": [round(x, 3) for x in e.dxf.center],
                             "r": round(e.dxf.radius, 3),
                             "a1": round(e.dxf.start_angle, 2),
                             "a2": round(e.dxf.end_angle, 2)})
            elif t in ("LWPOLYLINE", "POLYLINE"):
                pts = [(round(p[0], 3), round(p[1], 3)) for p in e.get_points()]
                polylines.append({"points": pts, "closed": getattr(e, "closed", False)})
            elif t in ("TEXT", "MTEXT"):
                txt = e.text[:200].replace("\n", " ") if hasattr(e, "text") else str(e)
                texts.append({"type": t, "text": txt[:100]})
        
        # 计算边界
        bbox = msp.bounding_box()
        bb = None
        if bbox:
            bb = {"min": [round(x, 3) for x in bbox.extmin],
                  "max": [round(x, 3) for x in bbox.extmax]}
        
        return {
            "status": "ok",
            "version": version,
            "total_entities": len(entities),
            "entity_types": etype_counts,
            "lines_sample": lines[:30],
            "circles_sample": circles[:20],
            "arcs_sample": arcs[:20],
            "polylines_sample": polylines[:20],
            "texts_sample": texts[:20],
            "layers": layers,
            "blocks": blocks,
            "bbox": bb,
            "file_size_mb": round(os.path.getsize(fpath) / 1e6, 3)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)[:120], "version": version}

def anonymize(text):
    if not text:
        return text
    t = str(text)
    t = t.replace("龙湖", "[某房企]").replace("Longfor", "[某房企]")
    t = t.replace("黄葛渡", "[示范区]").replace("南坪", "[项目地]")
    t = t.replace("设计单位：", "设计单位：").replace("设计单位", "设计单位")
    return t

def main():
    files = find_dwg_files()
    print("Found {} DWG files".format(len(files)))
    print()
    
    results = {}
    ok_count = 0
    err_count = 0
    
    for fpath in sorted(files):
        rel = os.path.relpath(fpath, SRC)
        version = check_dwg_version(fpath)
        
        print("[{}] {}".format(version, rel))
        result = try_parse(fpath, version)
        result["original_path"] = rel
        
        if result["status"] == "ok":
            ok_count += 1
            # 清洗文本
            for t in result.get("texts_sample", []):
                t["text"] = anonymize(t["text"])
            print("  OK: {} entities | {} lines | {} circles | {} layers".format(
                result["total_entities"],
                result["entity_types"].get("LINE", 0),
                result["entity_types"].get("CIRCLE", 0),
                len(result["layers"])))
        else:
            err_count += 1
            print("  ERR: {} [{}]".format(result["error"][:60], version))
        
        # 存储相对路径作为 key（避免中文路径问题）
        results[rel] = result
    
    print()
    print("=" * 50)
    print("Summary: {} OK | {} ERR".format(ok_count, err_count))
    
    # 保存
    OUT = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\huangguidu\dwg_parsed.json"
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("Saved to: {}".format(OUT))
    
    # 按版本统计
    versions = {}
    for rel, r in results.items():
        v = r.get("version", "unknown")
        if v not in versions:
            versions[v] = {"count": 0, "ok": 0, "err": 0, "files": []}
        versions[v]["count"] += 1
        if r["status"] == "ok":
            versions[v]["ok"] += 1
        else:
            versions[v]["err"] += 1
        versions[v]["files"].append(rel)
    
    print()
    print("Version breakdown:")
    for v, info in sorted(versions.items()):
        print("  {}: {} OK / {} ERR".format(v, info["ok"], info["err"]))

if __name__ == "__main__":
    main()
