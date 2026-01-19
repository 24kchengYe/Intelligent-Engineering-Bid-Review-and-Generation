# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based **Intelligent Bidding Document Review and Technical Proposal Generation System** (智能标书审查系统/智标领航) that uses Claude AI to:
1. Parse and analyze engineering bidding documents with **7-category structured analysis**
2. Extract evaluation criteria automatically
3. Generate technical proposal outlines based on evaluation criteria
4. Generate technical proposal sections step-by-step

The system is designed for internal use and operates as a standalone web application without separate frontend/backend architecture.

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key (required before first run)
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Running the Application
```bash
# Start the Streamlit application
streamlit run app.py

# Quick start (Windows) - Recommended
启动系统.bat

# Quick start (Mac/Linux)
./start.sh
```

### Testing
```bash
# Verify environment configuration
python test_setup.py

# Test AI prompts
python test_prompts.py
```

## Core Architecture

### Three-Phase Workflow
The system implements a sequential workflow with strict dependencies:

#### **Phase 1: File Upload** (`file_upload_tab`)
- User uploads bidding documents (PDF/Word/Excel) - All 6 categories are optional
- Files are saved to `database/` folder with timestamped names
- `DocumentParser` immediately extracts text content with encoding support for Chinese/English/numbers
- File metadata and content stored in `st.session_state`
- Record saved to database with status='draft'
- UI displays **6 file categories** in two sections:
  - **招标文件** (2 categories): 招标文件正文, 技术要求附件
  - **招标文件附件** (4 categories): 工程量清单, 评审标准附件, 施工设计说明, 方案建议书附件

#### **Phase 2: Structured Analysis** (`analysis_tab`)
**Requires**: Uploaded files in session state

**Step 1: 7-Category Structured Parsing**
- Calls `ClaudeService.parse_bidding_document_structured(uploaded_files_content)`
- Uses `BIDDING_DOCUMENT_ANALYSIS_PROMPT` from `modules/prompts.py`
- Analyzes across 7 major categories:
  1. 基础信息 (Basic Information)
  2. 资格要求 (Qualification Requirements)
  3. 评审要求 (Evaluation Requirements)
  4. 投标文件要求 (Bidding Document Requirements)
  5. 无效标与废标项 (Invalid & Rejected Bid Items)
  6. 应标需提交文件 (Required Submission Documents)
  7. 招标文件审查 (Bidding Document Review - includes 6 risk types + 5 fairness dimensions)
- Result saved to session state and database (status='analyzed')
- **UI**: Left/right pane layout showing parsed results + original document content

**Step 2: Evaluation Criteria Extraction**
- Automatically called after structured parsing
- Calls `ClaudeService.extract_evaluation_criteria(analysis_report)`
- Uses `EVALUATION_CRITERIA_EXTRACTION_PROMPT` from `modules/prompts.py`
- Extracts detailed evaluation criteria from analysis report
- Focuses on "施工组织设计" (Construction Organization Design) evaluation factors
- Result saved to `session_state.evaluation_criteria` and `database.bidding_response` field

#### **Phase 3: Technical Proposal Generation** (`generation_tab`)
**Requires**: Completed analysis report + extracted evaluation criteria

**Step 1: Generate Technical Proposal Outline**
- Calls `ClaudeService.generate_technical_proposal_outline(project_requirements, evaluation_criteria)`
- Uses `TECHNICAL_PROPOSAL_OUTLINE_PROMPT` from `modules/prompts.py`
- Returns JSON structure with:
  - Multi-level outline (一、二、三... / 1. 2. 3...)
  - Suggested word count for each section
  - Brief description of section requirements
- UI displays outline as expandable tree structure

**Step 2: Generate Sections Step-by-Step**
- User selects section from dropdown
- Calls `ClaudeService.generate_technical_proposal_section(section_title, word_count, section_requirements, project_info, evaluation_criteria)`
- Uses `TECHNICAL_PROPOSAL_SECTION_PROMPT` from `modules/prompts.py`
- Generated content saved to `session_state.generated_sections[section_title]`
- UI shows progress: "X/Y sections generated"
- User repeats until all sections complete

**Step 3: Export Complete Technical Proposal**
- Merges all generated sections into complete document
- Exports as Markdown or TXT format

