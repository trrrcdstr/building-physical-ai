"""
L2 多模态工程编码层 - 语义嵌入模块（本地版）
TF-IDF + jieba 分词，纯本地运行，无需网络
"""

import re
import math
import json
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────
# 中文分词（纯手写实现，无需 jieba）
# ─────────────────────────────────────────────
class ChineseTokenizer:
    """简单但实用的中文分词器（基于规则+词典）"""

    # 常见中文词组（建筑场景专用）
    WORD_DICT = {
        # 清洁类
        "清洁": 1, "扫地": 1, "拖地": 1, "擦拭": 1, "打扫": 1, "清洗": 1,
        "地面": 1, "地板": 1, "家具": 1, "表面": 1, "窗户": 1, "玻璃": 1,
        "厨房": 1, "油污": 1, "卫生间": 1, "浴室": 1, "桌面": 1, "床铺": 1,
        # 移动类
        "移动": 1, "搬运": 1, "整理": 1, "归置": 1, "分类": 1, "存放": 1,
        "重物": 1, "箱子": 1, "书架": 1, "衣柜": 1, "家具": 1, "沙发": 1,
        "茶几": 1, "餐桌": 1, "床": 1,
        # 施工类
        "安装": 1, "组装": 1, "固定": 1, "挂钩": 1, "打孔": 1, "布线": 1,
        "接电": 1, "管道": 1, "铺设": 1, "管线": 1, "灯具": 1, "设备": 1,
        # 巡检类
        "巡检": 1, "检查": 1, "查看": 1, "记录": 1, "仪表": 1, "异常": 1,
        "安全": 1, "通道": 1, "设备间": 1, "消防": 1,
        # 服务类
        "递送": 1, "送餐": 1, "引导": 1, "访客": 1, "咨询": 1, "客房": 1,
        # 园林类
        "浇花": 1, "浇水": 1, "灌溉": 1, "修剪": 1, "草坪": 1, "落叶": 1,
        "施肥": 1, "绿化": 1, "园林": 1, "花": 1, "植物": 1,
        # 空间
        "客厅": 1, "卧室": 1, "书房": 1, "阳台": 1, "走廊": 1, "门口": 1,
        "房间": 1, "室内": 1, "室外": 1, "花园": 1, "公园": 1,
        # 动作
        "走到": 1, "去": 1, "导航": 1, "抓取": 1, "拿起": 1, "放下": 1,
        "放置": 1, "推": 1, "拉": 1, "关": 1, "开": 1,
        # 工具
        "扫帚": 1, "拖把": 1, "抹布": 1, "清洁剂": 1, "刷子": 1,
    }

    def __init__(self):
        # 按长度排序（优先匹配长词）
        self.dict_words = sorted(self.WORD_DICT.keys(), key=len, reverse=True)
        print(f"[ChineseTokenizer] Loaded {len(self.dict_words)} domain words")

    def tokenize(self, text: str) -> list[str]:
        """中英文混合分词"""
        tokens = []

        # 英文和数字
        for token in re.findall(r'[a-zA-Z0-9]+', text):
            tokens.append(token.lower())

        # 中文
        remaining = text
        while remaining:
            matched = False
            for word in self.dict_words:
                if remaining.startswith(word):
                    tokens.append(word)
                    remaining = remaining[len(word):]
                    matched = True
                    break
            if not matched:
                # 单字
                c = remaining[0]
                if '\u4e00' <= c <= '\u9fff':  # 是汉字
                    tokens.append(c)
                remaining = remaining[1:]

        return [t for t in tokens if t.strip()]


# ─────────────────────────────────────────────
# TF-IDF 向量化器（纯本地）
# ─────────────────────────────────────────────
class TFIDFVectorizer:
    """TF-IDF 向量化：无需外部 API"""

    def __init__(self, tokenizer: ChineseTokenizer = None):
        self.tokenizer = tokenizer or ChineseTokenizer()
        self.vocab: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self.corpus: list[list[str]] = []

    def fit(self, texts: list[str]) -> "TFIDFVectorizer":
        """从语料库构建词汇表和 IDF"""
        # 分词
        self.corpus = [self.tokenizer.tokenize(t) for t in texts]

        # 构建词汇表
        vocab_set = set()
        for tokens in self.corpus:
            vocab_set.update(tokens)
        self.vocab = {w: i for i, w in enumerate(sorted(vocab_set))}
        print(f"[TFIDFVectorizer] Vocab size: {len(self.vocab)}")

        # 计算 IDF
        n = len(self.corpus)
        df = {}
        for tokens in self.corpus:
            for w in set(tokens):
                df[w] = df.get(w, 0) + 1
        self.idf = {w: math.log(n / max(df[w], 1)) + 1 for w in df}

        return self

    def _text_to_tfidf(self, tokens: list[str]) -> list[float]:
        """单文档 -> TF-IDF 向量"""
        tf = {}
        for w in tokens:
            tf[w] = tf.get(w, 0) + 1
        n = len(tokens)
        vec = [0.0] * len(self.vocab)
        for w, count in tf.items():
            if w in self.vocab:
                tf_val = count / n
                idf_val = self.idf.get(w, math.log(len(self.corpus)) + 1)
                vec[self.vocab[w]] = tf_val * idf_val
        return vec

    def transform(self, texts: list[str]) -> list[list[float]]:
        """批量转换"""
        corpus = [self.tokenizer.tokenize(t) for t in texts]
        return [self._text_to_tfidf(tokens) for tokens in corpus]

    def fit_transform(self, texts: list[str]) -> list[list[float]]:
        self.fit(texts)
        return self.transform(texts)

    @property
    def dimension(self) -> int:
        return len(self.vocab)


