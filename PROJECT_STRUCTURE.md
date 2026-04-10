# 项目结构说明

## 完整目录树

```
obsidian-wiki-agent/
├── KIMICODE.md                  # Agent 核心配置文件
├── README.md                    # 完整文档
├── QUICKSTART.md               # 快速开始指南
├── PROJECT_STRUCTURE.md        # 本文件
├── requirements.txt            # Python 依赖
├── .gitignore                  # Git 忽略配置
├── start.py                    # 统一启动脚本
│
├── .kimi/
│   └── skills/
│       └── obsidian_wiki/      # KimiCode Skill
│           ├── SKILL.md        # Skill 说明
│           ├── __init__.py     # 模块初始化
│           ├── wiki_manager.py # 核心管理类
│           ├── ingest.py       # 资料摄入
│           ├── query.py        # 知识查询
│           ├── lint.py         # 健康检查
│           ├── entities.py     # 实体管理
│           ├── concepts.py     # 概念管理
│           ├── index_manager.py# 索引管理
│           └── utils.py        # 工具函数
│
├── prompts/                    # Prompt 模板
│   ├── ingest_prompt.md        # 摄入 Prompt
│   ├── query_prompt.md         # 查询 Prompt
│   └── lint_prompt.md          # 检查 Prompt
│
├── templates/                  # 页面模板
│   ├── source.md               # 源资料模板
│   ├── entity.md               # 实体页模板
│   ├── concept.md              # 概念页模板
│   ├── topic.md                # 主题页模板
│   └── analysis.md             # 分析页模板
│
├── raw/                        # 原始资料（只读）- 直接放入，Agent 自动分类
│   ├── example-估值系统需求文档.md
│   ├── example-日本旅行攻略.md
│   └── example-产品经理方法论.md
│
├── wiki/                       # 维基内容（Agent 维护）
│   ├── .obsidian/              # Obsidian 配置
│   │   ├── app.json            # 应用设置
│   │   ├── appearance.json     # 外观设置
│   │   ├── core-plugins.json   # 核心插件
│   │   └── hotkeys.json        # 快捷键
│   │
│   ├── index.md                # 内容索引
│   ├── log.md                  # 操作日志
│   │
│   ├── work/                   # 工作知识
│   │   ├── sources/            # 源资料摘要
│   │   ├── topics/             # 主题页面
│   │   └── analyses/           # 分析页面
│   │
│   ├── life/                   # 生活知识
│   │   ├── sources/
│   │   ├── topics/
│   │   └── analyses/
│   │
│   ├── learning/               # 学习知识
│   │   ├── sources/
│   │   ├── topics/
│   │   └── analyses/
│   │
│   ├── entities/               # 实体页面
│   └── concepts/               # 概念页面
│
└── scripts/                    # 命令行工具
    ├── setup.py                # 初始化脚本
    ├── ingest.py               # 资料摄入
    ├── query.py                # 知识查询
    ├── lint.py                 # 健康检查
    └── stats.py                # 统计信息
```

## 文件说明

### 核心配置

| 文件 | 说明 |
|------|------|
| `KIMICODE.md` | Agent 核心配置文件，定义行为、工作流程、命名规范等 |
| `README.md` | 完整使用文档 |
| `QUICKSTART.md` | 5分钟快速开始指南 |
| `requirements.txt` | Python 依赖列表 |

### Skill 模块

| 文件 | 说明 |
|------|------|
| `wiki_manager.py` | 核心管理类，提供文件操作、frontmatter 解析、链接管理等功能 |
| `ingest.py` | 资料摄入功能，处理新资料并更新知识库 |
| `query.py` | 知识查询功能，基于知识库回答用户问题 |
| `lint.py` | 健康检查功能，检查知识库中的问题 |
| `entities.py` | 实体管理，创建和管理实体页面 |
| `concepts.py` | 概念管理，创建和管理概念页面 |
| `index_manager.py` | 索引管理，维护知识库索引 |
| `utils.py` | 工具函数，提供搜索、统计等辅助功能 |

### 模板文件

| 文件 | 用途 |
|------|------|
| `source.md` | 源资料摘要页模板 |
| `entity.md` | 实体页模板（人、公司、产品、项目） |
| `concept.md` | 概念页模板（业务概念、技术概念、方法论） |
| `topic.md` | 主题页模板 |
| `analysis.md` | 分析页模板（查询结果） |

### 脚本工具

| 文件 | 用途 |
|------|------|
| `start.py` | 统一启动脚本，整合所有功能 |
| `setup.py` | 初始化知识库 |
| `ingest.py` | 命令行资料摄入 |
| `query.py` | 命令行知识查询 |
| `lint.py` | 命令行健康检查 |
| `stats.py` | 统计信息 |

### 示例资料

| 文件 | 说明 |
|------|------|
| `example-估值系统需求文档.md` | 工作资料示例（资管系统） |
| `example-日本旅行攻略.md` | 生活笔记示例（旅游） |
| `example-产品经理方法论.md` | 学习资料示例（方法论） |

## 工作流程

### 1. 资料摄入流程

```
用户放入资料 → Agent 读取 → 自动分类 → 创建摘要页 → 提取实体 → 提取概念 → 更新索引 → 记录日志
```

**自动分类规则**:
- **work**: 业务文档、需求、项目、调研、会议等
- **life**: 旅行、购物、宠物、情感、健康等
- **learning**: 读书笔记、课程、技术、方法论等

### 2. 知识查询流程

```
用户提问 → Agent 读取索引 → 搜索相关页面 → 综合分析 → 生成回答 → 可选保存
```

### 3. 健康检查流程

```
运行检查 → 检查孤立页面 → 检查死链 → 检查矛盾 → 检查缺失实体 → 生成报告
```

## 数据流

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Raw/      │────▶│   Agent     │────▶│  自动分类   │────▶│   Wiki/     │
│  原始资料   │     │  读取内容   │     │ work/life/  │     │  知识库     │
└─────────────┘     └─────────────┘     │  learning   │     └─────────────┘
                            │            └─────────────┘
                            ▼
                     ┌─────────────┐
                     │  KIMICODE.md │
                     │   配置文件   │
                     └─────────────┘
```

**自动分类**: Agent 根据标题和内容关键词自动判断资料类别

## 扩展点

### 添加新的页面类型

1. 在 `templates/` 创建新模板
2. 在 `KIMICODE.md` 中添加类型说明
3. 在 Skill 中添加处理逻辑

### 添加新的命令

1. 在 `scripts/` 创建新脚本
2. 在 `start.py` 中添加命令映射

### 自定义模板

直接修改 `templates/` 目录下的模板文件即可。

## 注意事项

1. `raw/` 目录为只读，Agent 不会修改其中的文件
2. `wiki/` 目录由 Agent 维护，用户可以审阅但建议通过 Agent 修改
3. `KIMICODE.md` 是核心配置文件，修改后 Agent 行为会相应改变
4. 定期备份 `wiki/` 目录（建议使用 Git 管理）
