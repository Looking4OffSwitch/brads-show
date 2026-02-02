"""
Staff Writer A - High-energy pitch generator.

Staff Writer A brings enthusiasm, volume, and fresh perspectives. Excels at
rapid ideation, identifying topical hooks, and making unexpected connections.
"""

import logging
from typing import Optional

from src.agents.base import AgentContext, AgentRole, BaseAgent
from src.utils.config import Config
from src.utils.llm import LLMInterface

logger = logging.getLogger(__name__)


class StaffWriterA(BaseAgent):
    """
    Staff Writer A - High-Energy Pitch Generator.

    Responsibilities:
    - Generate high volume of pitch concepts (3+ per session)
    - Bring topical and cultural hooks to premises
    - Propose alternative approaches during revision
    - Identify fresh angles on familiar concepts
    - Request research support for topical material
    """

    def __init__(
        self,
        config: Config,
        llm: Optional[LLMInterface] = None,
    ) -> None:
        """Initialize Staff Writer A agent."""
        super().__init__(AgentRole.STAFF_WRITER_A, config, llm)

    def get_system_prompt(self) -> str:
        """Get Staff Writer A's system prompt."""
        return """# STAFF WRITER AGENT A - HIGH-ENERGY PITCH GENERATOR

## YOUR ROLE
You are the High-Energy Pitcher - the idea machine. You generate high volumes of diverse pitches, bring fresh perspectives and unexpected angles, identify topical hooks, and contribute enthusiastic creativity.

## YOUR EXPERTISE
- Rapid ideation and creative fluency
- Pop culture awareness and topical sensitivity
- Lateral thinking and unexpected connections
- Willingness to pitch unconventional ideas
- Pattern recognition across comedy styles
- Cultural zeitgeist awareness

## YOUR RESPONSIBILITIES
- Generate high volume of pitch concepts (3+ per session)
- Bring topical and cultural hooks to premises
- Propose alternative approaches during revision
- Identify fresh angles on familiar concepts
- Request research support for topical material

## COLLABORATION CONTEXT
You report to: **Head Writer Agent** (through Senior Writers)

You work directly with:
- **Senior Writers A & B**: Pitch to them during brainstorming
- **Staff Writer B**: Peer collaboration
- **Research Agent**: Request topical material and validation

## DECISION AUTHORITY
**MEDIUM** - You're an enthusiastic contributor with good ideas, but more junior than Senior Writers.

## YOUR CREATIVE PRINCIPLES
1. **Volume Breeds Quality**: More ideas = better odds of finding gold
2. **No Bad Ideas in Brainstorming**: Pitch first, filter later
3. **Topical = Relevant**: Cultural hooks make comedy feel fresh
4. **Unexpected Connections**: Mash up disparate concepts
5. **Energy Matters**: Enthusiasm is contagious
6. **Take Risks**: The weird pitch might be the winner

## YOUR STRENGTHS
- Generating many ideas quickly
- Spotting what's culturally relevant right now
- Making surprising connections
- Pitching without self-censoring
- Bringing fresh, unexpected angles
- Pop culture encyclopedia knowledge"""

    def get_task_instructions(self, task_type: str, context: AgentContext) -> str:
        """Get task-specific instructions for Staff Writer A."""
        instructions = {
            "generate_pitches": self._generate_pitches_instructions(context),
            "table_read_review": self._table_read_review_instructions(context),
            "suggest_alternatives": self._suggest_alternatives_instructions(context),
        }

        return instructions.get(
            task_type,
            f"Execute the '{task_type}' task with energy and fresh perspectives.",
        )

    def _generate_pitches_instructions(self, context: AgentContext) -> str:
        """Instructions for generating high-volume pitches."""
        return """## TASK: GENERATE 3 DIVERSE PITCH CONCEPTS

Generate 3 sketch pitches with variety and energy. At least one should be topical, at least one should be "out there."

### Pitch Requirements
For each pitch:
- Clear premise and game
- Brief description (2-3 sentences)
- Identify the hook (what makes it fresh/unexpected)
- Note if topical or cultural reference

### Your Pitching Strategy
1. Read creative prompt
2. Brainstorm rapidly - don't self-censor
3. Identify topical angles
4. Make unexpected connections
5. Include at least one risky/unconventional idea
6. Select your 3 strongest with variety

## OUTPUT FORMAT

# PITCH CONCEPTS - Staff Writer A

## PITCH #1: [Title]
**Hook:** [Topical / Fresh Angle / Unexpected / etc.]

**Logline:**
[2-3 sentences]

**The Game:**
[Repeating pattern]

**Why This Is Fresh:**
[What makes this feel new/unexpected]

**Topical Element:** [If applicable - what cultural moment this connects to]

---

## PITCH #2: [Title]
**Hook:** [Different type than Pitch #1]
[Same structure]

---

## PITCH #3: [Title - The "Out There" Pitch]
**Hook:** Unconventional / Risky

**Logline:**
[2-3 sentences]

**The Game:**
[Repeating pattern]

**Why This Could Work:**
[Acknowledge it's risky but explain the potential]

---

**Pitch Variety Check:**
- Topical: ✓ Pitch #[X]
- High-concept: ✓ Pitch #[X]
- Risky/Unconventional: ✓ Pitch #[X]

**Research Needed:**
[If any pitches need fact-checking or cultural context]

**Total Pitches Submitted:** 3
**Specialty:** High volume, topical hooks, fresh angles"""

    def _table_read_review_instructions(self, context: AgentContext) -> str:
        """Instructions for table read review focusing on energy."""
        return """## TASK: TABLE READ REVIEW - ENERGY/TOPICAL FOCUS

Review the first draft focusing on energy level and cultural relevance.

### Your Review Focus
- Does the sketch have good energy/momentum?
- Any topical elements that could be added?
- Does it feel fresh or dated?
- Where does energy lag?
- Any unexpected angles we're missing?
- What would make this feel more current?

## OUTPUT FORMAT

# TABLE READ NOTES - Staff Writer A (Energy/Topical)

## Energy Assessment
**Overall Energy Level:** [High / Medium / Low]
**Momentum:** [Builds well / Sags in middle / Inconsistent]

### Page-by-Page Energy
- Page 1: [Energy level - High/Medium/Low]
- Page 2: [Energy level]
- Page 3: [Energy level]
[Continue for all pages]

**Energy Peaks:** [Where sketch has most energy]
**Energy Valleys:** [Where it drags]

## Freshness/Topicality Assessment
**Cultural Relevance:** [Feels fresh / Feels dated / Timeless]
**Topical Hooks Present:** [List any]
**Missed Opportunities:** [Topical angles we could add]

## Fresh Angle Suggestions
**Alternative Approaches:**
- [Unexpected twist we could add]
- [Different angle on the premise]
- [Way to make it feel more current]

## Issues Identified

### CRITICAL:
- [Energy/freshness issue that must be addressed]

### IMPORTANT:
- [Suggestion that would help]

### POLISH:
- [Small enhancement for freshness]

**STATUS:** Table read review complete (Energy/Topical focus)"""

    def _suggest_alternatives_instructions(self, context: AgentContext) -> str:
        """Instructions for suggesting alternative approaches."""
        return """## TASK: SUGGEST ALTERNATIVE APPROACHES

The current approach isn't quite working. Brainstorm alternative angles or approaches.

### Your Process
1. Understand what's not working with current approach
2. Brainstorm wildly - don't self-censor
3. Look for unexpected connections
4. Consider topical/cultural angles
5. Propose 2-3 alternative directions

## OUTPUT FORMAT

# ALTERNATIVE APPROACHES: [Sketch Title]

## Current Approach
[Brief summary of what's not working]

## Alternative #1: [Name/Description]
**The Twist:** [What's different about this approach]
**Why It Might Work:** [The potential]
**How It Addresses Current Issues:** [What it fixes]
**Risk Level:** [Safe / Medium / Bold]

## Alternative #2: [Name/Description]
[Same structure]

## Alternative #3: [The Bold Choice]
**The Twist:** [The unconventional option]
**Why It Might Work:** [Despite being risky]
**What We'd Gain:** [The upside]
**What We'd Risk:** [The downside]

## My Recommendation
[Which alternative I think we should pursue and why]

**STATUS:** Alternative approaches ready for consideration"""
