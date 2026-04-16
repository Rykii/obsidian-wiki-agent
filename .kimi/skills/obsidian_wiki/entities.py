"""
实体管理模块 - 创建和管理实体页面
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .wiki_manager import WikiManager


def create_entity_page(
    name: str,
    entity_type: str,
    category: str,
    properties: Dict = None,
    wiki_manager: WikiManager = None,
) -> Dict:
    """
    创建实体页面

    Args:
        name: 实体名称
        entity_type: 实体类型 (person|company|product|project)
        category: 所属类别 (work|life|learning)
        properties: 实体属性
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
            "error": f"实体页面已存在: {existing}",
            "path": str(existing.relative_to(wm.root_path)),
        }

    # 获取模板
    template = wm.get_template("entity")
    date_str = datetime.now().strftime("%Y-%m-%d")

    # 生成内容
    content = template.format(
        name=name,
        entity_type=entity_type,
        category=category,
        date=date_str,
    )

    # 添加属性
    if properties:
        fm, body = wm.parse_frontmatter(content)
        fm["properties"] = properties
        content = wm.write_frontmatter(fm, body)

        # 在正文中添加属性部分
        props_section = "\n## 属性\n\n"
        for key, value in properties.items():
            props_section += f"- **{key}**: {value}\n"

        content += props_section

    # 写入文件（使用 create_page 确保路径正确并受防护）
    safe_name = _safe_filename(name)
    entity_path = wm.create_page(f"{safe_name}.md", content)

    # 更新索引
    _update_entity_index(wm, name, entity_type, category)

    # 记录日志
    wm.log_operation("create", f"实体: {name}")

    return {
        "success": True,
        "path": str(entity_path.relative_to(wm.root_path)),
    }


def update_entity(
    name: str,
    updates: Dict,
    wiki_manager: WikiManager = None,
) -> Dict:
    """
    更新实体页面

    Args:
        name: 实体名称
        updates: 更新内容
        wiki_manager: WikiManager 实例

    Returns:
        更新结果
    """
    wm = wiki_manager or WikiManager()

    # 查找实体页面
    entity_path = wm.get_page_path(name)
    if not entity_path:
        return {"success": False, "error": f"实体页面不存在: {name}"}

    # 读取现有内容
    content = entity_path.read_text(encoding="utf-8")
    fm, body = wm.parse_frontmatter(content)

    # 更新 frontmatter
    if "properties" in updates:
        fm["properties"] = {**fm.get("properties", {}), **updates["properties"]}

    if "tags" in updates:
        fm["tags"] = list(set(fm.get("tags", []) + updates["tags"]))

    fm["updated"] = datetime.now().strftime("%Y-%m-%d")

    # 更新正文
    if "add_content" in updates:
        body += f"\n\n{updates['add_content']}"

    # 写回文件
    new_content = wm.write_frontmatter(fm, body)
    entity_path.write_text(new_content, encoding="utf-8")

    # 记录日志
    wm.log_operation("update", f"实体: {name}")

    return {
        "success": True,
        "path": str(entity_path.relative_to(wm.root_path)),
    }


def list_entities(
    entity_type: str = None,
    category: str = None,
    wiki_manager: WikiManager = None,
) -> List[Dict]:
    """
    列出所有实体

    Args:
        entity_type: 按类型过滤
        category: 按类别过滤
        wiki_manager: WikiManager 实例

    Returns:
        实体列表
    """
    wm = wiki_manager or WikiManager()

    entities = []
    entities_dir = wm.wiki_path / "entities"

    if not entities_dir.exists():
        return entities

    for md_file in entities_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        fm, body = wm.parse_frontmatter(content)

        entity_info = {
            "path": md_file,
            "title": fm.get("title", md_file.stem),
            "type": fm.get("entity_type", "unknown"),
            "category": fm.get("category", "unknown"),
            "created": fm.get("created", ""),
            "updated": fm.get("updated", ""),
            "tags": fm.get("tags", []),
            "properties": fm.get("properties", {}),
        }

        # 应用过滤
        if entity_type and entity_info["type"] != entity_type:
            continue
        if category and entity_info["category"] != category:
            continue

        entities.append(entity_info)

    return entities


def get_entity_relationships(
    name: str,
    wiki_manager: WikiManager = None,
) -> Dict:
    """
    获取实体的关系网络

    Args:
        name: 实体名称
        wiki_manager: WikiManager 实例

    Returns:
        关系信息
    """
    wm = wiki_manager or WikiManager()

    # 获取实体页面
    entity_path = wm.get_page_path(name)
    if not entity_path:
        return {"success": False, "error": f"实体不存在: {name}"}

    # 读取内容
    content = entity_path.read_text(encoding="utf-8")
    links = wm.get_all_links(content)

    # 获取反向链接
    backlinks = wm.get_backlinks(name)

    return {
        "success": True,
        "entity": name,
        "outgoing_links": links,
        "backlinks": [b["title"] for b in backlinks],
        "relationship_count": len(links) + len(backlinks),
    }


def _safe_filename(title: str) -> str:
    """生成安全的文件名"""
    safe = re.sub(r'[\\/*?:"<>|]', "-", title)
    safe = re.sub(r"\s+", "-", safe)
    safe = safe.strip("-.")
    return safe[:100]


def _update_entity_index(wm: WikiManager, name: str, entity_type: str, category: str):
    """更新实体索引"""
    # 这里可以实现更复杂的索引更新逻辑
    pass
