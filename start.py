#!/usr/bin/env python3
"""
Obsidian Wiki Agent - 启动器

用法:
    python start.py [command] [options]

Commands:
    setup       初始化知识库
    ingest      摄入资料
    query       查询知识
    lint        健康检查
    stats       统计信息
    help        显示帮助

Examples:
    python start.py setup
    python start.py ingest raw/work/文档.md --category work
    python start.py query "什么是估值核算?"
    python start.py lint
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入脚本模块
sys.path.insert(0, str(Path(__file__).parent / "scripts"))


def print_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("  Obsidian Wiki Agent")
    print("  基于 Karpathy's LLM-Wiki 模式")
    print("=" * 60)
    print()


def print_help():
    """打印帮助信息"""
    print(__doc__)
    print()
    print("快速开始:")
    print("  1. 初始化: python start.py setup")
    print("  2. 摄入资料: python start.py ingest <文件路径>")
    print("  3. 查询知识: python start.py query <问题>")
    print("  4. 健康检查: python start.py lint")
    print()
    print("更多信息: 查看 README.md 和 QUICKSTART.md")


def main():
    print_banner()

    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    command = sys.argv[1]

    # 移除命令名，保留其他参数
    sys.argv = [sys.argv[0]] + sys.argv[2:]

    if command == "setup":
        from scripts.setup import main as setup_main
        setup_main()
    elif command == "ingest":
        from scripts.ingest import main as ingest_main
        ingest_main()
    elif command == "query":
        from scripts.query import main as query_main
        query_main()
    elif command == "lint":
        from scripts.lint import main as lint_main
        lint_main()
    elif command == "stats":
        from scripts.stats import main as stats_main
        stats_main()
    elif command in ["help", "-h", "--help"]:
        print_help()
    else:
        print(f"未知命令: {command}")
        print()
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
