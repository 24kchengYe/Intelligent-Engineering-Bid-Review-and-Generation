# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

from modules.prompts import TECHNICAL_PROPOSAL_OUTLINE_PROMPT

# Test formatting
try:
    result = TECHNICAL_PROPOSAL_OUTLINE_PROMPT.format(
        project_requirements="test",
        evaluation_criteria="test"
    )
    print("SUCCESS: TECHNICAL_PROPOSAL_OUTLINE_PROMPT can be formatted")
    print(f"Length: {len(result)}")
except KeyError as e:
    print(f"ERROR: Missing placeholder - {e}")
except Exception as e:
    print(f"ERROR: {e}")
