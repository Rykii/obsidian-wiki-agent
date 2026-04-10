#!/usr/bin/env python3
"""
健康检查脚本 - 命令行工具

用法:
    python scripts/lint.py [--type all|orphans|deadlinks|contradictions|missing]

示例:
    python scripts/lint.py
    python scripts/lint.py --type orphans
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from obsidian_wiki import lint_wiki


def main():
    parser = argparse.ArgumentParser(description="检查知识库健康")
    parser.add_argument(
        "--type",
        choices=["all", "orphans", "deadlinks", "contradictions", "missing", "tags"],
        default="all",
        help="检查类型",
    )
    parser.add_argument("--fix", action="store_true", help="自动修复问题")

    args = parser.parse_args()

    print(f"执行健康检查: {args.type}")
    print("-" * 50)

    result = lint_wiki(
        check_type=args.type,
        auto_fix=args.fix,
    )

    if result["success"]:
        print(f"\n✓ 检查完成!")
        print(f"\n发现问题: {result['total_issues']}")

        issues = result["issues"]
        print(f"  - 孤立页面: {len(issues['orphan_pages'])}")
        print(f"  - 死链: {len(issues['dead_links'])}")
        print(f"  - 矛盾信息: {len(issues['contradictions'])}")
        print(f"  - 缺失实体: {len(issues['missing_entities'])}")
        print(f"  - 标签不一致: {len(issues['inconsistent_tags'])}")

        print(f"\n详细报告: {result['report_path']}")

        if result["total_issues"] > 0:
            print("\n建议:")
            if issues["missing_entities"]:
                print(f"  - 考虑为高频提及实体创建页面")
            if issues["dead_links"]:
                print(f"  - 修复死链或创建缺失页面")
            if issues["orphan_pages"]:
                print(f"  - 检查孤立页面是否需要保留")
    else:
        print(f"\n✗ 检查失败: {result.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
