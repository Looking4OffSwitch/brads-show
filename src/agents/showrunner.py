"""
Showrunner Agent - Final creative authority for the sketch comedy system.

The Showrunner makes final decisions on all creative matters, maintains
show identity, and approves scripts for production.
"""

import logging
from typing import Any, Optional

from src.agents.base import AgentContext, AgentRole, BaseAgent
from src.utils.config import Config
from src.utils.llm import LLMInterface

logger = logging.getLogger(__name__)


class ShowrunnerAgent(BaseAgent):
    """
    The Showrunner Agent - ultimate creative authority.

    Responsibilities:
    - Review pitch concepts and select which to develop
    - Provide creative vision and direction for chosen sketches
    - Review first drafts and flag major issues
    - Make final approval decisions on completed scripts
    - Arbitrate disagreements between other agents
    - Maintain show identity and quality standards

    Note: System prompts and task instructions are now loaded from
    config/agents/showrunner.md when agent_loader is configured.
    """

    def __init__(
        self,
        config: Config,
        llm: Optional[LLMInterface] = None,
        agent_loader: Optional[Any] = None,
    ) -> None:
        """
        Initialize Showrunner agent.

        Args:
            config: System configuration
            llm: Optional LLM interface
            agent_loader: Optional AgentLoader for loading from markdown configs
        """
        super().__init__(AgentRole.SHOWRUNNER, config, llm, agent_loader)
