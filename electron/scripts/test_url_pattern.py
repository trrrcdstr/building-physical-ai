# -*- coding: utf-8 -*-
import re

test = "1.https://vr.justeasy.cn/view/1ya7627u655t37q6-1762765756.html2.https://vr.justeasy.cn/view/17g0yl2409x54345-1704954590.html"

# 当前pattern（字符类中不排除.）
p1 = r'https?://[^<>\"\'{}|\\^`\[\]\s,;:]+'
# 更宽松
p2 = r'https?://[^\s<>\"\'{}|\\^`\[\]]+'

r1 = re.findall(p1, test)
r2 = re.findall(p2, test)

print("p1:", r1)
print("p2:", r2)

# 更聪明的方法：从"数字.https://"或".https://"模式提取
p3 = re.compile(r'(?:^|\d\.)(https?://[^\s<>"\'{}\\|\\^`\[\]]+)')
r3 = re.findall(p3, test)
print("p3 (number prefix):", r3)

# 最简单：把"数字."替换成换行符，再提取
test_nl = re.sub(r'(\d)\.(https?://)', r'\1\n\2', test)
lines = [l.strip() for l in test_nl.split('\n') if 'https://' in l]
print("split method:", lines)
