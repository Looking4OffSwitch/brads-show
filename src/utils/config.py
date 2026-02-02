"""
Configuration loader for the sketch comedy writing system.

Handles loading environment variables, show bible, and creative prompt files.
Provides validation and sensible defaults.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Configure module logger
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing required values."""

    pass


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""

    provider: str  # "anthropic" or "openai"
    api_key: str
    creative_model: str  # Model for creative roles (Sonnet)
    support_model: str  # Model for support roles (Haiku)

    def __post_init__(self) -> None:
        """Validate LLM configuration."""
        if not self.api_key:
            raise ConfigurationError(f"API key required for provider: {self.provider}")
        if not self.creative_model:
            raise ConfigurationError("Creative model not specified")
        if not self.support_model:
            raise ConfigurationError("Support model not specified")
        logger.debug(
            "LLM config validated: provider=%s, creative_model=%s, support_model=%s",
            self.provider,
            self.creative_model,
            self.support_model,
        )


@dataclass
class WorkflowConfig:
    """Configuration for workflow behavior."""

    max_revision_cycles: int = 3
    target_sketch_length: int = 5  # pages

    def __post_init__(self) -> None:
        """Validate workflow configuration."""
        if self.max_revision_cycles < 1:
            raise ConfigurationError("max_revision_cycles must be at least 1")
        if self.target_sketch_length < 1:
            raise ConfigurationError("target_sketch_length must be at least 1")
        logger.debug(
            "Workflow config: max_revisions=%d, target_length=%d pages",
            self.max_revision_cycles,
            self.target_sketch_length,
        )


@dataclass
class ShowConfig:
    """Configuration for the current show being worked on."""

    show_folder: str
    show_bible: str
    creative_prompt: str
    output_dir: Path

    def __post_init__(self) -> None:
        """Validate show configuration."""
        if not self.show_folder:
            raise ConfigurationError("show_folder is required")
        if not self.show_bible:
            raise ConfigurationError("show_bible content is empty")
        if not self.creative_prompt:
            raise ConfigurationError("creative_prompt content is empty")
        logger.debug("Show config loaded: folder=%s", self.show_folder)


@dataclass
class Config:
    """Complete configuration for the sketch comedy system."""

    llm: LLMConfig
    workflow: WorkflowConfig
    show: ShowConfig
    project_root: Path
    debug: bool = False

    # Optional monitoring configuration
    langsmith_enabled: bool = False
    langsmith_api_key: Optional[str] = None
    langsmith_project: str = "sketch-comedy-agents"


def _get_project_root() -> Path:
    """
    Determine the project root directory.

    Walks up from this file's location to find the project root
    (directory containing pyproject.toml or .env).

    Returns:
        Path to project root directory.

    Raises:
        ConfigurationError: If project root cannot be determined.
    """
    current = Path(__file__).resolve().parent
    markers = ["pyproject.toml", ".env", "CLAUDE.md"]

    # Walk up the directory tree
    for _ in range(10):  # Limit search depth
        for marker in markers:
            if (current / marker).exists():
                logger.debug("Found project root at: %s", current)
                return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    raise ConfigurationError(
        "Could not determine project root. Ensure pyproject.toml or .env exists."
    )


def _load_file_content(file_path: Path, description: str) -> str:
    """
    Load content from a file with error handling.

    Args:
        file_path: Path to the file to load.
        description: Human-readable description for error messages.

    Returns:
        Content of the file as a string.

    Raises:
        ConfigurationError: If file cannot be read.
    """
    logger.debug("Loading %s from: %s", description, file_path)

    if not file_path.exists():
        raise ConfigurationError(f"{description} not found: {file_path}")

    if not file_path.is_file():
        raise ConfigurationError(f"{description} is not a file: {file_path}")

    try:
        content = file_path.read_text(encoding="utf-8")
        if not content.strip():
            raise ConfigurationError(f"{description} is empty: {file_path}")
        logger.debug("Loaded %s (%d characters)", description, len(content))
        return content
    except UnicodeDecodeError as e:
        raise ConfigurationError(f"Cannot decode {description} as UTF-8: {e}") from e
    except OSError as e:
        raise ConfigurationError(f"Cannot read {description}: {e}") from e


def _detect_llm_provider() -> tuple[str, str, str, str]:
    """
    Detect which LLM provider is configured based on environment variables.

    Returns:
        Tuple of (provider_name, api_key, creative_model, support_model).

    Raises:
        ConfigurationError: If no valid provider configuration found.
    """
    # Check for Anthropic first (preferred)
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        creative = os.getenv("ANTHROPIC_MODEL_CREATIVE", "claude-sonnet-4-20250514")
        support = os.getenv("ANTHROPIC_MODEL_SUPPORT", "claude-3-5-haiku-20241022")
        logger.info("Using Anthropic provider")
        return ("anthropic", anthropic_key, creative, support)

    # Check for OpenAI as fallback
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        creative = os.getenv("OPENAI_MODEL_CREATIVE", "gpt-4")
        support = os.getenv("OPENAI_MODEL_SUPPORT", "gpt-3.5-turbo")
        logger.info("Using OpenAI provider")
        return ("openai", openai_key, creative, support)

    raise ConfigurationError(
        "No LLM provider configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env"
    )


