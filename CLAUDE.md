# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based intelligent bidding document review system that uses Claude AI to analyze engineering bidding documents (标书) and generate bidding responses. The system is designed for internal use and operates as a standalone web application without separate frontend/backend architecture.

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

# Quick start (Windows)
start.bat

# Quick start (Mac/Linux)
./start.sh
```

### Testing
```bash
# Verify environment configuration
python test_setup.py
```

## Core Architecture

### Three-Phase Workflow
The system implements a sequential workflow with strict dependencies:

1. **File Upload Phase** (`file_upload_tab`)
   - User uploads bidding documents (PDF/Word/Excel)
   - Files are saved to `database/` folder with timestamped names (changed from `uploads/`)
   - `DocumentParser` immediately extracts text content with encoding support for Chinese/English/numbers
   - File metadata and content stored in `st.session_state`
   - Record saved to database with status='draft'
   - UI displays two sections: "招标文件" (2 categories) and "招标文件附件" (4 categories)

2. **Analysis Phase** (`analysis_tab`)
   - **Requires**: uploaded files in session state
   - Calls `ClaudeService.analyze_bidding_document()`
   - Uses structured prompt in `_build_analysis_prompt()` covering 7 analysis dimensions
   - Result saved to session state and database (status='analyzed')

3. **Generation Phase** (`generation_tab`)
   - **Requires**: completed analysis report
   - Calls `ClaudeService.generate_bidding_response()`
   - Uses both analysis report and original document content
   - Optional user requirements can be added
   - Result saved to database (status='completed')

### Session State Management
Critical session state variables that maintain workflow continuity:
- `current_record_id`: Links UI to database record
- `uploaded_files_content`: Dict[category, text_content] - Required for analysis
- `analysis_report`: Text - Required for generation
- `bidding_response`: Text - Final output
- `project_name`: String - User-defined project identifier

When loading historical records (`load_record`), files must be re-parsed from `database/` directory since only filenames are stored in database.

### Service Initialization Pattern
Services are initialized using `@st.cache_resource` to persist across Streamlit reruns:
```python
ai_service, db_manager, document_parser = init_services()
```

This caching is critical - services should NOT be re-instantiated in individual functions.

### File Category Configuration
File types are defined in `file_upload_tab` via `file_categories` list, following the "智标领航" system design:
```python
file_categories = [
    # 招标文件 (2 categories)
    {"name": "招标文件正文", "types": [...], "category": "招标文件"},
    {"name": "技术要求附件", "types": [...], "category": "招标文件"},
    # 招标文件附件 (4 categories)
    {"name": "工程量清单", "types": [...], "category": "招标文件附件"},
    {"name": "评审标准附件", "types": [...], "category": "招标文件附件"},
    {"name": "施工设计说明", "types": [...], "category": "招标文件附件"},
    {"name": "方案建议书附件", "types": [...], "category": "招标文件附件"}
]
```

Key features:
- All file categories support multiple formats (PDF, Word, Excel)
- All categories are optional by design
- Files are grouped into "招标文件" and "招标文件附件" sections in UI
- To add new categories, append to this list with appropriate `category` field

## Module Details

### `modules/document_parser.py`
- **DocumentParser**: Registry pattern with `supported_formats` dict mapping extensions to parser methods
- Each parser returns `{'content': str, 'metadata': dict}`
- PDF: Uses PyMuPDF (fitz), extracts text page-by-page with encoding support
- Word: Extracts paragraphs and tables separately, handles mixed Chinese/English text
- Excel:
  - Processes all sheets with `pd.ExcelFile`
  - Uses `dtype=str` to preserve original formatting (numbers, Chinese, English)
  - Uses appropriate engine: openpyxl for .xlsx, xlrd for .xls
  - Returns metadata including sheet count, names, and total rows
  - Converts DataFrames to readable string format with column width limit (100 chars)

### `modules/ai_service.py`
- **ClaudeService**: Wraps Anthropic API client
- Default model: `claude-sonnet-4-20250514`
- Two specialized prompts:
  - `_build_analysis_prompt`: Structures 7-dimension analysis (project overview, technical requirements, business terms, qualifications, risks, focus areas, recommendations)
  - `_build_generation_prompt`: Generates 5-section bidding response (technical proposal, business terms, qualification list, quality assurance, after-sales service)
- Document content is truncated to 2000 chars per file in generation prompt to manage context length

### `modules/database.py`
- **BiddingRecord** ORM model with SQLAlchemy
- Fields: `project_name`, `uploaded_files` (JSON), `analysis_report`, `bidding_response`, `status`
- Status progression: draft → analyzed → completed
- `uploaded_files` stored as JSON string: `{"PDF规范": "filename.pdf", ...}`
- Database auto-created at `data/bidding_system.db` on first run

## AI Prompt Engineering

### Analysis Prompt Structure
The analysis prompt (`_build_analysis_prompt`) is designed for comprehensive bidding document review with emphasis on:
- Risk identification (technical, business, compliance, timeline)
- Easily overlooked requirements
- Scoring weight analysis
- Actionable recommendations

### Generation Prompt Strategy
The generation prompt (`_build_generation_prompt`) includes:
- Full analysis report for context
- Truncated original documents (2000 chars each) to stay within token limits
- Optional user requirements field for customization
- Higher temperature (0.5 vs 0.3) for more creative output

## Configuration

### Environment Variables (.env)
```
ANTHROPIC_API_KEY=sk-ant-api03-...  # Required
MAX_FILE_SIZE_MB=50                  # Optional
UPLOAD_FOLDER=uploads                # Optional
DATABASE_PATH=data/bidding_system.db # Optional
```

### Model Selection
To change Claude model, edit `modules/ai_service.py`:
```python
self.model = "claude-opus-4-20250514"  # For higher quality
```

## Common Development Tasks

### Adding Support for New File Format
1. Add parser method to `DocumentParser` class following signature:
   ```python
   def parse_newformat(self, file_path: str) -> Dict[str, str]:
       return {'content': str, 'metadata': dict}
   ```
2. Register in `supported_formats` dict in `__init__`
3. Add file extension to appropriate category in `file_categories` or create new category

### Modifying Analysis Dimensions
Edit the structured requirements section in `_build_analysis_prompt()`. The current 7-dimension framework can be extended or modified based on domain requirements.

### Extending Database Schema
1. Add columns to `BiddingRecord` model
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

## Important Notes

- Python 3.9+ required
- Streamlit reruns entire script on user interaction - use session state for persistence
- Uploaded files persist in `database/` directory - implement cleanup if needed
- Database session managed by `DatabaseManager` - no manual commit needed except in CRUD methods
- All file categories are intentionally optional to accommodate varying bidding document structures

## TODO

### Next Tasks
1. Review and optimize system prompts in `ai_service.py` based on detailed feature descriptions of '智标领航' system
2. Test initial bidding document parsing effectiveness and generation quality
