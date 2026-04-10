"""
知识查询模块 - 基于知识库回答用户问题
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .wiki_manager import WikiManager


def query_wiki(
    question: str,
    output_format: str = "markdown",
    save_to_wiki: bool = False,
    category: str = None,
    wiki_manager: WikiManager = None,
) -> Dict:
    """
    查询知识库

    Args:
        question: 用户问题
        output_format: 输出格式 (markdown|table|list)
        save_to_wiki: 是否保存结果到 wiki
        category: 限制查询类别
        wiki_manager: WikiManager 实例

    Returns:
        查询结果
    """
    wm = wiki_manager or WikiManager()

    # 1. 读取索引
    index_content = _read_index(wm)

    # 2. 搜索相关页面
    relevant_pages = _find_relevant_pages(wm, question, category)

    # 3. 读取相关页面内容
    page_contents = []
    for page in relevant_pages:
        content = page["path"].read_text(encoding="utf-8")
        fm, body = wm.parse_frontmatter(content)
        page_contents.append(
            {
                "title": page["title"],
                "type": page["type"],
                "content": body[:2000],  # 限制内容长度
            }
        )

    # 4. 生成回答
    answer = _generate_answer(question, page_contents, output_format)

    # 5. 如果需要，保存到 wiki
    saved_path = None
    if save_to_wiki:
        saved_path = _save_analysis(wm, question, answer, category)

    # 6. 记录日志
    wm.log_operation("query", question[:50], f"找到 {len(relevant_pages)} 个相关页面")

    return {
        "success": True,
        "question": question,
        "answer": answer,
        "relevant_pages": [p["title"] for p in relevant_pages],
        "saved_path": saved_path,
    }


def _read_index(wm: WikiManager) -> str:
    """读取索引文件"""
    index_file = wm.wiki_path / "index.md"
    if index_file.exists():
        return index_file.read_text(encoding="utf-8")
    return ""


def _find_relevant_pages(
    wm: WikiManager, question: str, category: str = None
) -> List[Dict]:
    """
    查找相关页面

    使用关键词匹配和简单相关性评分
    """
    # 提取问题关键词
    keywords = _extract_keywords(question)

    # 获取所有页面
    all_pages = wm.list_pages(category=category)

    # 计算相关性评分
    scored_pages = []
    for page in all_pages:
        score = 0
        content = page["path"].read_text(encoding="utf-8")
        content_lower = content.lower()

        for keyword in keywords:
            keyword_lower = keyword.lower()
            # 标题匹配权重更高
            if keyword_lower in page["title"].lower():
                score += 10
            # 内容匹配
            if keyword_lower in content_lower:
                score += content_lower.count(keyword_lower)

        if score > 0:
            scored_pages.append({**page, "score": score})

    # 按评分排序，返回前10个
    scored_pages.sort(key=lambda x: x["score"], reverse=True)
    return scored_pages[:10]


def _extract_keywords(text: str) -> List[str]:
    """提取关键词"""
    # 简单的关键词提取
    # 移除常见停用词
    stopwords = {
        "的",
        "了",
        "是",
        "在",
        "我",
        "有",
        "和",
        "就",
        "不",
        "人",
        "都",
        "一",
        "一个",
        "上",
        "也",
        "很",
        "到",
        "说",
        "要",
        "去",
        "你",
        "会",
        "着",
        "没有",
        "看",
        "好",
        "自己",
        "这",
        "那",
        "什么",
        "怎么",
        "如何",
        "为什么",
        "吗",
        "呢",
        "啊",
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "can",
        "shall",
    }

    # 分词（简单实现）
    words = re.findall(r"[\u4e00-\u9fa5]+|[a-zA-Z]+", text)
    keywords = [w for w in words if w.lower() not in stopwords and len(w) > 1]

    return keywords


def _generate_answer(
    question: str, page_contents: List[Dict], output_format: str
) -> str:
    """生成回答"""
    if not page_contents:
        return "未找到相关知识。请尝试添加相关资料到知识库。"

    if output_format == "table":
        return _generate_table_answer(question, page_contents)
    elif output_format == "list":
        return _generate_list_answer(question, page_contents)
    else:
        return _generate_markdown_answer(question, page_contents)


def _generate_markdown_answer(question: str, page_contents: List[Dict]) -> str:
    """生成 Markdown 格式回答"""
    answer = f"## 回答: {question}\n\n"

    answer += "基于以下资料:\n\n"
    for page in page_contents:
        answer += f"- [[{page['title']}]]\n"

    answer += "\n---\n\n"
    answer += "### 相关内容\n\n"

    for page in page_contents:
        answer += f"**来自 [[{page['title']}]]**:\n\n"
        # 提取关键段落
        paragraphs = page["content"].split("\n\n")
        for para in paragraphs[:3]:  # 最多显示3个段落
            para = para.strip()
            if para and not para.startswith("#"):
                answer += f"> {para[:200]}...\n\n"
                break

    return answer


def _generate_table_answer(question: str, page_contents: List[Dict]) -> str:
    """生成表格格式回答"""
    answer = f"## 对比分析: {question}\n\n"

    answer += "| 来源 | 类型 | 关键内容 |\n"
    answer += "|------|------|----------|\n"

    for page in page_contents:
        # 提取关键内容
        content = page["content"].replace("|", "\\|").replace("\n", " ")[:100]
        answer += f"| [[{page['title']}]] | {page['type']} | {content}... |\n"

    return answer


def _generate_list_answer(question: str, page_contents: List[Dict]) -> str:
    """生成列表格式回答"""
    answer = f"## {question}\n\n"

    for i, page in enumerate(page_contents, 1):
        answer += f"{i}. **[[{page['title']}]]** ({page['type']})\n"
        # 提取摘要
        paragraphs = page["content"].split("\n\n")
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith("#"):
                answer += f"   - {para[:150]}...\n"
                break
        answer += "\n"

    return answer


def _save_analysis(wm: WikiManager, question: str, answer: str, category: str) -> str:
    """保存分析结果到 wiki"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_name = re.sub(r'[\\/*?:"<>|]', "-", question)[:50]

    cat = category or "work"
    analysis_path = wm.wiki_path / cat / "analyses" / f"{date_str}-{safe_name}.md"

    # 添加 frontmatter
    content = f"""---
title: {question}
type: analysis
category: {cat}
created: {date_str}
updated: {date_str}
tags: [query-result]
status: draft
---

{answer}

---
*生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    analysis_path.write_text(content, encoding="utf-8")
    return str(analysis_path.relative_to(wm.root_path))


def quick_search(keyword: str, wiki_manager: WikiManager = None) -> List[Dict]:
    """
    快速搜索

    Args:
        keyword: 搜索关键词
        wiki_manager: WikiManager 实例

    Returns:
        匹配的页面列表
    """
    wm = wiki_manager or WikiManager()
    return wm.search_in_pages(keyword)
