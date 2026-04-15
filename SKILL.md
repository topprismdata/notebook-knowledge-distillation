---
name: notebook-knowledge-distillation
description: |
  将 NotebookLM 笔记本中的多源知识蒸馏为可复用技能的工作流。触发场景：用户说"蒸馏"、"从 NotebookLM 创建技能"、提供 notebook URL 并要求"提炼成技能"。当用户给出 NotebookLM notebook URL 或笔记本名，并要求创建可复用技能时激活。
---

# NotebookLM 知识蒸馏工作流

## 核心方法论

从 NotebookLM 笔记本提取知识的本质是**强制脱水**：AI 被迫剔除废话，抓住核心概念、因果关系和操作逻辑。

**两种工具分工**：
- **Flashcard**：验证知识密度（厚度），快速扫描有多少可提取考点
- **深度蒸馏（`nlm notebook query`）**：跨来源关联概念，形成结构化输出

---

## 触发条件

### 中文
- "蒸馏" + 笔记本相关词
  - "蒸馏这个笔记本"
  - "把笔记本蒸馏成技能"
  - "把 notebook 内容提取为可复用技能"
  - "把学习资料变成可复用技能"
- "NotebookLM" + 动作词
  - "从 NotebookLM 创建技能"
  - "这个笔记本能做成技能吗"
  - "NotebookLM 笔记本 → 技能"
- 给出 notebook URL 并要求处理

### English
- "distill this notebook into a skill"
- "create skill from notebook"
- "turn notebook into skill"
- "package notebook as skill"
- "NotebookLM → skill"
- "extract skill from NotebookLM"

---

## 快速参考

```bash
# Step 0: 环境检查（含外部依赖检测）
python3 scripts/check_environment.py

# Step 1: 解析 URL 或笔记本名
python3 scripts/parse_notebook_url.py "https://notebooklm.google.com/notebook/..."

# 获取来源数量
nlm source list <notebook_id> -j | grep -c .

# Step 2: Flashcard 扫描（可选）
nlm flashcards create <notebook_id> -y

# Step 3: 深度蒸馏
nlm notebook query <notebook_id> "$(cat prompts/distill_basic.md)"

# 质量差时精简版
nlm notebook query <notebook_id> "$(cat prompts/distill_focused.md)"

# Step 4: 生成测试用例（保存蒸馏结果后）
python3 scripts/generate_test_cases.py <distilled_output>.txt

# Step 5: 结构验证（假设新技能目录已创建）
python3 ~/.claude/skills/skill-creator/scripts/quick_validate.py <skill-dir>/SKILL.md

# 打包
python3 ~/.claude/skills/skill-creator/scripts/package_skill.py <skill-dir>
```

---

## 完整工作流（6 步）

### Step 0: 环境检查

```bash
python3 ~/.claude/skills/notebook-knowledge-distillation/scripts/check_environment.py
```

**检查项**：

| 检查项 | 命令 | 失败处理 |
|--------|------|---------|
| nlm 安装 | `nlm --version` | `pip install notebooklm-cli` |
| nlm 认证 | `nlm auth status` | `nlm auth login` |
| 网络连通 | `nlm notebook list` | 检查网络 |

**nlm 不可用时的 Fallback**：
1. 请求用户导出笔记本为 PDF/Markdown
2. 直接读取本地文件蒸馏
3. 警告：Flashcard/Chat 功能不可用

---

### Step 1: 识别目标 Notebook

**输入**：URL 或笔记本名

**URL 解析**：
```
python3 scripts/parse_notebook_url.py "https://notebooklm.google.com/notebook/2c725daf..."
→ NOTebook ID: 2c725daf-99a6-4ac0-8729-1b0d8860e3f9
→ Title: 看板之魂：智能化时代的人性化重构
→ VALID: True
```

**笔记本名匹配**（无 URL 时）：
```
python3 scripts/parse_notebook_url.py "看板之魂"
→ 唯一匹配或列出候选
```

**来源检查**：

| sources 数量 | 判断 | 行动 |
|-------------|------|------|
| ≥ 5 | 内容充实 | 继续蒸馏 |
| 2-4 | 内容适中 | 可选继续 |
| 1 | 内容单薄 | 警告：建议补充 sources |
| 0 | 空白笔记本 | **终止**：提示先添加 sources |

---

### Step 2: 快速扫描（可选）

```bash
nlm flashcards create <notebook_id> -y
```

**判断标准**：

| Flashcard 数量 | 判断 | 行动 |
|---------------|------|------|
| ≥ 20 张 | 高密度 | 继续深度蒸馏 |
| 10-19 张 | 中等密度 | 可跳过 |
| < 10 张 | 低密度 | 警告：内容可能不够扎实 |
| 0 张或失败 | 内容空洞 | 换 prompt 或终止 |

