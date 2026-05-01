import os, json, re, sys

# 遍历桌面目录
desktop = r"C:\Users\Administrator\Desktop"
results = []

for item in os.listdir(desktop):
    full = os.path.join(desktop, item)
    if os.path.isdir(full) and ("施工图" in item or "锦钰" in item):
        print("DIR:", repr(item))
        for f in os.listdir(full):
            fp = os.path.join(full, f)
            if os.path.isfile(fp) and f.lower().endswith('.dwg'):
                sz = os.path.getsize(fp) / 1e6
                try:
                    with open(fp, "rb") as fh:
                        hdr = fh.read(6)
                    ver = hdr.decode("ascii", errors="ignore")[:6]
                except:
                    ver = "???"
                results.append({
                    "dir": item,
                    "file": f,
                    "version": ver,
                    "size_mb": round(sz, 2)
                })
                print("  [{}] {} ({:.1f}MB)".format(ver, f, sz))

print("\nTotal DWG files:", len(results))
sys.stdout.flush()
