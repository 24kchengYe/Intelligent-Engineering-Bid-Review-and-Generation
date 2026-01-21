# 系统升级指南 (v1.0 → v1.1)

## 版本概览

**版本**: v1.1.0
**发布日期**: 2026-01-19
**升级类型**: 功能增强（向后兼容）

---

## 🆕 新功能

### 1. OCR扫描版PDF识别
- 自动检测扫描版PDF（无文本层的页面）
- 使用RapidOCR引擎进行文字识别
- 在文件上传界面显示OCR统计信息

### 2. PDF表格结构化提取
- 从PDF中提取表格为二维数组（而非纯文本）
- 保留表格结构，便于AI分析
- 显示提取到的表格数量

### 3. 国标文件管理系统
- 新增"国标管理"Tab页
- 上传国家/行业/地方标准文件
- 自动提取标准编号（GB/JGJ/CJJ/DB等）
- 全局存储，不随项目记录删除
- 支持搜索和分类筛选

---

## 📦 安装步骤

### 方法1: 全新安装（推荐）

```bash
# 1. 安装新依赖
pip install -r requirements.txt

# 新增的依赖：
# - rapidocr-onnxruntime==1.3.22 (OCR引擎，约30MB)

# 2. 首次运行会自动创建新目录
streamlit run app.py
# 自动创建:
# - data/standards.db (国标数据库)
# - data/standards/ (国标文件存储)
```

### 方法2: 从v1.0升级

```bash
# 1. 备份数据（重要！）
mkdir backup
cp -r data/ backup/
cp -r database/ backup/

# 2. 更新代码（拉取最新代码）
git pull origin main

# 3. 安装新依赖
pip install rapidocr-onnxruntime==1.3.22

# 4. 启动系统
streamlit run app.py

# 注意：国标数据库会自动创建，旧项目数据不受影响
```

---

## 🔧 配置说明

### OCR功能配置

如果不需要OCR功能（仅处理文本层PDF），可在 `app.py` 中禁用：

```python
# 第25行修改为：
document_parser = DocumentParser(enable_ocr=False)  # 禁用OCR
```

### 国标存储路径

默认路径：
- 数据库: `data/standards.db`
- 文件: `data/standards/`

如需修改，编辑 `app.py` 第27行：

```python
standards_manager = StandardsManager(
    db_path='custom/path/standards.db',
    storage_path='custom/path/standards'
)
```

---

## 📊 数据库变更

### 新增数据库表

```sql
-- 国标文件表（新增）
CREATE TABLE standard_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_code VARCHAR(100) UNIQUE NOT NULL,
    standard_name VARCHAR(500) NOT NULL,
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    file_size INTEGER,
    category VARCHAR(100),
    content_preview TEXT,
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**注意**: 此表独立于项目记录表(`bidding_record`)，互不影响。

### 旧数据兼容性

✅ **完全兼容** - 旧项目记录无需迁移，可正常使用。

---

## 🎯 功能使用指南

### 1. 上传扫描版PDF

```
1. 切换到"文件上传"Tab
2. 选择扫描版PDF文件
3. 系统自动检测并使用OCR识别
4. 查看识别结果：
   - ✅ 已上传并解析: xxx.pdf
   - 📄 共 10 页
   - 🔍 检测到扫描版PDF，已使用OCR识别 8/10 页
   - 📋 提取到 3 个表格
```

### 2. 管理国标文件

```
1. 切换到"国标管理"Tab
2. 点击"选择标准文件"上传PDF/Word格式国标
3. （可选）输入标准名称，留空则自动提取
4. 点击"确认上传"
5. 系统自动：
   - 提取标准编号（如：GB50500-2013）
   - 分类（国家标准/行业标准/地方标准）
   - 防止重复上传（SHA256校验）
```

### 3. 查看国标内容

```
1. 在国标列表中展开某个标准
2. 点击"👁️ 查看"按钮
3. 查看完整文本内容
4. 点击"关闭"折叠内容
```

### 4. 搜索国标

```
1. 在"搜索标准"框输入关键词
   - 支持标准编号：GB50500
   - 支持标准名称：工程量清单
2. 使用"分类筛选"下拉框过滤
```

---

## 🐛 常见问题

### Q1: OCR识别速度慢？

**原因**: RapidOCR是CPU推理，高DPI渲染耗时较长。

**解决方案**:
```python
# 在 modules/document_parser.py 第128行
# 降低DPI (2倍 → 1.5倍)
mat = fitz.Matrix(1.5, 1.5)  # 原为 2, 2
```

### Q2: 国标文件上传失败？

**可能原因**:
1. 文件已存在（相同SHA256哈希）
2. 标准编号重复
3. 文件格式不支持

**排查方法**:
```bash
# 查看错误详情
streamlit run app.py --logger.level=debug
```

### Q3: OCR识别不准确？

**原因**: 扫描版PDF质量太差（倾斜、噪点、模糊）

**建议**:
- 使用清晰度≥300DPI的扫描件
- 避免过度压缩的PDF
- 可尝试预先使用PDF编辑工具（Adobe Acrobat）进行OCR

### Q4: 如何卸载OCR功能？

```bash
# 1. 卸载依赖
pip uninstall rapidocr-onnxruntime -y

# 2. 禁用功能
# 编辑 app.py 第25行：
document_parser = DocumentParser(enable_ocr=False)

# 系统会自动回退到v1.0行为（跳过扫描页）
```

---

## 💾 备份建议

在升级前，建议备份以下内容：

```bash
# 备份数据库
cp data/bidding_system.db backup/

# 备份上传文件
cp -r database/ backup/

# 备份环境配置
cp .env backup/
```

---

## 🔄 回滚方案

如需回滚到v1.0:

```bash
# 1. 恢复代码
git checkout v1.0.0  # 或对应的commit hash

# 2. 恢复数据
cp backup/bidding_system.db data/
cp -r backup/database/ .

# 3. 重新安装旧依赖
pip install -r requirements.txt

# 注意：国标数据将丢失（独立数据库，可手动保留）
```

---

## 📞 技术支持

**问题反馈**:
- GitHub Issues: https://github.com/your-repo/issues
- 邮箱: support@example.com

**更新日志**:
- 查看 `CHANGELOG.md` 了解详细变更记录

---

## ✅ 升级检查清单

- [ ] 备份现有数据
- [ ] 安装新依赖 (`rapidocr-onnxruntime`)
- [ ] 启动系统并测试基本功能
- [ ] 测试OCR功能（上传扫描版PDF）
- [ ] 测试国标管理功能（上传1-2个标准文件）
- [ ] 验证旧项目记录可正常加载
- [ ] 检查文件上传是否正常
- [ ] 检查分析和生成功能是否正常

**升级完成！** 🎉
