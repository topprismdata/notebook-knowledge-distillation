#!/usr/bin/env python3
"""Step 0: 环境检查 - 确保 nlm CLI 可用"""

import subprocess
import sys
import json


def check_nlm_installed() -> bool:
    """检查 nlm 是否安装"""
    try:
        result = subprocess.run(
            ['nlm', '--version'],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_nlm_auth() -> bool:
    """检查 nlm 认证状态"""
    try:
        result = subprocess.run(
            ['nlm', 'auth', 'status'],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def check_nlm_network() -> bool:
    """检查网络连通性"""
    try:
        result = subprocess.run(
            ['nlm', 'notebook', 'list'],
            capture_output=True, text=True, timeout=15
        )
        return result.returncode == 0
    except Exception:
        return False


def get_notebook_count() -> int:
    """获取笔记本数量（网络测试的副产品）"""
    try:
        result = subprocess.run(
            ['nlm', 'notebook', 'list'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            count = 0
            for line in result.stdout.split('\n'):
                if line.strip().startswith('{'):
                    count += 1
            return count
        return -1
    except Exception:
        return -1


def check_skill_creator() -> bool:
    """检查 skill-creator 技能是否存在"""
    import os
    return os.path.isdir('/Users/guohongbin/.claude/skills/skill-creator')


def check_skill_tester() -> bool:
    """检查 skill-tester 技能是否存在"""
    import os
    return os.path.isdir('/Users/guohongbin/.claude/skills/skill-tester')


def main():
    print("=" * 50)
    print("NotebookLM 环境检查")
    print("=" * 50)

    # 检查 nlm 安装
    installed = check_nlm_installed()
    print(f"\n[1/5] nlm 安装: {'✓' if installed else '✗'}")
    if not installed:
        print("  → 请安装: pip install notebooklm-cli")
        print("  → 文档: https://github.com/google/noteable-cli")

    # 检查认证
    authed = check_nlm_auth()
    print(f"[2/5] nlm 认证: {'✓' if authed else '✗'}")
    if not authed:
        print("  → 请登录: nlm auth login")

    # 检查网络
    network_ok = check_nlm_network()
    print(f"[3/5] 网络连通: {'✓' if network_ok else '✗'}")
    if not network_ok:
        print("  → 请检查网络连接")

    # 检查 skill-creator
    sc_ok = check_skill_creator()
    print(f"[4/5] skill-creator: {'✓' if sc_ok else '✗'}")
    if not sc_ok:
        print("  → 技能不存在: ~/.claude/skills/skill-creator")

    # 检查 skill-tester
    st_ok = check_skill_tester()
    print(f"[5/5] skill-tester: {'✓' if st_ok else '✗'}")
    if not st_ok:
        print("  → 技能不存在: ~/.claude/skills/skill-tester")

    # 额外信息
    if installed:
        count = get_notebook_count()
        if count >= 0:
            print(f"\n📚 当前笔记本数: {count}")

    print("\n" + "=" * 50)
    if installed and authed and network_ok and sc_ok and st_ok:
        print("状态: ✓ 所有检查通过，可以继续蒸馏流程")
        sys.exit(0)
    else:
        print("状态: ✗ 存在问题，请先修复后再试")
        sys.exit(1)


if __name__ == '__main__':
    main()
