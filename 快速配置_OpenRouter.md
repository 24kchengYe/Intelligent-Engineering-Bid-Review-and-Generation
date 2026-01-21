# OpenRouter + GPT-4o-mini 快速配置

## 🎯 您的配置

**平台**: OpenRouter (https://openrouter.ai)
**模型**: openai/gpt-4o-mini

---

## ✅ 完整配置步骤

### 步骤1: 创建 .env 文件

```bash
# 在项目根目录创建.env文件，内容如下：

# ============ AI模型配置 ============

# 使用OpenAI Provider（通过OpenRouter平台）
AI_PROVIDER=openai

# OpenRouter API密钥（从 https://openrouter.ai 获取）
OPENAI_API_KEY=sk-or-v1-your-key-here

# OpenRouter API端点
OPENAI_BASE_URL=https://openrouter.ai/api/v1

# 模型选择（OpenRouter格式）
OPENAI_MODEL=openai/gpt-4o-mini

# ============ 其他配置 ============
MAX_FILE_SIZE_MB=50
UPLOAD_FOLDER=uploads
DATABASE_PATH=data/bidding_system.db
```

### 步骤2: 替换您的API Key

将 `OPENAI_API_KEY=sk-or-v1-your-key-here` 替换为您实际的OpenRouter API key。

### 步骤3: 安装依赖

```bash
pip install openai>=1.0.0
```

### 步骤4: 重启服务

```bash
# Ctrl+C 停止当前服务
streamlit run app.py

# 查看日志确认：
[AI Provider] 使用OpenAI - 模型: openai/gpt-4o-mini
[AI Provider] API端点: https://openrouter.ai/api/v1
```

---

## 🔍 配置验证

### 检查配置是否生效

启动后应该看到：

```
[AI Provider] 使用OpenAI - 模型: openai/gpt-4o-mini  ✅
[AI Provider] API端点: https://openrouter.ai/api/v1  ✅
```

**如果看到**：
- ✅ `openai/gpt-4o-mini` + `openrouter.ai` → 配置成功
- ❌ `claude-opus-4` → .env配置未生效，检查文件

---

## 💰 成本优势

### GPT-4o-mini 价格（OpenRouter）

| 项目 | 价格 |
|-----|------|
| Input | $0.15/1M tokens |
| Output | $0.60/1M tokens |

### 单次分析成本（200页PDF）

```
输入：~80k tokens = $0.012
输出：~20k tokens = $0.012
总计：~$0.024/次

对比：
- PyCharm Claude Opus: $3.15/次
- 节省：99%！
```

### 月度成本（50次分析）

```
GPT-4o-mini: $1.2/月  ✅
Claude Opus: $158/月

节省：$156.8/月（99%）
```

---

## 📝 配置文件示例

### .env 文件（完整版）

```bash
# ============ AI模型配置 ============

# 使用OpenRouter调用GPT-4o-mini
AI_PROVIDER=openai
OPENAI_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini

# ============ 其他配置 ============
MAX_FILE_SIZE_MB=50
UPLOAD_FOLDER=uploads
DATABASE_PATH=data/bidding_system.db
```

---

## 🎯 关键确认

### Q1: PyCharm的Claude配置会被调用吗？

**答：不会！** ✅

```
系统读取优先级：
.env 文件的 AI_PROVIDER=openai
    ↓
只读取 OPENAI_API_KEY 和 OPENAI_MODEL
    ↓
完全忽略 PyCharm 的 ANTHROPIC_* 配置

结果：
[AI Provider] 使用OpenAI - 模型: openai/gpt-4o-mini
（不会调用PyCharm的Claude Opus）
```

### Q2: 所有AI调用都用这个配置吗？

**答：是的！** ✅

```
标书分析 → 用 openai/gpt-4o-mini
评审标准提取 → 用 openai/gpt-4o-mini
技术标生成 → 用 openai/gpt-4o-mini

全部通过 OpenRouter 调用
```

### Q3: 数据转换也调用AI吗？

**答：不会！** ✅

```
DocumentParser（文档解析）：
❌ 不调用任何AI
✅ 纯本地处理（PyMuPDF + OCR）
✅ 不消耗API费用
```

---

## 🧪 测试清单

### 配置后测试

```
□ 创建.env文件
□ 填写OpenRouter API key
□ 设置URL和MODEL
□ 重启服务
□ 查看日志确认模型
□ 上传标书文件
□ 点击"开始结构化解析"
□ 查看分析结果
□ 在OpenRouter后台查看API调用记录
□ 确认成本（应该只有几分钱）
```

---

## 🎉 配置完成

**您的最终配置**：
```
平台：OpenRouter
模型：openai/gpt-4o-mini
成本：$0.024/次分析
节省：99%（vs PyCharm Opus）
```

**现在可以**：
1. 停止服务（Ctrl+C）
2. 创建/编辑.env文件
3. 填写您的OpenRouter API key
4. 重启服务
5. 测试分析功能

**所有AI调用都会使用OpenRouter的gpt-4o-mini，完全避免PyCharm的Claude配置！** ✅