### Session State Management
Critical session state variables that maintain workflow continuity:
- `current_record_id`: Links UI to database record
- `project_name`: User-defined project identifier
- `uploaded_files_info`: Dict[category, filename] - File metadata
- `uploaded_files_content`: Dict[category, text_content] - Required for analysis
- `files_processed`: Set[file_id] - For deduplication
- `analysis_report`: Text - 7-category structured parsing result
- `evaluation_criteria`: Text - Extracted evaluation criteria
- `technical_outline`: Dict - JSON outline structure
- `generated_sections`: Dict[section_title, content] - Generated proposal sections
- `bidding_response`: Text - Actually stores evaluation criteria (legacy field name)

When loading historical records (`load_record`), files must be re-parsed from `database/` directory since only filenames are stored in database.

### Service Initialization Pattern
Services are initialized using `@st.cache_resource` to persist across Streamlit reruns:
```python
ai_service, db_manager, document_parser = init_services()
```

This caching is critical - services should NOT be re-instantiated in individual functions.

### File Category Configuration
File types are defined in `file_upload_tab` via `file_categories` list:
```python
file_categories = [
    # 招标文件 (2 categories)
    {"name": "招标文件正文", "types": ["pdf", "docx", "doc", "xlsx", "xls"], "category": "招标文件"},
    {"name": "技术要求附件", "types": ["pdf", "docx", "doc", "xlsx", "xls"], "category": "招标文件"},
    # 招标文件附件 (4 categories)
    {"name": "工程量清单", "types": ["pdf", "xlsx", "xls", "docx", "doc"], "category": "招标文件附件"},
    {"name": "评审标准附件", "types": ["pdf", "docx", "doc", "xlsx", "xls"], "category": "招标文件附件"},
    {"name": "施工设计说明", "types": ["pdf", "docx", "doc", "dwg"], "category": "招标文件附件"},
    {"name": "方案建议书附件", "types": ["pdf", "docx", "doc", "xlsx", "xls"], "category": "招标文件附件"}
]
```

Key features:
- All file categories support multiple formats (PDF, Word, Excel)
- All 6 categories are **optional** by design
- Files are grouped into "招标文件" and "招标文件附件" sections in UI
- To add new categories, append to this list with appropriate `category` field

## Module Details

### `modules/document_parser.py` (175 lines)
- **DocumentParser**: Registry pattern with `supported_formats` dict mapping extensions to parser methods
- Each parser returns `{'content': str, 'metadata': dict}`
- **PDF**: Uses PyMuPDF (fitz), extracts text page-by-page with encoding support
- **Word**: Extracts paragraphs and tables separately, handles mixed Chinese/English text
- **Excel**:
  - Processes all sheets with `pd.ExcelFile`
  - Uses `dtype=str` to preserve original formatting (numbers, Chinese, English)
  - Uses appropriate engine: openpyxl for .xlsx, xlrd for .xls
  - Returns metadata including sheet count, names, and total rows
  - Converts DataFrames to readable string format with column width limit (100 chars)

### `modules/ai_service.py` (412 lines)
- **ClaudeService**: Wraps Anthropic API client
- Default model: `claude-sonnet-4-20250514` (Sonnet 4)
- Alternative model: `claude-opus-4-20250514` (Opus 4 - higher quality, higher cost)

**Core Methods (New Architecture)**:
1. **`parse_bidding_document_structured(document_contents)`**
   - 7-category structured parsing
   - max_tokens: 16000
   - temperature: 0.2 (high accuracy)
   - Uses `BIDDING_DOCUMENT_ANALYSIS_PROMPT`

2. **`extract_evaluation_criteria(analysis_report)`**
   - Extract evaluation criteria from analysis report
   - max_tokens: 8000
   - temperature: 0.3
   - Uses `EVALUATION_CRITERIA_EXTRACTION_PROMPT`

3. **`generate_technical_proposal_outline(project_requirements, evaluation_criteria)`**
   - Generate JSON outline structure
   - max_tokens: 8000
   - temperature: 0.4
   - Uses `TECHNICAL_PROPOSAL_OUTLINE_PROMPT`

4. **`generate_technical_proposal_section(section_title, word_count, section_requirements, project_info, evaluation_criteria)`**
   - Generate individual sections
   - max_tokens: 8000
   - temperature: 0.5 (moderate creativity)
   - Uses `TECHNICAL_PROPOSAL_SECTION_PROMPT`

**Legacy Methods** (preserved for compatibility):
- `analyze_bidding_document()`: Old analysis method (not recommended)
- `generate_bidding_response()`: Old generation method (not recommended)
- `chat()`: Generic chat interface

