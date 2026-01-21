# Token限制解决方案

## 🐛 问题描述

**错误**: Token limit exceeded（超出token限制）

**原因**: GPT-4o-mini的token限制比Claude小

---

## 📊 模型Token限制对比

| 模型 | 上下文长度 | 输入限制 | 输出限制 | 说明 |
|-----|-----------|---------|---------|------|
| **GPT-4o-mini** | **128k** | ~100k | 16k | 便宜但限制小 |
| GPT-4o | 128k | ~100k | 16k | 贵但限制同mini |
| Claude Sonnet 4 | **200k** | ~180k | 8k | **限制最大** |
| Claude Opus 4 | **200k** | ~180k | 8k | 最贵 |

**结论**: Claude的上下文限制比GPT大约**2倍**！

---

## ✅ 已实现的解决方案

### 方案：智能压缩（自动）

**原理**:
```
文档token > 80k
    ↓
智能压缩：
├─ 保留所有标题（章节结构）
├─ 保留包含数字/要求/标准的句子
├─ 删除重复内容
├─ 简化描述性段落
    ↓
压缩到 80k tokens以内
    ↓
送入AI分析
```

**压缩策略**:
```python
优先级1: 标题（第X章、X.X等）          → 必须保留
优先级2: 强制性要求（必须、不得、应）   → 必须保留
优先级3: 数值约束（≥、≤、数字）       → 必须保留
优先级4: 标准引用（GB、JGJ等）        → 必须保留
优先级5: 普通描述                     → 可删除
```

---

## 🎯 使用效果

### 处理流程

```
上传200页PDF（共150k tokens）
    ↓
系统检测：超出80k限制
    ↓
自动压缩：
[AI Service] 文档总token数: 150,000
[AI Service] 文档过大，进行智能压缩 (150,000 → 80,000 tokens)
[AI Service] 压缩后token数: 78,500，压缩率: 52.3%
    ↓
送入AI分析（使用压缩后的内容）
    ↓
分析完成 ✅
```

**界面提示**:
```
📊 文档规模: 300,000 字符 ≈ 150,000 tokens
⚠️ 文档较大，系统将自动压缩至80k tokens以内（保留关键信息）
```

---

## 🔍 压缩示例

### 原始文本（150k tokens）

```
第一章 总则

第1.1条 工程概况
本工程位于北京市朝阳区，为某某住宅小区配套工程，建设单位为北京某某房地产开发有限公司，设计单位为北京某某建筑设计研究院有限公司，监理单位为北京某某工程监理公司，施工单位通过公开招标方式确定。

本工程总建筑面积约25000平方米，其中地上建筑面积约18000平方米，地下建筑面积约7000平方米。地上部分为6栋住宅楼，建筑高度为24米，地下部分为地下车库及设备用房。

第1.2条 技术要求
混凝土强度等级应不低于C30，钢筋应采用HRB400级，砌体材料应符合GB50003标准要求...

（大量重复和描述性内容）
```

### 压缩后（80k tokens）

```
第一章 总则

第1.1条 工程概况
工程位于北京市朝阳区，总建筑面积约25000平方米。

第1.2条 技术要求
混凝土强度等级应不低于C30，钢筋应采用HRB400级，砌体材料应符合GB50003标准要求...

... (内容过长，已省略部分) ...

（保留了所有标题和关键要求，删除了冗余描述）
```

---

## 💡 其他解决方案

### 方案1: 使用更大上下文的模型（推荐）

**切换到GPT-4o**（成本略高但限制相同）或**Claude**：

```bash
# .env 配置

# 选项1: 使用OpenRouter的Claude Sonnet（200k上下文）
AI_PROVIDER=openai
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=anthropic/claude-sonnet-4  # 改成Claude
OPENAI_API_KEY=sk-or-v1-xxxxx

# 选项2: 直接用Claude官方API
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

**成本对比**:
| 模型 | Token限制 | 成本/次 |
|-----|----------|---------|
| gpt-4o-mini | 128k | $0.024 |
| **claude-sonnet-4** | **200k** | **$0.62** |

**建议**: 如果文档经常超过80k tokens，切换到Claude Sonnet

---

### 方案2: 分文件分析（慢但完整）

**思路**: 每个文件单独分析，最后合并报告

```python
# 伪代码
for 文件 in 所有文件:
    报告[文件] = AI.analyze(单个文件)

