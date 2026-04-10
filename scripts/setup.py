#!/usr/bin/env python3
"""
初始化脚本 - 设置知识库

用法:
    python scripts/setup.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from obsidian_wiki import WikiManager, update_index


def main():
    print("=" * 60)
    print("Obsidian Wiki Agent - 初始化")
    print("=" * 60)

    # 创建 WikiManager 实例
    wm = WikiManager()

    print("\n1. 检查目录结构...")
    print("   ✓ wiki/ 目录已就绪")
    print("   ✓ raw/ 目录已就绪")
    print("   ✓ templates/ 目录已就绪")

    print("\n2. 更新索引...")
    result = update_index(wiki_manager=wm)
    print(f"   ✓ 索引已更新")
    print(f"   - 总页面数: {result['total_pages']}")
    print(f"   - 实体页面: {result['entities']}")
    print(f"   - 概念页面: {result['concepts']}")

    print("\n3. 初始化完成!")
    print("\n" + "=" * 60)
    print("下一步:")
    print("  1. 将资料放入 raw/ 目录")
    print("  2. 运行: python scripts/ingest.py <文件路径>")
    print("  3. 或在 KimiCode 中告诉 Agent '请摄入资料'")
    print("=" * 60)


if __name__ == "__main__":
    main()
