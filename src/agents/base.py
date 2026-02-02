"""
Base agent class for the sketch comedy writing system.

Provides abstract base class with common functionality for all 10 agents:
- System prompt management
- Task prompt building
- LLM call execution with retry logic
- Output parsing
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from src.utils.config import Config
from src.utils.llm import LLMInterface, LLMResponse, ModelTier, create_messages, get_llm

# Configure module logger
logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Enumeration of all agent roles in the system."""

    # Leadership Tier
    SHOWRUNNER = "showrunner"
    HEAD_WRITER = "head_writer"

    # Creative Tier
    SENIOR_WRITER_A = "senior_writer_a"
    SENIOR_WRITER_B = "senior_writer_b"
    STAFF_WRITER_A = "staff_writer_a"
    STAFF_WRITER_B = "staff_writer_b"

    # Support Tier
    STORY_EDITOR = "story_editor"
    RESEARCH = "research"

    # QA Tier
    SCRIPT_COORDINATOR = "script_coordinator"
    QA = "qa"


# Map agent roles to model tiers
AGENT_MODEL_TIERS: dict[AgentRole, ModelTier] = {
    # Leadership uses creative tier (Sonnet)
    AgentRole.SHOWRUNNER: ModelTier.CREATIVE,
    AgentRole.HEAD_WRITER: ModelTier.CREATIVE,
    # Creative tier uses creative models (Sonnet)
    AgentRole.SENIOR_WRITER_A: ModelTier.CREATIVE,
    AgentRole.SENIOR_WRITER_B: ModelTier.CREATIVE,
    AgentRole.STAFF_WRITER_A: ModelTier.CREATIVE,
    AgentRole.STAFF_WRITER_B: ModelTier.CREATIVE,
    # Support tier uses support models (Haiku)
    AgentRole.STORY_EDITOR: ModelTier.SUPPORT,
    AgentRole.RESEARCH: ModelTier.SUPPORT,
    # QA tier uses support models (Haiku)
    AgentRole.SCRIPT_COORDINATOR: ModelTier.SUPPORT,
    AgentRole.QA: ModelTier.SUPPORT,
}


