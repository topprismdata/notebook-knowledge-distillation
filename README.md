# notebook-knowledge-distillation

Claude Code skill: 将 NotebookLM 笔记本中的多源知识蒸馏为可复用技能的工作流。

## 核心特性

- **Flashcard 密度扫描**：快速判断笔记本是否值得蒸馏
- **贝叶斯多源验证**：置信度由多源交叉验证驱动，而非硬性数量规则
- **3 轮迭代蒸馏**：高频共识 → 低频验证 → 缺口探测
- **skill-tester 评分**：4D  rubric，TIER: POWERFUL ≥ 8.5
- **完整边界处理**：空白 notebook、nlm 不可用、评分 < 5 等场景全覆盖

## 快速使用

```bash
# Step 0: 环境检查
python3 scripts/check_environment.py

# Step 1: 解析 URL
python3 scripts/parse_notebook_url.py "https://notebooklm.google.com/notebook/..."

# Step 2: Flashcard 扫描（可选）
nlm flashcards create <notebook_id> -y

# Step 3: 深度蒸馏
nlm notebook query <notebook_id> "$(cat prompts/distill_basic.md)"

# Step 4: 生成测试用例
python3 scripts/generate_test_cases.py /tmp/distilled_output.txt

# Step 5: 验证并打包
python3 ~/.claude/skills/skill-creator/scripts/quick_validate.py <skill-dir>/SKILL.md
python3 ~/.claude/skills/skill-creator/scripts/package_skill.py <skill-dir>
```

## 评分结果

- **TIER**: ★ POWERFUL ★ (8.75/10)
- **Documentation**: 9/10
- **Code/Scripts**: 8/10
- **Completeness**: 9/10
- **Usability**: 9/10

## 依赖

- `nlm` CLI (`pip install notebooklm-cli`)
- `skill-tester`
- `skill-creator` (quick_validate.py, package_skill.py)

---
*Built on Claude Code × NotebookLM × skill-tester 联合工作流（2026-04）*
