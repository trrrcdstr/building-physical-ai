import re, json, os

base = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\electron"

# Check main.js
with open(os.path.join(base, "main.js"), encoding="utf-8") as f:
    main = f.read()
checks = {
    "启动时拉起后端服务": "startService" in main or "spawn" in main,
    "每项最多重试3次": "retry" in main.lower() or "maxAttempts" in main or "maxRetries" in main,
    "服务就绪后加载前端": "loadURL" in main or "BrowserWindow" in main,
    "内置守护进程": "ServiceManager" in main or "daemon" in main.lower() or "watchdog" in main.lower(),
}
for k, v in checks.items():
    status = "OK" if v else "MISSING"
    print(f"[{status}] main.js - {k}")

# Check preload.js
preload_path = os.path.join(base, "preload.js")
preload_ok = os.path.exists(preload_path)
size = os.path.getsize(preload_path) if preload_ok else 0
print(f"[{'OK' if preload_ok else 'MISSING'}] preload.js: {size} bytes")

# Check package.json
pkg_path = os.path.join(base, "package.json")
with open(pkg_path, encoding="utf-8-sig") as f:
    pkg = json.load(f)
main_field = pkg.get("main", "")
main_ok = main_field == "electron/main.js"
print(f"[{'OK' if main_ok else 'WRONG'}] package.json main: {main_field}")
scripts = list(pkg.get("scripts", {}).keys())
devdeps = list(pkg.get("devDependencies", {}).keys())
print(f"  scripts: {scripts}")
print(f"  devDependencies: {devdeps}")
has_builder = "electron-builder" in devdeps
print(f"  electron-builder installed: {has_builder}")
