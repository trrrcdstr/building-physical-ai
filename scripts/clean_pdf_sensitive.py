# -*- coding: utf-8 -*-
"""
CAD PDF 去敏感信息处理
去掉：公司名称、logo、电话、地址、邮箱、网址等
"""
import fitz  # pymupdf
import os
import re

def clean_pdf(input_path, output_path):
    """清理PDF中的公司敏感信息"""
    doc = fitz.open(input_path)
    fname = os.path.basename(input_path)
    print(f"\n处理: {fname} ({len(doc)}页)")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        rect = page.rect
        w, h = rect.width, rect.height
        
        # 策略1: 覆盖常见敏感区域（基于CAD图纸标准图框）
        # 通常公司信息在：右下角标题栏、左上角logo区、页脚
        
        # 右下角标题栏区域 (约 右下角 200x80 pt)
        bottom_right = fitz.Rect(w - 250, h - 100, w - 10, h - 10)
        
        # 左上角logo区域
        top_left = fitz.Rect(10, 10, 200, 80)
        
        # 页脚信息区
        footer = fitz.Rect(50, h - 50, w - 50, h - 10)
        
        # 用白色矩形覆盖这些区域
        white = (1, 1, 1)  # RGB white
        page.draw_rect(bottom_right, color=white, fill=white)
        page.draw_rect(top_left, color=white, fill=white)
        
        # 策略2: 查找并覆盖包含敏感关键词的文字块
        blocks = page.get_text("blocks")
        for block in blocks:
            x0, y0, x1, y1, text, *_ = block
            text_clean = text.strip()
            
            # 敏感关键词
            sensitive_keywords = [
                '公司', '有限', '设计', '建筑', '工程', '事务所', '设计院',
                '电话', '传真', 'TEL', 'FAX', '邮箱', 'E-mail', '网址', 'www', '.com', '.cn',
                '地址', 'Address', '邮编', '邮政编码',
                'LOGO', 'Logo', 'logo', '标志',
                '资质', '证书', '甲级', '乙级',
                '@', 'http', 'https',
            ]
            
            if any(kw in text_clean for kw in sensitive_keywords):
                # 扩大覆盖区域
                cover_rect = fitz.Rect(x0-5, y0-2, x1+5, y1+2)
                page.draw_rect(cover_rect, color=white, fill=white)
                print(f"  页{page_num+1}: 覆盖 '{text_clean[:30]}'")
        
        # 策略3: 覆盖页眉页脚区域（可能有页码和公司名）
        header = fitz.Rect(0, 0, w, 60)
        page.draw_rect(header, color=white, fill=white)
    
    # 保存
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    print(f"  输出: {output_path}")
    return True

def main():
    input_dir = r"C:\Users\Administrator\Desktop\CAD施工图"
    output_dir = r"C:\Users\Administrator\Desktop\CAD施工图\已清理"
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
    
    print(f"发现 {len(pdf_files)} 个PDF文件")
    
    for fname in pdf_files:
        input_path = os.path.join(input_dir, fname)
        output_path = os.path.join(output_dir, fname.replace('.pdf', '_cleaned.pdf'))
        try:
            clean_pdf(input_path, output_path)
        except Exception as e:
            print(f"  错误: {e}")
    
    print(f"\n完成！清理后的文件在: {output_dir}")

if __name__ == '__main__':
    main()
