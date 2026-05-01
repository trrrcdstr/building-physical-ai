import os, json, re

# 直接用 os.listdir 遍历
src = r"C:\Users\Administrator\Desktop"
for item in os.listdir(src):
    if "锦钰" in item or "和瑞" in item or "施工图" in item:
        full = os.path.join(src, item)
        if os.path.isdir(full):
            print("DIR:", item)
            for f in os.listdir(full):
                fp = os.path.join(full, f)
                sz = os.path.getsize(fp) / 1e6
                with open(fp, "rb") as fh:
                    hdr = fh.read(6)
                ver = hdr.decode("ascii", errors="ignore")[:6]
                print("  [{}] {} ({:.1f}MB)".format(ver, f, sz))
