#!/usr/bin/env python3
"""从 URL 或笔记本名提取 notebook_id"""

import re
import subprocess
import sys
from typing import Optional


def extract_notebook_id(url: str) -> Optional[str]:
    """从各种 NotebookLM URL 格式中提取 notebook_id"""
    patterns = [
        r'notebook/([a-f0-9-]{36})',          # 标准格式
        r'notebook\/([a-z0-9]{32,})',         # 短格式
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def find_notebook_by_name(name: str) -> list[tuple[str, str]]:
    """根据笔记本名模糊匹配 notebook_id 和标题"""
    try:
        result = subprocess.run(
            ['nlm', 'notebook', 'list', '--json'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return []

        matches = []
        for line in result.stdout.split('\n'):
            if not line.strip():
                continue
            # 尝试解析 JSON 行
            try:
                import json
                nb = json.loads(line)
                nb_id = nb.get('id', '')
                nb_title = nb.get('title', '')
                if name.lower() in nb_title.lower():
                    matches.append((nb_id, nb_title))
            except json.JSONDecodeError:
                # 降级：纯文本匹配
                if name.lower() in line.lower():
                    parts = line.split(None, 1)
                    if len(parts) >= 1:
                        matches.append((parts[0], parts[1] if len(parts) > 1 else ''))
        return matches
    except Exception:
        return []


def validate_notebook_exists(notebook_id: str) -> bool:
    """验证 notebook 是否存在"""
    try:
        result = subprocess.run(
            ['nlm', 'notebook', 'list', '--json'],
            capture_output=True, text=True, timeout=10
        )
        return notebook_id in result.stdout
    except Exception:
        return False


def get_notebook_info(notebook_id: str) -> Optional[dict]:
    """获取笔记本基本信息"""
    try:
        result = subprocess.run(
            ['nlm', 'notebook', 'list', '--json'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return None
        import json
        for line in result.stdout.split('\n'):
            try:
                nb = json.loads(line)
                if nb.get('id') == notebook_id:
                    return nb
            except json.JSONDecodeError:
                continue
        return None
    except Exception:
        return None


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: parse_notebook_url.py <url_or_name>")
        sys.exit(1)

    query = sys.argv[1]

    # 尝试作为 URL 解析
    notebook_id = extract_notebook_id(query)
    if notebook_id:
        if validate_notebook_exists(notebook_id):
            info = get_notebook_info(notebook_id)
            title = info.get('title', 'Unknown') if info else 'Unknown'
            print(f"NOTebook ID: {notebook_id}")
            print(f"Title: {title}")
            print(f"VALID: True")
        else:
            print(f"ERROR: Notebook {notebook_id} not found")
            print(f"VALID: False")
        sys.exit(0)

    # 尝试作为笔记本名匹配
    matches = find_notebook_by_name(query)
    if len(matches) == 0:
        print(f"ERROR: No notebooks matching '{query}'")
        print(f"VALID: False")
        sys.exit(1)
    elif len(matches) == 1:
        nb_id, nb_title = matches[0]
        print(f"NOTebook ID: {nb_id}")
        print(f"Title: {nb_title}")
        print(f"VALID: True")
        sys.exit(0)
    else:
        print(f"Multiple matches for '{query}':")
        for i, (nb_id, nb_title) in enumerate(matches, 1):
            print(f"  {i}. [{nb_id}] {nb_title}")
        print(f"VALID: ambiguous")
        sys.exit(2)
