#!/usr/bin/env python3
"""
资料摄入脚本 - 命令行工具

用法:
    python scripts/ingest.py <source_path> [--category work|life|learning]

示例:
    python scripts/ingest.py raw/work/需求文档.md --category work
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from obsidian_wiki import ingest_source, WikiManager


def main():
    parser = argparse.ArgumentParser(description="摄入资料到知识库")
    parser.add_argument("source", help="源文件路径（相对于 raw/ 目录）")
    parser.add_argument(
        "--category",
        choices=["work", "life", "learning"],
        default="work",
        help="资料类别",
    )
    parser.add_argument("--title", help="资料标题（可选）")

    args = parser.parse_args()

    print(f"正在摄入资料: {args.source}")
    print(f"类别: {args.category}")

    result = ingest_source(
        source_path=args.source,
        category=args.category,
        title=args.title,
    )

    if result["success"]:
        print("\n✓ 摄入成功!")
        print(f"源摘要页: {result['source_page']}")
        print(f"\n提取的实体 ({len(result['entities'])}):")
        for entity in result["entities"]:
            print(f"  - {entity}")
        print(f"\n提取的概念 ({len(result['concepts'])}):")
        for concept in result["concepts"]:
            print(f"  - {concept}")
    else:
        print(f"\n✗ 摄入失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
