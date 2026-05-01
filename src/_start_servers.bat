@echo off
cd /d C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\src
start /min cmd /c "python neural_inference_server.py > _nn.log 2>&1"
start /min cmd /c "python four_layer_api.py > _scene.log 2>&1"
start /min cmd /c "python vla_server.py > _vla.log 2>&1"
echo Servers starting...
