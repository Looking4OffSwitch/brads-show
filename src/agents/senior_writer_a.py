"""
Senior Writer A - Premise and character expert.
"""

import logging
from typing import Any, Optional

from src.agents.base import AgentContext, AgentRole, BaseAgent
from src.utils.config import Config
from src.utils.llm import LLMInterface

logger = logging.getLogger(__name__)


class SeniorWriterA(BaseAgent):
    """
    SeniorWriterA.

    Note: System prompts and task instructions are now loaded from
    config/agents/senior_writer_a.md when agent_loader is configured.
    """

    def __init__(
        self,
        config: Config,
        llm: Optional[LLMInterface] = None,
        agent_loader: Optional[Any] = None,
    ) -> None:
        """
        Initialize SeniorWriterA.

        Args:
            config: System configuration
            llm: Optional LLM interface
            agent_loader: Optional AgentLoader for loading from markdown configs
        """
        super().__init__(AgentRole.SENIOR_WRITER_A, config, llm, agent_loader)
