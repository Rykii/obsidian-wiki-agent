"""
概念管理模块 - 创建和管理概念页面
"""

import re
from datetime import datetime
from typing import Dict, List

from .wiki_manager import WikiManager


def create_concept_page(
    name: str,
    concept_type: str,
    category: str,
    definition: str = "",
    wiki_manager: WikiManager = None,
) -> Dict:
    """
    创建概念页面

    Args:
        name: 概念名称
        concept_type: 概念类型 (business|tech|methodology)
        category: 所属类别
        definition: 概念定义
        wiki_manager: WikiManager 实例

    Returns:
        创建结果
    """
    wm = wiki_manager or WikiManager()

    # 检查是否已存在
    existing = wm.get_page_path(name)
    if existing:
        return {
            "success": False,
            "error": f"概念页面已存在: {existing}",
            "path": str(existing.relative_to(wm.root_path)),
        }

    # 获取模板
    template = wm.get_template("concept")
    date_str = datetime.now().strftime("%Y-%m-%d")

    # 生成内容
    content = template.format(
        name=name,
        concept_type=concept_type,
        category=category,
        date=date_str,
        definition=definition or f"{name}是...",
    )

    # 写入文件
    safe_name = _safe_filename(name)
    concept_path = wm.wiki_path / "concepts" / f"{safe_name}.md"
    concept_path.write_text(content, encoding="utf-8")

    # 记录日志
    wm.log_operation("create", f"概念: {name}")

    return {
        "success": True,
        "path": str(concept_path.relative_to(wm.root_path)),
    }


def update_concept(
    name: str,
    updates: Dict,
    wiki_manager: WikiManager = None,
) -> Dict:
    """
    更新概念页面

    Args:
        name: 概念名称
        updates: 更新内容
        wiki_manager: WikiManager 实例

    Returns:
        更新结果
    """
    wm = wiki_manager or WikiManager()

    # 查找概念页面
    concept_path = wm.get_page_path(name)
    if not concept_path:
        return {"success": False, "error": f"概念页面不存在: {name}"}

    # 读取现有内容
    content = concept_path.read_text(encoding="utf-8")
    fm, body = wm.parse_frontmatter(content)

    # 更新 frontmatter
    if "definition" in updates:
        fm["definition"] = updates["definition"]

    if "tags" in updates:
        fm["tags"] = list(set(fm.get("tags", []) + updates["tags"]))

    fm["updated"] = datetime.now().strftime("%Y-%m-%d")

    # 更新正文
    if "add_content" in updates:
        body += f"\n\n{updates['add_content']}"

    # 写回文件
    new_content = wm.write_frontmatter(fm, body)
    concept_path.write_text(new_content, encoding="utf-8")

    # 记录日志
    wm.log_operation("update", f"概念: {name}")

    return {
        "success": True,
        "path": str(concept_path.relative_to(wm.root_path)),
    }


def list_concepts(
    concept_type: str = None,
    category: str = None,
    wiki_manager: WikiManager = None,
) -> List[Dict]:
    """
    列出所有概念

    Args:
        concept_type: 按类型过滤
        category: 按类别过滤
        wiki_manager: WikiManager 实例

    Returns:
        概念列表
    """
    wm = wiki_manager or WikiManager()

    concepts = []
    concepts_dir = wm.wiki_path / "concepts"

    if not concepts_dir.exists():
        return concepts

    for md_file in concepts_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        fm, body = wm.parse_frontmatter(content)

        concept_info = {
            "path": md_file,
            "title": fm.get("title", md_file.stem),
            "type": fm.get("concept_type", "unknown"),
            "category": fm.get("category", "unknown"),
            "definition": fm.get("definition", ""),
            "created": fm.get("created", ""),
            "updated": fm.get("updated", ""),
            "tags": fm.get("tags", []),
        }

        # 应用过滤
        if concept_type and concept_info["type"] != concept_type:
            continue
        if category and concept_info["category"] != category:
            continue

        concepts.append(concept_info)

    return concepts


def find_related_concepts(
    name: str,
    wiki_manager: WikiManager = None,
) -> List[str]:
    """
    查找相关概念

    Args:
        name: 概念名称
        wiki_manager: WikiManager 实例

    Returns:
        相关概念列表
    """
    wm = wiki_manager or WikiManager()

    # 获取概念页面
    concept_path = wm.get_page_path(name)
    if not concept_path:
        return []

    # 读取内容并提取链接
    content = concept_path.read_text(encoding="utf-8")
    links = wm.get_all_links(content)

    # 过滤出概念链接
    concepts_dir = wm.wiki_path / "concepts"
    concept_names = {f.stem for f in concepts_dir.glob("*.md")}

    related = [link for link in links if _safe_filename(link) in concept_names]

    return related


def _safe_filename(title: str) -> str:
    """生成安全的文件名"""
    safe = re.sub(r'[\\/*?:"<>|]', "-", title)
    safe = re.sub(r"\s+", "-", safe)
    safe = safe.strip("-.")
    return safe[:100]
