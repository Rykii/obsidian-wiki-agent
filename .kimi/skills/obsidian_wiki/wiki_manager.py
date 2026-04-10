"""
Wiki 管理器 - 核心管理类
"""

import os
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class WikiManager:
    """Obsidian Wiki 管理器"""

    def __init__(self, root_path: str = None):
        """
        初始化 Wiki 管理器

        Args:
            root_path: 项目根目录路径，默认为当前工作目录
        """
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.wiki_path = self.root_path / "wiki"
        self.raw_path = self.root_path / "raw"
        self.templates_path = self.root_path / "templates"

        # 确保目录存在
        self._ensure_directories()

    def _ensure_directories(self):
        """确保必要目录存在"""
        dirs = [
            self.wiki_path / "work" / "sources",
            self.wiki_path / "work" / "topics",
            self.wiki_path / "work" / "analyses",
            self.wiki_path / "life" / "sources",
            self.wiki_path / "life" / "topics",
            self.wiki_path / "life" / "analyses",
            self.wiki_path / "learning" / "sources",
            self.wiki_path / "learning" / "topics",
            self.wiki_path / "learning" / "analyses",
            self.wiki_path / "entities",
            self.wiki_path / "concepts",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def get_template(self, template_name: str) -> str:
        """
        获取模板内容

        Args:
            template_name: 模板名称（不含 .md 后缀）

        Returns:
            模板内容字符串
        """
        template_file = self.templates_path / f"{template_name}.md"
        if template_file.exists():
            return template_file.read_text(encoding="utf-8")
        return self._get_default_template(template_name)

    def _get_default_template(self, template_name: str) -> str:
        """获取默认模板"""
        templates = {
            "source": """---
title: {title}
type: source
category: {category}
created: {date}
updated: {date}
tags: []
source_file: {source_file}
status: draft
---

# {title}

## 基本信息

- **来源**: {source_file}
- **日期**: {date}
- **类别**: {category}

## 内容摘要

<!-- 在此处添加内容摘要 -->

## 关键要点

1. 
2. 
3. 

## 相关实体

- [[实体1]]
- [[实体2]]

## 相关概念

- [[概念1]]
- [[概念2]]

## 个人思考

<!-- 添加个人思考 -->

## 待办事项

- [ ] 

---
*创建于 {date}*
""",
            "entity": """---
title: {name}
type: entity
entity_type: {entity_type}
category: {category}
created: {date}
updated: {date}
tags: []
status: draft
---

# {name}

## 基本信息

<!-- 填写基本信息 -->

## 描述

<!-- 详细描述 -->

## 相关实体

- [[相关实体1]]
- [[相关实体2]]

## 相关概念

- [[相关概念1]]
- [[相关概念2]]

## 相关源资料

- [[源资料1]]
- [[源资料2]]

## 备注

<!-- 其他备注 -->

---
*创建于 {date}*
""",
            "concept": """---
title: {name}
type: concept
concept_type: {concept_type}
category: {category}
created: {date}
updated: {date}
tags: []
status: draft
---

# {name}

## 定义

{definition}

## 详细说明

<!-- 详细说明 -->

## 相关概念

- [[相关概念1]]
- [[相关概念2]]

## 相关实体

- [[相关实体1]]
- [[相关实体2]]

## 应用场景

<!-- 应用场景 -->

## 参考资料

- [[参考源1]]
- [[参考源2]]

---
*创建于 {date}*
""",
            "topic": """---
title: {title}
type: topic
category: {category}
created: {date}
updated: {date}
tags: []
status: draft
---

# {title}

## 概述

<!-- 主题概述 -->

## 子主题

- [[子主题1]]
- [[子主题2]]

## 相关源资料

- [[源资料1]]
- [[源资料2]]

## 相关实体

- [[实体1]]
- [[实体2]]

## 相关概念

- [[概念1]]
- [[概念2]]

## 最新更新

<!-- 记录最新更新 -->

---
*创建于 {date}*
""",
            "analysis": """---
title: {title}
type: analysis
category: {category}
created: {date}
updated: {date}
tags: []
status: draft
---

# {title}

## 问题/目标

<!-- 分析问题或目标 -->

## 分析过程

<!-- 详细分析 -->

## 结论

<!-- 分析结论 -->

## 相关页面

- [[页面1]]
- [[页面2]]

## 参考来源

- [[来源1]]
- [[来源2]]

---
*创建于 {date}*
""",
        }
        return templates.get(template_name, "")

    def parse_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """
        解析 frontmatter

        Args:
            content: 文件内容

        Returns:
            (frontmatter_dict, body_content)
        """
        pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(pattern, content, re.DOTALL)

        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1))
                body = match.group(2)
                return frontmatter or {}, body
            except yaml.YAMLError:
                pass

        return {}, content

    def write_frontmatter(self, frontmatter: Dict, body: str) -> str:
        """
        写入 frontmatter

        Args:
            frontmatter: frontmatter 字典
            body: 正文内容

        Returns:
            完整文件内容
        """
        if frontmatter:
            fm_yaml = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
            return f"---\n{fm_yaml}---\n{body}"
        return body

    def page_exists(self, page_name: str, subdir: str = None) -> bool:
        """
        检查页面是否存在

        Args:
            page_name: 页面名称
            subdir: 子目录（可选）

        Returns:
            是否存在
        """
        search_dirs = [self.wiki_path]
        if subdir:
            search_dirs = [self.wiki_path / subdir]

        for search_dir in search_dirs:
            for md_file in search_dir.rglob("*.md"):
                # 检查文件名或 frontmatter 中的 title
                if md_file.stem == page_name:
                    return True
                content = md_file.read_text(encoding="utf-8")
                fm, _ = self.parse_frontmatter(content)
                if fm.get("title") == page_name:
                    return True

        return False

    def get_page_path(self, page_name: str) -> Optional[Path]:
        """
        获取页面路径

        Args:
            page_name: 页面名称

        Returns:
            页面路径或 None
        """
        for md_file in self.wiki_path.rglob("*.md"):
            if md_file.stem == page_name:
                return md_file
            content = md_file.read_text(encoding="utf-8")
            fm, _ = self.parse_frontmatter(content)
            if fm.get("title") == page_name:
                return md_file
        return None

    def list_pages(self, category: str = None, page_type: str = None) -> List[Dict]:
        """
        列出所有页面

        Args:
            category: 按类别过滤
            page_type: 按类型过滤

        Returns:
            页面信息列表
        """
        pages = []
        search_path = self.wiki_path

        if category:
            search_path = self.wiki_path / category

        if not search_path.exists():
            return pages

        for md_file in search_path.rglob("*.md"):
            if md_file.name in ["index.md", "log.md"]:
                continue

            content = md_file.read_text(encoding="utf-8")
            fm, body = self.parse_frontmatter(content)

            if page_type and fm.get("type") != page_type:
                continue

            pages.append({
                "path": md_file,
                "title": fm.get("title", md_file.stem),
                "type": fm.get("type", "unknown"),
                "category": fm.get("category", "unknown"),
                "created": fm.get("created", ""),
                "updated": fm.get("updated", ""),
                "tags": fm.get("tags", []),
            })

        return pages

    def search_in_pages(self, keyword: str, category: str = None) -> List[Dict]:
        """
        在页面中搜索关键词

        Args:
            keyword: 搜索关键词
            category: 按类别过滤

        Returns:
            匹配的页面列表
        """
        results = []
        pages = self.list_pages(category=category)

        for page in pages:
            content = page["path"].read_text(encoding="utf-8")
            if keyword.lower() in content.lower():
                # 找到匹配位置上下文
                lines = content.split("\n")
                contexts = []
                for i, line in enumerate(lines):
                    if keyword.lower() in line.lower():
                        start = max(0, i - 1)
                        end = min(len(lines), i + 2)
                        contexts.append("\n".join(lines[start:end]))

                results.append({
                    **page,
                    "contexts": contexts[:3],  # 最多返回3个上下文
                })

        return results

    def get_all_links(self, content: str) -> List[str]:
        """
        提取内容中的所有 Obsidian 链接

        Args:
            content: 页面内容

        Returns:
            链接目标列表
        """
        # 匹配 [[链接]] 和 [[链接|别名]]
        pattern = r"\[\[([^|\]]+)(?:\|[^\]]*)?\]\]"
        return list(set(re.findall(pattern, content)))

    def get_backlinks(self, page_name: str) -> List[Dict]:
        """
        获取反向链接

        Args:
            page_name: 页面名称

        Returns:
            反向链接列表
        """
        backlinks = []

        for md_file in self.wiki_path.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            links = self.get_all_links(content)

            if page_name in links:
                fm, _ = self.parse_frontmatter(content)
                backlinks.append({
                    "path": md_file,
                    "title": fm.get("title", md_file.stem),
                    "type": fm.get("type", "unknown"),
                })

        return backlinks

    def log_operation(self, operation: str, subject: str, details: str = ""):
        """
        记录操作日志

        Args:
            operation: 操作类型 (ingest|query|lint|update)
            subject: 操作主题
            details: 详细信息
        """
        log_file = self.wiki_path / "log.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        log_entry = f"\n## [{timestamp}] {operation} | {subject}\n\n"
        if details:
            log_entry += f"{details}\n"

        if log_file.exists():
            content = log_file.read_text(encoding="utf-8")
            content += log_entry
        else:
            content = f"# 操作日志\n\n{log_entry}"

        log_file.write_text(content, encoding="utf-8")

    def update_page_timestamp(self, page_path: Path):
        """
        更新页面的 updated 时间戳

        Args:
            page_path: 页面路径
        """
        content = page_path.read_text(encoding="utf-8")
        fm, body = self.parse_frontmatter(content)

        if "updated" in fm:
            fm["updated"] = datetime.now().strftime("%Y-%m-%d")
            new_content = self.write_frontmatter(fm, body)
            page_path.write_text(new_content, encoding="utf-8")
