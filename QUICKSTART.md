# 快速开始指南

## 5 分钟上手 Obsidian Wiki Agent

### 1. 启动 Agent

在 KimiCode 中，将 `KIMICODE.md` 的内容复制到 Agent 配置中，Agent 会自动读取并执行。

或者，直接告诉 Agent:

```
请读取 KIMICODE.md 配置文件，成为我的 Obsidian Wiki Agent
```

### 2. 摄入第一份资料

将资料放入 `raw/` 目录，然后告诉 Agent:

```
请摄入 raw/work/example-估值系统需求文档.md
```

Agent 会:
- 读取资料内容
- 创建源摘要页
- 提取实体（估值系统、TA系统、资金清算系统）
- 提取概念（估值核算、净值化转型）
- 更新索引

### 3. 查看结果

打开 Obsidian:
1. 选择 "打开本地仓库"
2. 选择 `obsidian-wiki-agent/wiki/` 目录
3. 查看创建的页面

### 4. 提问查询

向 Agent 提问:

```
什么是估值核算？
```

Agent 会基于知识库内容回答，并引用相关页面。

### 5. 健康检查

定期检查知识库:

```
请检查知识库健康
```

## 常用操作

### 摄入资料

```
请摄入 raw/work/新产品需求.md
请摄入 raw/life/旅行计划.md，类别为生活
请摄入 raw/learning/读书笔记.md，类别为学习
```

### 查询知识

```
什么是净值化转型？
对比估值系统和TA系统
分析资管行业趋势
总结我的工作项目
```

### 创建实体

```
请创建实体页面：估值系统，类型为产品
请创建实体页面：某某公司，类型为公司
```

### 创建概念

```
请创建概念页面：摊余成本法，类型为业务概念
请创建概念页面：敏捷开发，类型为方法论
```

### 健康检查

```
检查知识库健康
检查孤立页面
检查死链
检查缺失实体
```

## 目录结构速览

```
obsidian-wiki-agent/
├── KIMICODE.md          # Agent 配置（重要！）
├── raw/                  # 放你的原始资料
│   ├── work/            # 工作资料
│   ├── life/            # 生活笔记
│   └── learning/        # 学习资料
├── wiki/                 # Agent 维护的知识库
│   ├── index.md         # 索引
│   ├── log.md           # 日志
│   ├── work/            # 工作知识
│   ├── life/            # 生活知识
│   ├── learning/        # 学习知识
│   ├── entities/        # 实体页面
│   └── concepts/        # 概念页面
└── scripts/             # 命令行工具
    ├── ingest.py        # 摄入资料
    ├── query.py         # 查询知识
    └── lint.py          # 健康检查
```

## 命令行工具

### 摄入资料

```bash
python scripts/ingest.py raw/work/需求文档.md --category work
```

### 查询知识

```bash
python scripts/query.py "什么是估值核算?"
python scripts/query.py "对比TA系统和估值系统" --format table
```

### 健康检查

```bash
python scripts/lint.py
python scripts/lint.py --type orphans
```

### 统计信息

```bash
python scripts/stats.py
```

## 最佳实践

1. **及时摄入**: 看完资料后立即摄入
2. **定期审阅**: 每周审阅 Agent 创建的页面
3. **运行检查**: 每月运行一次健康检查
4. **使用标签**: 为页面添加合适的标签
5. **建立连接**: 主动创建页面间的链接

## 故障排除

### Agent 不工作

- 确认 `KIMICODE.md` 已正确配置
- 检查文件路径是否正确

### 页面链接不工作

- 检查 Obsidian 设置: Settings → Files and links → New link format
- 确保选择 "Shortest path when possible"

### 索引未更新

- 手动运行: `python scripts/setup.py`
- 或告诉 Agent: "请更新索引"

## 下一步

- 阅读 [README.md](README.md) 了解完整功能
- 查看 `raw/` 目录中的示例资料
- 开始构建你的个人知识库！

---

**有问题？** 查看 README.md 或询问 Agent!