**跳过条件**：
- sources 仅 1-2 个
- 用户明确要求跳过
- 内容已足够聚焦

---

### Step 3: 深度蒸馏（核心步骤）

**原理**：知识的置信度由**多源交叉验证**决定，而非来源数量直接决定知识点数量。

**分层蒸馏流程**（3 轮迭代）：

```
┌──────────────────────────────────────────────────────┐
│ 第 1 轮：高频共识提取                                  │
│ → "哪些知识点被 ≥2 个独立来源共同支撑？"              │
│ → 标记为 [已验证]，直接进入技能要点                    │
│ → 标记为 [推测] 的内容暂时搁置                        │
├──────────────────────────────────────────────────────┤
│ 第 2 轮：低频验证 & 冲突消解                           │
│ → 剩余 [推测] 知识，逐个追问：                        │
│   "还有哪些来源支持或反驳这个观点？"                  │
│ → 反驳 > 支持 → 降级为 [存疑]，不进入技能            │
│   支持 ≥2 → 升级为 [已验证]                          │
│   支持 = 1，支持者可信 → 保留为 [推测]                │
├──────────────────────────────────────────────────────┤
│ 第 3 轮：知识缺口探测（可选）                          │
│ → "这个领域新手最常踩的坑是什么？"                   │
│ → "有哪些重要概念但来源中未被充分覆盖？"             │
│ → 探测到的缺口标记为 [待补充]，提示用户补充 sources  │
└──────────────────────────────────────────────────────┘
```

**停止规则**（满足任一即停）：
- 第 2 轮结束后，已验证知识点 ≥ 5 个 → 停止
- 连续 2 个 [推测] 被降级为 [存疑] → 停止（边际收益递减）
- 总轮次达到 3 轮（防止无限迭代）

**输出格式**（每条知识带置信度标注）：
```
- **[概念名]** [已验证/推测/存疑]
  - 来源：A, B（≥2来源=已验证）
  - 场景：在 X 情况下，Y 做法是对的
  - 陷阱：Z 做法是错的
```

> **为什么不用"按来源数量决定知识点数"**：3 个来源可能提炼出 15 个高质量已验证知识点，40 个来源也可能只有 8 个真正有价值的共识点。贝叶斯方式让知识密度自己说话。

**基础 Prompt**（`prompts/distill_basic.md`）：
```bash
nlm notebook query <notebook_id> "$(cat prompts/distill_basic.md)"
```

**精简 Prompt**（Fallback，质量差时用 `prompts/distill_focused.md`）：
```bash
nlm notebook query <notebook_id> "$(cat prompts/distill_focused.md)"
```

**超时/失败处理**：

| 失败类型 | 处理 |
|---------|------|
| 输出被截断 | 用截断内容继续，手动标注"未完整" |
| 纯超时 | 缩短 prompt，要求精简输出（1000字内） |
| 格式错误 | 重新请求，明确返回 Markdown |
| 质量差（全是废话） | 换 distill_focused.md 重试 |

---

### Step 4: 生成测试用例

```bash
python3 scripts/generate_test_cases.py /tmp/distilled_output.txt
```

**自动生成**：
- Happy Path 测试：每个核心能力 1 个
- Edge Case 测试：每个核心能力至少 1 个

**数量指导**：

| 技能复杂度 | 测试用例数 |
|-----------|-----------|
| 简单（单一能力） | 5-8 个 |
| 中等（3-5 个能力） | 10-15 个 |
| 复杂（5+ 能力） | 15-25 个 |
| **超过 25 个** | 考虑拆分成多个技能 |

---

### Step 5: 验证与封装

**结构验证**：
```bash
python3 ~/.claude/skills/skill-creator/scripts/quick_validate.py <skill-dir>/SKILL.md
```

**自动评分**（调用 skill-tester）：
```bash
# 完整测试
python3 ~/.claude/skills/skill-tester/scripts/run_tests.py <skill-dir>

# 或手动运行 5 个代表性测试
```

**TIER 判断**：

| TIER | 分数 | 行动 |
|------|------|------|
| **POWERFUL** | ≥ 8.5 | 打包部署 |
| **STANDARD** | 7.0-8.4 | 小幅改进后部署 |
| **BASIC** | 5.0-6.9 | 需要一轮改进循环 |
| **REJECT** | < 5.0 | 重新蒸馏或放弃 |

**打包**：
```bash
python3 ~/.claude/skills/skill-creator/scripts/package_skill.py <skill-dir>
```

---

## 质量保障

### 防止幻觉

每个知识点必须标注来源，区分：
- `[已验证]` — 多个来源一致
- `[推测]` — 单来源，可能有例外
- `[存疑]` — 来源矛盾或未确认

