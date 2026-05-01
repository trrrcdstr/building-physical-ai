# -*- coding: utf-8 -*-
import re

# 模拟文档真实内容
test = "1.https://vr.justeasy.cn/view/1ya7627u655t37q6-1762765756.html2.https://vr.justeasy.cn/view/17g0yl2409x54345-1704954590.html"

# 改进：只匹配"数字序列.https://"作为分隔符，不匹配URL内部的
# 思路：(?<!\d) = 前一个字符不是数字
p_split = re.compile(r'(?<!\d)\.(\d{1,3}\.(https?://))')
# 更简单：用非数字字符或行首作为锚点
p2 = re.compile(r'(?:^|[^\d])(\d{1,3}\.(https?://[^\s<>"\'{}\\|\\^`\\[\\]]+))')

# 最直接：把"非URL字符 + 数字序列 + . + https"替换为\n
p3 = re.compile(r'(?<=[^\d\w])(\d{1,3}\.)(https?://)')
result = p3.split(test)
print("parts:", result)
urls = [result[i+2] for i in range(0, len(result)-2, 3) if result[i+2]]
print("urls:", urls)

# 也试试行首
p4 = re.compile(r'(?:^|[\n\r\s]+)(\d+\.)(https?://[^\s<>"\'{}\\|\\^`\\[\\]]+)', re.M)
p4_repl = re.compile(r'\n?(\d+)\.(https?://[^\s<>"\'{}\\|\\^`\\[\\]]+)')
lines = [l.strip() for l in re.split(r'(?:^|\n)(\d+\.)', test) if l.strip() and 'https://' in l]
print("line split:", lines)
