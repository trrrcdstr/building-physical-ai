"""
RAG-Skill 融合架构

将RAG（检索增强生成）封装为Skill，与Harness L1-L3无缝集成。

架构:
  RAGSkill(BaseSkill)
    ├── VectorRetriever    — 向量检索（sentence-transformers + FAISS）
    ├── CrossEncoderReranker — 重排序（cross-encoder）
    ├── LLMGenerator       — 生成（本地LLM / OpenAI API）
    └── KnowledgeIndex     — 知识库索引管理

设计哲学:
  RAG不是独立系统，而是Harness的"感知器官"
  - L1 PromptRegistry: 提供查询模板
  - L2 ContextEngine: 提供记忆+知识
  - L3 WorldModel: 提供物理约束
  - RAG: 提供事实检索+语义理解
"""

from .base import BaseSkill, SkillMetadata, SkillCategory, SkillResult
from .retriever import VectorRetriever, KnowledgeIndex
from .reranker import CrossEncoderReranker
from .generator import LLMGenerator
from .rag_skill import RAGSkill
from .pipeline import RAGPipeline

__version__ = "0.1.0"
__all__ = [
    "BaseSkill", "SkillMetadata", "SkillCategory", "SkillResult",
    "VectorRetriever", "KnowledgeIndex",
    "CrossEncoderReranker", "LLMGenerator",
    "RAGSkill", "RAGPipeline"
]
