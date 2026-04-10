"""
索引管理模块 - 管理知识库索引
"""

from datetime import datetime
from typing import Dict, List

from .wiki_manager import WikiManager


def update_index(wiki_manager: WikiManager = None) -> Dict:
    """
    更新知识库索引

    Args:
        wiki_manager: WikiManager 实例

    Returns:
        更新结果
    """
    wm = wiki_manager or WikiManager()

    # 获取所有页面
    all_pages = wm.list_pages()

    # 按类别分组
    categories = {"work": [], "life": [], "learning": []}
    entities = []
    concepts = []

    for page in all_pages:
        if page["type"] == "entity":
            entities.append(page)
        elif page["type"] == "concept":
            concepts.append(page)
        elif page["category"] in categories:
            categories[page["category"]].append(page)

    # 生成索引内容
    content = _generate_index_content(categories, entities, concepts)

    # 写入索引文件
    index_file = wm.wiki_path / "index.md"
    index_file.write_text(content, encoding="utf-8")

    # 记录日志
    wm.log_operation("update", "索引")

    return {
        "success": True,
        "total_pages": len(all_pages),
        "entities": len(entities),
        "concepts": len(concepts),
    }


def _generate_index_content(
    categories: Dict[str, List[Dict]],
    entities: List[Dict],
    concepts: List[Dict],
) -> str:
    """生成索引内容"""
    content = """# 知识库索引

本索引由 Agent 自动维护，记录知识库中的所有页面。

## 统计

"""

    total = sum(len(pages) for pages in categories.values()) + len(entities) + len(
        concepts
    )
    content += f"- **总页面数**: {total}\n"
    content += f"- **工作资料**: {len(categories['work'])}\n"
    content += f"- **生活笔记**: {len(categories['life'])}\n"
    content += f"- **学习资料**: {len(categories['learning'])}\n"
    content += f"- **实体页面**: {len(entities)}\n"
    content += f"- **概念页面**: {len(concepts)}\n"

    # Work 部分
    content += "\n## Work（工作）\n\n"
    content += "### 源资料\n\n"
    for page in categories["work"]:
        if "sources" in str(page["path"]):
            content += _format_page_entry(page)

    content += "\n### 主题\n\n"
    for page in categories["work"]:
        if "topics" in str(page["path"]):
            content += _format_page_entry(page)

    content += "\n### 分析\n\n"
    for page in categories["work"]:
        if "analyses" in str(page["path"]):
            content += _format_page_entry(page)

    # Life 部分
    content += "\n## Life（生活）\n\n"
    content += "### 源资料\n\n"
    for page in categories["life"]:
        if "sources" in str(page["path"]):
            content += _format_page_entry(page)

    content += "\n### 主题\n\n"
    for page in categories["life"]:
        if "topics" in str(page["path"]):
            content += _format_page_entry(page)

    # Learning 部分
    content += "\n## Learning（学习）\n\n"
    content += "### 源资料\n\n"
    for page in categories["learning"]:
        if "sources" in str(page["path"]):
            content += _format_page_entry(page)

    content += "\n### 主题\n\n"
    for page in categories["learning"]:
        if "topics" in str(page["path"]):
            content += _format_page_entry(page)

    # Entities 部分
    content += "\n## Entities（实体）\n\n"
    content += "### 人物\n\n"
    for page in entities:
        if page.get("entity_type") == "person":
            content += _format_page_entry(page)

    content += "\n### 公司\n\n"
    for page in entities:
        if page.get("entity_type") == "company":
            content += _format_page_entry(page)

    content += "\n### 产品\n\n"
    for page in entities:
        if page.get("entity_type") == "product":
            content += _format_page_entry(page)

    content += "\n### 项目\n\n"
    for page in entities:
        if page.get("entity_type") == "project":
            content += _format_page_entry(page)

    content += "\n### 其他\n\n"
    for page in entities:
        if page.get("entity_type") not in ["person", "company", "product", "project"]:
            content += _format_page_entry(page)

    # Concepts 部分
    content += "\n## Concepts（概念）\n\n"
    content += "### 业务概念\n\n"
    for page in concepts:
        if page.get("concept_type") == "business":
            content += _format_page_entry(page)

    content += "\n### 技术概念\n\n"
    for page in concepts:
        if page.get("concept_type") == "tech":
            content += _format_page_entry(page)

    content += "\n### 方法论\n\n"
    for page in concepts:
        if page.get("concept_type") == "methodology":
            content += _format_page_entry(page)

    content += "\n### 其他\n\n"
    for page in concepts:
        if page.get("concept_type") not in ["business", "tech", "methodology"]:
            content += _format_page_entry(page)

    # 标签云
    content += "\n## 标签\n\n"
    all_tags = _collect_tags(categories, entities, concepts)
    for tag, count in sorted(all_tags.items(), key=lambda x: x[1], reverse=True):
        content += f"- `#{tag}` ({count})\n"

    content += f"\n---\n\n"
    content += f"*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"

    return content


def _format_page_entry(page: Dict) -> str:
    """格式化页面条目"""
    title = page["title"]
    page_type = page.get("type", "unknown")
    created = page.get("created", "")
    tags = page.get("tags", [])

    entry = f"- [[{title}]]"
    if created:
        entry += f" ({created})"
    if tags:
        entry += f" `{'` `'.join(tags[:3])}`"
    entry += "\n"

    return entry


def _collect_tags(
    categories: Dict[str, List[Dict]],
    entities: List[Dict],
    concepts: List[Dict],
) -> Dict[str, int]:
    """收集所有标签"""
    tags = {}

    all_pages = []
    for pages in categories.values():
        all_pages.extend(pages)
    all_pages.extend(entities)
    all_pages.extend(concepts)

    for page in all_pages:
        for tag in page.get("tags", []):
            tags[tag] = tags.get(tag, 0) + 1

    return tags


def search_index(keyword: str, wiki_manager: WikiManager = None) -> List[Dict]:
    """
    在索引中搜索

    Args:
        keyword: 搜索关键词
        wiki_manager: WikiManager 实例

    Returns:
        匹配的页面列表
    """
    wm = wiki_manager or WikiManager()

    index_file = wm.wiki_path / "index.md"
    if not index_file.exists():
        return []

    content = index_file.read_text(encoding="utf-8")
    lines = content.split("\n")

    results = []
    for line in lines:
        if keyword.lower() in line.lower() and "[[" in line:
            # 提取页面名
            import re

            match = re.search(r"\[\[([^\]]+)\]\]", line)
            if match:
                page_name = match.group(1)
                page_path = wm.get_page_path(page_name)
                if page_path:
                    results.append(
                        {
                            "title": page_name,
                            "path": str(page_path.relative_to(wm.root_path)),
                            "context": line.strip(),
                        }
                    )

    return results
