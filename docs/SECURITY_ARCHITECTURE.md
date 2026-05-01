# 瀹夊叏鏋舵瀯鏂囨。

## 1. 璁捐鍘熷垯

| 鍘熷垯 | 璇存槑 |
|------|------|
| **鏁版嵁鏈湴鍖?* | 鎵€鏈夊師濮嬫暟鎹紙CAD/VR/娓叉煋鍥撅級瀛樺偍鍦ㄦ湰鍦帮紝涓嶄笂浼犱簯绔?|
| **鏈€灏忓寲娉勯湶** | 浠呭鍑鸿劚鏁忓悗鐨勭粨鏋勫寲鏁版嵁锛堝潗鏍?鍏崇郴/宓屽叆锛夛紝涓嶅惈鍘熷鍐呭 |
| **缃戠粶闅旂** | 鎺ㄧ悊鏈嶅姟鍣ㄤ粎鐩戝惉 localhost锛屼笉鏆撮湶鍏綉绔彛 |
| **鍙璁℃€?* | 鎵€鏈夋暟鎹搷浣滆褰曟棩蹇楋紝鏀寔杩芥函 |

## 2. 鏁版嵁鍒嗙被涓庡畨鍏ㄧ瓥鐣?
| 鏁版嵁绫诲埆 | 绀轰緥 | 瀛樺偍浣嶇疆 | 瀹夊叏绛夌骇 |
|----------|------|----------|----------|
| 鍘熷CAD/VR | DWG/VR鍏ㄦ櫙閾炬帴 | 妗岄潰/椤圭洰鐩綍 | 馃敶 鏈€楂?|
| 鐭ヨ瘑搴?| 瀹℃煡鎰忚/宸ヨ壓鏍囧噯 | `knowledge/` | 馃煚 楂?|
| 璁粌鏁版嵁 | 鍧愭爣/鍏崇郴/宓屽叆 | `data/processed/` | 馃煛 涓?|
| 妯″瀷鏉冮噸 | .pth/.pt鏂囦欢 | `models/` | 馃煛 涓?|
| 鎺ㄧ悊杈撳嚭 | 鍦烘櫙鍥?鍏崇郴棰勬祴 | 鍐呭瓨/涓存椂鏂囦欢 | 馃煝 浣?|

## 3. 鏁版嵁娴佸嚭绠℃帶

### 3.1 瀵硅瘽灞傞潰

```
鉂?绂佹鍦ㄥ璇濅腑閫忛湶锛?   - 鍏蜂綋椤圭洰鍚嶇О锛堥緳婀?閲戣灣铻?鏅熻拏楣忥級
   - 瀹㈡埛濮撳悕/鑱旂郴鏂瑰紡
   - CAD鍥剧焊鍐呭
   - VR閾炬帴鍘熷URL

鉁?鍏佽瀵煎嚭锛?   - 缁熻淇℃伅锛?鍏?51涓棬/绐楀璞?锛?   - 鍧愭爣鑼冨洿锛?X: [0, 300]m"锛?   - 妯″瀷绮惧害锛?Val Acc: 98.1%"锛?```

### 3.2 鏂囦欢灞傞潰

```python
# 鏁版嵁瀵煎嚭鏃剁殑寮哄埗鑴辨晱
def export_safe_data(data: dict) -> dict:
    """瀵煎嚭鏃剁Щ闄ゆ晱鎰熷瓧娈?""
    SAFE_FIELDS = {
        "scene_id", "category", "scene_type", 
        "position", "rotation", "dimensions",
        "relation_type", "confidence"
    }
    
    SENSITIVE_FIELDS = {
        "original_path", "url", "designer", 
        "company", "client", "project_name"
    }
    
    return {
        k: v for k, v in data.items() 
        if k in SAFE_FIELDS
    }
```

### 3.3 缃戠粶灞傞潰

