# 2026-04-29 未完成任务记录

## 当前阻塞项

### 1. DWG → DXF 转换（长期阻塞）
- 76 个 DWG 全部为二进制格式（AC1027/AC1021/AC1018），ezdxf 不支持
- LibreCAD 安装失败，ODA File Converter 网络不通
- 方案：需手动在有 AutoCAD 的机器上导出，或找 portable 版 LibreCAD

### 2. gsplat CUDA 不可用
- 系统只有 NVIDIA 驱动，无 CUDA Toolkit
- gsplat CUDA 内核无法编译，报 "No CUDA toolkit found"
- 当前方案：纯 PyTorch 2D Gaussian Splatting（图像空间，非真 3DGS）
- 替代：已验证可行，但渲染为 2D 图像平面

### 3. VLA 指令分类准确率低
- 80 epochs 训练后，val_acc=77.4%，但类别严重不平衡
- inspect 类 100%，其他类全为 0%
- 需要重新平衡训练数据

## 待推进

- [ ] 前端 GaussianScene 切换到真实模型（已有 3 个场景模型）
- [ ] App.tsx 中 GaussianScene 集成（当前可能未激活）
- [ ] 3DGS 多视角训练（当前每场景 15 张图，300 iter 偏少）
- [ ] Electron 桌面应用打包（已有 electron/ 目录框架）
- [ ] DWG 解析方案
