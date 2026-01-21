# OpenRouter + GPT-4o-mini 配置指南

## 🎯 您的配置需求

**使用平台**: OpenRouter (https://openrouter.ai)
**调用模型**: OpenAI GPT-4o-mini
**目的**: 避免调用PyCharm环境变量里的Claude模型

---

## ✅ 完整配置

### .env 文件配置

```bash
# ============ AI模型配置 ============

# 使用OpenAI Provider
AI_PROVIDER=openai

# OpenRouter API密钥（从 https://openrouter.ai 获取）
OPENAI_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxx

# OpenRouter API端点
OPENAI_BASE_URL=https://openrouter.ai/api/v1

# OpenRouter模型选择（注意格式：提供商/模型名）
OPENAI_MODEL=openai/gpt-4o-mini

# ============ 其他配置 ============
MAX_FILE_SIZE_MB=50
UPLOAD_FOLDER=uploads
DATABASE_PATH=data/bidding_system.db
```

---

## 🔑 获取OpenRouter API Key

### 步骤

1. **访问**: https://openrouter.ai
2. **注册/登录**账户
3. **进入**: Keys → Create Key
4. **复制**: sk-or-v1-xxxxx
5. **粘贴**到.env文件的 `OPENAI_API_KEY`

### 充值（可选）

- OpenRouter支持按需付费
- 建议先充值$5-10测试
- Credits余额在网站可查看

---

## 📊 OpenRouter模型选择

### 推荐：openai/gpt-4o-mini ⭐⭐⭐⭐⭐

| 特性 | 参数 |
|-----|------|
| **Input价格** | **$0.15/1M tokens** |
| **Output价格** | **$0.60/1M tokens** |
| 质量 | ⭐⭐⭐⭐（足够标书分析） |
| 速度 | ⚡⚡⚡⚡（很快） |
| 上下文 | 128k tokens |

**单次分析成本**：约$0.08-0.15（**比Claude便宜90%！**）

---

### 备选模型对比

| 模型 | Input价格 | Output价格 | 适用场景 |
|-----|----------|-----------|---------|
| **openai/gpt-4o-mini** | **$0.15** | **$0.60** | **日常使用（推荐）** |
| openai/gpt-4o | $2.5 | $10 | 需要更高质量 |
| openai/gpt-4-turbo | $10 | $30 | 复杂分析 |
| anthropic/claude-sonnet-4 | $3 | $15 | Claude风格输出 |
| anthropic/claude-opus-4 | $15 | $75 | 最高质量 |

---

## 🔧 配置验证

### 启动服务后查看日志

```bash
streamlit run app.py

# 应该看到：
[AI Provider] 使用OpenAI - 模型: openai/gpt-4o-mini
[AI Provider] API端点: https://openrouter.ai/api/v1
```

**如果显示这个** → ✅ 配置成功！

**如果显示Claude** → ❌ 检查.env的AI_PROVIDER是否为openai

---

## 💰 成本对比

### 单次标书分析（200页PDF，约10万tokens）

| 方案 | 模型 | 成本 |
|-----|------|------|
| PyCharm Claude | claude-opus-4 | **$3.15** 💸 |
| .env Claude | claude-sonnet-4 | $0.62 |
| **OpenRouter + GPT-4o-mini** | **openai/gpt-4o-mini** | **$0.12** ✅ |

**节省**：
- vs PyCharm Opus: 节省**96%**！
- vs Claude Sonnet: 节省**80%**！

### 月度成本（50次分析）

| 方案 | 月成本 |
|-----|--------|
| PyCharm Opus | $158 |
| Claude Sonnet | $31 |
| **OpenRouter GPT-4o-mini** | **$6** ✅ |

---

## 🎯 为什么选择OpenRouter？

### 优势

1. **统一平台**：
   - 一个API key访问多种模型
   - OpenAI、Claude、Gemini等都支持

2. **价格优势**：
   - 比官方API更便宜（批量采购）
   - GPT-4o-mini特别便宜

3. **国内访问友好**：
   - 比OpenAI官方API更稳定
   - 无需特殊网络配置

4. **灵活切换**：
   ```bash
   # 改一行配置就能切换模型
   OPENAI_MODEL=openai/gpt-4o-mini      # 便宜
   # OPENAI_MODEL=openai/gpt-4o         # 更强
   # OPENAI_MODEL=anthropic/claude-sonnet-4  # Claude
   ```

---

## 📋 完整的.env配置

### 推荐配置（OpenRouter + GPT-4o-mini）

```bash
# ============ AI模型配置 ============

# 使用OpenAI Provider（通过OpenRouter平台）
AI_PROVIDER=openai

# OpenRouter API密钥（从 https://openrouter.ai 获取）
OPENAI_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxx

# OpenRouter API端点（固定地址）
OPENAI_BASE_URL=https://openrouter.ai/api/v1

# 模型选择（OpenRouter格式：提供商/模型名）
OPENAI_MODEL=openai/gpt-4o-mini

# ============ 其他配置 ============
MAX_FILE_SIZE_MB=50
UPLOAD_FOLDER=uploads
DATABASE_PATH=data/bidding_system.db
```

---

## 🔄 模型切换示例

### 场景1: 日常使用（最便宜）

```bash
OPENAI_MODEL=openai/gpt-4o-mini
成本：$0.12/次
```

### 场景2: 需要更好质量

```bash
OPENAI_MODEL=openai/gpt-4o
成本：$0.30/次
```

### 场景3: 需要使用Claude

```bash
OPENAI_MODEL=anthropic/claude-sonnet-4
成本：$0.62/次
```

**注意**: 所有模型都通过OpenRouter调用，只需改一行配置！

---

## 🧪 测试验证

### 测试步骤

1. **配置.env**
   ```bash
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-or-v1-xxxxx
   OPENAI_BASE_URL=https://openrouter.ai/api/v1
   OPENAI_MODEL=openai/gpt-4o-mini
   ```

2. **重启服务**
   ```bash
   streamlit run app.py
   ```

3. **查看日志**
   ```
   [AI Provider] 使用OpenAI - 模型: openai/gpt-4o-mini
   [AI Provider] API端点: https://openrouter.ai/api/v1
   ```

4. **上传标书测试**
   - 上传文件
   - 点击"开始结构化解析"
   - 查看分析结果质量

5. **检查成本**
   - 访问 https://openrouter.ai/activity
   - 查看API usage和费用

---

## 💡 OpenRouter特殊功能

### 1. 模型降级（Fallback）

如果某个模型不可用，OpenRouter会自动切换到备选模型。

### 2. 模型路由

OpenRouter会自动选择最快的API端点。

### 3. 成本优化

批量采购，价格比官方便宜。

---

## ⚠️ 常见问题

### Q1: OpenRouter API Key格式？

**格式**: `sk-or-v1-xxxxxxxxx`

**获取**: https://openrouter.ai/keys

### Q2: 模型名称必须是 openai/gpt-4o-mini 吗？

**是的！** OpenRouter的模型格式是：`提供商/模型名`

**正确格式**:
- ✅ `openai/gpt-4o-mini`
- ✅ `openai/gpt-4o`
- ✅ `anthropic/claude-sonnet-4`

**错误格式**:
- ❌ `gpt-4o-mini`（缺少提供商前缀）
- ❌ `GPT-4o-mini`（大小写错误）

### Q3: 如何查看OpenRouter支持的模型？

访问：https://openrouter.ai/models

**热门模型**:
- openai/gpt-4o-mini ($0.15/$0.60)
- openai/gpt-4o ($2.5/$10)
- anthropic/claude-sonnet-4 ($3/$15)
- google/gemini-pro-1.5 (免费)

---

## 🎯 总结

### 您的最终配置

```bash
# .env 文件
AI_PROVIDER=openai
OPENAI_API_KEY=sk-or-v1-xxxxx        # OpenRouter key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini      # OpenRouter格式
```

### 优势

✅ **避免PyCharm Claude干扰**（完全独立）
✅ **成本最低**（$0.12/次，比Opus便宜96%）
✅ **速度快**（GPT-4o-mini很快）
✅ **质量足够**（标书分析完全够用）
✅ **国内访问友好**（OpenRouter稳定性好）

---

## 📝 完整配置示例

### .env 文件（复制即用）

```bash
# ============ AI模型配置 ============

# 使用OpenRouter平台调用GPT-4o-mini
AI_PROVIDER=openai
OPENAI_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini

# ============ 其他配置 ============
MAX_FILE_SIZE_MB=50
UPLOAD_FOLDER=uploads
DATABASE_PATH=data/bidding_system.db
```

### PyCharm环境变量（保持不变）

```
# PyCharm全局配置（不会被调用）
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-opus-4

# 本项目会忽略这些配置，使用.env的OpenRouter
```

---

## 🚀 立即开始

```bash
# 1. 编辑.env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-or-v1-xxxxx
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini

# 2. 重启服务
streamlit run app.py

# 3. 验证日志
[AI Provider] 使用OpenAI - 模型: openai/gpt-4o-mini
[AI Provider] API端点: https://openrouter.ai/api/v1

# 4. 测试分析
上传标书 → 分析 → 检查质量和成本

完成！✅
```

---

**成本节省：96%！从$3.15降到$0.12！** 🎉
