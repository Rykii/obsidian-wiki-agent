# 开始使用 Obsidian Wiki Agent

## 你已经获得了什么

这是一个完整的、可直接启动的 Obsidian 知识库管理 Agent 工程，基于 Karpathy's LLM-Wiki 模式构建。

### 项目包含

- **Agent 配置文件** (`KIMICODE.md`): 定义 Agent 的行为和工作流程
- **KimiCode Skill**: 完整的 Python 模块，提供摄入、查询、检查功能
- **页面模板**: 5 种页面类型的模板文件
- **示例资料**: 3 份示例资料（工作、生活、学习各一份）
- **命令行工具**: 5 个实用脚本
- **Obsidian 配置**: 预配置的 Obsidian 设置

## 3 种启动方式

### 方式 1: 使用 KimiCode Agent（推荐）

1. 将 `KIMICODE.md` 的内容复制到 KimiCode 的 Agent 配置中
2. Agent 会自动读取配置并执行
3. 告诉 Agent: "请摄入 raw/example-估值系统需求文档.md"
4. Agent 会自动分析内容并分类
5. 开始与 Agent 对话，管理你的知识库

### 方式 2: 使用命令行工具

```bash
# 初始化
python start.py setup

# 摄入资料（自动分类）
python start.py ingest raw/文档.md

# 查询知识
python start.py query "什么是估值核算?"

# 健康检查
python start.py lint
```

### 方式 3: 直接使用 Python 脚本

```bash
# 设置 Python 路径
export PYTHONPATH="${PYTHONPATH}:."

# 摄入资料（自动分类）
python scripts/ingest.py raw/文档.md

# 查询知识
python scripts/query.py "问题"

# 健康检查
python scripts/lint.py
```

## 第一步：初始化

```bash
# 进入项目目录
cd obsidian-wiki-agent

# 初始化知识库
python start.py setup
```

## 第二步：摄入示例资料

```bash
# 摄入示例资料（Agent 会自动分类）
python start.py ingest raw/example-估值系统需求文档.md
python start.py ingest raw/example-日本旅行攻略.md
python start.py ingest raw/example-产品经理方法论.md
```

## 第三步：在 Obsidian 中查看

1. 打开 Obsidian 应用
2. 点击 "打开本地仓库"
3. 选择 `obsidian-wiki-agent/wiki/` 目录
4. 查看生成的页面和图谱

## 第四步：开始查询

```bash
# 简单查询
python start.py query "什么是估值核算?"

# 对比查询
python start.py query "对比TA系统和估值系统" --format table

# 保存查询结果
python start.py query "分析资管行业趋势" --save
```

## 第五步：定期维护

```bash
# 健康检查
python start.py lint

# 查看统计
python start.py stats
```

## 添加你自己的资料

1. 将资料文件直接放入 `raw/` 目录

2. 告诉 Agent 摄入:
   ```
   请摄入 raw/我的文档.md
   ```
   Agent 会自动分析内容并分类到 work/life/learning

3. 或使用命令行:
   ```bash
   # 自动分类
   python start.py ingest raw/我的文档.md
   
   # 手动指定类别
   python start.py ingest raw/我的文档.md --category work
   ```

## 目录结构速览

```
obsidian-wiki-agent/
├── KIMICODE.md          # Agent 配置（核心）
├── start.py             # 启动脚本
├── raw/                 # 放你的原始资料
├── wiki/                # Agent 维护的知识库
│   ├── index.md         # 索引
│   ├── log.md           # 日志
│   └── .obsidian/       # Obsidian 配置
└── scripts/             # 命令行工具
```

## 常用命令速查

| 命令 | 说明 |
|------|------|
| `python start.py setup` | 初始化知识库 |
| `python start.py ingest <文件>` | 摄入资料 |
| `python start.py query <问题>` | 查询知识 |
| `python start.py lint` | 健康检查 |
| `python start.py stats` | 统计信息 |
| `python start.py help` | 显示帮助 |

## 下一步

1. 阅读 [README.md](README.md) 了解完整功能
2. 阅读 [QUICKSTART.md](QUICKSTART.md) 了解快速开始
3. 阅读 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) 了解项目结构
4. 开始构建你的个人知识库！

## 需要帮助？

1. 查看 `wiki/log.md` 了解操作历史
2. 运行 `python start.py lint` 检查问题
3. 询问 KimiCode Agent

---

**祝你构建知识库愉快！**
