import re

file_path = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\web-app\src\components\AgentExecutionPanel.tsx"

with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 1. Add import
if "from '../shared/materialPhysicsDb'" not in content:
    old = "import { useBuildingStore } from '../store/buildingStore'"
    new = "import { useBuildingStore } from '../store/buildingStore'\nimport { inferMaterialFromTask, MATERIAL_PHYSICS_DB } from '../shared/materialPhysicsDb'"
    content = content.replace(old, new, 1)
    print('Added import')

# 2. Add state  
if 'physicsAnalysis' not in content:
    old = 'const [harnessResult, setHarnessResult] = useState<HarnessResult | null>(null)'
    new = 'const [harnessResult, setHarnessResult] = useState<HarnessResult | null>(null)\n  const [physicsAnalysis, setPhysicsAnalysis] = useState<any>(null)'
    content = content.replace(old, new, 1)
    print('Added state')

# 3. Update handleStart - add material inference before loop
if 'inferMaterialFromTask' not in content.split('handleStart')[-1]:
    # Find the setCurrentStep line and add material inference before it
    target = "setCurrentStep(0)"
    if target in content:
        insert = """setCurrentStep(0)
    // 获取材质物理数据
    const materialKey = inferMaterialFromTask(template.desc)
    const physicsData = MATERIAL_PHYSICS_DB[materialKey]
    setPhysicsAnalysis(physicsData)"""
        content = content.replace(target, insert, 1)
        print('Added material inference')

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('AgentExecutionPanel patched successfully')