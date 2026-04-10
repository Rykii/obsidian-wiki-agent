#!/usr/bin/env python3
"""
统计信息脚本 - 命令行工具

用法:
    python scripts/stats.py

示例:
    python scripts/stats.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from obsidian_wiki import get_wiki_stats


def main():
    print("知识库统计信息")
    print("=" * 50)

    stats = get_wiki_stats()

    print(f"\n总页面数: {stats['total_pages']}")
    print(f"总标签数: {stats['total_tags']}")
    print(f"总链接数: {stats['total_links']}")

    print("\n按类型分布:")
    for page_type, count in stats["by_type"].items():
        print(f"  - {page_type}: {count}")

    print("\n按类别分布:")
    for category, count in stats["by_category"].items():
        print(f"  - {category}: {count}")

    if stats["tags_list"]:
        print(f"\n标签列表 ({len(stats['tags_list'])}):")
        for tag in stats["tags_list"][:20]:  # 最多显示20个
            print(f"  - #{tag}")
        if len(stats["tags_list"]) > 20:
            print(f"  ... 还有 {len(stats['tags_list']) - 20} 个标签")


if __name__ == "__main__":
    main()
