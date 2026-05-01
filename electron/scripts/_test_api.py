import requests, json
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Accept': 'application/json'}

apis = [
    'https://www.archdaily.cn/api/v1/projects?limit=20&offset=0',
    'https://www.archdaily.cn/api/projects?limit=20',
    'https://www.archdaily.cn/search/cn/projects?q=&page=1',
]
for url in apis:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        is_json = r.text.strip().startswith('{') or r.text.strip().startswith('[')
        print(f'{url.split("?")[0]}: status={r.status_code}, len={len(r.text)}, is_json={is_json}')
        if r.status_code == 200 and is_json:
            d = json.loads(r.text)
            print(f'  keys: {list(d.keys())[:5]}')
    except Exception as e:
        print(f'{url.split("?")[0]}: ERR {e}')