# ─────────────────────────────────────────────
# 余弦相似度
# ─────────────────────────────────────────────
def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ─────────────────────────────────────────────
# 语义编码器（本地 TF-IDF）
# ─────────────────────────────────────────────
class SemanticEncoder:
    """
    本地语义编码器：TF-IDF + 中文分词
    - 纯本地运行，无需网络
    - 支持中文建筑场景
    - 启动速度快（无模型下载）
    """

    def __init__(self):
        self.tokenizer = ChineseTokenizer()

        # 建筑场景任务指令词库
        self.task_corpus = [
            # 清洁类
            "清洁地面", "扫地拖地", "擦拭家具表面", "清理厨房油污",
            "打扫卫生间", "擦拭窗户玻璃", "整理床铺", "收拾桌面杂物",
            "清理垃圾桶", "清洁地板", "洗碗", "清洁浴室",
            # 搬运类
            "搬运家具", "移动重物", "搬箱子", "整理书架",
            "归置物品", "分类存放", "整理衣柜", "整理房间",
            # 施工类
            "安装家具", "组装柜子", "固定挂钩", "打孔安装",
            "布线接电", "铺设管道", "安装灯具", "调试设备",
            # 巡检类
            "巡检设备间", "检查消防通道", "查看仪表读数",
            "记录异常情况", "环境安全检查", "设备巡检", "隐患排查",
            # 服务类
            "送餐到房间", "递送物品", "引导访客",
            "回答咨询", "客房服务",
            # 园林类
            "浇花浇水", "修剪草坪", "清理落叶",
            "施肥养护", "巡查园林", "绿化维护",
            # 厨房类
            "烹饪准备", "切配食材", "餐具消毒", "厨房清洁",
            # 办公类
            "文件整理", "会议室布置", "办公设备维护",
        ]

        # 预计算词库 TF-IDF
        self.vectorizer = TFIDFVectorizer(self.tokenizer)
        self.task_vectors = self.vectorizer.fit_transform(self.task_corpus)
        self.dim = self.vectorizer.dimension
        print(f"[SemanticEncoder] TF-IDF | Vocab: {self.dim} | Tasks: {len(self.task_corpus)} | Device: LOCAL (no GPU)")

    def encode_instruction(self, text: str) -> list[float]:
        """将自然语言指令编码为 TF-IDF 向量"""
        tokens = self.tokenizer.tokenize(text)
        return self.vectorizer._text_to_tfidf(tokens)

    def find_similar_tasks(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.1,
    ) -> list[dict]:
        """
        在任务库中查找语义相似的任务
        """
        query_vec = self.encode_instruction(query)
        scores = [(cosine_similarity(query_vec, vec), i)
                  for i, vec in enumerate(self.task_vectors)]
        scores.sort(reverse=True)

        results = []
        for score, i in scores[:top_k]:
            if score >= threshold:
                results.append({
                    "task": self.task_corpus[i],
                    "similarity": round(score, 3),
                    "index": i,
                })
        return results

    def semantic_match(
        self,
        query: str,
        candidates: list[str],
        top_k: int = 3,
    ) -> list[dict]:
        """在候选列表中语义匹配"""
        if not candidates:
            return []
        cand_vectors = self.vectorizer.transform(candidates)
        query_vec = self.encode_instruction(query)
        scores = [cosine_similarity(query_vec, v) for v in cand_vectors]
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [{"text": candidates[i], "similarity": round(scores[i], 3)} for i in top_indices]

    @property
    def embedding_dimension(self) -> int:
        return self.dim

    @property
    def device(self) -> str:
        return "cpu"  # 本地方案，无 GPU 加速
