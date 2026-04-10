"""
Obsidian Wiki Skill - KimiCode Agent 知识库管理工具

基于 Karpathy's LLM-Wiki 模式实现
"""

from .wiki_manager import WikiManager
from .ingest import ingest_source
from .query import query_wiki
from .lint import lint_wiki
from .entities import create_entity_page
from .concepts import create_concept_page
from .index_manager import update_index
from .utils import search_pages, get_backlinks, extract_entities

__version__ = "1.0.0"
__author__ = "KimiCode Agent"

__all__ = [
    "WikiManager",
    "ingest_source",
    "query_wiki",
    "lint_wiki",
    "create_entity_page",
    "create_concept_page",
    "update_index",
    "search_pages",
    "get_backlinks",
    "extract_entities",
]
