#!/usr/bin/env python3
"""
知识查询脚本 - 命令行工具

用法:
    python scripts/query.py <question> [--format markdown|table] [--save]

示例:
    python scripts/query.py "什么是估值核算?"
    python scripts/query.py "对比TA系统和估值系统" --format table
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from obsidian_wiki import query_wiki


def main():
    parser = argparse.ArgumentParser(description="查询知识库")
    parser.add_argument("question", help="查询问题")
    parser.add_argument(
        "--format",
        choices=["markdown", "table", "list"],
        default="markdown",
        help="输出格式",
    )
    parser.add_argument("--save", action="store_true", help="保存结果到 wiki")
    parser.add_argument("--category", choices=["work", "life", "learning"], help="限制查询类别")

    args = parser.parse_args()

    print(f"查询: {args.question}")
    print("-" * 50)

    result = query_wiki(
        question=args.question,
        output_format=args.format,
        save_to_wiki=args.save,
        category=args.category,
    )

    if result["success"]:
        print("\n" + result["answer"])
        print("\n" + "-" * 50)
        print(f"\n相关页面 ({len(result['relevant_pages'])}):")
        for page in result["relevant_pages"]:
            print(f"  - {page}")

        if result["saved_path"]:
            print(f"\n✓ 结果已保存: {result['saved_path']}")
    else:
        print(f"\n✗ 查询失败: {result.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
