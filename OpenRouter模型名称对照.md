# OpenRouter 正确的模型名称

## ❌ 您的错误

**错误配置**:
```bash
OPENAI_MODEL=google/gemini-pro-1.5
```

**错误信息**: `No end points found for google/gemini-pro-1.5`

**原因**: OpenRouter上没有这个模型名称！

---

## ✅ 正确的Gemini模型名称（2026年最新）

### 推荐模型

| 模型名称 | 特点 | 上下文 | 价格 |
|---------|------|--------|------|
| **google/gemini-2.5-flash** | **最推荐！快速便宜** | 1M | 超低 |
| **google/gemini-2.5-pro** | 高级推理、数学 | 1M | 低 |
| google/gemini-3-flash-preview | 最新实验版 | 1M | 可能免费 |
| google/gemini-2.0-flash | 稳定版 | 1M | 超低 |

### OpenAI模型（稳定推荐）

| 模型名称 | 特点 | 上下文 | 价格 |
|---------|------|--------|------|
| **openai/gpt-4o-mini** | **性价比最高** | 128k | $0.15/$0.60 |
| openai/gpt-4o | 质量更好 | 128k | $2.5/$10 |
| openai/gpt-4-turbo | 快速 | 128k | $10/$30 |

### Claude模型（大上下文）

| 模型名称 | 特点 | 上下文 | 价格 |
|---------|------|--------|------|
| **anthropic/claude-sonnet-4** | **平衡推荐** | 200k | $3/$15 |
| anthropic/claude-opus-4 | 最高质量 | 200k | $15/$75 |

---

## 🔧 修正配置

### 方案1: 使用Gemini 2.5 Flash（推荐）

```bash
# .env 文件修改
OPENAI_MODEL=google/gemini-2.5-flash

# 其他保持不变
COMPRESSION_RATIO=1
MAX_INPUT_TOKENS=1000000  # Gemini支持1M
```

### 方案2: 使用GPT-4o-mini（稳定）

```bash
# .env 文件修改
OPENAI_MODEL=openai/gpt-4o-mini

# 其他配置
COMPRESSION_RATIO=0.6      # 推荐压缩
MAX_INPUT_TOKENS=80000     # GPT限制
```

### 方案3: 使用Claude Sonnet 4（大上下文）

```bash
# .env 文件修改
OPENAI_MODEL=anthropic/claude-sonnet-4

# 其他配置
COMPRESSION_RATIO=1.0      # 不压缩
MAX_INPUT_TOKENS=180000    # Claude限制
```

---

## 🎯 快速修复

### 立即修改 .env 文件

**选择一个正确的模型名称**：

```bash
# 最推荐：Gemini 2.5 Flash（快速、便宜、大上下文）
OPENAI_MODEL=google/gemini-2.5-flash

# 或者：GPT-4o-mini（稳定、便宜）
OPENAI_MODEL=openai/gpt-4o-mini

# 或者：Claude Sonnet 4（质量高、大上下文）
OPENAI_MODEL=anthropic/claude-sonnet-4
```

**然后重启服务**:
```bash
streamlit run app.py
```

---

## 📋 推荐配置组合

### 组合1: Gemini 2.5 Flash（最推荐）

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-or-v1-xxxxx
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=google/gemini-2.5-flash
COMPRESSION_RATIO=1.0
MAX_INPUT_TOKENS=1000000
```

**优势**:
- ✅ 1M上下文（超大）
- ✅ 超便宜或免费
- ✅ 速度快
- ✅ 不需要压缩

---

### 组合2: GPT-4o-mini（稳定）

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-or-v1-xxxxx
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini
COMPRESSION_RATIO=0.6
MAX_INPUT_TOKENS=80000
```

**优势**:
- ✅ 稳定可靠
- ✅ 价格便宜
- ⚠️ 上下文较小（需要压缩）

---

### 组合3: Claude Sonnet 4（质量优先）

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-or-v1-xxxxx
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=anthropic/claude-sonnet-4
COMPRESSION_RATIO=1.0
MAX_INPUT_TOKENS=180000
```

**优势**:
- ✅ 分析质量最高
- ✅ 200k上下文
- ⚠️ 价格相对高

---

## 🚀 立即操作

```bash
# 1. 编辑 .env 文件，修改模型名称为正确的名称
OPENAI_MODEL=google/gemini-2.5-flash

# 2. 保存文件

# 3. 重启服务
streamlit run app.py

# 4. 应该能正常工作了
```

**请选择一个正确的模型名称，修改.env后重启服务！**