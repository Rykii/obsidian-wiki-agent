"""
健康检查模块 - 检查知识库健康状况
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

from .wiki_manager import WikiManager


def lint_wiki(
    check_type: str = "all",
    auto_fix: bool = False,
    wiki_manager: WikiManager = None,
) -> Dict:
    """
    检查知识库健康状况

    Args:
        check_type: 检查类型 (all|orphans|deadlinks|contradictions|missing)
        auto_fix: 是否自动修复
        wiki_manager: WikiManager 实例

    Returns:
        检查结果
    """
    wm = wiki_manager or WikiManager()

    issues = {
        "orphan_pages": [],
        "dead_links": [],
        "contradictions": [],
        "missing_entities": [],
        "inconsistent_tags": [],
    }

    # 获取所有页面
    all_pages = wm.list_pages()

    # 1. 检查孤立页面
    if check_type in ["all", "orphans"]:
        issues["orphan_pages"] = _check_orphan_pages(wm, all_pages)

    # 2. 检查死链
    if check_type in ["all", "deadlinks"]:
        issues["dead_links"] = _check_dead_links(wm, all_pages)

    # 3. 检查矛盾
    if check_type in ["all", "contradictions"]:
        issues["contradictions"] = _check_contradictions(wm, all_pages)

    # 4. 检查缺失实体
    if check_type in ["all", "missing"]:
        issues["missing_entities"] = _check_missing_entities(wm, all_pages)

    # 5. 检查标签一致性
    if check_type in ["all", "tags"]:
        issues["inconsistent_tags"] = _check_tag_consistency(wm, all_pages)

    # 生成报告
    report = _generate_lint_report(issues)

    # 保存报告
    report_path = wm.wiki_path / "lint-report.md"
    report_path.write_text(report, encoding="utf-8")

    # 记录日志
    total_issues = sum(len(v) for v in issues.values())
    wm.log_operation("lint", "健康检查", f"发现 {total_issues} 个问题")

    return {
        "success": True,
        "issues": issues,
        "report_path": str(report_path.relative_to(wm.root_path)),
        "total_issues": total_issues,
    }


def _check_orphan_pages(wm: WikiManager, all_pages: List[Dict]) -> List[Dict]:
    """检查孤立页面（没有入链的页面）"""
    orphans = []

    # 收集所有链接
    all_links = set()
    for page in all_pages:
        content = page["path"].read_text(encoding="utf-8")
        links = wm.get_all_links(content)
        all_links.update(links)

    # 检查每个页面
    for page in all_pages:
        page_title = page["title"]
        if page_title not in all_links and page["path"].name not in [
            "index.md",
            "log.md",
        ]:
            # 检查文件名是否被引用
            file_stem = page["path"].stem
            if file_stem not in all_links:
                orphans.append(
                    {
                        "title": page_title,
                        "path": str(page["path"].relative_to(wm.root_path)),
                        "type": page["type"],
                    }
                )

    return orphans


def _check_dead_links(wm: WikiManager, all_pages: List[Dict]) -> List[Dict]:
    """检查死链（指向不存在的页面的链接）"""
    dead_links = []

    # 收集所有有效页面名
    valid_pages = set()
    for page in all_pages:
        valid_pages.add(page["title"])
        valid_pages.add(page["path"].stem)

    # 检查每个页面的链接
    for page in all_pages:
        content = page["path"].read_text(encoding="utf-8")
        links = wm.get_all_links(content)

        for link in links:
            # 处理锚点
            link_target = link.split("#")[0]

            if link_target and link_target not in valid_pages:
                dead_links.append(
                    {
                        "source": page["title"],
                        "source_path": str(page["path"].relative_to(wm.root_path)),
                        "broken_link": link,
                    }
                )

    return dead_links


def _check_contradictions(wm: WikiManager, all_pages: List[Dict]) -> List[Dict]:
    """检查矛盾信息"""
    contradictions = []

    # 收集日期相关信息
    date_info = {}
    for page in all_pages:
        content = page["path"].read_text(encoding="utf-8")
        fm, body = wm.parse_frontmatter(content)

        # 查找日期模式
        date_pattern = r"(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)|(\d{4}[-/]\d{1,2})"
        dates = re.findall(date_pattern, body)

        for date_match in dates:
            date_str = date_match[0] or date_match[1]
            if date_str:
                if date_str not in date_info:
                    date_info[date_str] = []
                date_info[date_str].append(
                    {"page": page["title"], "context": body[:200]}
                )

    # 检查同一实体在不同页面的不同描述
    entity_mentions = {}
    for page in all_pages:
        content = page["path"].read_text(encoding="utf-8")
        fm, body = wm.parse_frontmatter(content)

        # 查找实体引用
        for other_page in all_pages:
            if other_page["title"] != page["title"]:
                if other_page["title"] in body:
                    if other_page["title"] not in entity_mentions:
                        entity_mentions[other_page["title"]] = []
                    entity_mentions[other_page["title"]].append(page["title"])

    # 这里可以实现更复杂的矛盾检测逻辑
    # 目前只是简单示例

    return contradictions


def _check_missing_entities(wm: WikiManager, all_pages: List[Dict]) -> List[Dict]:
    """检查被多次提及但没有独立页面的实体"""
    missing = []

    # 收集所有实体页面的名称
    entity_pages = set()
    for page in all_pages:
        if page["type"] == "entity":
            entity_pages.add(page["title"])
            entity_pages.add(page["path"].stem)

    # 统计提及次数
    mention_count = {}
    for page in all_pages:
        content = page["path"].read_text(encoding="utf-8")
        fm, body = wm.parse_frontmatter(content)

        # 查找可能的实体（大写开头的连续词语）
        potential_entities = re.findall(r"[\u4e00-\u9fa5]{2,10}系统", body)
        potential_entities += re.findall(r"[\u4e00-\u9fa5]{2,10}平台", body)
        potential_entities += re.findall(r"[\u4e00-\u9fa5]{2,10}公司", body)

        for entity in potential_entities:
            if entity not in entity_pages:
                if entity not in mention_count:
                    mention_count[entity] = {"count": 0, "pages": []}
                mention_count[entity]["count"] += 1
                if page["title"] not in mention_count[entity]["pages"]:
                    mention_count[entity]["pages"].append(page["title"])

    # 找出被多次提及的实体
    for entity, info in mention_count.items():
        if info["count"] >= 3:  # 被提及3次以上
            missing.append(
                {
                    "name": entity,
                    "mention_count": info["count"],
                    "mentioned_in": info["pages"],
                }
            )

    # 按提及次数排序
    missing.sort(key=lambda x: x["mention_count"], reverse=True)

    return missing[:10]  # 返回前10个


def _check_tag_consistency(wm: WikiManager, all_pages: List[Dict]) -> List[Dict]:
    """检查标签使用一致性"""
    inconsistencies = []

    # 收集所有标签
    all_tags = {}
    for page in all_pages:
        content = page["path"].read_text(encoding="utf-8")
        fm, body = wm.parse_frontmatter(content)

        tags = fm.get("tags", [])
        for tag in tags:
            normalized = tag.lower().strip()
            if normalized not in all_tags:
                all_tags[normalized] = {"variants": set(), "pages": []}
            all_tags[normalized]["variants"].add(tag)
            all_tags[normalized]["pages"].append(page["title"])

    # 检查变体
    for normalized, info in all_tags.items():
        if len(info["variants"]) > 1:
            inconsistencies.append(
                {
                    "tag": normalized,
                    "variants": list(info["variants"]),
                    "pages": info["pages"],
                }
            )

    return inconsistencies


def _generate_lint_report(issues: Dict) -> str:
    """生成检查报告"""
    report = f"""# 知识库健康检查报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 摘要