| 鎺ュ彛 | 璁块棶鎺у埗 | 璁よ瘉 |
|------|----------|------|
| `/api/scene` | localhost only | None |
| `/api/relation` | localhost only | None |
| `/api/physics` | localhost only | None |
| 鍓嶇WebSocket | localhost only | None |

**閮ㄧ讲鏃?*锛氳嫢闇€杩滅▼璁块棶锛屼娇鐢?VPN 鎴?SSH 闅ч亾锛屼笉寮€鏀惧叕缃戠鍙ｃ€?
## 4. 鏈湴鏁版嵁瀛樺偍

```
椤圭洰鏍圭洰褰?鈹溾攢鈹€ data/
鈹?  鈹溾攢鈹€ raw/                    # 鍘熷鏁版嵁锛堜笉鎻愪氦锛?鈹?  鈹?  鈹溾攢鈹€ cad/                # DWG鏂囦欢
鈹?  鈹?  鈹溾攢鈹€ vr/                 # VR鍏ㄦ櫙鎴浘
鈹?  鈹?  鈹斺攢鈹€ renderings/         # 鏁堟灉鍥?鈹?  鈹溾攢鈹€ processed/              # 鑴辨晱鍚庢暟鎹?鈹?  鈹?  鈹溾攢鈹€ scene_graph.json   # 浠呭惈鍧愭爣/鍏崇郴
鈹?  鈹?  鈹斺攢鈹€ embeddings/         # 鍚戦噺宓屽叆
鈹?  鈹溾攢鈹€ camera_poses/           # 鐩告満浣嶅Э
鈹?  鈹斺攢鈹€ gaussian_models/        # 璁粌妯″瀷
鈹?鈹溾攢鈹€ knowledge/                  # 鐭ヨ瘑搴擄紙宸茶劚鏁忥級
鈹?  鈹溾攢鈹€ VR_KNOWLEDGE.json       # 浠呭惈鍒嗙被/鍦烘櫙
鈹?  鈹斺攢鈹€ PHYSICS_KNOWLEDGE.md   # 閫氱敤鐗╃悊鐭ヨ瘑
鈹?鈹斺攢鈹€ .gitignore                  # 鎺掗櫎鍘熷鏁版嵁
```

## 5. 闅愮娓呯悊娴佺▼

### 5.1 鑷姩娓呯悊鑴氭湰

```python
def clean_project_data(data_dir: Path) -> dict:
    """鑷姩娓呯悊鏁忔劅淇℃伅"""
    patterns = {
        "phone": r"1[3-9]\d{9}",           # 鎵嬫満鍙?        "company": r"(瑁呴グ|璁捐|瑁呬慨|宸ョ▼)", # 鍏徃鍚?        "person": r"[\u4e00-\u9fa5]{2,4}", # 濮撳悕
    }
    
    cleaned = 0
    for file in data_dir.glob("*.json"):
        content = file.read_text()
        for pattern in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, "***", content)
                cleaned += 1
        file.write_text(content)
    
    return {"cleaned_files": cleaned}
```

### 5.2 宸插畬鎴愮殑娓呯悊

| 鏂囦欢 | 娓呯悊鍐呭 | 鐘舵€?|
|------|----------|------|
| `rendering_objects.json` | 绉婚櫎 `original_path` | 鉁?|
| `VR_KNOWLEDGE.json` | 绉婚櫎 `designer` 鑱旂郴鏂瑰紡 | 鉁?|
| `building_objects.json` | 绉婚櫎 `source_file` | 鉁?|

## 6. 缃戠粶璁块棶闄愬埗

### 6.1 绂佹鐨勮闂?
```
鉂?涓嶈闂細
   - 澶栭儴API锛堥櫎蹇呰闀滃儚锛?   - 澧冨妯″瀷API
   - 绗笁鏂规暟鎹湇鍔?   - 绀句氦濯掍綋/璁哄潧

鉁?浠呭厑璁革細
   - pypi.org / pypi.tuna.tsinghua.edu.cn  # Python鍖?   - download.pytorch.org                   # PyTorch
   - 鏈湴localhost:3000 / localhost:5000    # 鍓嶅悗绔?```

