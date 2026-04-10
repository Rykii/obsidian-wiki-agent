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
    category: str = None,
    title: str = None,
    wiki_manager: WikiManager = None,
) -> Dict:
    """
    摄入新资料

    Args:
        source_path: 原始资料路径（相对于 raw/ 目录或绝对路径）
        category: 资料类别 (work|life|learning)，如不指定则自动分类
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

    # 自动分类（如果未指定类别）
    if category is None:
        category = auto_classify(doc_title, source_content)

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
        f"分类: {category} | 创建了源摘要页，提取了 {len(entities)} 个实体和 {len(concepts)} 个概念",
    )

    return {
        "success": True,
        "category": category,
        "source_page": str(source_page_path.relative_to(wm.root_path)),
        "entities": entity_pages,
        "concepts": concept_pages,
    }


def auto_classify(title: str, content: str) -> str:
    """
    自动分类文档

    根据标题和内容自动判断类别 (work|life|learning)

    Args:
        title: 文档标题
        content: 文档内容

    Returns:
        分类结果: work|life|learning
    """
    title_lower = title.lower()
    content_sample = content[:2000].lower()  # 只分析前2000字符

    # 工作相关关键词
    work_keywords = [
        # 业务相关
        "需求", "prd", "产品", "项目", "系统", "平台", "功能", "模块",
        "业务", "客户", "用户", "运营", "数据", "分析", "报告",
        "设计", "开发", "测试", "上线", "迭代", "版本", "发布",
        "会议", "纪要", "评审", "汇报", "总结", "复盘", "规划",
        "调研", "竞品", "市场", "行业", "趋势", "策略", "方案",
        "合同", "协议", "报价", "预算", "成本", "收益", "roi",
        "资管", "估值", "ta", "清算", "基金", "证券", "银行",
        "金融", "理财", "投资", "风控", "合规", "监管", "新规",
        # 英文关键词
        "requirement", "product", "project", "system", "platform",
        "business", "client", "meeting", "report", "analysis",
        "design", "development", "plan", "proposal", "review",
    ]

    # 生活相关关键词
    life_keywords = [
        # 旅行相关
        "旅行", "旅游", "游记", "攻略", "行程", "酒店", "机票", "景点",
        # 购物相关
        "购物", "购买", "评测", "体验", "推荐", "清单", "对比",
        "家具", "家电", "数码", "手机", "电脑", "相机", "耳机",
        # 宠物相关
        "宠物", "猫", "狗", "猫咪", "狗狗", "疫苗", "绝育", "喂养",
        # 情感生活
        "情感", "感情", "恋爱", "婚姻", "家庭", "亲子", "日记", "感悟",
        # 健康运动
        "健康", "运动", "健身", "饮食", "减肥", "睡眠", "体检",
        # 娱乐休闲
        "电影", "音乐", "游戏", "读书", "美食", "烹饪", "手工",
        # 英文关键词
        "travel", "trip", "hotel", "shopping", "pet", "cat", "dog",
        "life", "daily", "diary", "emotion", "feeling", "family",
        "health", "fitness", "exercise", "food", "cooking", "movie",
    ]

    # 学习相关关键词
    learning_keywords = [
        # 学习相关
        "学习", "笔记", "读书", "阅读", "课程", "培训", "教程",
        "方法", "方法论", "框架", "模型", "理论", "原理", "概念",
        # 技术相关
        "技术", "编程", "代码", "算法", "架构", "数据库", "前端", "后端",
        "python", "java", "javascript", "sql", "api", "git",
        # 考试证书
        "考试", "证书", "认证", "资格", "pmp", "cpa", "cfa", "frm",
        # 语言学习
        "英语", "日语", "韩语", "法语", "德语", "雅思", "托福",
        # 行业知识
        "行业", "研究", "论文", "文献", "综述", "深度", "洞察",
        "趋势", "前景", "发展", "变革", "创新", "突破",
        # 英文关键词
        "learning", "study", "course", "book", "note", "method",
        "technology", "programming", "algorithm", "exam", "certification",
        "research", "paper", "thesis", "knowledge", "skill", "tutorial",
    ]

    # 计算各类别得分
    work_score = 0
    life_score = 0
    learning_score = 0

    # 标题权重更高
    title_weight = 3
    content_weight = 1

    for keyword in work_keywords:
        if keyword in title_lower:
            work_score += title_weight
        if keyword in content_sample:
            work_score += content_weight

    for keyword in life_keywords:
        if keyword in title_lower:
            life_score += title_weight
        if keyword in content_sample:
            life_score += content_weight

    for keyword in learning_keywords:
        if keyword in title_lower:
            learning_score += title_weight
        if keyword in content_sample:
            learning_score += content_weight

    # 根据得分判断类别
    scores = {
        "work": work_score,
        "life": life_score,
        "learning": learning_score,
    }

    # 返回得分最高的类别
    max_category = max(scores, key=scores.get)
    max_score = scores[max_category]

    # 如果所有得分都是0，默认归为 work
    if max_score == 0:
        return "work"

    return max_category


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