**禁止行为**：
- 没有来源支撑时创造"知识点"
- 把"我认为"写成"知识"
- 省略冲突信息的标注

### 知识型 vs 操作型判断

| 特征 | 知识型 | 操作型 |
|------|--------|--------|
| 来源 | 论文、书籍、博客 | 代码、脚本、配置 |
| 核心内容 | 概念、原理、决策框架 | 命令行、API、工作流 |
| 验证方式 | 测试用例在子 agent | 实际操作验证 |
| Code 评分 | baseline=10（N/A） | 需实测脚本 |

---

## 边界情况处理

| # | 场景 | 识别信号 | 处理 |
|---|------|---------|------|
| 1 | notebook 为空 | sources = 0 | **终止**，提示先添加 sources |
| 2 | 蒸馏结果空洞 | Chat 输出无实质知识点 | 换 distill_focused.md 重试，再失败则终止 |
| 3 | nlm CLI 不可用 | `nlm --version` 失败 | 降级到手动模式（见下方 fallback） |
| 4 | 评分 < 5 | skill-tester 多次 < 5 | 终止，提示重新整理 sources 后再试 |

**nlm 不可用时的最低保障 Fallback**：
1. 请求用户从 NotebookLM 导出笔记本为 PDF/Markdown
2. 直接读取本地文件，在 Claude Code 中手动完成蒸馏
3. 明确告知 Flashcard/Chat 功能不可用

---

## 完整示例

参见：`agentic-ai-design` 技能
- 来源：NotebookLM 笔记本「看板之魂」（38 sources）
- 流程：check_env → parse_url → flashcard → chat → test_cases → skill-tester
- 结果：5/5 测试 PASS，评分 9.25，**POWERFUL**，deployed

---

## 依赖关系

| 工具/技能 | 依赖方式 | 说明 |
|-----------|---------|------|
| `nlm` CLI | 必须 | 核心蒸馏工具 |
| skill-tester | 自动调用 | 蒸馏完成后评分 |
| quick_validate.py | 必须 | 结构验证 |
| package_skill.py | 打包时调用 | 最终部署 |

---

## 输出文件约定

每个步骤输出固定格式的文件名，便于后续步骤串联：

| 步骤 | 输出文件 | 格式 | 用途 |
|------|---------|------|------|
| Step 1 | `/tmp/nlm_notebook_info.json` | JSON | 保存 notebook_id + 标题，供后续步骤引用 |
| Step 2 | `/tmp/nlm_flashcards.md` | Markdown | Flashcard 扫描结果，存根备查 |
| Step 3 | `/tmp/distilled_output.txt` | Plain Text | 深度蒸馏原始输出 |
| Step 3 | `<skill-dir>/SKILL.md` | Markdown | 格式化后的技能定义 |
| Step 4 | `/tmp/test_cases.md` | Markdown | 生成的测试用例表 |

**自动化提示**：在 Step 1 完成后，将 notebook_id 保存到 `/tmp/nlm_notebook_info.json`，后续所有步骤从该文件读取，避免重复解析 URL。

---

## AI-用户交互协议

规范蒸馏流程中每个步骤向用户报告的内容，保持体验一致性：

### 步骤间报告规范

| 步骤 | 报告时机 | 报告内容 | 格式示例 |
|------|---------|---------|---------|
| Step 0 | 检查后 | 5 项检查结果 + 笔记本数量 | `[1/5] nlm 安装: ✓` |
| Step 1 | 解析后 | notebook_id、标题、来源数量、密度判断 | `📚 38 sources → 高密度，建议蒸馏` |
| Step 2 | 扫描后 | Flashcard 数量、密度判断、操作建议 | `📝 25 张闪卡 → 高密度，继续` |
| Step 3 | 执行后 | 输出长度、知识点数量、质量判断 | `📦 提炼出 9 个核心能力` |
| Step 4 | 生成后 | 能力数、测试用例数（HP + EC） | `✅ 生成 18 个测试用例（9 HP + 9 EC）` |
| Step 5 | 评分后 | TIER 等级、总分、4D 各维度分数 | `🏆 TIER: POWERFUL (9.25)` |

### 用户确认节点

在以下节点**必须等待用户确认**再继续：
1. **Step 1 之后**：来源数量过少（< 5）或空白笔记本，提示风险
2. **Step 3 之后**：蒸馏结果质量差，提示换 prompt 或终止
3. **Step 5 之后**：TIER < 7.0，询问是否改进或终止

### 终止条件（自动终止，不等待确认）
- sources = 0（空白笔记本）
- skill-tester 评分连续 2 次 < 5.0
- nlm CLI 完全不可用且无本地文件 fallback

---

## 来源

本技能封装自 Claude Code × NotebookLM × skill-tester 联合工作流实战经验（2026-04）。