- 孤立页面: {len(issues['orphan_pages'])}
- 死链: {len(issues['dead_links'])}
- 矛盾信息: {len(issues['contradictions'])}
- 缺失实体: {len(issues['missing_entities'])}
- 标签不一致: {len(issues['inconsistent_tags'])}

---

"""

    # 孤立页面
    if issues["orphan_pages"]:
        report += "## 孤立页面\n\n"
        report += "以下页面没有被其他页面引用:\n\n"
        for page in issues["orphan_pages"]:
            report += f"- [[{page['title']}]] ({page['type']})\n"
        report += "\n**建议**: 考虑从相关页面添加链接，或检查是否需要保留。\n\n"

    # 死链
    if issues["dead_links"]:
        report += "## 死链\n\n"
        report += "以下链接指向不存在的页面:\n\n"
        for link in issues["dead_links"]:
            report += f"- 在 [[{link['source']}]] 中: `[[{link['broken_link']}]]`\n"
        report += "\n**建议**: 创建缺失的页面或修复链接。\n\n"

    # 矛盾信息
    if issues["contradictions"]:
        report += "## 矛盾信息\n\n"
        report += "发现以下潜在矛盾:\n\n"
        for contra in issues["contradictions"]:
            report += f"- {contra}\n"
        report += "\n"

    # 缺失实体
    if issues["missing_entities"]:
        report += "## 建议创建的实体页面\n\n"
        report += "以下实体被多次提及但没有独立页面:\n\n"
        report += "| 实体名称 | 提及次数 | 出现在 |\n"
        report += "|---------|---------|--------|\n"
        for entity in issues["missing_entities"]:
            pages = ", ".join([f"[[{p}]]" for p in entity["mentioned_in"][:3]])
            report += f"| {entity['name']} | {entity['mention_count']} | {pages} |\n"
        report += "\n**建议**: 考虑为这些实体创建独立页面。\n\n"

    # 标签不一致
    if issues["inconsistent_tags"]:
        report += "## 标签使用不一致\n\n"
        report += "以下标签存在多种写法:\n\n"
        for tag in issues["inconsistent_tags"]:
            variants = ", ".join([f"`{v}`" for v in tag["variants"]])
            report += f"- `{tag['tag']}`: {variants}\n"
        report += "\n**建议**: 统一标签写法。\n\n"

    report += "---\n\n"
    report += "*本报告由 Agent 自动生成*\n"

    return report