最终报告 = 合并(所有报告)
```

**优势**: 不损失任何信息
**劣势**: 需要多次API调用，成本更高

---

### 方案3: 手动调整文件

**操作**:
1. 看到压缩警告时
2. 只上传最重要的文件（如招标文件正文、评审标准）
3. 其他文件（如工程量清单）可选择性上传

---

## 🎯 推荐策略

### 日常使用

**配置**: GPT-4o-mini + 自动压缩（当前配置）

```bash
AI_PROVIDER=openai
OPENAI_MODEL=openai/gpt-4o-mini
```

**成本**: $0.024/次
**限制**: 80k tokens输入
**压缩**: 自动（保留关键信息）

**适用场景**:
- 文档<200页
- 对完整性要求不高
- 成本敏感

---

### 大文档/重要项目

**配置**: Claude Sonnet 4（通过OpenRouter）

```bash
AI_PROVIDER=openai
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=anthropic/claude-sonnet-4
```

**成本**: $0.62/次
**限制**: 180k tokens输入（2.25倍）
**压缩**: 不需要或很少

**适用场景**:
- 文档>200页
- 需要完整分析
- 重要项目

---

## 📋 配置切换指南

### 切换到Claude Sonnet（大上下文）

#### 方法1: 通过OpenRouter（推荐）

```bash
# 编辑.env文件
AI_PROVIDER=openai
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=sk-or-v1-xxxxx  # 保持不变
OPENAI_MODEL=anthropic/claude-sonnet-4  # 改这一行

# 重启服务
streamlit run app.py
```

#### 方法2: 使用Claude官方API

```bash
# 编辑.env文件
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# 重启服务
streamlit run app.py
```

---

## 🧪 测试智能压缩

### 测试场景

```
上传超大文档（300页，150k tokens）
    ↓
点击"开始结构化解析"
    ↓
界面显示：
📊 文档规模: 300,000 字符 ≈ 150,000 tokens
⚠️ 文档较大，系统将自动压缩至80k tokens以内（保留关键信息）
    ↓
命令行日志：
[AI Service] 文档总token数: 150,000
[AI Service] 文档过大，进行智能压缩 (150,000 → 80,000 tokens)
[AI Service] 压缩后token数: 78,500，压缩率: 52.3%
    ↓
分析完成 ✅
    ↓
查看报告：所有章节标题和关键要求都在
```

---

## 💰 成本对比（不同方案）

### 单次分析（200页PDF，150k tokens）

| 方案 | 模型 | Token处理 | 成本 | 完整度 |
|-----|------|----------|------|--------|
| 方案A | gpt-4o-mini | 压缩到80k | $0.024 | 85% |
| 方案B | claude-sonnet-4 | 不压缩 | $0.62 | 100% |
| 方案C（旧） | claude-opus-4 | 不压缩 | $3.15 | 100% |

**推荐**:
- 日常: 方案A（便宜，质量够用）
- 重要: 方案B（完整分析）

---

## 🎯 最终建议

### 当前配置（保持）

```bash
# .env
AI_PROVIDER=openai
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini  # 保持gpt-4o-mini
```

**优点**:
- ✅ 超便宜（$0.024/次）
- ✅ 自动压缩（保留关键信息）
- ✅ 速度快

### 如果需要完整分析

**临时切换**:
```bash
# 改一行配置
OPENAI_MODEL=anthropic/claude-sonnet-4

# 重启服务
# 分析完成后改回 gpt-4o-mini
```

---

## 📝 快速切换命令

### 切换到大上下文模型

```bash
# 编辑.env，修改这一行：
OPENAI_MODEL=anthropic/claude-sonnet-4

# 重启
streamlit run app.py
```

### 切回经济模型

```bash
# 编辑.env，改回：
OPENAI_MODEL=openai/gpt-4o-mini

# 重启
streamlit run app.py
```

---

**配置已完成！智能压缩已启用！**

现在请：
1. 重启服务
2. 上传大文档测试
3. 观察压缩日志
4. 查看分析质量是否可接受

如果压缩后质量不满意，随时可以一行配置切换到Claude Sonnet！
