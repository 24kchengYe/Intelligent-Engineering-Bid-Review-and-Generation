# 智能标书审查系统

一个基于 Streamlit 和 Claude AI 的工程类标书自动审查系统，支持文件上传、智能解析和投标文件生成。

## 功能特性

- 支持多种文件格式上传（PDF、Word、Excel）
- 使用 Claude AI 智能解析标书内容
- 自动生成标书审查报告
- 智能生成投标文件
- 历史记录管理

## 技术栈

- **应用框架**: Streamlit
- **AI模型**: Anthropic Claude API
- **文档处理**: PyMuPDF, python-docx, openpyxl
- **数据库**: SQLite

## 安装说明

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env` 并填入你的 Claude API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
ANTHROPIC_API_KEY=your_actual_api_key
```

### 3. 运行系统

```bash
streamlit run app.py

系统将在浏览器中自动打开，默认地址：http://localhost:8501

## 使用指南

### 上传标书文件

1. 选择文件类型（PDF规范、Word方案、Excel清单等）
2. 上传对应文件（可选，非必填）
3. 点击"开始解析"

### 查看解析报告

系统会自动调用 Claude AI 分析标书内容，生成详细的审查报告，包括：
- 标书要求总结
- 关键条款提取
- 风险点识别
- 合规性检查

### 生成投标文件

基于解析结果，系统可以协助生成：
- 技术方案
- 商务应答
- 其他投标材料

## 项目结构

```
.
├── app.py                 # Streamlit 主应用
├── modules/
│   ├── document_parser.py # 文档解析模块
│   ├── ai_service.py      # Claude API 服务
│   ├── database.py        # 数据库操作
│   └── report_generator.py # 报告生成
├── data/                  # 数据库文件夹
├── uploads/               # 上传文件临时存储
├── requirements.txt       # 项目依赖
└── README.md             # 说明文档
```

## 注意事项

- 确保网络可以访问 Anthropic API
- 建议使用 Python 3.9 或更高版本
- 首次运行会自动创建必要的文件夹和数据库

## 后续扩展

- 支持更多文件格式
- 批量处理功能
- 导出报告为 PDF/Word
- 模板管理功能
- 用户权限管理
