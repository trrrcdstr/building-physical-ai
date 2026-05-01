import fitz
import os

folder = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\raw\产业园'
out_folder = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed'

os.makedirs(out_folder, exist_ok=True)

for f in sorted(os.listdir(folder)):
    if f.endswith('.pdf'):
        path = os.path.join(folder, f)
        print(f'Processing: {f}')
        doc = fitz.open(path)
        
        all_text = []
        for page in doc:
            text = page.get_text('text')
            if text.strip():
                all_text.append(text)
        
        txt_path = os.path.join(out_folder, f.replace('.pdf', '.txt'))
        combined = '\n'.join(all_text)
        with open(txt_path, 'w', encoding='utf-8') as out:
            out.write(combined)
        
        print(f'  Pages: {len(doc)}, Chars: {len(combined)}')
        doc.close()
