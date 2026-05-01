import sys, json, re, os
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'C:/Users/Administrator/.qclaw/workspace/projects/building-physical-ai/'

# ─── robot v1 ───────────────────────────────────────
with open(BASE+'data/training/robot_training_data.json','rb') as f:
    raw = f.read().decode('utf-8', errors='replace')
clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', raw)
r1 = json.loads(clean)
meta1 = r1.get('meta', {})
samples1 = r1.get('samples', [])
print('=== robot_training_data_v1 ===')
print('样本数:', meta1.get('total_samples', len(samples1)))
print('来源:', meta1.get('source'))
dr = meta1.get('data_root', '')
print('数据目录(脱敏):', dr.replace('C:\\Users\\Administrator\\Desktop\\','').split('\\')[0] if dr else 'N/A')
print('场景分布:', meta1.get('stats', {}))
if samples1:
    print('记录字段:', list(samples1[0].keys()))
print()

# ─── robot v2 ────────────────────────────────────────
with open(BASE+'data/training/robot_training_data_v2.json','rb') as f:
    raw2 = f.read()
    if raw2.startswith(b'\xef\xbb\xbf'):
        raw2 = raw2[3:]
    raw2 = raw2.decode('utf-8', errors='replace')
clean2 = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', raw2)
r2 = json.loads(clean2)
if isinstance(r2, dict):
    meta2 = r2.get('meta', r2)
    samples2 = r2.get('samples', r2.get('data', []))
else:
    meta2 = {}; samples2 = r2

print('=== robot_training_data_v2 ===')
if isinstance(samples2, list):
    print('样本数:', len(samples2))
    print('元数据keys:', list(meta2.keys())[:10] if isinstance(meta2, dict) else 'N/A')
    if samples2 and isinstance(samples2[0], dict):
        print('记录字段:', list(samples2[0].keys()))
        # Show task_type distribution if exists
        if 'task_type' in samples2[0]:
            tt = {}
            for s in samples2:
                k = s.get('task_type','?')
                tt[k] = tt.get(k,0)+1
            print('任务类型:', tt)
        # Show scene distribution
        if 'scene_type' in samples2[0]:
            st = {}
            for s in samples2:
                k = s.get('scene_type','?')
                st[k] = st.get(k,0)+1
            print('场景类型:', st)
elif isinstance(r2, dict):
    print('类型: dict')
    for k in list(r2.keys())[:8]:
        v = r2[k]
        if isinstance(v, list):
            print(f'  {k}: list[{len(v)}]')
        elif isinstance(v, dict):
            print(f'  {k}: dict[{len(v)}]')
        else:
            print(f'  {k}: {str(v)[:60]}')
print()

# ─── summary ─────────────────────────────────────────
print('=== 训练数据总览 ===')
files = {
    'qa_pairs_v1.json':        (BASE+'data/training/qa_pairs_v1.json', 77, 'QA问答对'),
    'synthetic_scenes_v1.json': (BASE+'data/training/synthetic_scenes_v1.json', 100, '合成场景'),
    'robot_training_v1.json':  (BASE+'data/training/robot_training_data.json', meta1.get('total_samples', len(samples1)), '机器人训练v1'),
    'robot_training_v2.json':  (BASE+'data/training/robot_training_data_v2.json', len(samples2) if isinstance(samples2,list) else '?', '机器人训练v2'),
}
total_chars = 0
for name, (fp, count, desc) in files.items():
    sz = os.path.getsize(fp)
    chars = sz
    total_chars += chars
    tokens = chars // 2
    print(f'  {name:35s} {count:>5}条  {sz//1024:>6} KB  ~{tokens:>8,} token  [{desc}]')
print(f'  {"总计":35s} {"":>5}    {total_chars//1024:>6} KB  ~{total_chars//2:>8,} token')