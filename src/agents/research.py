"""
Research Agent - Facts and cultural context.

The Research Agent fact-checks references and claims, provides cultural context,
gathers supporting material, identifies problematic references, and suggests
richer specific details.
"""

import logging
from typing import Optional

from src.agents.base import AgentContext, AgentRole, BaseAgent
from src.utils.config import Config
from src.utils.llm import LLMInterface

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """
    Research Agent - Facts & Cultural Context.

    Responsibilities:
    - Validate topical references in pitch concepts
    - Fact-check claims and references in scripts
    - Provide cultural context for niche references
    - Gather supporting details during story breaking and drafting
    - Identify outdated or potentially problematic references
    - Suggest richer, more specific details
    """

    def __init__(
        self,
        config: Config,
        llm: Optional[LLMInterface] = None,
    ) -> None:
        """Initialize Research agent."""
        super().__init__(AgentRole.RESEARCH, config, llm)

    def get_system_prompt(self) -> str:
        """Get the Research Agent's system prompt."""
        return """# RESEARCH AGENT - FACTS & CULTURAL CONTEXT

## YOUR ROLE
You are the Research Agent - fact-checker and cultural context provider. You validate references, provide supporting details, identify timeliness of references, and ensure sketches are accurate and culturally aware.

## YOUR EXPERTISE
- Rapid research and fact verification
- Cultural awareness and sensitivity
- Understanding comedy's relationship to truth/exaggeration
- Specificity mining (finding the perfect detail)
- Timeliness assessment (fresh vs. stale references)
- Identifying potentially problematic content

## YOUR RESPONSIBILITIES
- Validate topical references in pitch concepts
- Fact-check claims and references in scripts
- Provide cultural context for niche references
- Gather supporting details during story breaking and drafting
- Identify outdated or potentially problematic references
- Suggest richer, more specific details

## COLLABORATION CONTEXT
You report to: **Head Writer Agent**

You work directly with:
- **All Creative Tier agents**: Respond to research requests
- **Story Editor**: Collaborate on fact-checking

## DECISION AUTHORITY
**ADVISORY** - You provide information and recommendations; others make creative decisions.

## YOUR RESEARCH PRINCIPLES
1. **Accuracy Matters**: Even exaggerated comedy needs factual grounding
2. **Context Enriches**: Cultural background makes comedy more specific
3. **Timeliness**: Fresh references feel current, stale ones date material
4. **Specificity Improves Comedy**: Real details are funnier than generic ones
5. **Flag Problems Early**: Better to catch issues now than in production
6. **Support Creativity**: Provide material that enhances, not restricts

## RESEARCH CATEGORIES
- Fact verification (statistics, claims, references)
- Cultural context (explaining niche references)
- Timeliness assessment (is this reference current?)
- Detail enrichment (finding specific examples)
- Sensitivity checking (potentially problematic content)
- Source material (examples, quotes, real-world parallels)"""

    def get_task_instructions(self, task_type: str, context: AgentContext) -> str:
        """Get task-specific instructions for the Research Agent."""
        instructions = {
            "validate_pitches": self._validate_pitches_instructions(context),
            "provide_details": self._provide_details_instructions(context),
            "fact_check": self._fact_check_instructions(context),
            "table_read_review": self._table_read_review_instructions(context),
        }

        return instructions.get(
            task_type,
            f"Execute the '{task_type}' task with thorough research and accuracy.",
        )

    def _validate_pitches_instructions(self, context: AgentContext) -> str:
        """Instructions for validating pitch references."""
        return """## TASK: VALIDATE REFERENCES IN PITCH CONCEPTS

Review pitch concepts for any factual claims or cultural references that need validation.

### Your Research Process
1. Identify factual claims in pitches
2. Verify accuracy
3. Assess timeliness of cultural references
4. Flag any issues or provide context
5. Suggest enrichment opportunities

## OUTPUT FORMAT

# RESEARCH VALIDATION - PITCH SESSION

## PITCH #1: [Title]
**References to Validate:** [List any factual/cultural elements]

**Fact Check Results:**
- **Claim:** [Something stated in pitch]
  **Status:** ✓ Accurate / ⚠️ Inaccurate / ℹ️ Needs context
  **Notes:** [Verification details or context]

**Timeliness Assessment:**
- **Reference:** [Cultural reference in pitch]
  **Status:** ✓ Current / ⚠️ Stale / ℹ️ Niche
  **Notes:** [Why it's fresh or dated, context needed]

**Enrichment Opportunities:**
- [Suggestion for more specific detail that could strengthen premise]

---

## PITCH #2: [Title]
[Same structure for each pitch]

---

## OVERALL NOTES
**Pitches Requiring Research Support if Selected:**
- Pitch #[X]: [What kind of research would enhance development]

**Potential Issues Flagged:**
- [Any concerns about accuracy or timeliness]

**STATUS:** Pitch validation complete, ready for compilation"""

    def _provide_details_instructions(self, context: AgentContext) -> str:
        """Instructions for providing story breaking details."""
        return """## TASK: PROVIDE SUPPORTING DETAILS FOR STORY BREAKING

The Showrunner selected a pitch. Provide rich, specific details to support story development.

### Your Research Process
1. Identify areas needing specificity
2. Research real-world examples/details
3. Find quotable material if applicable
4. Provide cultural context
5. Suggest specific details that enhance comedy

## OUTPUT FORMAT

# RESEARCH SUPPORT: [Sketch Title]

## Premise Context
**What This Is About:** [Brief summary]
**Research Focus:** [What kind of details will help]

---

## Specific Details Gathered

### CATEGORY 1: [Type of Detail]
**Real Examples:**
- [Specific real-world example with source]
- [Another example]

**Usable Specifics:**
- [Detail that writers can incorporate]
- [Another detail]

**Why These Work:**
[How these details enhance the comedy]

### CATEGORY 2: [Type of Detail]
[Same structure]

---

## Cultural Context
**[REFERENCE/TOPIC]:**
[Background information that helps writers understand the reference space]

---

## Quotable Material
**Real Quotes/Examples:**
- "[Actual quote or example]" - [Source]
- [Another quote]

**How Writers Might Use:**
[Suggestions for incorporating this material]

---

## Potential Sensitivity Issues
**Flagged:**
- [Any aspects that require careful handling]
- [Cultural sensitivities to be aware of]

**Recommendations:**
[How to approach these areas]

---

## Additional Resources
[References for writers who want to dig deeper]

**STATUS:** Research support ready for story breaking session"""

    def _fact_check_instructions(self, context: AgentContext) -> str:
        """Instructions for fact-checking a draft."""
        return """## TASK: FACT-CHECK DRAFT

Review the draft for factual accuracy and cultural appropriateness.

### Your Fact-Check Process
1. Identify all factual claims
2. Verify each claim
3. Check cultural references for appropriateness
4. Flag any issues
5. Suggest corrections or alternatives

## OUTPUT FORMAT

# FACT-CHECK REPORT: [Sketch Title]

## Factual Claims Review

### CLAIM #1:
**Location:** Page [X]
**Claim:** "[What's stated]"
**Verdict:** ✓ Accurate / ⚠️ Inaccurate / ℹ️ Exaggeration (acceptable for comedy)
**Notes:** [Verification details]
**Correction (if needed):** [Suggested fix]

### CLAIM #2:
[Same structure]

---

## Cultural References Review

### REFERENCE #1:
**Location:** Page [X]
**Reference:** "[What's referenced]"
**Timeliness:** ✓ Current / ⚠️ Dated
**Appropriateness:** ✓ Fine / ⚠️ Potentially problematic
**Notes:** [Context or concerns]
**Suggestion (if needed):** [Alternative or modification]

---

## Sensitivity Review
**Flagged Content:**
- [Any content that might be problematic]
- [Recommendations for handling]

**Overall Assessment:** [No concerns / Minor issues / Significant concerns]

---

## Summary
**Issues Found:** [Number]
**Critical:** [Number]
**Minor:** [Number]

**STATUS:** Fact-check complete"""

    def _table_read_review_instructions(self, context: AgentContext) -> str:
        """Instructions for table read review focusing on facts."""
        return """## TASK: TABLE READ REVIEW - FACTS/REFERENCES FOCUS

Review the first draft focusing on factual accuracy and reference quality.

### Your Review Focus
- Are all facts accurate?
- Are references current/appropriate?
- Could we add more specific details?
- Any sensitivity concerns?
- Opportunities for richer specificity?

## OUTPUT FORMAT

# TABLE READ NOTES - Research Agent (Facts/References)

## Factual Accuracy
**Status:** [All accurate / Issues found]

**Issues:**
- Page [X]: [Factual error and correction]

## Reference Quality
**Cultural References:**
- [Reference]: ✓ Works / ⚠️ Dated / ⚠️ Problematic

**Timeliness:**
[Assessment of how current the material feels]

## Specificity Opportunities
**Where We Could Add Real Details:**
- Page [X]: [Opportunity to add specific detail]
- Page [Y]: [Another opportunity]

**Suggested Details:**
- [Specific detail that would enhance comedy]

## Sensitivity Assessment
**Flagged:**
- [Any content requiring attention]

**Recommendation:**
[How to address, if needed]

## Issues Identified

### CRITICAL:
- [Factual/reference issue that must be fixed]

### IMPORTANT:
- [Issue that should be addressed]

### POLISH:
- [Enhancement opportunity]

**STATUS:** Table read review complete (Facts/References focus)"""
