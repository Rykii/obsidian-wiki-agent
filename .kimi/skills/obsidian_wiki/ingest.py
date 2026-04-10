"""
资料摄入模块 - 处理新资料并更新知识库
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .wiki_manager import WikiManager


def ingest_source(
    source_path: str,
    category: str,
    title: str = None,
    wiki_manager: WikiManager = None,
) -> Dict:
    """
    摄入新资料

    Args:
        source_path: 原始资料路径（相对于 raw/ 目录或绝对路径）
        category: 资料类别 (work|life|learning)
        title: 资料标题（可选）
        wiki_manager: WikiManager 实例（可选）

    Returns:
        摄入结果信息
    """
    wm = wiki_manager or WikiManager()

    # 解析源文件路径
    raw_file = _resolve_source_path(source_path, wm)
    if not raw_file or not raw_file.exists():
        return {"success": False, "error": f"源文件不存在: {source_path}"}

    # 读取源文件内容
    source_content = _read_source_file(raw_file)

    # 确定标题
    doc_title = title or _extract_title(source_content) or raw_file.stem

    # 创建源摘要页
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_filename = _safe_filename(doc_title)
    source_page_path = (
        wm.wiki_path / category / "sources" / f"{date_str}-{safe_filename}.md"
    )

    # 生成源摘要页内容
    template = wm.get_template("source")
    source_page_content = template.format(
        title=doc_title,
        category=category,
        date=date_str,
        source_file=str(raw_file.relative_to(wm.root_path)),
    )

    # 写入源摘要页
    source_page_path.write_text(source_page_content, encoding="utf-8")

    # 提取实体
    entities = extract_entities_from_text(source_content)
    entity_pages = []
    for entity in entities:
        entity_page = _create_or_update_entity(wm, entity, category, doc_title)
        if entity_page:
            entity_pages.append(entity_page)

    # 提取概念
    concepts = extract_concepts_from_text(source_content)
    concept_pages = []
    for concept in concepts:
        concept_page = _create_or_update_concept(wm, concept, category, doc_title)
        if concept_page:
            concept_pages.append(concept_page)

    # 更新索引
    _update_index(wm, doc_title, category, source_page_path)

    # 记录日志
    wm.log_operation(
        "ingest",
        doc_title,
        f"创建了源摘要页，提取了 {len(entities)} 个实体和 {len(concepts)} 个概念",
    )

    return {
        "success": True,
        "source_page": str(source_page_path.relative_to(wm.root_path)),
        "entities": entity_pages,
        "concepts": concept_pages,
    }


def _resolve_source_path(source_path: str, wm: WikiManager) -> Optional[Path]:
    """解析源文件路径"""
    # 尝试作为绝对路径
    path = Path(source_path)
    if path.exists():
        return path

    # 尝试相对于 raw/ 目录
    path = wm.raw_path / source_path
    if path.exists():
        return path

    # 尝试相对于项目根目录
    path = wm.root_path / source_path
    if path.exists():
        return path

    return None


def _read_source_file(file_path: Path) -> str:
    """读取源文件内容"""
    suffix = file_path.suffix.lower()

    if suffix == ".md":
        return file_path.read_text(encoding="utf-8")
    elif suffix in [".txt", ".rst"]:
        return file_path.read_text(encoding="utf-8")
    elif suffix in [".docx"]:
        try:
            import docx

            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            return f"[无法读取 .docx 文件，请安装 python-docx: pip install python-docx]"
    elif suffix in [".pdf"]:
        try:
            import PyPDF2

            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join([page.extract_text() for page in reader.pages])
        except ImportError:
            return f"[无法读取 PDF 文件，请安装 PyPDF2: pip install PyPDF2]"
    else:
        return f"[不支持的文件格式: {suffix}]"


def _extract_title(content: str) -> Optional[str]:
    """从内容中提取标题"""
    # 尝试从 frontmatter 提取
    import yaml

    pattern = r"^---\s*\n(.*?)\n---"
    match = re.match(pattern, content, re.DOTALL)
    if match:
        try:
            fm = yaml.safe_load(match.group(1))
            if "title" in fm:
                return fm["title"]
        except:
            pass

    # 尝试从第一个 # 标题提取
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()

    return None


def _safe_filename(title: str) -> str:
    """生成安全的文件名"""
    # 移除或替换不安全字符
    safe = re.sub(r'[\\/*?:"<>|]', "-", title)
    safe = re.sub(r"\s+", "-", safe)
    safe = safe.strip("-.")
    return safe[:100]  # 限制长度


def extract_entities_from_text(text: str) -> List[Dict]:
    """
    从文本中提取实体

    返回实体列表，每个实体包含:
    - name: 实体名称
    - type: 实体类型 (person|company|product|project|other)
    - context: 上下文
    """
    entities = []

    # 简单的实体识别模式（实际应用中可以使用更复杂的 NLP）
    patterns = {
        "company": [
            r"([\u4e00-\u9fa5]{2,10}(?:公司|集团|银行|证券|基金|科技|网络))",
            r"([A-Z][a-zA-Z\s]{1,20}(?:Inc\.?|Corp\.?|Ltd\.?|Company|Group))",
        ],
        "product": [
            r"([\u4e00-\u9fa5]{2,10}(?:系统|平台|产品|模块|工具))",
            r"([A-Z][a-zA-Z0-9]*(?:System|Platform|Product|Tool|Module))",
        ],
        "project": [
            r"([\u4e00-\u9fa5]{2,15}(?:项目|计划|工程))",
        ],
    }

    for entity_type, type_patterns in patterns.items():
        for pattern in type_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1)
                # 获取上下文
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]

                # 检查是否已存在
                if not any(e["name"] == name for e in entities):
                    entities.append(
                        {
                            "name": name,
                            "type": entity_type,
                            "context": context,
                        }
                    )

    return entities


def extract_concepts_from_text(text: str) -> List[Dict]:
    """
    从文本中提取概念

    返回概念列表，每个概念包含:
    - name: 概念名称
    - type: 概念类型 (business|tech|methodology|other)
    - context: 上下文
    """
    concepts = []

    # 业务术语模式
    business_terms = [
        r"(估值核算)",
        r"(份额登记)",
        r"(资金清算)",
        r"(净值化转型)",
        r"(资管新规)",
        r"(打破刚兑)",
        r"(期限匹配)",
        r"(公允价值)",
        r"(摊余成本)",
    ]

    # 技术术语模式
    tech_terms = [
        r"(微服务)",
        r"(分布式)",
        r"(API)",
        r"(数据库)",
        r"(缓存)",
        r"(消息队列)",
    ]

    # 方法论模式
    method_terms = [
        r"(用户故事)",
        r"(敏捷开发)",
        r"(需求分析)",
        r"(竞品分析)",
        r"(用户调研)",
    ]

    patterns = {
        "business": business_terms,
        "tech": tech_terms,
        "methodology": method_terms,
    }

    for concept_type, type_patterns in patterns.items():
        for pattern in type_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]

                if not any(c["name"] == name for c in concepts):
                    concepts.append(
                        {
                            "name": name,
                            "type": concept_type,
                            "context": context,
                        }
                    )

    return concepts


def _create_or_update_entity(
    wm: WikiManager, entity: Dict, category: str, source_title: str
) -> Optional[str]:
    """创建或更新实体页"""
    entity_name = entity["name"]
    entity_type = entity["type"]

    # 检查是否已存在
    existing_path = wm.get_page_path(entity_name)

    if existing_path:
        # 更新现有实体页
        content = existing_path.read_text(encoding="utf-8")
        fm, body = wm.parse_frontmatter(content)

        # 添加新的源资料引用
        sources = fm.get("sources", [])
        if source_title not in sources:
            sources.append(source_title)
            fm["sources"] = sources
            fm["updated"] = datetime.now().strftime("%Y-%m-%d")

            # 在正文中添加引用
            if f"[[{source_title}]]" not in body:
                body += f"\n- [[{source_title}]]"

            new_content = wm.write_frontmatter(fm, body)
            existing_path.write_text(new_content, encoding="utf-8")

        return str(existing_path.relative_to(wm.root_path))

    else:
        # 创建新实体页
        template = wm.get_template("entity")
        date_str = datetime.now().strftime("%Y-%m-%d")

        content = template.format(
            name=entity_name,
            entity_type=entity_type,
            category=category,
            date=date_str,
        )

        # 添加 frontmatter 中的 sources
        fm, body = wm.parse_frontmatter(content)
        fm["sources"] = [source_title]
        content = wm.write_frontmatter(fm, body)

        # 在正文中添加源引用
        content += f"\n## 相关源资料\n\n- [[{source_title}]]\n"

        # 写入文件
        safe_name = _safe_filename(entity_name)
        entity_path = wm.wiki_path / "entities" / f"{safe_name}.md"
        entity_path.write_text(content, encoding="utf-8")

        return str(entity_path.relative_to(wm.root_path))


def _create_or_update_concept(
    wm: WikiManager, concept: Dict, category: str, source_title: str
) -> Optional[str]:
    """创建或更新概念页"""
    concept_name = concept["name"]
    concept_type = concept["type"]

    # 检查是否已存在
    existing_path = wm.get_page_path(concept_name)

    if existing_path:
        # 更新现有概念页
        content = existing_path.read_text(encoding="utf-8")
        fm, body = wm.parse_frontmatter(content)

        sources = fm.get("sources", [])
        if source_title not in sources:
            sources.append(source_title)
            fm["sources"] = sources
            fm["updated"] = datetime.now().strftime("%Y-%m-%d")

            if f"[[{source_title}]]" not in body:
                body += f"\n- [[{source_title}]]"

            new_content = wm.write_frontmatter(fm, body)
            existing_path.write_text(new_content, encoding="utf-8")

        return str(existing_path.relative_to(wm.root_path))

    else:
        # 创建新概念页
        template = wm.get_template("concept")
        date_str = datetime.now().strftime("%Y-%m-%d")

        content = template.format(
            name=concept_name,
            concept_type=concept_type,
            category=category,
            date=date_str,
            definition=f"{concept_name}是...",
        )

        fm, body = wm.parse_frontmatter(content)
        fm["sources"] = [source_title]
        content = wm.write_frontmatter(fm, body)

        content += f"\n## 参考来源\n\n- [[{source_title}]]\n"

        safe_name = _safe_filename(concept_name)
        concept_path = wm.wiki_path / "concepts" / f"{safe_name}.md"
        concept_path.write_text(content, encoding="utf-8")

        return str(concept_path.relative_to(wm.root_path))


def _update_index(wm: WikiManager, title: str, category: str, source_path: Path):
    """更新索引文件"""
    index_file = wm.wiki_path / "index.md"

    entry = f"- [[{title}]] - {category} 源资料 ({datetime.now().strftime('%Y-%m-%d')})\n"

    if index_file.exists():
        content = index_file.read_text(encoding="utf-8")
        # 在对应类别下添加
        category_section = f"## {category.capitalize()}"
        if category_section in content:
            # 在类别部分后添加
            pattern = f"({category_section}.*?)(\n## |\Z)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                insert_pos = match.end(1)
                content = content[:insert_pos] + "\n" + entry + content[insert_pos:]
            else:
                content += f"\n{category_section}\n\n{entry}"
        else:
            content += f"\n{category_section}\n\n{entry}"
    else:
        content = f"""# 知识库索引

本索引由 Agent 自动维护，记录知识库中的所有页面。

## {category.capitalize()}

{entry}

---
*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    index_file.write_text(content, encoding="utf-8")
