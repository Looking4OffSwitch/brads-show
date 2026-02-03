"""
Quality Assurance Agent - Final validation and quality assessment.

The QA Agent performs comprehensive final review, validates integration of all
agents' work, checks against quality criteria, and provides readiness assessment.
"""

import logging
from typing import Any, Optional

from src.agents.base import AgentContext, AgentRole, BaseAgent
from src.utils.config import Config
from src.utils.llm import LLMInterface

logger = logging.getLogger(__name__)


class QAAgent(BaseAgent):
    """
    Quality Assurance Agent - Final Validation.

    Responsibilities:
    - Perform final comprehensive review of formatted script
    - Validate all previous agents' work is properly integrated
    - Check against quality criteria checklist
    - Ensure sketch meets minimum standards
    - Flag any remaining issues or gaps
    - Provide confidence score and readiness assessment
    - Gate progression to human review

    Note: System prompts and task instructions are now loaded from
    config/agents/qa.md when agent_loader is configured.
    """

    def __init__(
        self,
        config: Config,
        llm: Optional[LLMInterface] = None,
        agent_loader: Optional[Any] = None,
    ) -> None:
        """
        Initialize QA agent.

        Args:
            config: System configuration
            llm: Optional LLM interface
            agent_loader: Optional AgentLoader for loading from markdown configs
        """
        super().__init__(AgentRole.QA, config, llm, agent_loader)
