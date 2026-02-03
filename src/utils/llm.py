"""
LLM interface for the sketch comedy writing system.

Provides unified interface to Anthropic and OpenAI providers with:
- Automatic retry logic with exponential backoff
- Token usage tracking
- Async and sync call support
- Model tier selection (creative vs support)
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.utils.config import Config, LLMConfig

# Configure module logger
logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model tier selection for different agent types."""

    CREATIVE = "creative"  # Senior roles: Sonnet/GPT-4
    SUPPORT = "support"  # Junior roles: Haiku/GPT-3.5


@dataclass
class TokenUsage:
    """Tracks token usage across LLM calls."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    call_count: int = 0

    def add(self, prompt_tokens: int, completion_tokens: int, total_tokens: int) -> None:
        """
        Add token counts from a single LLM call.

        Args:
            prompt_tokens: Number of input tokens.
            completion_tokens: Number of output tokens.
            total_tokens: Total tokens used.
        """
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens += total_tokens
        self.call_count += 1
        logger.debug(
            "Token usage updated: +%d prompt, +%d completion (total: %d)",
            prompt_tokens,
            completion_tokens,
            self.total_tokens,
        )

    def reset(self) -> None:
        """Reset all counters to zero."""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.call_count = 0
        logger.debug("Token usage counters reset")

    def __str__(self) -> str:
        return (
            f"TokenUsage(calls={self.call_count}, "
            f"prompt={self.prompt_tokens}, "
            f"completion={self.completion_tokens}, "
            f"total={self.total_tokens})"
        )


@dataclass
class LLMResponse:
    """Response from an LLM call with metadata."""

    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    raw_response: Optional[Any] = None

    def __str__(self) -> str:
        return f"LLMResponse(model={self.model}, tokens={self.total_tokens})"


class LLMInterface(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: LLMConfig) -> None:
        """
        Initialize LLM interface.

        Args:
            config: LLM configuration with API keys and model names.
        """
        self.config = config
        self.usage = TokenUsage()
        logger.info("Initialized %s LLM interface", self.__class__.__name__)

    @abstractmethod
    def get_model(self, tier: ModelTier) -> Any:
        """
        Get LangChain model instance for the specified tier.

        Args:
            tier: Model tier (CREATIVE or SUPPORT).

        Returns:
            LangChain chat model instance.
        """
        pass

    @abstractmethod
    async def acall(
        self,
        messages: list[BaseMessage],
        tier: ModelTier = ModelTier.CREATIVE,
        *,
        run_name: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> LLMResponse:
        """
        Make async LLM call with messages.

        Args:
            messages: List of LangChain messages.
            tier: Model tier to use.
            run_name: Optional name for this run in LangSmith tracing.
            tags: Optional tags for filtering in LangSmith.
            metadata: Optional key-value metadata for the trace.

        Returns:
            LLMResponse with content and usage metadata.
        """
        pass

    def call(
        self,
        messages: list[BaseMessage],
        tier: ModelTier = ModelTier.CREATIVE,
        *,
        run_name: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> LLMResponse:
        """
        Make sync LLM call with messages.

        Args:
            messages: List of LangChain messages.
            tier: Model tier to use.
            run_name: Optional name for this run in LangSmith tracing.
            tags: Optional tags for filtering in LangSmith.
            metadata: Optional key-value metadata for the trace.

        Returns:
            LLMResponse with content and usage metadata.
        """
        return asyncio.run(
            self.acall(messages, tier, run_name=run_name, tags=tags, metadata=metadata)
        )

    def get_usage(self) -> TokenUsage:
        """Get current token usage statistics."""
        return self.usage

    def reset_usage(self) -> None:
        """Reset token usage counters."""
        self.usage.reset()


class AnthropicLLM(LLMInterface):
    """Anthropic Claude LLM interface."""

    def __init__(self, config: LLMConfig) -> None:
        """
        Initialize Anthropic LLM interface.

        Args:
            config: LLM configuration with Anthropic API key.
        """
        super().__init__(config)

        # Initialize models for each tier
        self._creative_model = ChatAnthropic(
            model=config.creative_model,
            api_key=config.api_key,
            max_tokens=4096,
            temperature=0.7,  # Higher creativity for creative roles
        )
        self._support_model = ChatAnthropic(
            model=config.support_model,
            api_key=config.api_key,
            max_tokens=4096,
            temperature=0.3,  # More deterministic for support roles
        )

        logger.info(
            "Anthropic models initialized: creative=%s, support=%s",
            config.creative_model,
            config.support_model,
        )

    def get_model(self, tier: ModelTier) -> ChatAnthropic:
        """Get Anthropic model for specified tier."""
        if tier == ModelTier.CREATIVE:
            return self._creative_model
        return self._support_model

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        before_sleep=lambda retry_state: logger.warning(
            "Anthropic API call failed, retrying (attempt %d)...",
            retry_state.attempt_number,
        ),
    )
    async def acall(
        self,
        messages: list[BaseMessage],
        tier: ModelTier = ModelTier.CREATIVE,
        *,
        run_name: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> LLMResponse:
        """
        Make async call to Anthropic Claude.

        Args:
            messages: List of LangChain messages.
            tier: Model tier to use.
            run_name: Optional name for this run in LangSmith tracing.
            tags: Optional tags for filtering in LangSmith.
            metadata: Optional key-value metadata for the trace.

        Returns:
            LLMResponse with content and usage metadata.
        """
        model = self.get_model(tier)
        model_name = (
            self.config.creative_model if tier == ModelTier.CREATIVE else self.config.support_model
        )

        logger.debug("Calling Anthropic %s with %d messages", model_name, len(messages))

        # Build config for LangSmith tracing
        invoke_config: dict[str, Any] = {}
        if run_name:
            invoke_config["run_name"] = run_name
        if tags:
            invoke_config["tags"] = tags
        if metadata:
            invoke_config["metadata"] = metadata

        # Add model info to metadata for tracing
        if invoke_config:
            if "metadata" not in invoke_config:
                invoke_config["metadata"] = {}
            invoke_config["metadata"]["model_tier"] = tier.value
            invoke_config["metadata"]["model_name"] = model_name

        # Make the call with or without config
        if invoke_config:
            response = await model.ainvoke(messages, config=invoke_config)
        else:
            response = await model.ainvoke(messages)

        # Extract token usage from response metadata
        usage_metadata = getattr(response, "usage_metadata", {}) or {}
        prompt_tokens = usage_metadata.get("input_tokens", 0)
        completion_tokens = usage_metadata.get("output_tokens", 0)
        total_tokens = prompt_tokens + completion_tokens

        # Update usage tracking
        self.usage.add(prompt_tokens, completion_tokens, total_tokens)

        logger.debug(
            "Anthropic response: %d chars, %d tokens",
            len(response.content),
            total_tokens,
        )

        return LLMResponse(
            content=response.content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model=model_name,
            raw_response=response,
        )


class OpenAILLM(LLMInterface):
    """OpenAI GPT LLM interface."""

    def __init__(self, config: LLMConfig) -> None:
        """
        Initialize OpenAI LLM interface.

        Args:
            config: LLM configuration with OpenAI API key.
        """
        super().__init__(config)

        # Initialize models for each tier
        self._creative_model = ChatOpenAI(
            model=config.creative_model,
            api_key=config.api_key,
            max_tokens=4096,
            temperature=0.7,
        )
        self._support_model = ChatOpenAI(
            model=config.support_model,
            api_key=config.api_key,
            max_tokens=4096,
            temperature=0.3,
        )

        logger.info(
            "OpenAI models initialized: creative=%s, support=%s",
            config.creative_model,
            config.support_model,
        )

    def get_model(self, tier: ModelTier) -> ChatOpenAI:
        """Get OpenAI model for specified tier."""
        if tier == ModelTier.CREATIVE:
            return self._creative_model
        return self._support_model

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        before_sleep=lambda retry_state: logger.warning(
            "OpenAI API call failed, retrying (attempt %d)...",
            retry_state.attempt_number,
        ),
    )
    async def acall(
        self,
        messages: list[BaseMessage],
        tier: ModelTier = ModelTier.CREATIVE,
        *,
        run_name: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> LLMResponse:
        """
        Make async call to OpenAI GPT.

        Args:
            messages: List of LangChain messages.
            tier: Model tier to use.
            run_name: Optional name for this run in LangSmith tracing.
            tags: Optional tags for filtering in LangSmith.
            metadata: Optional key-value metadata for the trace.

        Returns:
            LLMResponse with content and usage metadata.
        """
        model = self.get_model(tier)
        model_name = (
            self.config.creative_model if tier == ModelTier.CREATIVE else self.config.support_model
        )

        logger.debug("Calling OpenAI %s with %d messages", model_name, len(messages))

        # Build config for LangSmith tracing
        invoke_config: dict[str, Any] = {}
        if run_name:
            invoke_config["run_name"] = run_name
        if tags:
            invoke_config["tags"] = tags
        if metadata:
            invoke_config["metadata"] = metadata

        # Add model info to metadata for tracing
        if invoke_config:
            if "metadata" not in invoke_config:
                invoke_config["metadata"] = {}
            invoke_config["metadata"]["model_tier"] = tier.value
            invoke_config["metadata"]["model_name"] = model_name

        # Make the call with or without config
        if invoke_config:
            response = await model.ainvoke(messages, config=invoke_config)
        else:
            response = await model.ainvoke(messages)

        # Extract token usage from response metadata
        usage_metadata = getattr(response, "usage_metadata", {}) or {}
        prompt_tokens = usage_metadata.get("input_tokens", 0)
        completion_tokens = usage_metadata.get("output_tokens", 0)
        total_tokens = usage_metadata.get("total_tokens", prompt_tokens + completion_tokens)

        # Update usage tracking
        self.usage.add(prompt_tokens, completion_tokens, total_tokens)

        logger.debug(
            "OpenAI response: %d chars, %d tokens",
            len(response.content),
            total_tokens,
        )

        return LLMResponse(
            content=response.content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model=model_name,
            raw_response=response,
        )


def get_llm(config: Optional[Config] = None) -> LLMInterface:
    """
    Get LLM interface based on configuration.

    This is the primary factory function for obtaining an LLM interface.
    It automatically selects the appropriate provider based on configuration.

    Args:
        config: Optional Config object. If None, loads default configuration.

    Returns:
        LLMInterface implementation for the configured provider.

    Raises:
        ValueError: If provider is not supported.

    Example:
        >>> llm = get_llm()
        >>> response = llm.call([HumanMessage(content="Hello")])
        >>> print(response.content)
    """
    if config is None:
        from src.utils.config import load_config

        config = load_config()

    llm_config = config.llm

    if llm_config.provider == "anthropic":
        logger.info("Creating Anthropic LLM interface")
        return AnthropicLLM(llm_config)
    elif llm_config.provider == "openai":
        logger.info("Creating OpenAI LLM interface")
        return OpenAILLM(llm_config)
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_config.provider}")


def create_messages(
    system_prompt: str,
    user_prompt: str,
    conversation_history: Optional[list[dict[str, str]]] = None,
) -> list[BaseMessage]:
    """
    Create a list of LangChain messages from prompts.

    Helper function to construct message lists for LLM calls.

    Args:
        system_prompt: System message content (agent identity/instructions).
        user_prompt: User message content (current task).
        conversation_history: Optional list of previous messages as dicts
            with "role" and "content" keys.

    Returns:
        List of LangChain BaseMessage objects.

    Example:
        >>> messages = create_messages(
        ...     system_prompt="You are a helpful assistant.",
        ...     user_prompt="Write a joke.",
        ... )
        >>> len(messages)
        2
    """
    messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]

    # Add conversation history if provided
    if conversation_history:
        for msg in conversation_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

    # Add current user prompt
    messages.append(HumanMessage(content=user_prompt))

    logger.debug("Created %d messages for LLM call", len(messages))
    return messages
