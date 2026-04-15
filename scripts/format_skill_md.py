#!/usr/bin/env python3
"""将蒸馏内容格式化为标准 SKILL.md"""

import sys
import re
from datetime import datetime


def parse_distilled(content: str) -> dict:
    """解析蒸馏输出，提取结构化信息"""
    lines = content.split('\n')

    meta = {
        'skill_name': '',
        'description': '',
        'trigger_conditions': [],
        'modules': [],
        'sources': [],
    }

    current_section = None
    current_lines = []

    for line in lines:
        if line.startswith('### '):
            # 能力点
            capability_name = re.sub(r'^\d+[\.\)]\s*', '', line[4:].strip())
            meta['modules'].append({
                'name': capability_name,
                'content': '\n'.join(current_lines)
            })
            current_lines = []
        elif line.startswith('## '):
            section = line[3:].strip()
            if section == '触发条件' or section == 'Trigger Conditions':
                current_section = 'triggers'
            elif '元信息' in section or 'Meta' in section:
                current_section = 'meta'
            elif '来源' in section or 'Source' in section:
                current_section = 'sources'
            else:
                current_section = 'other'
        elif current_section == 'triggers' and line.strip().startswith('-'):
            meta['trigger_conditions'].append(line.strip().lstrip('- '))
        elif current_section == 'meta':
            if '名称' in line or 'name' in line.lower():
                parts = line.split(':', 1)
                if len(parts) > 1:
                    meta['skill_name'] = parts[1].strip().replace('**', '').replace('`', '')
            if '描述' in line or 'description' in line.lower():
                parts = line.split(':', 1)
                if len(parts) > 1:
                    meta['description'] = parts[1].strip().replace('**', '').replace('`', '')

        if current_section != 'triggers':
            current_lines.append(line)

    return meta


def generate_skill_md(meta: dict, notebook_title: str = "") -> str:
    """生成 SKILL.md 内容"""

    name = meta.get('skill_name', 'unnamed-skill')
    # 确保名称符合规范
    name = name.lower().replace(' ', '-').replace('_', '-')
    name = re.sub(r'[^a-z0-9-]', '', name)

    description = meta.get('description', '从 NotebookLM 笔记本蒸馏生成的可复用技能。')

    today = datetime.now().strftime('%Y-%m-%d')

    modules_md = []
    for mod in meta.get('modules', []):
        modules_md.append(f"### {mod['name']}\n{mod['content'].strip()}")

    triggers_md = []
    for t in meta.get('trigger_conditions', []):
        triggers_md.append(f"- {t}")

    body = "\n\n".join(modules_md)
    triggers = "\n".join(triggers_md) if triggers_md else (
        "- \"把笔记本蒸馏成技能\"\n"
        "- \"从 NotebookLM 创建技能\"\n"
        "- \"distill this notebook\"\n"
        "- \"create skill from notebook\""
    )

    return f"""---
name: {name}
description: |
  {description}
  触发场景：{triggers[:100]}...等。
---

# {name.replace('-', ' ').title()}

## 核心能力

{body}

## 触发条件

{triggers}

---

## 来源

本技能蒸馏自 NotebookLM 笔记本「{notebook_title or "未命名笔记本"}」
生成日期：{today}

知识来源：{', '.join(meta.get('sources', ['N/A']))}
"""