### `modules/prompts.py` (405 lines) ✨ **NEW MODULE**
Centralized AI prompt template library using Python f-strings:

1. **`BIDDING_DOCUMENT_ANALYSIS_PROMPT`** (160 lines)
   - 7-category structured parsing template
   - Categories: 基础信息, 资格要求, 评审要求, 投标文件要求, 无效标与废标项, 应标需提交文件, 招标文件审查
   - Includes risk identification (6 types) and fairness review (5 dimensions)
   - Output: Markdown format with clear hierarchy

2. **`EVALUATION_CRITERIA_EXTRACTION_PROMPT`** (53 lines)
   - Extract project requirements and evaluation criteria
   - Focus on "施工组织设计" evaluation factors
   - Output: Markdown format with scoring details

3. **`TECHNICAL_PROPOSAL_OUTLINE_PROMPT`** (127 lines)
   - Generate technical proposal outline structure
   - Output: JSON format with word count suggestions
   - Reference structure: 一、技术文件 / 二、项目经理视频陈述及答辩 / 三、施工组织设计

4. **`TECHNICAL_PROPOSAL_SECTION_PROMPT`** (55 lines)
   - Generate individual section content
   - Input: section title, word count, requirements, project info, evaluation criteria
   - Output: Markdown format, professional engineering language

### `modules/database.py` (150 lines)
- **BiddingRecord** ORM model with SQLAlchemy
- Fields: `project_name`, `uploaded_files` (JSON), `analysis_report`, `bidding_response`, `status`, `create_time`, `update_time`
- Status progression: draft → analyzed → completed
- `uploaded_files` stored as JSON string: `{"招标文件正文": "filename.pdf", ...}`
- `bidding_response` field **actually stores evaluation criteria** (legacy naming for DB compatibility)
- Database auto-created at `data/bidding_system.db` on first run

## AI Prompt Engineering Strategy

### Modular Prompt Management
All prompts are centralized in `modules/prompts.py`:
- **Benefits**: Version control, easy maintenance, consistent formatting
- **Format**: Markdown output for easy parsing and display
- **Structure**: Clear hierarchical organization with numbered lists

### Multi-Step Generation Approach
Complex tasks are broken into sequential steps to improve accuracy:
1. **Parse** → 7-category structured parsing (high accuracy, low creativity)
2. **Extract** → Evaluation criteria extraction (moderate accuracy)
3. **Outline** → Technical proposal outline (moderate creativity)
4. **Generate** → Section-by-section content generation (higher creativity)

Each step builds on previous results, creating a pipeline of increasing specificity.

### Temperature Strategy
- **0.2** (parse): Maximize accuracy for information extraction
- **0.3** (extract): Balance accuracy and interpretation
- **0.4** (outline): Allow creative structuring
- **0.5** (generate): Enable professional writing with creativity

## Configuration

### Environment Variables (.env)
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional - For OpenRouter or custom endpoints
ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1
ANTHROPIC_MODEL=anthropic/claude-sonnet-4

# Optional - System settings
MAX_FILE_SIZE_MB=50
UPLOAD_FOLDER=database
DATABASE_PATH=data/bidding_system.db
```

### Model Selection
To change Claude model, edit `modules/ai_service.py` line 49:
```python
self.model = "claude-opus-4-20250514"  # For higher quality
```

### Using OpenRouter
Configure in `.env`:
```bash
ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1
ANTHROPIC_MODEL=anthropic/claude-sonnet-4
```
Code automatically detects `ANTHROPIC_BASE_URL` and switches to custom service.

## Common Development Tasks

### Adding Support for New File Format
1. Add parser method to `DocumentParser` class following signature:
   ```python
   def parse_newformat(self, file_path: str) -> Dict[str, str]:
       return {'content': str, 'metadata': dict}
   ```
2. Register in `supported_formats` dict in `__init__`
3. Add file extension to appropriate category in `file_categories` or create new category

### Adding New File Upload Category
Modify `file_categories` list in `app.py` `file_upload_tab()` function:
```python
file_categories.append({
    "name": "新类别名称",
    "types": ["pdf", "docx"],
    "category": "招标文件"  # or "招标文件附件"
})
```

### Modifying Analysis Categories
Edit `BIDDING_DOCUMENT_ANALYSIS_PROMPT` in `modules/prompts.py`:
- Add new category under the 7 main categories
- Add new subcategory under existing categories
- Modify extraction requirements for specific fields

### Customizing Technical Proposal Structure
Edit `TECHNICAL_PROPOSAL_OUTLINE_PROMPT` in `modules/prompts.py`:
- Modify reference outline structure
- Adjust suggested word counts
- Add new chapter templates

### Extending Database Schema
1. Add columns to `BiddingRecord` model in `modules/database.py`
2. Database auto-migrates on next run (SQLite limitation: some migrations may fail, may need to drop table)
3. Update `create_record` and `update_record` methods if needed

## Code Style Guidelines

### String Quoting for UI Messages
When UI messages contain quotation marks, use alternating single and double quotes to avoid syntax errors:
```python
# Correct: Use single quotes inside double-quoted strings
st.warning("⚠️ 请先在'文件上传'标签页上传标书文件")

