# -*- coding: utf-8 -*-
import subprocess, sys

# Run pandoc
result = subprocess.run(
    ["pandoc", r"C:\Users\Administrator\Desktop\设计数据库\新3D效果图链接.docx", "-o", r"C:\Users\Administrator\vr_links_raw.md"],
    capture_output=True, text=True
)
print("pandoc:", result.returncode, result.stderr[:200] if result.stderr else "OK")

# Read output
try:
    with open(r"C:\Users\Administrator\vr_links_raw.md", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    print(f"Total chars: {len(content)}")
    print("="*60)
    print(content[:3000])
    print("="*60)
    print("... (truncated)")
    print("Last 1000 chars:")
    print(content[-1000:])
except Exception as e:
    print(f"Error: {e}")
