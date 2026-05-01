# -*- coding: utf-8 -*-
"""
修复1: 让RelationScene的门/窗可以被点击
问题: onClick在<group>上不工作，需要加到mesh上
"""
import re

path = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\web-app\src\scenes\RelationScene.tsx'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 DoorMesh 组件中的 onClick 位置并修复
old = """  return (
    <group onClick={onClick}"""

new = """  return (
    <group
      onClick={(e) => { e.stopPropagation(); onClick(); }}
      onPointerEnter={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer' }}
      onPointerLeave={(e) => { e.stopPropagation(); setHovered(false); document.body.style.cursor = 'default' }}
    >
      {/* 主点击区域 - 实际接收点击 */}
      <mesh>
        <boxGeometry args={[width, height, depth]} />
        <meshStandardMaterial
          color={isSelected ? '#4CAF50' : hovered ? '#FF9800' : baseColor}
          transparent
          opacity={isSelected ? 0.95 : hovered ? 0.9 : 0.75}
          emissive={isSelected ? '#4CAF50' : hovered ? '#FF9800' : '#000000'}
          emissiveIntensity={isSelected ? 0.4 : hovered ? 0.3 : 0}
        />
      </mesh>"""

# 找到原始的 return group 并替换
# 在 DoorMesh 函数中找到 return <group onClick={onClick}>
# 替换整个 return group 块
pattern = r'  return \(\s*\n    <group onClick=\{onClick\}'
if re.search(pattern, content):
    content = re.sub(pattern, new, content, count=1)
    print('Fixed DoorMesh onClick')
else:
    # 手动找到并替换
    lines = content.split('\n')
    new_lines = []
    i = 0
    found = False
    while i < len(lines):
        line = lines[i]
        if '  return (' in line and not found:
            # 检查接下来几行
            next_lines = '\n'.join(lines[i:i+3])
            if 'onClick={onClick}' in next_lines and '<group' in next_lines:
                # 找到目标位置，插入修复后的 group
                new_lines.append('  return (')
                new_lines.append('    <group')
                new_lines.append('      onClick={(e) => { e.stopPropagation(); onClick(); }}')
                new_lines.append('      onPointerEnter={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = \'pointer\' }}')
                new_lines.append('      onPointerLeave={(e) => { e.stopPropagation(); setHovered(false); document.body.style.cursor = \'default\' }}')
                new_lines.append('    >')
                new_lines.append('      {/* 主点击区域 - 实际接收点击 */}')
                new_lines.append('      <mesh>')
                new_lines.append('        <boxGeometry args={[width, height, depth]} />')
                new_lines.append('        <meshStandardMaterial')
                new_lines.append('          color={isSelected ? \'#4CAF50\' : hovered ? \'#FF9800\' : baseColor}')
                new_lines.append('          transparent')
                new_lines.append('          opacity={isSelected ? 0.95 : hovered ? 0.9 : 0.75}')
                new_lines.append('          emissive={isSelected ? \'#4CAF50\' : hovered ? \'#FF9800\' : \'#000000\'}')
                new_lines.append('          emissiveIntensity={isSelected ? 0.4 : hovered ? 0.3 : 0}')
                new_lines.append('        />')
                new_lines.append('      </mesh>')
                # 跳过原始的 group 行和 onClick 行
                i += 2  # skip "  return (" and "    <group onClick={onClick}>"
                while i < len(lines) and not lines[i].strip().endswith('</group>'):
                    i += 1  # skip body until </group>
                i += 1  # skip </group>
                found = True
                continue
        new_lines.append(line)
        i += 1
    
    if found:
        content = '\n'.join(new_lines)
        print('Fixed via manual replacement')
    else:
        print('WARNING: Could not find pattern to fix')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')