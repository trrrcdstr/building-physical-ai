import os, json, re, sys

SRC = r"C:\Users\Administrator\Desktop\设计数据库\和瑞" + "\u00b7" + "锦钰城-建筑施工图2024.06.26合格版"

print("Path exists:", os.path.isdir(SRC))
if not os.path.isdir(SRC):
    # 试试直接列出
    parent = r"C:\Users\Administrator\Desktop\设计数据库"
    for d in os.listdir(parent):
        print("  Dir:", repr(d))
    sys.exit(1)

def anon(t):
    return re.sub(r"和瑞" + "\u00b7" + r"|锦钰城", "[项目名]", t)

results = []
total = 0
for f in os.listdir(SRC):
    fp = os.path.join(SRC, f)
    if os.path.isfile(fp) and f.lower().endswith(".dwg"):
        sz = os.path.getsize(fp) / 1e6
        total += sz
        with open(fp, "rb") as fh:
            hdr = fh.read(6)
        ver = hdr.decode("ascii", errors="ignore")[:6]
        results.append({"file": anon(f), "original": f, "version": ver, "size_mb": round(sz, 2)})
        print("[{}] {} ({:.1f}MB)".format(ver, anon(f), sz))

print("\nTotal: {} DWG files, {:.1f} MB".format(len(results), total))

# 更新知识库
kb_path = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\JINRUI_ARCHITECTURE.json"
with open(kb_path, "r", encoding="utf-8") as f:
    kb = json.load(f)
kb["cad_files"] = results
kb["total_cad_size_mb"] = round(total, 2)
with open(kb_path, "w", encoding="utf-8") as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)
print("Updated JINRUI_ARCHITECTURE.json: {} files, {:.1f}MB".format(len(results), total))
