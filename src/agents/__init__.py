"""
Agent implementations for the sketch comedy writing system.

Contains 10 specialized agents:
- Leadership: Showrunner, Head Writer
- Creative: Senior Writer A, Senior Writer B, Staff Writer A, Staff Writer B
- Support: Story Editor, Research Agent
- QA: Script Coordinator, Quality Assurance
"""

from src.agents.base import AgentContext, AgentOutput, AgentRole, BaseAgent
from src.agents.head_writer import HeadWriterAgent
from src.agents.qa import QAAgent
from src.agents.research import ResearchAgent
from src.agents.script_coordinator import ScriptCoordinatorAgent
from src.agents.senior_writer_a import SeniorWriterA
from src.agents.senior_writer_b import SeniorWriterB
from src.agents.showrunner import ShowrunnerAgent
from src.agents.staff_writer_a import StaffWriterA
from src.agents.staff_writer_b import StaffWriterB
from src.agents.story_editor import StoryEditorAgent

__all__ = [
    "AgentContext",
    "AgentOutput",
    "AgentRole",
    "BaseAgent",
    "HeadWriterAgent",
    "QAAgent",
    "ResearchAgent",
    "ScriptCoordinatorAgent",
    "SeniorWriterA",
    "SeniorWriterB",
    "ShowrunnerAgent",
    "StaffWriterA",
    "StaffWriterB",
    "StoryEditorAgent",
]