### 6.2 鏈湴浼樺厛鍘熷垯

```python
# 鎵€鏈夋ā鍨嬩紭鍏堜娇鐢ㄦ湰鍦?LLM_CONFIG = {
    "provider": "local",  # 鏈湴LLM浼樺厛
    "api_key": None,      # 涓嶄娇鐢∣penAI
    "model": "llama3.local" # 鏈湴妯″瀷
}

# Embedding浣跨敤鏈湴
EMBEDDING_CONFIG = {
    "provider": "local",  # sentence-transformers
    "model": "paraphrase-multilingual-MiniLM-L12-v2"
}
```

## 7. 瀹¤鏃ュ織

```python
@dataclass
class AuditLog:
    timestamp: str
    action: str          # "read" | "write" | "export" | "query"
    resource: str        # 鏂囦欢/鎺ュ彛璺緞
    user: str            # "system" | "user"
    result: str          # "success" | "blocked"
    details: str         # 鍏蜂綋鎿嶄綔

# 璁板綍鍒版湰鍦版棩蹇?def log_audit(entry: AuditLog):
    log_file = Path("logs/audit.log")
    log_file.append_json(entry)
```

## 8. 涓栫晫妯″瀷娌欑闅旂锛圦Claw 闆嗘垚锛?
### 8.1 鏋舵瀯璁捐

```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?                    QClaw 涓昏繘绋?                            鈹?鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?   鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?               鈹?鈹? 鈹? 鏍稿績绠楁硶搴?    鈹?   鈹? 瑙勮寖鐭ヨ瘑搴?    鈹?               鈹?鈹? 鈹? (鏈湴淇濇姢)     鈹?   鈹? (鏈湴淇濇姢)     鈹?               鈹?鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?   鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?               鈹?鈹?          鈹?                     鈹?                         鈹?鈹?          鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                         鈹?鈹?                     鈻?                                     鈹?鈹?          鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                          鈹?鈹?          鈹? 鑴辨晱鏁版嵁鎺ュ彛灞?    鈹?                          鈹?鈹?          鈹? (鍑犱綍澶栧３ only)    鈹?                          鈹?鈹?          鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                          鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                     鈹?IPC / localhost API
                     鈻?鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?                 涓栫晫妯″瀷娌欑                                鈹?鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?  鈹?鈹? 鈹? 杈撳叆: 鑴辨晱鍑犱綍澶栧３ (鍧愭爣/灏哄/鍏崇郴)                  鈹?  鈹?鈹? 鈹? 澶勭悊: 鐗╃悊浠跨湡 + 绌洪棿鎺ㄧ悊 + 4D棰勬祴                  鈹?  鈹?鈹? 鈹? 杈撳嚭: 鍔ㄤ綔搴忓垪 + 椋庨櫓璇勪及 + 鍙鍖栨暟鎹?             鈹?  鈹?鈹? 鈹? 鉂?鏃犳硶璁块棶: 鍘熷BIM / 椤圭洰鍚嶇О / 瀹㈡埛淇℃伅          鈹?  鈹?鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?  鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?```

### 8.2 鏁版嵁娴佽劚鏁?
```python
class GeometricHull:
    """鍑犱綍澶栧３锛氫粎鍖呭惈绌洪棿淇℃伅锛屼笉鍚笟鍔″厓鏁版嵁"""
    scene_id: str           # 闅忔満ID锛岄潪椤圭洰鍚?    objects: list[Object3D] # 浠呭潗鏍?灏哄/绫诲瀷
    relations: list[Edge]   # 绌洪棿鍏崇郴
    # 鉂?涓嶅寘鍚? project_name, client, designer, source_file

def export_to_sandbox(scene: Scene) -> GeometricHull:
    """瀵煎嚭鍒版矙绠憋細寮哄埗鑴辨晱"""
    return GeometricHull(
        scene_id=hashlib.sha256(scene.id).hexdigest()[:16],
        objects=[Object3D(
            id=obj.id,
            type=obj.type,        # "door"/"window"/"furniture"
            position=obj.position,  # (x, y, z)
            dimensions=obj.dimensions,  # (w, h, d)
        ) for obj in scene.objects],
        relations=extract_relations(scene),
    )
```

