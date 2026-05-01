import fitz
import os

folder = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\raw\产业园'
out_folder = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\产业园_images'

os.makedirs(out_folder, exist_ok=True)

for f in sorted(os.listdir(folder)):
    if f.endswith('.pdf'):
        path = os.path.join(folder, f)
        print(f'Processing: {f}')
        doc = fitz.open(path)
        
        img_count = 0
        for page_idx, page in enumerate(doc):
            images = page.get_images(full=True)
            for img_idx, img in enumerate(images):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                
                if pix.n - pix.alpha < 4:
                    # RGB/Grayscale
                    ext = 'png' if pix.n - pix.alpha == 4 else 'jpg'
                    img_path = os.path.join(out_folder, f'{f[:20]}_p{page_idx+1}_{img_idx}.{ext}')
                    if ext == 'jpg':
                        pix.save(img_path)
                    else:
                        pix.save(img_path)
                else:
                    # CMYK - convert to RGB first
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                    img_path = os.path.join(out_folder, f'{f[:20]}_p{page_idx+1}_{img_idx}.png')
                    pix.save(img_path)
                
                img_count += 1
                print(f'  Extracted: {os.path.basename(img_path)}')
        
        print(f'  Total images: {img_count}')
        doc.close()

print('Done!')
