"""
工具函数模块 - 通用工具函数
"""

import re
from typing import Dict, List

from .wiki_manager import WikiManager


def search_pages(keyword: str, category: str = None, wiki_manager: WikiManager = None) -> List[Dict]:
    """
    搜索页面

    Args:
        keyword: 搜索关键词
        category: 按类别过滤
        wiki_manager: WikiManager 实例

    Returns:
        匹配的页面列表
    """
    wm = wiki_manager or WikiManager()
    return wm.search_in_pages(keyword, category)


def get_backlinks(page_name: str, wiki_manager: WikiManager = None) -> List[Dict]:
    """
    获取反向链接

    Args:
        page_name: 页面名称
        wiki_manager: WikiManager 实例

    Returns:
        反向链接列表
    """
    wm = wiki_manager or WikiManager()
    return wm.get_backlinks(page_name)


def extract_entities(text: str) -> List[Dict]:
    """
    从文本中提取实体

    Args:
        text: 输入文本

    Returns:
        识别的实体列表
    """
    entities = []

    # 公司模式
    company_pattern = r"([\u4e00-\u9fa5]{2,10}(?:公司|集团|银行|证券|基金|科技|网络))"
    for match in re.finditer(company_pattern, text):
        name = match.group(1)
        if not any(e["name"] == name for e in entities):
            entities.append({
                "name": name,
                "type": "company",
                "position": match.start()
            })

    # 产品模式
    product_pattern = r"([\u4e00-\u9fa5]{2,10}(?:系统|平台|产品|模块|工具))"
    for match in re.finditer(product_pattern, text):
        name = match.group(1)
        if not any(e["name"] == name for e in entities):
            entities.append({
                "name": name,
                "type": "product",
                "position": match.start()
            })

    # 人名模式（简单实现）
    person_pattern = r"([\u4e00-\u9fa5]{2,4})(?:先生|女士|经理|总监|总裁)"
    for match in re.finditer(person_pattern, text):
        name = match.group(1)
        if not any(e["name"] == name for e in entities):
            entities.append({
                "name": name,
                "type": "person",
                "position": match.start()
            })

    return entities


def get_wiki_stats(wiki_manager: WikiManager = None) -> Dict:
    """
    获取知识库统计信息

    Args:
        wiki_manager: WikiManager 实例

    Returns:
        统计信息
    """
    wm = wiki_manager or WikiManager()

    all_pages = wm.list_pages()

    stats = {
        "total_pages": len(all_pages),
        "by_type": {},
        "by_category": {},
        "total_tags": 0,
        "total_links": 0,
    }

    all_tags = set()
    all_links = 0

    for page in all_pages:
        # 按类型统计
        page_type = page.get("type", "unknown")
        stats["by_type"][page_type] = stats["by_type"].get(page_type, 0) + 1

        # 按类别统计
        category = page.get("category", "unknown")
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

        # 统计标签
        tags = page.get("tags", [])
        all_tags.update(tags)

        # 统计链接
        content = page["path"].read_text(encoding="utf-8")
        links = wm.get_all_links(content)
        all_links += len(links)

    stats["total_tags"] = len(all_tags)
    stats["total_links"] = all_links
    stats["tags_list"] = sorted(list(all_tags))

    return stats


def find_orphan_pages(wiki_manager: WikiManager = None) -> List[Dict]:
    """
    查找孤立页面

    Args:
        wiki_manager: WikiManager 实例

    Returns:
        孤立页面列表
    """
    wm = wiki_manager or WikiManager()

    all_pages = wm.list_pages()

    # 收集所有链接
    all_links = set()
    for page in all_pages:
        content = page["path"].read_text(encoding="utf-8")
        links = wm.get_all_links(content)
        all_links.update(links)

    # 检查孤立页面
    orphans = []
    for page in all_pages:
        page_title = page["title"]
        file_stem = page["path"].stem

        if page_title not in all_links and file_stem not in all_links:
            if page["path"].name not in ["index.md", "log.md"]:
                orphans.append({
                    "title": page_title,
                    "path": str(page["path"].relative_to(wm.root_path)),
                    "type": page.get("type", "unknown"),
                })

    return orphans


def find_dead_links(wiki_manager: WikiManager = None) -> List[Dict]:
    """
    查找死链

    Args:
        wiki_manager: WikiManager 实例

    Returns:
        死链列表
    """
    wm = wiki_manager or WikiManager()

    all_pages = wm.list_pages()

    # 收集所有有效页面名
    valid_pages = set()
    for page in all_pages:
        valid_pages.add(page["title"])
        valid_pages.add(page["path"].stem)

    # 检查死链
    dead_links = []
    for page in all_pages:
        content = page["path"].read_text(encoding="utf-8")
        links = wm.get_all_links(content)

        for link in links:
            link_target = link.split("#")[0]
            if link_target and link_target not in valid_pages:
                dead_links.append({
                    "source": page["title"],
                    "source_path": str(page["path"].relative_to(wm.root_path)),
                    "broken_link": link,
                })

    return dead_links


def generate_tag_cloud(wiki_manager: WikiManager = None) -> Dict[str, int]:
    """
    生成标签云

    Args:
        wiki_manager: WikiManager 实例

    Returns:
        标签及其出现次数
    """
    wm = wiki_manager or WikiManager()

    all_pages = wm.list_pages()

    tag_counts = {}
    for page in all_pages:
        for tag in page.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return tag_counts


def suggest_links(page_name: str, wiki_manager: WikiManager = None) -> List[str]:
    """
    为页面建议可能的链接

    Args:
        page_name: 页面名称
        wiki_manager: WikiManager 实例

    Returns:
        建议的链接列表
    """
    wm = wiki_manager or WikiManager()

    # 获取页面内容
    page_path = wm.get_page_path(page_name)
    if not page_path:
        return []

    content = page_path.read_text(encoding="utf-8")
    fm, body = wm.parse_frontmatter(content)

    # 获取所有其他页面
    all_pages = wm.list_pages()

    suggestions = []
    for other_page in all_pages:
        other_title = other_page["title"]
        if other_title == page_name:
            continue

        # 检查页面名是否出现在内容中但未链接
        if other_title in body and f"[[{other_title}]]" not in body:
            suggestions.append(other_title)

    return suggestions[:10]  # 返回前10个建议