### 8.3 璋冪敤杈圭晫

| 璋冪敤鏂瑰悜 | 鍏佽 | 璇存槑 |
|----------|------|------|
| QClaw 鈫?涓栫晫妯″瀷 | 鉁?| 鍙戦€佸嚑浣曞澹筹紝鎺ユ敹棰勬祴缁撴灉 |
| 涓栫晫妯″瀷 鈫?QClaw | 鉂?| 娌欑鏃犳硶鍙嶅悜璁块棶鏍稿績鏁版嵁 |
| 涓栫晫妯″瀷 鈫?澶栫綉 | 鉂?| 瀹屽叏绂荤嚎杩愯 |
| 涓栫晫妯″瀷 鈫?鍘熷BIM | 鉂?| 浠呮帴鏀惰劚鏁忓悗鐨勫嚑浣?|

### 8.4 妯″瀷淇濇姢

```python
# 鏍稿績绠楁硶淇濇寔鍦ㄦ湰鍦帮紝涓嶆毚闇茬粰娌欑
CORE_ALGORITHMS = {
    "rule_library": "鏈湴瑙勮寖搴擄紙GB瑙勮寖锛?,
    "prompt_registry": "鏈湴Prompt绉嶅瓙",
    "vla_controller": "鏈湴VLA鎺у埗鍣?,
    "feedback_loop": "鏈湴鏁版嵁椋炶疆",
}

# 娌欑浠呰皟鐢ㄧ敓鎴怉PI
SANDBOX_API = {
    "/api/physics/simulate": "鐗╃悊浠跨湡",
    "/api/scene/predict": "鍦烘櫙棰勬祴",
    "/api/relation/infer": "鍏崇郴鎺ㄧ悊",
}
```

### 8.5 瀹夊叏鏀剁泭

| 椋庨櫓 | 闃叉姢鎺柦 |
|------|----------|
| 椤圭洰鏁版嵁娉勯湶 | 娌欑浠呮帴鏀跺嚑浣曞澹筹紝鏃犱笟鍔″厓鏁版嵁 |
| 绠楃悊绔敾鍑?| 鏍稿績绠楁硶鏈湴淇濇姢锛屾矙绠辨棤娉曡闂?|
| 妯″瀷绐冨彇 | 鏉冮噸鏂囦欢鍔犲瘑瀛樺偍锛屾矙绠变粎鎺ㄧ悊涓嶈缁?|
| 渚涘簲閾炬敾鍑?| 瀹屽叏绂荤嚎锛屼笉渚濊禆澶栫綉妯″瀷API |

---

## 9. 蹇€熸鏌ユ竻鍗?
- [ ] 鍘熷鏁版嵁鍦?`data/raw/` 涓嶆彁浜ゅ埌Git
- [ ] `knowledge/` 鐩綍涓嶅寘鍚」鐩悕绉?瀹㈡埛淇℃伅
- [ ] 鎺ㄧ悊鏈嶅姟鍣ㄤ粎鐩戝惉 localhost:5000
- [ ] 鍓嶇涓嶈皟鐢ㄥ閮ˋPI锛堥櫎鏈湴璧勬簮锛?- [ ] 瀵煎嚭鏁版嵁鎵ц鑴辨晱妫€鏌?- [ ] 瀵硅瘽涓笉閫忛湶鍏蜂綋椤圭洰/瀹㈡埛淇℃伅

---

*鏇存柊鏃堕棿锛?026-04-16*

