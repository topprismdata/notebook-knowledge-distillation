#!/usr/bin/env python3
"""从蒸馏内容自动生成测试用例"""

import sys
import re


def extract_capabilities(distilled_content: str) -> list[dict]:
    """从蒸馏内容中提取核心能力点"""
    capabilities = []
    lines = distilled_content.split('\n')

    current_cap = None
    current_desc = []

    for line in lines:
        # 检测 ## 标题（模块）
        if line.startswith('## '):
            if current_cap:
                capabilities.append({
                    'module': current_cap.get('module', '通用'),
                    'name': current_cap.get('name', '未命名'),
                    'description': ' '.join(current_desc) if current_desc else current_cap.get('desc', '')
                })
            current_cap = {'module': line[3:].strip()}
            current_desc = []
        # 检测 ### 标题（具体能力）
        elif line.startswith('### '):
            if current_cap and current_desc:
                capabilities.append({
                    'module': current_cap.get('module', '通用'),
                    'name': current_cap.get('name', '未命名'),
                    'description': ' '.join(current_desc)
                })
            # 从标题中提取能力名
            name = line[4:].strip()
            # 去掉可能的序号
            name = re.sub(r'^\d+[\.\)]\s*', '', name)
            current_cap['name'] = name
            current_desc = []
        elif current_cap and line.strip() and not line.startswith('#'):
            # 收集描述内容
            current_desc.append(line.strip())

    # 最后一个能力
    if current_cap:
        capabilities.append({
            'module': current_cap.get('module', '通用'),
            'name': current_cap.get('name', '未命名'),
            'description': ' '.join(current_desc) if current_desc else current_cap.get('desc', '')
        })

    return capabilities


def generate_test_cases(capabilities: list[dict]) -> list[dict]:
    """为每个能力生成测试用例"""
    test_cases = []

    trigger_templates_zh = [
        "我需要{}，应该怎么做？",
        "关于{}你能帮我分析一下吗？",
        "{}相关的场景下要注意什么？",
        "遇到{}问题，怎么处理？",
        "帮我评审一下这个{}的设计",
    ]

    trigger_templates_en = [
        "I need help with {}, how should I approach it?",
        "Can you analyze {} for me?",
        "What should I watch out for in {} scenarios?",
        "How do I handle {} issues?",
        "Review this {} design for me",
    ]

    edge_case_templates_zh = [
        "{}失灵了怎么办？",
        "如果{}不适用，有什么替代方案？",
        "{}边界情况怎么处理？",
    ]

    for i, cap in enumerate(capabilities):
        # Happy Path 测试
        trigger_zh = trigger_templates_zh[i % len(trigger_templates_zh)].format(cap['name'])
        trigger_en = trigger_templates_en[i % len(trigger_templates_en)].format(cap['name'])

        test_cases.append({
            'id': i + 1,
            'type': 'happy_path',
            'capability': cap['name'],
            'module': cap['module'],
            'prompt_zh': trigger_zh,
            'prompt_en': trigger_en,
        })

        # Edge Case 测试（每个能力至少1个，用 modulo 循环模板）
        edge_zh = edge_case_templates_zh[i % len(edge_case_templates_zh)].format(cap['name'])
        test_cases.append({
            'id': len(test_cases) + 1,  # 前面已 append Happy Path，故 +1
            'type': 'edge_case',
            'capability': cap['name'],
            'module': cap['module'],
            'prompt_zh': edge_zh,
            'prompt_en': f"What if {cap['name']} fails?",
        })

    return test_cases


def format_table(test_cases: list[dict]) -> str:
    """格式化为 Markdown 表格"""
    lines = [
        "| # | 类型 | 能力 | 测试 Prompt（中文） |",
        "|---|------|------|---------------------|",
    ]
    for tc in test_cases:
        prompt = tc['prompt_zh']
        # 截断过长的 prompt
        if len(prompt) > 40:
            prompt = prompt[:37] + "..."
        lines.append(
            f"| {tc['id']} | {tc['type']} | {tc['capability']} | {prompt} |"
        )
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_test_cases.py <distilled_content_file>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        content = f.read()

    capabilities = extract_capabilities(content)
    test_cases = generate_test_cases(capabilities)

    print(f"# 测试用例生成报告")
    print(f"\n发现 {len(capabilities)} 个核心能力")
    print(f"生成 {len(test_cases)} 个测试用例（{sum(1 for tc in test_cases if tc['type'] == 'happy_path')} Happy Path + {sum(1 for tc in test_cases if tc['type'] == 'edge_case')} Edge Case）")
    print(f"\n## 测试用例表\n")
    print(format_table(test_cases))


if __name__ == '__main__':
    main()
