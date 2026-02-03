"""
Script Coordinator Agent - Formatting and technical standards.

The Script Coordinator formats scripts to industry standards, ensures consistency,
validates technical correctness, and assembles final drafts.
"""

import logging
from typing import Any, Optional

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

    Note: System prompts and task instructions are now loaded from
    config/agents/script_coordinator.md when agent_loader is configured.
    """

    def __init__(
        self,
        config: Config,
        llm: Optional[LLMInterface] = None,
        agent_loader: Optional[Any] = None,
    ) -> None:
        """
        Initialize Script Coordinator agent.

        Args:
            config: System configuration
            llm: Optional LLM interface
            agent_loader: Optional AgentLoader for loading from markdown configs
        """
        super().__init__(AgentRole.SCRIPT_COORDINATOR, config, llm, agent_loader)
