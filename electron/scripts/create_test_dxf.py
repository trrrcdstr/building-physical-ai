"""
创建简单的DXF测试文件
使用ezdxf库生成包含建筑构件的DXF文件
"""

import ezdxf
from pathlib import Path

def create_test_dxf(output_path: str):
    """创建测试DXF文件"""
    
    # 创建新DXF文档
    doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()
    
    # 定义图层
    doc.layers.new(name='WALLS', dxfattribs={'color': 1})  # 红色
    doc.layers.new(name='DOORS', dxfattribs={'color': 3})  # 绿色
    doc.layers.new(name='WINDOWS', dxfattribs={'color': 4})  # 青色
    doc.layers.new(name='PIPES', dxfattribs={'color': 6})  # 洋红色
    doc.layers.new(name='DIMENSIONS', dxfattribs={'color': 2})  # 黄色
    
    # ========== 墙体 ==========
    
    # 北墙（承重墙）
    wall_thickness = 240  # mm
    wall_height = 3000  # mm
    room_width = 5000  # mm
    room_length = 6000  # mm
    
    # 外轮廓
    # 北墙
    msp.add_line((0, 0), (room_width, 0), dxfattribs={'layer': 'WALLS'})
    msp.add_line((0, 0), (0, wall_thickness), dxfattribs={'layer': 'WALLS'})
    msp.add_line((0, wall_thickness), (room_width, wall_thickness), dxfattribs={'layer': 'WALLS'})
    msp.add_line((room_width, 0), (room_width, wall_thickness), dxfattribs={'layer': 'WALLS'})
    
    # 南墙（非承重墙）
    msp.add_line((0, room_length), (room_width, room_length), dxfattribs={'layer': 'WALLS'})
    msp.add_line((0, room_length), (0, room_length - wall_thickness), dxfattribs={'layer': 'WALLS'})
    msp.add_line((0, room_length - wall_thickness), (room_width, room_length - wall_thickness), dxfattribs={'layer': 'WALLS'})
    msp.add_line((room_width, room_length), (room_width, room_length - wall_thickness), dxfattribs={'layer': 'WALLS'})
    
    # 东墙（隔墙）
    partition_thickness = 100  # mm
    msp.add_line((0, 0), (0, room_length), dxfattribs={'layer': 'WALLS'})
    msp.add_line((0, 0), (-partition_thickness, 0), dxfattribs={'layer': 'WALLS'})
    msp.add_line((-partition_thickness, 0), (-partition_thickness, room_length), dxfattribs={'layer': 'WALLS'})
    msp.add_line((0, room_length), (-partition_thickness, room_length), dxfattribs={'layer': 'WALLS'})
    
    # 西墙（非承重墙）
    msp.add_line((room_width, 0), (room_width, room_length), dxfattribs={'layer': 'WALLS'})
    msp.add_line((room_width, 0), (room_width + 150, 0), dxfattribs={'layer': 'WALLS'})
    msp.add_line((room_width + 150, 0), (room_width + 150, room_length), dxfattribs={'layer': 'WALLS'})
    msp.add_line((room_width, room_length), (room_width + 150, room_length), dxfattribs={'layer': 'WALLS'})
    
    # ========== 门 ==========
    
    # 北墙门洞（900mm宽）
    door_width = 900
    door_x = 2000
    msp.add_line((door_x, 0), (door_x, wall_thickness), dxfattribs={'layer': 'DOORS'})
    msp.add_line((door_x + door_width, 0), (door_x + door_width, wall_thickness), dxfattribs={'layer': 'DOORS'})
    msp.add_arc((door_x, 0), door_width, 0, 90, dxfattribs={'layer': 'DOORS'})
    
    # 门标记
    msp.add_text('M1 900x2100', dxfattribs={
        'layer': 'DOORS',
        'height': 200,
        'insert': (door_x + door_width/2, wall_thickness + 200)
    })
    
    # ========== 窗户 ==========
    
    # 南墙窗户（1200mm宽）
    window_width = 1200
    window_x = 1500
    window_sill_height = 900  # 窗台高900mm
    
    msp.add_line((window_x, room_length - wall_thickness), 
                 (window_x + window_width, room_length - wall_thickness), 
                 dxfattribs={'layer': 'WINDOWS'})
    msp.add_line((window_x, room_length), 
                 (window_x + window_width, room_length), 
                 dxfattribs={'layer': 'WINDOWS'})
    
    # 窗标记
    msp.add_text('C1 1200x1500', dxfattribs={
        'layer': 'WINDOWS',
        'height': 200,
        'insert': (window_x + window_width/2, room_length + 200)
    })
    
    # ========== 管线 ==========
    
    # 电气管线（北墙）
    msp.add_line((1000, 150), (4500, 150), dxfattribs={'layer': 'PIPES'})
    msp.add_text('电气管线', dxfattribs={
        'layer': 'PIPES',
        'height': 150,
        'insert': (2750, 300)
    })
    
    # 水管（北墙）
    msp.add_line((3000, 200), (4500, 200), dxfattribs={'layer': 'PIPES'})
    msp.add_text('水管', dxfattribs={
        'layer': 'PIPES',
        'height': 150,
        'insert': (3750, 350)
    })
    
    # ========== 尺寸标注 ==========
    
    # 房间尺寸
    msp.add_linear_dim(
        (0, -500),
        (0, 0),
        (room_width, 0),
        dxfattribs={'layer': 'DIMENSIONS'}
    )
    
    msp.add_text('房间尺寸: 5000x6000mm', dxfattribs={
        'layer': 'DIMENSIONS',
        'height': 250,
        'insert': (room_width/2, -1000)
    })
    
    # ========== 元数据（扩展数据） ==========
    
    # 添加墙体类型信息到扩展数据
    wall_types = {
        'north': 'load_bearing',
        'south': 'non_load_bearing',
        'east': 'partition',
        'west': 'non_load_bearing'
    }
    
    # 保存DXF文件
    doc.saveas(output_path)
    print(f"[DXF生成器] 已保存到: {output_path}")
    
    return {
        'walls': wall_types,
        'doors': [{'id': 'M1', 'width': 900, 'height': 2100, 'wall': 'north'}],
        'windows': [{'id': 'C1', 'width': 1200, 'height': 1500, 'wall': 'south'}],
        'pipes': [
            {'type': 'electrical', 'depth_cm': 15, 'wall': 'north'},
            {'type': 'water', 'depth_cm': 20, 'wall': 'north'}
        ],
        'room_size': {'width_mm': room_width, 'length_mm': room_length}
    }

if __name__ == "__main__":
    output_dir = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\cad_samples")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "test_building.dxf"
    metadata = create_test_dxf(str(output_path))
    
    # 保存元数据
    import json
    metadata_path = output_dir / "test_building_metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"[元数据] 已保存到: {metadata_path}")
    print("\n场景信息:")
    print(f"  墙体类型: {metadata['walls']}")
    print(f"  门: {metadata['doors']}")
    print(f"  窗: {metadata['windows']}")
    print(f"  管线: {metadata['pipes']}")
