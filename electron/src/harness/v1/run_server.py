"""
世界模型 v1 推理服务器启动脚本
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai")
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from src.harness.v1.server import main

if __name__ == "__main__":
    main()