def load_config(
    show_folder: Optional[str] = None,
    env_file: Optional[Path] = None,
    debug: bool = False,
) -> Config:
    """
    Load complete configuration for the sketch comedy system.

    This function loads environment variables, detects LLM provider,
    loads show-specific files (show_bible.md, creative_prompt.md),
    and validates all configuration.

    Args:
        show_folder: Override for SHOW_FOLDER env var. If None, uses env var.
        env_file: Path to .env file. If None, auto-detects from project root.
        debug: Enable debug mode with verbose logging.

    Returns:
        Complete Config object with all settings.

    Raises:
        ConfigurationError: If required configuration is missing or invalid.

    Example:
        >>> config = load_config()
        >>> print(config.show.show_folder)
        'test_show'

        >>> config = load_config(show_folder="my_show", debug=True)
        >>> print(config.debug)
        True
    """
    # Configure logging based on debug flag
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Loading configuration...")

    # Determine project root
    project_root = _get_project_root()
    logger.debug("Project root: %s", project_root)

    # Load environment variables
    if env_file is None:
        env_file = project_root / ".env"

    if env_file.exists():
        load_dotenv(env_file)
        logger.debug("Loaded environment from: %s", env_file)
    else:
        logger.warning("No .env file found at: %s", env_file)

    # Detect LLM provider
    provider, api_key, creative_model, support_model = _detect_llm_provider()
    llm_config = LLMConfig(
        provider=provider,
        api_key=api_key,
        creative_model=creative_model,
        support_model=support_model,
    )

    # Load workflow configuration
    max_revisions = int(os.getenv("MAX_REVISION_CYCLES", "3"))
    target_length = int(os.getenv("TARGET_SKETCH_LENGTH", "5"))
    workflow_config = WorkflowConfig(
        max_revision_cycles=max_revisions,
        target_sketch_length=target_length,
    )

    # Determine show folder
    if show_folder is None:
        show_folder = os.getenv("SHOW_FOLDER")
        if not show_folder:
            raise ConfigurationError(
                "SHOW_FOLDER not specified. Set in .env or pass to load_config()"
            )

    # Validate show folder exists
    shows_dir = project_root / "Shows"
    show_dir = shows_dir / show_folder
    if not show_dir.exists():
        available = [d.name for d in shows_dir.iterdir() if d.is_dir()]
        raise ConfigurationError(
            f"Show folder not found: {show_dir}\n"
            f"Available shows: {available if available else 'None'}"
        )

    # Load show files
    show_bible_path = show_dir / "show_bible.md"
    creative_prompt_path = show_dir / "creative_prompt.md"
    output_dir = show_dir / "output"

    show_bible = _load_file_content(show_bible_path, "show_bible.md")
    creative_prompt = _load_file_content(creative_prompt_path, "creative_prompt.md")

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.debug("Output directory: %s", output_dir)

    show_config = ShowConfig(
        show_folder=show_folder,
        show_bible=show_bible,
        creative_prompt=creative_prompt,
        output_dir=output_dir,
    )

    # Check for LangSmith monitoring
    langsmith_enabled = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
    langsmith_key = os.getenv("LANGCHAIN_API_KEY")
    langsmith_project = os.getenv("LANGCHAIN_PROJECT", "sketch-comedy-agents")

    if langsmith_enabled and not langsmith_key:
        logger.warning("LANGCHAIN_TRACING_V2 enabled but LANGCHAIN_API_KEY not set")
        langsmith_enabled = False

    # Build complete config
    config = Config(
        llm=llm_config,
        workflow=workflow_config,
        show=show_config,
        project_root=project_root,
        debug=debug,
        langsmith_enabled=langsmith_enabled,
        langsmith_api_key=langsmith_key,
        langsmith_project=langsmith_project,
    )

    logger.info(
        "Configuration loaded successfully: show=%s, provider=%s",
        show_folder,
        provider,
    )

    return config


def get_agent_prompts_path(config: Config) -> Path:
    """
    Get path to the agent prompts documentation file.

    Args:
        config: Loaded configuration object.

    Returns:
        Path to agent-prompts.md file.

    Raises:
        ConfigurationError: If file not found.
    """
    prompts_path = config.project_root / "Docs" / "agent-prompts.md"
    if not prompts_path.exists():
        raise ConfigurationError(f"Agent prompts file not found: {prompts_path}")
    return prompts_path
