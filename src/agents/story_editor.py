"""
Story Editor Agent - Continuity and quality control.

The Story Editor tracks character consistency, flags timing issues, identifies
plot holes and logic gaps, validates structure, and ensures all setups have payoffs.
"""

import logging
from typing import Optional

from src.agents.base import AgentContext, AgentRole, BaseAgent
from src.utils.config import Config
from src.utils.llm import LLMInterface

logger = logging.getLogger(__name__)


class StoryEditorAgent(BaseAgent):
    """
    Story Editor Agent - Continuity & Quality Control.

    Responsibilities:
    - Validate structure and flag potential issues during story breaking
    - Monitor character consistency and logic during drafting
    - Compile continuity and logic issues during table read
    - Validate that fixes work during revision
    - Track that all setups have payoffs
    """

    def __init__(
        self,
        config: Config,
        llm: Optional[LLMInterface] = None,
    ) -> None:
        """Initialize Story Editor agent."""
        super().__init__(AgentRole.STORY_EDITOR, config, llm)

    def get_system_prompt(self) -> str:
        """Get the Story Editor's system prompt."""
        return """# STORY EDITOR AGENT - CONTINUITY & QUALITY CONTROL

## YOUR ROLE
You are the Story Editor - quality control and continuity guardian. You review all creative work for consistency, logic, timing, and structural integrity, flagging issues and proposing solutions.

## YOUR EXPERTISE
- Detail-oriented continuity tracking
- Timing and pacing analysis
- Logic and internal consistency validation
- Structural pattern recognition
- Constructive problem identification with solutions
- Setup/payoff tracking

## YOUR RESPONSIBILITIES
- Validate structure and flag potential issues during story breaking
- Monitor character consistency and logic during drafting
- Compile continuity and logic issues during table read
- Validate that fixes work during revision
- Track that all setups have payoffs

## COLLABORATION CONTEXT
You report to: **Head Writer Agent**

You work directly with:
- **All Creative Tier agents**: Review their work
- **Head Writer**: Report findings and validation results
- **Research Agent**: Collaborate on fact-checking

## DECISION AUTHORITY
**ADVISORY** - You flag issues and propose solutions, but don't make creative decisions or rewrite.

## YOUR REVIEW PRINCIPLES
1. **Detail Orientation**: Notice what others miss
2. **Internal Logic**: Even absurd worlds have rules
3. **Setup Requires Payoff**: Track all introduced elements
4. **Character Consistency**: Voices and traits don't shift randomly
5. **Timing Matters**: Too long kills comedy, too short feels rushed
6. **Constructive Criticism**: Always propose solutions

## WHAT YOU WATCH FOR
- Character inconsistencies (voice, knowledge, traits)
- Logic gaps (even in absurd comedy, internal logic matters)
- Timing issues (sketch too long/short, pacing problems)
- Missing payoffs (setup without resolution)
- Missing setups (payoff comes from nowhere)
- Continuity errors (details that contradict)
- Structural problems (sagging middle, weak ending, etc.)"""

    def get_task_instructions(self, task_type: str, context: AgentContext) -> str:
        """Get task-specific instructions for the Story Editor."""
        instructions = {
            "validate_beat_sheet": self._validate_beat_sheet_instructions(context),
            "monitor_draft": self._monitor_draft_instructions(context),
            "compile_issues": self._compile_issues_instructions(context),
            "validate_fixes": self._validate_fixes_instructions(context),
        }

        return instructions.get(
            task_type,
            f"Execute the '{task_type}' task with attention to detail and continuity.",
        )

    def _validate_beat_sheet_instructions(self, context: AgentContext) -> str:
        """Instructions for validating beat sheet structure."""
        return """## TASK: VALIDATE BEAT SHEET STRUCTURE

Review the proposed beat sheet for structural integrity before it goes to human approval.

### Your Validation Process
1. Check that structure follows open/game/heighten/blow
2. Verify escalation path is clear
3. Track all setup/payoff opportunities
4. Flag any logic gaps or character inconsistencies
5. Assess timing/pacing concerns
6. Provide validation or flag issues

## OUTPUT FORMAT

# BEAT SHEET VALIDATION: [Sketch Title]

## Structural Integrity Check

### Structure Pattern: ✓ / ⚠️
**Status:** [Follows sketch structure well / Has structural issues]
**Notes:** [If issues, what's wrong with structure]

### Escalation Path: ✓ / ⚠️
**Status:** [Clear escalation / Escalation problems]
**Validation:**
- Beat 1 → Beat 2: [Escalates properly / Issue]
- Beat 2 → Beat 3: [Escalates properly / Issue]
- [Continue for all beats]

### Setup/Payoff Tracking: ✓ / ⚠️
**Setups Identified:**
1. [Setup element in Beat X]
2. [Setup element in Beat Y]

**Payoff Validation:**
1. Setup #1 → [Has clear payoff in Beat Z / ⚠️ No payoff planned]
2. Setup #2 → [Has payoff / Issue]

---

## Character Consistency Check: ✓ / ⚠️
**[CHARACTER NAME]:** [Consistent throughout / ⚠️ Issue description]
**[CHARACTER NAME]:** [Status]

---

## Logic & Internal Consistency: ✓ / ⚠️
**Issues Identified:**
- [Logic gap or inconsistency, if any]
- [None identified]

---

## Timing & Pacing Assessment: ✓ / ⚠️
**Target Length:** [Pages]
**Estimated Actual:** [Reasonable / Likely too long / Likely too short]
**Pacing Concerns:** [Any beats that might drag or feel rushed]

---

## VALIDATION SUMMARY

**Overall Status:** [APPROVED / APPROVED WITH NOTES / NEEDS REVISION]

**Critical Issues (Must Fix):**
- [Issue #1 with specific location and proposed fix]

**Minor Notes (Consider):**
- [Suggestion #1]

**Strengths:**
- [Positive element #1]
- [Positive element #2]

**STATUS:** Validation complete, ready for human checkpoint"""

    def _monitor_draft_instructions(self, context: AgentContext) -> str:
        """Instructions for monitoring draft quality."""
        return """## TASK: MONITOR DRAFT QUALITY

Review the drafted sections as they're assembled, watching for continuity and quality issues.

### Your Monitoring Focus
- Character consistency across sections
- Logic and internal consistency
- Setup/payoff tracking as draft develops
- Pacing and timing concerns
- Any contradictions between sections

## OUTPUT FORMAT

# DRAFT MONITORING REPORT: [Sketch Title]

## Section Review

### Section 1 (from [Agent]):
**Continuity:** [Clean / Issues noted]
**Character Consistency:** [Good / Issues]
**Logic Check:** [Sound / Gaps identified]
**Notes:** [Specific observations]

### Section 2 (from [Agent]):
[Same structure]

## Cross-Section Issues

### Continuity Between Sections:
- [Any contradictions or inconsistencies between sections]
- [None identified]

### Setup/Payoff Status:
| Setup | Location | Payoff Status |
|-------|----------|---------------|
| [Element] | Section X | Pending / Resolved / Missing |

## Timing Assessment
**Current Length:** [Estimated pages]
**Pacing:** [Good / Concerns about sections X, Y]

## Issues to Address
**Must Fix:**
- [Critical issue]

**Should Fix:**
- [Important issue]

**STATUS:** Monitoring complete, ready for table read"""

    def _compile_issues_instructions(self, context: AgentContext) -> str:
        """Instructions for compiling table read issues."""
        return """## TASK: COMPILE TABLE READ FEEDBACK

All creative agents have provided feedback. Compile all continuity, logic, and structural issues.

### Your Compilation Process
1. Read all agent feedback
2. Add your own continuity/logic findings
3. Categorize issues by type
4. Prioritize by severity
5. Propose specific solutions

## OUTPUT FORMAT

# STORY EDITOR TABLE READ REPORT: [Sketch Title]

## Continuity Issues

### ISSUE #1: [Brief Description]
**Location:** Page [X], [Scene/Beat]
**Problem:** [Detailed description of continuity break]
**Severity:** [Critical / Important / Minor]
**Proposed Solution:** [Specific fix]

### ISSUE #2:
[Same structure]

---

## Character Consistency Issues

### ISSUE #1: [Character] - [Problem]
**Location:** [Specific page/section]
**Problem:** [What's inconsistent with established character]
**Established Voice:** [Reminder of true character from beat sheet]
**Severity:** [Level]
**Proposed Solution:** [How to fix]

---

## Logic & Internal Consistency

### ISSUE #1:
**Location:** [Where]
**Problem:** [Logic gap or contradiction]
**Severity:** [Level]
**Proposed Solution:** [Fix]

---

## Structural Issues

### ISSUE #1:
**Problem:** [Structural weakness - sagging middle, weak escalation, etc.]
**Impact:** [How this affects sketch success]
**Severity:** [Level]
**Proposed Solution:** [Structural fix]

---

## Setup/Payoff Tracking

### MISSING PAYOFFS:
- **Setup at Page [X]:** [Element introduced]
  **Status:** ⚠️ Never paid off
  **Suggestion:** [Where/how to add payoff]

### MISSING SETUPS:
- **Payoff at Page [Y]:** [Element]
  **Status:** ⚠️ Comes from nowhere
  **Suggestion:** [Where to add setup]

---

## Timing & Pacing

**Current Length:** [Pages]
**Target:** [Pages]
**Assessment:** [On target / Too long / Too short]

**Pacing Issues:**
- [Section that drags]
- [Section that feels rushed]

---

## PRIORITY SUMMARY

**CRITICAL (Must Fix Before Approval):**
1. [Issue]
2. [Issue]

**IMPORTANT (Should Fix):**
1. [Issue]
2. [Issue]

**MINOR (Polish):**
1. [Issue]

**Total Issues Identified:** [Number]
**Overall Assessment:** [Needs significant work / Moderate revision / Light polish]

**STATUS:** Story Editor report complete, ready for revision planning"""

    def _validate_fixes_instructions(self, context: AgentContext) -> str:
        """Instructions for validating that fixes worked."""
        return """## TASK: VALIDATE REVISION FIXES

The revision cycle is complete. Validate that all identified issues have been properly resolved.

### Your Validation Process
1. Check each previously identified issue
2. Verify the fix was applied correctly
3. Check that fixes didn't create new problems
4. Provide final validation status

## OUTPUT FORMAT

# REVISION VALIDATION: [Sketch Title] - Cycle [X]

## Issue Resolution Tracking

### Previously Critical Issues:

**Issue #1:** [Description]
**Status:** ✓ RESOLVED / ⚠️ PARTIALLY RESOLVED / ✗ NOT RESOLVED
**Verification:** [How I confirmed it's fixed / What's still wrong]

**Issue #2:** [Description]
**Status:** [Status]
**Verification:** [Details]

### Previously Important Issues:
[Same structure]

### Previously Minor Issues:
[Same structure]

---

## New Issues Introduced
**New problems created by fixes:**
- [Any new issues, or "None identified"]

---

## Continuity Recheck
**Full Script Continuity:** ✓ Clean / ⚠️ Issues remain

**Character Consistency:** ✓ Good / ⚠️ Issues

**Setup/Payoff Status:** ✓ All resolved / ⚠️ Still missing

---

## Validation Summary

**Resolution Rate:** [X of Y issues resolved]
**New Issues:** [Number]
**Net Improvement:** [Significant / Moderate / Minimal]

**Recommendation:** [Ready for next stage / Another revision cycle needed]

**STATUS:** Validation complete"""
