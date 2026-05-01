import requests, re, time, json
from pathlib import Path

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

test_urls = [
    'https://www.archdaily.cn/cn/tag/ju-zhu-jian-zhu',
    'https://www.archdaily.cn/cn/tag/jing-guan',
    'https://www.archdaily.cn/cn/tag/shi-nei-she-ji',
    'https://www.archdaily.cn/cn/tag/jing-guan-jian-zhu',
    'https://www.archdaily.cn/cn/tag/shang-ye-jian-zhu',
]

for url in test_urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        links = re.findall(r'href="(https://www\.archdaily\.cn/cn/\d+/[^"]+)"', r.text)
        links = list(set(links))
        print(f'{url.split("/")[-1]}: {len(links)} links, status={r.status_code}')
        if links:
            print('  sample:', links[:3])
    except Exception as e:
        print(f'ERR {url}: {e}')
