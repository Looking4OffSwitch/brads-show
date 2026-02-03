"""
Research Agent - Facts and cultural context.

The Research Agent fact-checks references and claims, provides cultural context,
gathers supporting material, identifies problematic references, and suggests
richer specific details.
"""

import logging
from typing import Any, Optional

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

    Note: System prompts and task instructions are now loaded from
    config/agents/research.md when agent_loader is configured.
    """

    def __init__(
        self,
        config: Config,
        llm: Optional[LLMInterface] = None,
        agent_loader: Optional[Any] = None,
    ) -> None:
        """
        Initialize Research agent.

        Args:
            config: System configuration
            llm: Optional LLM interface
            agent_loader: Optional AgentLoader for loading from markdown configs
        """
        super().__init__(AgentRole.RESEARCH, config, llm, agent_loader)
