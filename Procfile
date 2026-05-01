# Railway 部署配置
# 主推理服务（端口 5000）
neural: uvicorn src.neural_inference_server:create_app --host 0.0.0.0 --port $PORT --factory

# 场景 API 服务（端口 5001）
scene: python src/four_layer_api.py

# Agent API 服务（端口 5002）
agent: python agent_api_simple.py

# VLA 服务（端口 5004）
vla: python src/vla_server.py
