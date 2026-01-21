# OpenAI GPT-4o 配置指南

## 🎯 您的需求

**目标**: 避免调用PyCharm环境变量里的Claude模型（贵），改用.env里的OpenAI GPT-4o解析标书

---

## ✅ 解决方案

### 配置优先级

```
PyCharm环境变量（ANTHROPIC_API_KEY） → Claude模型
    ↓ （不影响）
.env文件（AI_PROVIDER=openai） → OpenAI模型 ✅
```

**关键**：现在系统支持**独立配置AI Provider**！

---

## 🔧 配置步骤

### 步骤1: 创建 .env 文件

```bash
# 如果没有.env文件
cp .env.example .env
```

### 步骤2: 编辑 .env 文件

```bash
# ============ AI模型配置 ============

# 选择AI Provider（使用OpenAI）
AI_PROVIDER=openai

# OpenAI API密钥
OPENAI_API_KEY=sk-proj-xxxxx  # 您的OpenAI API key

# OpenAI 模型选择（推荐gpt-4o）
OPENAI_MODEL=gpt-4o

# ============ 保持Claude配置为空或注释 ============
# ANTHROPIC_API_KEY=  # 留空，不使用Claude
# ANTHROPIC_MODEL=     # 留空
```

### 步骤3: 安装OpenAI依赖

```bash
pip install openai>=1.0.0
```

### 步骤4: 重启服务

```bash
# Ctrl+C 停止
streamlit run app.py

# 启动时会显示：
[AI Provider] 使用OpenAI - 模型: gpt-4o  ← 确认使用OpenAI
```

---

## 📊 配置验证

### 检查是否生效

启动服务后，命令行应该显示：

```
[AI Provider] 使用OpenAI - 模型: gpt-4o
```

**如果显示**：
- ✅ `OpenAI - gpt-4o` → 配置成功
- ❌ `Claude - claude-opus-4` → 配置失败，检查.env

---

## 🔄 两种模式对比

### 模式1: PyCharm Claude（旧）

```
PyCharm Environment Variables:
ANTHROPIC_API_KEY=sk-ant-xxx  # Claude API

运行方式：
在PyCharm中点击运行

使用模型：
Claude Opus/Sonnet（PyCharm配置）

成本：
$0.62-$3.15/次
```

### 模式2: .env OpenAI（新，推荐）

```
.env 文件：
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxx  # OpenAI API

运行方式：
streamlit run app.py

使用模型：
OpenAI GPT-4o（.env配置）

成本：
~$0.15-$0.30/次（比Claude便宜！）
```

---

## 💰 成本对比

### 单次标书分析（200页PDF）

| 模型 | Input价格 | Output价格 | 总成本 |
|-----|----------|-----------|--------|
| **GPT-4o** | $0. | $0.30 | **~$0.45** ✅ |
| Claude Sonnet 4 | $0.24 | $0.38 | ~$0.62 |
| Claude Opus 4 | $1.20 | $1.95 | ~$3.15 |

**结论**: GPT-4o比Claude Sonnet便宜25%，比Opus便宜85%！

---

## 🎯 模型质量对比

### 标书分析能力

| 任务 | GPT-4o | Claude Sonnet 4 | Claude Opus 4 |
|-----|--------|----------------|---------------|
| 结构化解析 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 风险识别 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 中文理解 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 生成质量 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 速度 | ⚡⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡ |
| **性价比** | **⭐⭐⭐⭐⭐** | ⭐⭐⭐⭐ | ⭐⭐ |

**建议**：
- 日常使用：**GPT-4o**（快速、便宜、质量好）
- 重要项目：Claude Opus 4（质量最高，但贵）

---

## 🔧 完整的 .env 配置

### 推荐配置（OpenAI GPT-4o）

```bash
# ============ AI模型配置 ============

# 使用OpenAI（推荐）
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o

# Claude配置留空（不使用）
# ANTHROPIC_API_KEY=
# ANTHROPIC_MODEL=

# ============ 其他配置 ============
MAX_FILE_SIZE_MB=50
UPLOAD_FOLDER=uploads
DATABASE_PATH=data/bidding_system.db
```

### 备选配置（更便宜的GPT-3.5）

```bash
# 仅供测试使用
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-3.5-turbo  # 便宜10倍，但质量稍差
```

---

## 🎓 API Key获取

### OpenAI API Key

1. 访问：https://platform.openai.com/
2. 注册/登录账户
3. 进入：API Keys
4. 点击"Create new secret key"
5. 复制key（格式：sk-proj-xxxxxx）
6. 粘贴到.env文件

### 国内用户注意

如果OpenAI API无法访问，可以使用：

#### 选项1: API代理服务

```bash
# .env 配置
AI_PROVIDER=openai
OPENAI_API_KEY=your_proxy_key
OPENAI_BASE_URL=https://your-proxy-service.com/v1
OPENAI_MODEL=gpt-4o
```

#### 选项2: OpenRouter（支持多种模型）

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-or-xxxxx  # OpenRouter key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o
```

---

## 🧪 测试验证

### 测试步骤

1. **配置.env**
   ```bash
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-xxxxx
   OPENAI_MODEL=gpt-4o
   ```

2. **重启服务**
   ```bash
   streamlit run app.py
   ```

3. **查看日志**
   ```
   应该显示：
   [AI Provider] 使用OpenAI - 模型: gpt-4o
   ```

4. **上传标书并分析**
   ```
   - 上传文件
   - 点击"开始结构化解析"
   - 观察是否能正常分析
   ```

5. **检查成本**
   ```
   在OpenAI控制台查看API usage
   应该是 $0.3-0.5/次（而非Claude的几美元）
   ```

---

## ⚠️ 常见问题

### Q1: OpenAI API 报错 401 Unauthorized

**原因**: API Key错误或过期

**解决**:
1. 检查.env中的OPENAI_API_KEY是否正确
2. 确认key格式：sk-proj-xxx（新格式）或 sk-xxx（旧格式）
3. 检查OpenAI账户是否有余额

### Q2: 分析质量下降

**原因**: GPT-4o与Claude的输出风格不同

**解决**:
- 保持使用GPT-4o（质量已足够）
- 如果需要更高质量，切换回Claude Sonnet

### Q3: 速度变慢

**原因**: OpenAI在国内可能有网络延迟

**解决**:
- 使用API代理
- 或切换回Claude（网络更稳定）

---

## 🎯 最终配置建议

### 日常开发/测试

```bash
# .env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL=gpt-4o
```

**优势**：
- ✅ 避免PyCharm Claude配置干扰
- ✅ 成本低
- ✅ 速度快
- ✅ 质量足够

### 重要项目

**临时修改 .env**：
```bash
# 切换到Claude Opus
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-opus-4-20250514
```

**用完后改回OpenAI**，避免长期使用昂贵模型。

---

## 📋 配置文件示例

### 完整的 .env 文件

```bash
# ============ AI模型配置（标书解析用） ============

# 使用OpenAI（避免与PyCharm Claude冲突）
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o

# ============ 其他配置 ============
MAX_FILE_SIZE_MB=50
UPLOAD_FOLDER=uploads
DATABASE_PATH=data/bidding_system.db
```

### PyCharm环境变量（保持不变）

```
# PyCharm仍然可以配置Claude（用于其他项目）
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-opus-4-20250514

# 不会影响本项目（因为本项目读取AI_PROVIDER=openai）
```

---

**配置完成后，重启服务即可！** 🎉

系统会自动使用OpenAI GPT-4o，不会再调用PyCharm的Claude配置。