@dataclass
class AgentContext:
    """Context passed to agents for task execution."""

    show_bible: str
    creative_prompt: str
    task_type: str
    previous_output: Optional[str] = None
    direction_notes: Optional[str] = None
    additional_context: Optional[dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Initialize additional context if not provided."""
        if self.additional_context is None:
            self.additional_context = {}


@dataclass
class AgentOutput:
    """Structured output from an agent execution."""

    agent_role: AgentRole
    task_type: str
    content: str
    success: bool
    error_message: Optional[str] = None
    token_usage: Optional[dict[str, int]] = None
    metadata: Optional[dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}

    def __str__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"AgentOutput({self.agent_role.value}, {self.task_type}, {status})"


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the sketch comedy system.

    Provides common functionality for system prompt management, task prompt
    building, and LLM call execution. Subclasses must implement the
    get_system_prompt() and get_task_instructions() methods.

    Attributes:
        role: The agent's role in the system.
        config: System configuration.
        llm: LLM interface for making API calls.
        model_tier: Which model tier this agent uses (creative/support).
    """

    def __init__(
        self,
        role: AgentRole,
        config: Config,
        llm: Optional[LLMInterface] = None,
    ) -> None:
        """
        Initialize base agent.

        Args:
            role: The agent's role in the system.
            config: System configuration.
            llm: Optional LLM interface. If None, creates one from config.
        """
        self.role = role
        self.config = config
        self.llm = llm or get_llm(config)
        self.model_tier = AGENT_MODEL_TIERS.get(role, ModelTier.SUPPORT)

        logger.info(
            "Initialized %s agent (tier: %s)",
            role.value,
            self.model_tier.value,
        )

    @property
    def name(self) -> str:
        """Human-readable name for this agent."""
        return self.role.value.replace("_", " ").title()

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        The system prompt defines the agent's identity, expertise,
        responsibilities, and decision authority.

        Returns:
            Complete system prompt string.
        """
        pass

    @abstractmethod
    def get_task_instructions(self, task_type: str, context: AgentContext) -> str:
        """
        Get task-specific instructions for the agent.

        Builds the detailed instructions for a specific task type,
        incorporating context from the workflow state.

        Args:
            task_type: The type of task to perform.
            context: Context containing show bible, creative prompt, etc.

        Returns:
            Task-specific instruction string.
        """
        pass

    def build_prompt(self, context: AgentContext) -> tuple[str, str]:
        """
        Build complete system and user prompts for an LLM call.

        Combines the agent's system prompt with task-specific instructions
        and context.

        Args:
            context: Context for the current task.

        Returns:
            Tuple of (system_prompt, user_prompt).
        """
        system_prompt = self.get_system_prompt()
        task_instructions = self.get_task_instructions(context.task_type, context)

        # Build user prompt with all context
        user_parts = [
            f"## CURRENT TASK: {context.task_type}",
            "",
            "### Show Bible",
            context.show_bible,
            "",
            "### Creative Prompt",
            context.creative_prompt,
        ]

        if context.previous_output:
            user_parts.extend(
                [
                    "",
                    "### Previous Stage Output",
                    context.previous_output,
                ]
            )

        if context.direction_notes:
            user_parts.extend(
                [
                    "",
                    "### Direction Notes",
                    context.direction_notes,
                ]
            )

        user_parts.extend(
            [
                "",
                "### Task Instructions",
                task_instructions,
            ]
        )

        user_prompt = "\n".join(user_parts)

        logger.debug(
            "Built prompt for %s: system=%d chars, user=%d chars",
            self.name,
            len(system_prompt),
            len(user_prompt),
        )

        return system_prompt, user_prompt

    async def execute(self, context: AgentContext) -> AgentOutput:
        """
        Execute the agent's task with given context.

        This is the main entry point for running an agent. It builds
        prompts, makes the LLM call, and returns structured output.

        Args:
            context: Context for the current task.

        Returns:
            AgentOutput with results and metadata.
        """
        logger.info(
            "Executing %s agent for task: %s",
            self.name,
            context.task_type,
        )

        try:
            # Build prompts
            system_prompt, user_prompt = self.build_prompt(context)

            # Create messages
            messages = create_messages(system_prompt, user_prompt)

            # Make LLM call
            response = await self.llm.acall(messages, tier=self.model_tier)

            logger.info(
                "%s agent completed: %d chars, %d tokens",
                self.name,
                len(response.content),
                response.total_tokens,
            )

            return AgentOutput(
                agent_role=self.role,
                task_type=context.task_type,
                content=response.content,
                success=True,
                token_usage={
                    "prompt_tokens": response.prompt_tokens,
                    "completion_tokens": response.completion_tokens,
                    "total_tokens": response.total_tokens,
                },
                metadata={
                    "model": response.model,
                },
            )

        except Exception as e:
            logger.error(
                "%s agent failed: %s",
                self.name,
                str(e),
                exc_info=True,
            )
            return AgentOutput(
                agent_role=self.role,
                task_type=context.task_type,
                content="",
                success=False,
                error_message=str(e),
            )

    def execute_sync(self, context: AgentContext) -> AgentOutput:
        """
        Synchronous wrapper for execute().

        Args:
            context: Context for the current task.

        Returns:
            AgentOutput with results and metadata.
        """
        import asyncio

        return asyncio.run(self.execute(context))


def get_agent_description(role: AgentRole) -> str:
    """
    Get a brief description of an agent's role.

    Args:
        role: The agent role to describe.

    Returns:
        Brief description string.
    """
    descriptions = {
        AgentRole.SHOWRUNNER: "Final creative authority and decision maker",
        AgentRole.HEAD_WRITER: "Process manager and creative synthesizer",
        AgentRole.SENIOR_WRITER_A: "Premise and character specialist",
        AgentRole.SENIOR_WRITER_B: "Dialogue and punch-up specialist",
        AgentRole.STAFF_WRITER_A: "High-volume pitch generator",
        AgentRole.STAFF_WRITER_B: "Structure and callback specialist",
        AgentRole.STORY_EDITOR: "Continuity and quality control",
        AgentRole.RESEARCH: "Facts and cultural context",
        AgentRole.SCRIPT_COORDINATOR: "Formatting and technical standards",
        AgentRole.QA: "Final validation and quality assurance",
    }
    return descriptions.get(role, "Unknown role")
