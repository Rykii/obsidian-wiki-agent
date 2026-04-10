# Obsidian Wiki Skill

## 概述

本 Skill 提供 Obsidian 知识库管理的核心功能，包括资料摄入(Ingest)、知识查询(Query)和健康检查(Lint)三大工作流。

## 功能模块

### 1. ingest - 资料摄入

处理新资料，提取关键信息，更新知识库。

**参数:**
- `source_path`: 原始资料路径（相对于 raw/ 目录）
- `category`: 资料类别 (work|life|learning)
- `title`: 资料标题（可选，默认从文件名提取）

**示例:**
```python
# 摄入工作相关资料
ingest(source_path="work/2024-资管系统需求评审.md", category="work")

# 摄入生活笔记
ingest(source_path="life/日本旅行攻略.md", category="life")
```

### 2. query - 知识查询

基于知识库内容回答用户问题。

**参数:**
- `question`: 用户问题
- `output_format`: 输出格式 (markdown|table|slides|chart)
- `save_to_wiki`: 是否保存结果到 wiki (默认 False)

**示例:**
```python
# 简单查询
query("什么是估值核算？")

# 生成对比表
query("对比 TA 系统和估值系统", output_format="table")

# 保存分析结果
query("分析资管行业趋势", save_to_wiki=True)
```

### 3. lint - 健康检查

检查知识库健康状况，发现潜在问题。

**参数:**
- `check_type`: 检查类型 (all|orphans|deadlinks|contradictions|missing)
- `auto_fix`: 是否自动修复（默认 False）

**示例:**
```python
# 完整检查
lint()

# 只检查孤立页面
lint(check_type="orphans")
```

### 4. update_index - 更新索引

更新 wiki/index.md 内容索引。

**示例:**
```python
update_index()
```

### 5. create_entity - 创建实体页

创建新的实体页面。

**参数:**
- `name`: 实体名称
- `entity_type`: 实体类型 (person|company|product|project)
- `category`: 所属类别 (work|life|learning)
- `properties`: 实体属性字典

**示例:**
```python
create_entity(
    name="TA系统",
    entity_type="product",
    category="work",
    properties={
        "full_name": "Transfer Agent System",
        "description": "份额登记系统",
        "related": ["估值系统", "资金清算"]
    }
)
```

### 6. create_concept - 创建概念页

创建新的概念页面。

**参数:**
- `name`: 概念名称
- `concept_type`: 概念类型 (business|tech|methodology)
- `category`: 所属类别
- `definition`: 概念定义

**示例:**
```python
create_concept(
    name="净值化转型",
    concept_type="business",
    category="work",
    definition="资管产品从预期收益型向净值型转变的过程"
)
```

## 工具函数

### get_wiki_structure()

获取 wiki 目录结构信息。

**返回:**
- 目录树结构
- 页面统计信息

### search_pages(keyword, category=None)

搜索 wiki 页面。

**参数:**
- `keyword`: 搜索关键词
- `category`: 限制搜索类别（可选）

**返回:**
- 匹配的页面列表

### get_backlinks(page_name)

获取指向某页面的所有链接。

**参数:**
- `page_name`: 页面名称

**返回:**
- 反向链接列表

### extract_entities(text)

从文本中提取实体。

**参数:**
- `text`: 输入文本

**返回:**
- 识别的实体列表

## 使用示例

### 完整工作流示例

```python
# 1. 摄入新资料
ingest("work/新产品需求文档.md", category="work")

# 2. 查询相关知识
result = query("新产品的核心功能有哪些？", save_to_wiki=True)

# 3. 检查知识库健康
lint()

# 4. 更新索引
update_index()
```

## 配置项

在 `KIMICODE.md` 中可配置：

- `WIKI_ROOT`: wiki 根目录路径
- `RAW_ROOT`: 原始资料目录路径
- `DEFAULT_CATEGORY`: 默认资料类别
- `AUTO_UPDATE_INDEX`: 是否自动更新索引
- `AUTO_LOG`: 是否自动记录日志

## 注意事项

1. 所有文件操作都基于相对路径
2. 原始资料目录 (raw/) 为只读
3. 创建页面前检查是否已存在
4. 保持 frontmatter 格式一致
5. 使用 Obsidian 维基链接格式
