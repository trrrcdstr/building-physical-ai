# -*- coding: utf-8 -*-
import re

test = "1.https://vr.justeasy.cn/view/1ya7627u655t37q6-1762765756.html2.https://vr.justeasy.cn/view/17g0yl2409x54345-1704954590.html"

# The text has URLs without space separators, like: "...html2.https://..."
# Strategy: find all "https://" start positions, then find the next URL start as boundary
positions = [(m.start(), m.group()) for m in re.finditer(r'https://', test)]
print("Positions:", positions)

urls = []
for i, (pos, _) in enumerate(positions):
    start = pos
    if i + 1 < len(positions):
        end = positions[i + 1][0]
        # The boundary is where the NEXT URL starts
        # But we want to end BEFORE the digit prefix of next URL
        # So we need to backtrack from end to exclude "...N.https://"
        # Find the last valid URL end before next https://
        substring = test[start:end]
        # Remove trailing number prefix: "...N.https://" 
        # This looks like "...\d{1,3}.https://"
        m = re.search(r'\d{1,3}\.https://$', substring)
        if m:
            end = start + m.start()
        url = substring[:end - start].strip()
    else:
        url = test[start:].strip()
    
    # Clean up trailing punctuation
    url = re.sub(r'[.,;:)\]]+$', '', url)
    urls.append(url)
    
print("Extracted URLs:", urls)

# Test on full paragraph sample
test2 = "5.https://vr.zhiouwang.com/tour/2c3ba3c5d8e201d36.https://vr.justeasy.cn/view/1vy7f419n33947j4-1775805594.html"
positions2 = [(m.start(), m.group()) for m in re.finditer(r'https://', test2)]
print("\nPositions2:", positions2)

# Fix: detect digit+.https:// boundary
for i, (pos, _) in enumerate(positions2):
    start = pos
    if i + 1 < len(positions2):
        end = positions2[i + 1][0]
        url = test2[start:end]
        m = re.search(r'\d+\.https://$', url)
        if m:
            end = start + m.start()
        url = url[:end-start].rstrip('.,;: ')
        print(f"URL {i+1}: {url}")
    else:
        url = test2[start:].rstrip('.,;: ')
        print(f"URL {i+1}: {url}")