# Incorrect: Nested double quotes cause syntax errors
st.warning("⚠️ 请先在"文件上传"标签页上传标书文件")  # SyntaxError
```

### Session State Access Pattern
Always initialize session state keys before using them:
```python
if 'key_name' not in st.session_state:
    st.session_state.key_name = default_value
```

### File Path Handling
Use `os.path.join()` for cross-platform compatibility:
```python
file_path = os.path.join("database", filename)  # NOT "database/" + filename
```

## Important Notes

- **Python 3.9+** required
- Streamlit reruns entire script on user interaction - **use session state for persistence**
- Uploaded files persist in `database/` directory (NOT `uploads/`) - implement cleanup if needed
- Database session managed by `DatabaseManager` - no manual commit needed except in CRUD methods
- All 6 file categories are **intentionally optional** to accommodate varying bidding document structures
- Evaluation criteria are stored in `bidding_response` field (legacy naming for DB compatibility)

## Debugging Tips

### Common Issues

**Issue**: Session state lost after page reload
- **Cause**: Not saving to database
- **Fix**: Ensure `db_manager.update_record()` is called after critical operations

**Issue**: File parsing returns empty content
- **Cause**: Encoding issues or unsupported format
- **Fix**: Check file encoding, verify file is not password-protected

**Issue**: API call timeout
- **Cause**: max_tokens too high or document too long
- **Fix**: Reduce max_tokens or implement text truncation

**Issue**: JSON parsing fails for outline
- **Cause**: AI returned non-JSON format
- **Fix**: Code includes fallback to raw text mode (check `raw: True` flag)

## Performance Optimization

### Current Limitations
- Max tokens per API call: 16000 (for structured parsing)
- Document content truncation: 2000 chars per file (in old generation method)
- No caching for repeated API calls with same input

### Optimization Suggestions
1. **Implement API response caching** - Cache results for identical inputs
2. **Add document chunking** - For very long documents, split into chunks
3. **Use streaming API** - If supported, for better user experience
4. **Add database indexes** - On project_name, create_time for faster searches
5. **Consider async processing** - For batch operations

## Testing

### Environment Setup Test
```bash
python test_setup.py
```
Verifies:
- API key configuration
- Package dependencies
- Database connectivity

### Prompt Testing
```bash
python test_prompts.py
```
Tests individual prompt templates with sample data.

## Version History

### v1.0.0 (2026-01-15)
- ✅ Complete system architecture with 3-phase workflow
- ✅ 7-category structured parsing
- ✅ Automatic evaluation criteria extraction
- ✅ Step-by-step technical proposal generation
- ✅ Centralized prompt management (`modules/prompts.py`)
- ✅ 6 optional file upload categories
- ✅ Historical record management
- ✅ MD/TXT format export

## TODO & Future Enhancements

### High Priority
- [ ] Add Word/PDF export for technical proposals (currently only MD/TXT)
- [ ] Implement API response caching to reduce costs
- [ ] Add document chunking for very long bidding documents

### Medium Priority
- [ ] Batch project processing functionality
- [ ] Technical proposal template library
- [ ] Section content editing functionality
- [ ] Evaluation criteria visualization

### Low Priority
- [ ] User authentication and permissions
- [ ] Multi-user collaboration features
- [ ] Support for CAD drawing text extraction
- [ ] Comparison analysis between multiple bidding documents

---

**Maintained by**: Yecheng Zhang & Claude Code
**Last Updated**: 2026-01-15
**License**: Internal Use
