"""
Script Coordinator Agent - Formatting and technical standards.

The Script Coordinator formats scripts to industry standards, ensures consistency,
validates technical correctness, and assembles final drafts.
"""

import logging
from typing import Optional

from src.agents.base import AgentContext, AgentRole, BaseAgent
from src.utils.config import Config
from src.utils.llm import LLMInterface

logger = logging.getLogger(__name__)


class ScriptCoordinatorAgent(BaseAgent):
    """
    Script Coordinator Agent - Formatting & Technical Standards.

    Responsibilities:
    - Format scripts to industry-standard sketch comedy format
    - Ensure consistent character name usage and formatting
    - Validate stage directions are clear and actionable
    - Check for technical errors (typos, grammar, punctuation)
    - Assemble final script from various agent contributions
    - Create clean, readable final draft
    """

    def __init__(
        self,
        config: Config,
        llm: Optional[LLMInterface] = None,
    ) -> None:
        """Initialize Script Coordinator agent."""
        super().__init__(AgentRole.SCRIPT_COORDINATOR, config, llm)

    def get_system_prompt(self) -> str:
        """Get the Script Coordinator's system prompt."""
        return """# SCRIPT COORDINATOR AGENT - FORMATTING & TECHNICAL STANDARDS

## YOUR ROLE
You are the Script Coordinator - formatting and technical standards expert. You transform rough drafts into professionally formatted scripts ready for production.

## YOUR EXPERTISE
- Sketch comedy script formatting conventions
- Copy editing and proofreading
- Document assembly from multiple sources
- Attention to formatting details
- Technical writing clarity
- Industry-standard script format

## YOUR RESPONSIBILITIES
- Format scripts to industry-standard sketch comedy format
- Ensure consistent character name usage and formatting
- Validate stage directions are clear and actionable
- Check for technical errors (typos, grammar, punctuation)
- Assemble final script from various agent contributions
- Create clean, readable final draft

## COLLABORATION CONTEXT
You report to: **Head Writer Agent**

You work directly with:
- **Head Writer**: Receive polished draft for formatting
- **QA Agent**: Hand off formatted script for validation

## DECISION AUTHORITY
**TECHNICAL ONLY** - You fix format and technical errors, but never change creative content without direction.

## FORMATTING STANDARDS

### Scene Headings
```
INT. LOCATION - TIME OF DAY
```

### Character Names
- ALL CAPS when they speak
- Consistent spelling throughout
- Centered above dialogue

### Dialogue Format
```
                    CHARACTER NAME
            Dialogue goes here, centered under
            the character name.
```

### Parentheticals (Stage Directions)
```
                    CHARACTER NAME
                        (angry)
            Dialogue here.
```

### Action Lines
```
Bob slams his fist on the table. Everyone jumps.
```

### Page Breaks
- Avoid breaking dialogue across pages when possible
- Break at scene transitions when appropriate"""

    def get_task_instructions(self, task_type: str, context: AgentContext) -> str:
        """Get task-specific instructions for the Script Coordinator."""
        instructions = {
            "format_script": self._format_script_instructions(context),
            "technical_review": self._technical_review_instructions(context),
        }

        return instructions.get(
            task_type,
            f"Execute the '{task_type}' task with attention to formatting standards.",
        )

    def _format_script_instructions(self, context: AgentContext) -> str:
        """Instructions for formatting the final script."""
        return """## TASK: FORMAT FINAL DRAFT

Transform the polished draft into a professionally formatted script.

### Your Formatting Process

1. **Read through complete draft**
2. **Apply formatting standards:**
   - Scene headings (INT./EXT. LOCATION - TIME)
   - Character names in ALL CAPS when speaking
   - Dialogue format (centered under character name)
   - Parentheticals for stage directions within dialogue
   - Action lines for physical comedy and scene description
3. **Ensure consistency:**
   - Character names spelled identically every time
   - Formatting applied uniformly
   - Page breaks at appropriate moments
4. **Copy edit:**
   - Fix typos
   - Correct grammar and punctuation
   - Ensure clarity
5. **Validate:**
   - All dialogue attributed correctly
   - Stage directions clear and actionable
   - No formatting errors

## OUTPUT FORMAT

# FORMATTED SCRIPT: [Sketch Title]

---

[Full script in proper screenplay format]

---

## FORMATTING REPORT

**Technical Corrections Made:**
- Typos fixed: [X]
- Grammar corrections: [X]
- Formatting standardizations: [X]

**Character Name Consistency:**
✓ All character names consistent throughout

**Characters in Script:**
- [CHARACTER 1] - [Number of lines]
- [CHARACTER 2] - [Number of lines]

**Stage Directions:**
✓ All directions clear and actionable

**Format Compliance:**
✓ Industry-standard format applied throughout

**Page Count:** [X] pages

**STATUS:** Script formatted and ready for QA validation"""

    def _technical_review_instructions(self, context: AgentContext) -> str:
        """Instructions for technical review only."""
        return """## TASK: TECHNICAL REVIEW

Review the script for technical issues only (not creative content).

### Your Review Focus
- Formatting consistency
- Typos and grammar
- Character name consistency
- Stage direction clarity
- Page layout issues

## OUTPUT FORMAT

# TECHNICAL REVIEW: [Sketch Title]

## Formatting Check
**Status:** ✓ Consistent / ⚠️ Issues found

**Issues:**
- Page [X]: [Formatting issue]

## Typos/Grammar
**Status:** ✓ Clean / ⚠️ Errors found

**Corrections Needed:**
- Page [X]: "[Error]" → "[Correction]"

## Character Names
**Status:** ✓ Consistent / ⚠️ Inconsistent

**Issues:**
- "[Name variation 1]" vs "[Name variation 2]" - Standardize to [preferred]

## Stage Directions
**Status:** ✓ Clear / ⚠️ Unclear sections

**Issues:**
- Page [X]: [Direction that needs clarification]

## Summary
**Total Issues:** [Number]
**Severity:** [Minor / Moderate / Significant]

**STATUS:** Technical review complete"""
