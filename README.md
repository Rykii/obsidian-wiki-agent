# Obsidian Wiki Agent

基于 [Karpathy's LLM-Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 模式构建的 Obsidian 知识库管理 Agent。

专为全资产管理系统产品经理设计，支持工作、生活、学习三大知识领域的管理。

## 核心特性

- **三层架构**: Raw Sources → Wiki → Schema
- **三大工作流**: Ingest(摄入) / Query(查询) / Lint(检查)
- **知识复利**: 持续积累，自动交叉引用
- **Obsidian 原生**: 完美兼容 Obsidian 的链接和图谱功能

## 目录结构

```
obsidian-wiki-agent/
├── KIMICODE.md              # Agent 配置文件（核心）
├── README.md                # 本文件
├── prompts/                 # Prompt 模板
│   ├── ingest_prompt.md
│   ├── query_prompt.md
│   └── lint_prompt.md
├── templates/               # 页面模板
│   ├── source.md
│   ├── entity.md
│   ├── concept.md
│   ├── topic.md
│   └── analysis.md
├── raw/                     # 原始资料（只读）- 直接放入，Agent 自动分类
├── wiki/                    # 维基内容（Agent 维护）
│   ├── work/               # 工作知识
│   ├── life/               # 生活知识
│   ├── learning/           # 学习知识
│   ├── entities/           # 实体页面
│   ├── concepts/           # 概念页面
│   ├── index.md            # 内容索引
│   └── log.md              # 操作日志
├── scripts/                 # 辅助脚本
│   ├── ingest.py           # 资料摄入
│   ├── query.py            # 知识查询
│   ├── lint.py             # 健康检查
│   └── stats.py            # 统计信息
└── .kimi/skills/obsidian_wiki/  # KimiCode Skill
    ├── SKILL.md
    ├── __init__.py
    ├── wiki_manager.py
    ├── ingest.py
    ├── query.py
    ├── lint.py
    ├── entities.py
    ├── concepts.py
    ├── index_manager.py
    └── utils.py
```

## 系统架构

### 架构分层图

```
┌─────────────────────────────────────────────────────────────────┐
│                      用户交互层 (User Interface)                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│   │  start.py    │  │  KIMICODE   │  │  Agent对话   │          │
│   │  (CLI入口)   │  │  (配置文件)  │  │  (对话入口)  │          │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└──────────┼────────────────┼────────────────┼────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    prompts/ (Prompt 模板层)                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│   │ingest_prompt │  │ query_prompt │  │ lint_prompt  │          │
│   └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    scripts/ (命令行工具层)                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │ ingest.py    │  │ query.py     │  │ lint.py      │        │
│   │ setup.py     │  │ stats.py     │  │              │        │
│   └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│              .kimi/skills/obsidian_wiki/ (核心库)                │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    __init__.py                          │  │
│   │              (导出核心函数，统一接口)                      │  │
│   └──────────────────────────────────────────────────────────┘  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │wiki_manager  │  │   ingest.py  │  │   query.py   │        │
│   │  (核心管理)   │  │  (资料摄入)  │  │  (知识查询)  │        │
│   └──────────────┘  └──────────────┘  └──────────────┘        │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │  entities.py │  │ concepts.py  │  │   lint.py   │        │
│   │  (实体管理)   │  │ (概念管理)   │  │ (健康检查)  │        │
│   └──────────────┘  └──────────────┘  └──────────────┘        │
│   ┌──────────────┐  ┌──────────────┐                          │
│   │index_manager │  │   utils.py   │                          │
│   │  (索引管理)   │  │  (工具函数)  │                          │
│   └──────────────┘  └──────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      存储层 (Storage)                            │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │    raw/      │  │    wiki/     │  │ templates/   │        │
│   │  (原始资料)   │  │  (知识库)    │  │   (模板)     │        │
│   └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### 核心模块作用

| 模块 | 职责 | 关键方法 |
|-----|------|---------|
| **WikiManager** | 核心管理器，路径/模板/页面 CRUD | `get_template()`, `create_page()`, `parse_frontmatter()` |
| **ingest.py** | 资料摄入，提取实体概念 | `ingest_source()`, `auto_classify()`, `extract_entities_from_text()` |
| **query.py** | 知识查询，搜索匹配 | `query_wiki()`, `_find_relevant_pages()`, `_extract_keywords()` |
| **lint.py** | 健康检查，6项检查 | `lint_wiki()`, `_check_orphan_pages()`, `_check_dead_links()` |
| **entities.py** | 实体页面管理 | `create_entity_page()` |
| **concepts.py** | 概念页面管理 | `create_concept_page()` |
| **index_manager.py** | 索引更新 | `update_index()` |

### 调用链路示例

```
CLI 调用:
python start.py ingest raw/xxx.md
    └── start.py
        └── scripts/ingest.py
            └── obsidian_wiki.ingest_source()
                └── ingest.py

Agent 对话调用:
"请处理这份资料"
    └── KimiCode Agent
        └── 读取 KIMICODE.md 配置
            └── 调用 LLM
                └── obsidian_wiki 模块
```

---

## 三大核心工作流程

### 1. Ingest（资料摄入）流程

```
用户提交资料
     │
     ▼
┌─────────────────────────────┐
│  步骤1: 读取源文件           │
│  - 解析文件路径              │
│  - 支持 .md/.docx/.pdf      │
│  - 提取文本内容              │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  步骤2: 自动分类             │
│  - 关键词打分机制            │
│  - work/life/learning       │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  步骤3: 创建源摘要页         │
│  - wiki/{category}/sources/ │
│  - YYYY-MM-DD-标题.md        │
│  - 使用 source 模板          │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  步骤4: 提取实体             │
│  - 正则匹配: 公司/产品/项目   │
│  - 检查是否已存在            │
│  - 创建或追加到 wiki/entities│
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  步骤5: 提取概念             │
│  - 正则匹配: 业务/技术/方法论 │
│  - 检查是否已存在            │
│  - 创建或追加到 wiki/concepts│
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  步骤6: 更新主题页           │
│  - 追加源资料链接到 topic    │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  步骤7: 更新索引             │
│  - wiki/index.md            │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  步骤8: 记录日志             │
│  - wiki/log.md              │
└─────────────────────────────┘
```

### 2. Query（知识查询）流程

```
用户提问
   │
   ▼
┌─────────────────────────────┐
│  步骤1: 读取索引             │
│  - wiki/index.md            │
│  - 了解知识库结构            │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  步骤2: 搜索相关页面         │
│  - 提取问题关键词            │
│  - 遍历所有页面计算相关性     │
│  - 按评分排序返回 Top 10     │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  步骤3: 读取页面内容         │
│  - 解析 frontmatter         │
│  - 截取正文前2000字符        │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  步骤4: 生成回答             │
│  - markdown/table/list格式  │
│  - 添加 [[页面链接]] 引用    │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  步骤5: 询问是否归档         │
│  - 保存到 wiki/{cat}/analyses│
└─────────────────────────────┘
```

### 3. Lint（健康检查）流程

```
用户触发检查
     │
     ▼
┌─────────────────────────────┐
│  检查1: 孤立页面             │
│  - 没有入链的页面            │
│  - 收集所有出链，被引用则正常  │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  检查2: 死链                 │
│  - 链接目标不存在的页面       │
│  - 遍历所有 [[链接]]         │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  检查3: 矛盾信息             │
│  - 同一实体的不同描述         │
│  - 日期冲突检测              │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  检查4: 缺失实体             │
│  - 被多次提及但无独立页面     │
│  - 提及次数 >= 3             │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  检查5: 标签一致性           │
│  - work vs Work 等大小写    │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  检查6: 根目录非法文件        │
│  - 非 index.md/log.md 的根目录md│
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  生成报告 wiki/lint-report.md│
└─────────────────────────────┘
```

---

## 快速开始

### 1. 环境准备

确保已安装 Python 3.8+:

```bash
python --version
```

### 2. 配置 KimiCode Agent

将 `KIMICODE.md` 的内容复制到 KimiCode 的 Agent 配置中，Agent 会自动读取并执行。

### 3. 使用 Agent 管理知识库

#### 资料摄入 (Ingest)

将资料直接放入 `raw/` 目录，然后告诉 Agent:

```
请摄入 raw/估值系统需求文档.md
```

Agent 会自动分析内容并分类到 work/life/learning 之一。

或使用命令行:

```bash
# 自动分类
python scripts/ingest.py raw/估值系统需求文档.md

# 手动指定类别
python scripts/ingest.py raw/估值系统需求文档.md --category work
```

#### 知识查询 (Query)

向 Agent 提问:

```
什么是估值核算？
对比 TA 系统和估值系统
分析资管行业趋势
```

或使用命令行:

```bash
python scripts/query.py "什么是估值核算?"
python scripts/query.py "对比TA系统和估值系统" --format table
```

#### 健康检查 (Lint)

定期检查知识库健康:

```
请检查知识库健康
```

或使用命令行:

```bash
python scripts/lint.py
python scripts/lint.py --type orphans
```

### 4. 在 Obsidian 中查看

1. 打开 Obsidian
2. 选择 "打开本地仓库"
3. 选择 `obsidian-wiki-agent/wiki/` 目录
4. 享受知识图谱!

## 页面类型

### 1. 源资料摘要 (Source)

- 位置: `wiki/{category}/sources/`
- 用途: 记录原始资料的摘要
- 模板: `templates/source.md`

### 2. 实体页 (Entity)

- 位置: `wiki/entities/`
- 类型: person, company, product, project
- 用途: 记录具体的人、公司、产品、项目
- 模板: `templates/entity.md`

### 3. 概念页 (Concept)

- 位置: `wiki/concepts/`
- 类型: business, tech, methodology
- 用途: 记录抽象概念、方法论、术语
- 模板: `templates/concept.md`

### 4. 主题页 (Topic)

- 位置: `wiki/{category}/topics/`
- 用途: 汇总某一主题的综合信息
- 模板: `templates/topic.md`

### 5. 分析页 (Analysis)

- 位置: `wiki/{category}/analyses/`
- 用途: 保存有价值的查询结果
- 模板: `templates/analysis.md`

## 特殊文件

### wiki/index.md

内容索引，由 Agent 自动维护。包含:
- 统计信息
- 按类别组织的页面列表
- 标签云

### wiki/log.md

操作日志，按时间顺序记录所有操作:
- 资料摄入
- 知识查询
- 健康检查
- 页面更新

### wiki/lint-report.md

健康检查报告，记录发现的问题:
- 孤立页面
- 死链
- 矛盾信息
- 缺失实体
- 标签不一致

## 命名规范

### 文件名
- 使用小写字母和连字符
- 日期格式: `YYYY-MM-DD`
- 示例: `2024-01-15-估值系统需求.md`

### 页面标题
- 使用中文标题
- 实体页: 实体名称
- 概念页: 概念名称
- 源摘要: 资料原标题

### 链接格式
- Obsidian 维基链接: `[[页面名]]`
- 别名链接: `[[页面名|显示文本]]`
- 块链接: `[[页面名#标题]]`

## Frontmatter 规范

所有 wiki 页面必须包含 YAML frontmatter:

```yaml
---
title: 页面标题
type: source|entity|concept|topic|analysis
category: work|life|learning
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
status: draft|review|complete
---
```

## 命令行工具

### ingest.py - 资料摄入

```bash
python scripts/ingest.py <source_path> [options]

Options:
  --category {work,life,learning}  资料类别 (默认: work)
  --title TEXT                    资料标题

Examples:
  python scripts/ingest.py raw/work/需求文档.md
  python scripts/ingest.py raw/life/旅行攻略.md --category life --title "日本旅行"
```

### query.py - 知识查询

```bash
python scripts/query.py <question> [options]

Options:
  --format {markdown,table,list}  输出格式 (默认: markdown)
  --save                         保存结果到 wiki
  --category {work,life,learning} 限制查询类别

Examples:
  python scripts/query.py "什么是估值核算?"
  python scripts/query.py "对比TA系统和估值系统" --format table
  python scripts/query.py "分析行业趋势" --save
```

### lint.py - 健康检查

```bash
python scripts/lint.py [options]

Options:
  --type {all,orphans,deadlinks,contradictions,missing,tags} 检查类型 (默认: all)
  --fix                                                      自动修复

Examples:
  python scripts/lint.py
  python scripts/lint.py --type orphans
```

### stats.py - 统计信息

```bash
python scripts/stats.py
```

## 使用示例

### 示例 1: 摄入工作资料

1. 将需求文档放入 `raw/work/`
2. 告诉 Agent: "请摄入 raw/work/估值系统需求文档.md"
3. Agent 会:
   - 创建源摘要页
   - 提取实体（估值系统、TA系统、资金清算系统）
   - 提取概念（估值核算、净值化转型）
   - 更新索引

### 示例 2: 查询知识

问 Agent: "什么是估值核算？"

Agent 会:
1. 搜索相关页面
2. 综合信息
3. 给出带引用的回答

### 示例 3: 健康检查

告诉 Agent: "检查知识库健康"

Agent 会:
1. 检查孤立页面
2. 检查死链
3. 检查缺失实体
4. 生成报告

## 最佳实践

1. **定期摄入**: 及时将新资料摄入知识库
2. **保持审阅**: 审阅 Agent 创建的页面，确保准确性
3. **定期清理**: 运行 lint 检查，修复问题
4. **使用标签**: 为页面添加合适的标签
5. **建立连接**: 主动创建页面间的链接

## Obsidian 插件推荐

- **Dataview**: 基于 frontmatter 的动态查询
- **Graph View**: 可视化知识图谱
- **Tag Wrangler**: 标签管理
- **Templater**: 高级模板功能
- **Marp**: 幻灯片生成

## 自定义配置

编辑 `KIMICODE.md` 可以自定义 Agent 行为:

- 修改目录结构
- 调整页面模板
- 自定义标签体系
- 修改工作流程

## 注意事项

1. **备份**: 定期备份知识库（可用 Git 管理）
2. **隐私**: 注意敏感信息的处理
3. **审核**: 重要内容建议人工审核
4. **协作**: 可与团队共享 wiki 目录

## 故障排除

### Agent 无法读取文件

检查文件路径是否正确，确保使用相对路径或绝对路径。

### 页面链接不工作

检查 Obsidian 设置:
- Settings → Files and links → New link format: "Shortest path when possible"

### 索引未更新

手动运行: `python scripts/stats.py`

## 贡献

欢迎提交 Issue 和 PR!

## 许可证

MIT License

## 致谢

- 基于 [Karpathy's LLM-Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 模式
- 为全资产管理系统产品经理定制

---

**开始使用**: 将资料放入 `raw/` 目录，告诉 Agent "请摄入资料"，即可开始构建你的个人知识库！
