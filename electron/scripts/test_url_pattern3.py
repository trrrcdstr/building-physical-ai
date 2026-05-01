# -*- coding: utf-8 -*-
import re

# Test case: two URLs without space
test = "1.https://vr.justeasy.cn/view/1ya7627u655t37q6-1762765756.html2.https://vr.justeasy.cn/view/17g0yl2409x54345-1704954590.html"

# Pattern: split on "NUMBER." + "https://" where the preceding digit sequence ends
# The separator is: (\d{1,3}\.)(https://)  -- note: \d{1,3} for 1-3 digits
# But we need to avoid matching .html or .asp parts inside URLs
# Strategy: the separator comes AFTER a non-alphanumeric boundary (space, digit seq end, etc)

# Better approach: use re.finditer with a pattern that matches "数字序列.https://" at the START
# of a URL segment (preceded by non-digit or start of string)
pattern = re.compile(r'(?:^|(?<=[^\d]))(\d{1,3}\.)(https?://[^\s<>"\']+)')

matches = list(pattern.finditer(test))
print("Matches:", [(m.group(), m.start(), m.end()) for m in matches])

# Alternative: split and take URL parts
split_result = pattern.split(test)
print("Split parts:", split_result)

# Extract URLs from split result: groups are [before, num, url, after, num, url, ...]
# The URL is in group 3 (index 2 in split)
urls = []
for i in range(2, len(split_result), 3):
    if 'https://' in split_result[i]:
        # strip trailing text that's not part of URL
        url = split_result[i].split()[0].rstrip('.,;:')
        urls.append(url)
print("Extracted URLs:", urls)
