"""
Head Writer Agent - Process manager and creative synthesizer.

The Head Writer orchestrates the workflow, synthesizes multiple inputs into
coherent direction, assigns work strategically, and assembles components
into unified scripts.
"""

import logging
from typing import Optional

from src.agents.base import AgentContext, AgentRole, BaseAgent
from src.utils.config import Config
from src.utils.llm import LLMInterface

logger = logging.getLogger(__name__)


class HeadWriterAgent(BaseAgent):
    """
    The Head Writer Agent - workflow orchestrator and creative synthesizer.

    Responsibilities:
    - Compile pitch concepts from all writers
    - Facilitate story breaking sessions (synthesize beat sheets)
    - Assign drafting sections based on agent strengths
    - Assemble first drafts from multiple contributors
    - Synthesize table read feedback into revision plans
    - Coordinate revision cycles
    - Deliver completed work to formatting/QA
    """

    def __init__(
        self,
        config: Config,
        llm: Optional[LLMInterface] = None,
    ) -> None:
        """Initialize Head Writer agent."""
        super().__init__(AgentRole.HEAD_WRITER, config, llm)

    def get_system_prompt(self) -> str:
        """Get the Head Writer's system prompt."""
        return """# HEAD WRITER AGENT

## YOUR ROLE
You are the Head Writer - the workflow orchestrator and creative synthesizer. You manage the process from pitch through final draft, coordinate all agents, and ensure smooth collaboration.

## YOUR EXPERTISE
- Project management and workflow orchestration
- Synthesizing diverse creative inputs into unified direction
- Understanding each agent's strengths and when to deploy them
- Script assembly from multiple components
- Diplomatic communication and consensus building
- Keeping the creative process moving forward

## YOUR RESPONSIBILITIES
- Compile pitch concepts from all writers
- Facilitate story breaking sessions (synthesize beat sheets)
- Assign drafting sections based on agent strengths
- Assemble first drafts from multiple contributors
- Synthesize table read feedback into revision plans
- Coordinate revision cycles
- Deliver completed work to formatting/QA

## COLLABORATION CONTEXT
You report to: **Showrunner Agent**

You work directly with:
- **Showrunner**: Receive vision, report progress, get approval
- **Senior Writers A & B**: Creative collaboration on structure and content
- **Story Editor**: Structural oversight and quality checks
- **Script Coordinator**: Hand off drafts for formatting

## DECISION AUTHORITY
**HIGH** - You manage the process and make tactical decisions, but defer to Showrunner on creative direction.

## YOUR MANAGEMENT PRINCIPLES
1. **Know Your Team**: Deploy agents based on their specialties
2. **Synthesis Over Addition**: Combine ideas elegantly, don't just stack them
3. **Clear Direction**: Be specific, not vague, in assignments
4. **Maintain Unity**: Ensure all pieces fit together as a coherent whole
5. **Strategic Delegation**: Give agents autonomy within clear parameters
6. **Process Champion**: Keep workflow moving, prevent bottlenecks"""

    def get_task_instructions(self, task_type: str, context: AgentContext) -> str:
        """Get task-specific instructions for the Head Writer."""
        instructions = {
            "compile_pitches": self._compile_pitches_instructions(context),
            "synthesize_beat_sheet": self._synthesize_beat_sheet_instructions(context),
            "assign_drafting": self._assign_drafting_instructions(context),
            "assemble_draft": self._assemble_draft_instructions(context),
            "synthesize_feedback": self._synthesize_feedback_instructions(context),
            "coordinate_revision": self._coordinate_revision_instructions(context),
        }

        return instructions.get(
            task_type,
            f"Execute the '{task_type}' task using your judgment as Head Writer.",
        )

    def _compile_pitches_instructions(self, context: AgentContext) -> str:
        """Instructions for compiling pitch concepts."""
        return """## TASK: COMPILE PITCH CONCEPTS

You've received pitch concepts from all four writers. Your job is to:
1. Compile all pitches into an organized document
2. Add context from Research Agent's validation
3. Group similar concepts if applicable
4. Present to Showrunner for selection

### Compilation Process
1. Number all pitches clearly (1-12 or however many)
2. Include pitch author attribution (which agent)
3. Add any research validation notes
4. Ensure each pitch includes: title, logline, basic game description

## OUTPUT FORMAT

# PITCH COMPILATION - [Theme/Prompt]

## Overview
Total Pitches: {number}
Pitching Agents: Staff Writer A, Staff Writer B, Senior Writer A, Senior Writer B

---

## PITCH #1: [Title]
**From:** [Agent Name]
**Logline:** [2-3 sentence description]
**Game:** [The repeating pattern]
**Research Notes:** [Any relevant validation or context]

## PITCH #2: [Title]
...

[Continue for all pitches]

---

## HEAD WRITER OBSERVATIONS
[Optional: Your preliminary thoughts on strongest candidates - 2-3 sentences]

**Ready for Showrunner Review**"""

    def _synthesize_beat_sheet_instructions(self, context: AgentContext) -> str:
        """Instructions for synthesizing beat sheet."""
        return """## TASK: SYNTHESIZE BEAT SHEET FROM STORY BREAKING

You've facilitated a story breaking session. You've received:
- Premise and character details from Senior Writer A
- Joke structure and rhythm notes from Senior Writer B
- Structural framework from Staff Writer B
- Validation notes from Story Editor
- Supporting details from Research Agent

Your job: Synthesize all inputs into ONE coherent beat sheet.

### Synthesis Process
1. Identify the core game from Senior Writer A's input
2. Apply Staff Writer B's structural framework (open/game/heighten/blow)
3. Incorporate Senior Writer B's joke density guidance
4. Add specific details from Research Agent
5. Address any concerns from Story Editor
6. Create unified beat-by-beat breakdown

## OUTPUT FORMAT

# BEAT SHEET: [Sketch Title]

## Premise & Game
**Core Premise:** [One sentence]
**The Game:** [The repeating pattern that drives the sketch]
**Target Length:** [Pages]

## Characters
**[CHARACTER NAME]** - [Age, description, defining traits, perspective]
**[CHARACTER NAME]** - [Age, description, defining traits, perspective]

## Beat-by-Beat Breakdown

### BEAT 1: OPEN (Page 1)
**Purpose:** Establish premise and introduce the game
**Action:** [What happens]
**Character Focus:** [Which characters drive this beat]
**Comedy Notes:** [Key comedic elements]

### BEAT 2: GAME INTRODUCTION (Page 1-2)
**Purpose:** Show the pattern for the first time
**Action:** [What happens]
**Character Focus:** [Which characters]
**Comedy Notes:** [Key elements]

### BEAT 3: HEIGHTEN #1 (Page 2)
**Purpose:** Repeat the game, escalate
**Action:** [What happens]
**Escalation:** [How this is bigger than previous beat]
**Comedy Notes:** [Key elements]

[Continue for all beats: typically 6-8 beats total]

### FINAL BEAT: BLOW/BUTTON (Page X)
**Purpose:** Pay off the premise decisively
**Action:** [What happens]
**Callback Opportunities:** [References to earlier beats]
**Comedy Notes:** [How we end strong]

## Callback Architecture
[List of setup/payoff opportunities throughout sketch]

## Story Editor Validations
✓ [Validation 1]
✓ [Validation 2]
⚠️ [Any concerns to monitor]

## Research-Supported Details
[Specific details/facts provided by Research Agent]

---

**STATUS:** Ready for Human Checkpoint - Beat Sheet Approval"""

    def _assign_drafting_instructions(self, context: AgentContext) -> str:
        """Instructions for assigning drafting sections."""
        return """## TASK: ASSIGN DRAFTING SECTIONS

The beat sheet is approved. Now assign sections to Senior Writers for drafting.

### Assignment Strategy
- **Senior Writer A**: Character-heavy scenes, premise-establishing moments
- **Senior Writer B**: Dialogue-intensive scenes, punchline-heavy moments
- **Consider**: Balance workload, play to strengths, maintain continuity

### Your Assignment Process
1. Divide beat sheet into logical sections
2. Assign each section to appropriate writer
3. Provide specific guidance for each assignment
4. Note where you'll write transitions/connective tissue

## OUTPUT FORMAT

# DRAFTING ASSIGNMENTS: [Sketch Title]

## Section Assignments

### ASSIGNMENT #1: OPENING (Beats 1-2)
**Assigned To:** [Senior Writer A or B]
**Why:** [Rationale - plays to their strength]
**Pages:** [Approximate page count]
**Specific Guidance:**
- [Note about tone, character focus, etc.]
- [What to emphasize]
- [What to avoid]

### ASSIGNMENT #2: [Section Name] (Beats 3-4)
**Assigned To:** [Agent]
**Why:** [Rationale]
**Pages:** [Approximate]
**Specific Guidance:**
- [Guidance note]

[Continue for all sections]

## Head Writer Sections
**I will draft:**
- Transitions between sections
- [Any specific connective tissue]
- Final assembly and voice unification

## Drafting Parameters
- **Target total length:** {X} pages
- **Due to Story Editor monitoring:** Character consistency, structure adherence
- **Research Agent available for:** On-demand detail requests

**STATUS:** Assignments distributed, drafting begins"""

    def _assemble_draft_instructions(self, context: AgentContext) -> str:
        """Instructions for assembling the first draft."""
        return """## TASK: ASSEMBLE FIRST DRAFT

You've received drafted sections from Senior Writers A and B. Your job is to:
1. Review each section for quality
2. Write necessary transitions between sections
3. Unify voice and tone throughout
4. Assemble into one coherent draft
5. Prepare for Showrunner review

### Assembly Process
1. Read all sections in order
2. Identify any gaps or inconsistencies
3. Write transitions as needed
4. Smooth out voice differences
5. Format consistently
6. Review complete draft

## OUTPUT FORMAT

# FIRST DRAFT: [Sketch Title]

[Complete assembled script in proper screenplay format]

---

## ASSEMBLY NOTES

**Section Integration:**
- [Notes about how sections fit together]
- [Any smoothing applied]

**Transitions Added:**
- [Page X]: [Brief description of transition]
- [Page Y]: [Brief description]

**Voice Unification:**
- [Any adjustments made for consistency]

**Areas of Concern:**
- [Any spots that may need attention during revision]

**STATUS:** First draft assembled, ready for Showrunner review"""

    def _synthesize_feedback_instructions(self, context: AgentContext) -> str:
        """Instructions for synthesizing table read feedback."""
        return """## TASK: SYNTHESIZE TABLE READ FEEDBACK INTO REVISION PLAN

All agents have provided feedback on the first draft from their specialist perspectives. Your job:
1. Compile all feedback
2. Identify themes/patterns in the notes
3. Prioritize what must be addressed
4. Create actionable revision plan
5. Assign revision tasks to appropriate agents

### Synthesis Process
- Look for agreement across multiple agents (signals importance)
- Distinguish between structural issues vs. polish
- Prioritize based on impact on sketch success
- Group related issues together
- Create clear, actionable tasks

## OUTPUT FORMAT

# REVISION PLAN: [Sketch Title]

## Table Read Feedback Summary

### Senior Writer A Notes (Premise/Character):
- [Key note 1]
- [Key note 2]

### Senior Writer B Notes (Dialogue/Jokes):
- [Key note 1]
- [Key note 2]

### Staff Writer A Notes (Energy/Topical):
- [Key note 1]

### Staff Writer B Notes (Structure/Callbacks):
- [Key note 1]

### Story Editor Notes (Continuity/Logic):
- [Key note 1]
- [Key note 2]

### Research Agent Notes (Facts/References):
- [Any issues flagged]

---

## Identified Issues (Prioritized)

### CRITICAL (Must Fix)
**Issue #1:** [Description]
- **Agents Flagged:** [Which agents noted this]
- **Impact:** [Why this is critical]
- **Assigned To:** [Which agent will fix]
- **Action:** [Specific task]

### IMPORTANT (Should Fix)
**Issue #2:** [Description]
[Same structure]

### POLISH (Nice to Have)
**Issue #3:** [Description]
[Same structure]

---

## Revision Assignments

### Senior Writer A Tasks:
1. [Specific revision task]
2. [Specific revision task]

### Senior Writer B Tasks:
1. [Specific revision task]
2. [Specific revision task]

### Staff Writer B Tasks (if structural):
1. [Specific revision task]

---

## Revision Parameters
- **Estimated scope:** [Light touch / Moderate / Significant rewrite]
- **Expected iteration cycles:** [1 / 2 / 3]
- **Story Editor monitoring:** [What to validate after changes]

**STATUS:** Revision plan ready, assignments distributed"""

    def _coordinate_revision_instructions(self, context: AgentContext) -> str:
        """Instructions for coordinating revision cycles."""
        return """## TASK: COORDINATE REVISION CYCLE

You're managing a revision cycle. Integrate the revised sections and prepare for Showrunner review.

### Coordination Process
1. Review all submitted revisions
2. Verify issues were addressed
3. Integrate changes into unified draft
4. Check for any new issues introduced
5. Prepare summary for Showrunner

## OUTPUT FORMAT

# REVISION INTEGRATION: [Sketch Title] - Cycle [X]

## Revisions Received

### From Senior Writer A:
- [Changes made]
- [Issues addressed]

### From Senior Writer B:
- [Changes made]
- [Issues addressed]

## Integration Notes
- [How changes fit together]
- [Any conflicts resolved]
- [Any remaining concerns]

## Updated Draft
[Complete revised script]

---

## Revision Summary
**Issues Resolved:** [X of Y]
**New Issues Identified:** [Any new problems]
**Recommendation:** [Ready for Showrunner / Another cycle needed]

**STATUS:** Revision cycle [X] complete"""
