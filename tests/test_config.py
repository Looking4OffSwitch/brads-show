"""
Unit tests for configuration loading and validation.

Tests the src/utils/config.py module including:
- Configuration dataclasses
- Environment variable loading
- Show file loading
- Validation and error handling
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.utils.config import (
    Config,
    ConfigurationError,
    LLMConfig,
    ShowConfig,
    WorkflowConfig,
    get_agent_prompts_path,
    load_config,
)


class TestLLMConfig:
    """Tests for LLMConfig dataclass."""

    def test_valid_anthropic_config(self):
        """Test valid Anthropic configuration."""
        config = LLMConfig(
            provider="anthropic",
            api_key="sk-ant-test-key",
            creative_model="claude-sonnet-4-20250514",
            support_model="claude-3-5-haiku-20241022",
        )
        assert config.provider == "anthropic"
        assert config.api_key == "sk-ant-test-key"
        assert "sonnet" in config.creative_model
        assert "haiku" in config.support_model

    def test_valid_openai_config(self):
        """Test valid OpenAI configuration."""
        config = LLMConfig(
            provider="openai",
            api_key="sk-openai-test-key",
            creative_model="gpt-4",
            support_model="gpt-3.5-turbo",
        )
        assert config.provider == "openai"
        assert config.api_key == "sk-openai-test-key"

    def test_missing_api_key_raises_error(self):
        """Test that missing API key raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="API key required"):
            LLMConfig(
                provider="anthropic",
                api_key="",
                creative_model="claude-sonnet-4-20250514",
                support_model="claude-3-5-haiku-20241022",
            )

    def test_missing_creative_model_raises_error(self):
        """Test that missing creative model raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Creative model"):
            LLMConfig(
                provider="anthropic",
                api_key="test-key",
                creative_model="",
                support_model="claude-3-5-haiku-20241022",
            )

    def test_missing_support_model_raises_error(self):
        """Test that missing support model raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Support model"):
            LLMConfig(
                provider="anthropic",
                api_key="test-key",
                creative_model="claude-sonnet-4-20250514",
                support_model="",
            )


class TestWorkflowConfig:
    """Tests for WorkflowConfig dataclass."""

    def test_default_values(self):
        """Test default workflow configuration values."""
        config = WorkflowConfig()
        assert config.max_revision_cycles == 3
        assert config.target_sketch_length == 5

    def test_custom_values(self):
        """Test custom workflow configuration values."""
        config = WorkflowConfig(
            max_revision_cycles=5,
            target_sketch_length=7,
        )
        assert config.max_revision_cycles == 5
        assert config.target_sketch_length == 7

    def test_invalid_max_revision_cycles(self):
        """Test that invalid max_revision_cycles raises error."""
        with pytest.raises(ConfigurationError, match="max_revision_cycles"):
            WorkflowConfig(max_revision_cycles=0)

    def test_invalid_target_sketch_length(self):
        """Test that invalid target_sketch_length raises error."""
        with pytest.raises(ConfigurationError, match="target_sketch_length"):
            WorkflowConfig(target_sketch_length=0)


class TestShowConfig:
    """Tests for ShowConfig dataclass."""

    def test_valid_show_config(self, temp_project_dir: Path):
        """Test valid show configuration."""
        config = ShowConfig(
            show_folder="test_show",
            show_bible="# Show Bible\nContent here",
            creative_prompt="# Creative Prompt\nContent here",
            output_dir=temp_project_dir / "output",
        )
        assert config.show_folder == "test_show"
        assert "Show Bible" in config.show_bible
        assert "Creative Prompt" in config.creative_prompt

    def test_missing_show_folder_raises_error(self, temp_project_dir: Path):
        """Test that missing show_folder raises error."""
        with pytest.raises(ConfigurationError, match="show_folder"):
            ShowConfig(
                show_folder="",
                show_bible="content",
                creative_prompt="content",
                output_dir=temp_project_dir / "output",
            )

    def test_empty_show_bible_raises_error(self, temp_project_dir: Path):
        """Test that empty show_bible raises error."""
        with pytest.raises(ConfigurationError, match="show_bible"):
            ShowConfig(
                show_folder="test",
                show_bible="",
                creative_prompt="content",
                output_dir=temp_project_dir / "output",
            )

    def test_empty_creative_prompt_raises_error(self, temp_project_dir: Path):
        """Test that empty creative_prompt raises error."""
        with pytest.raises(ConfigurationError, match="creative_prompt"):
            ShowConfig(
                show_folder="test",
                show_bible="content",
                creative_prompt="",
                output_dir=temp_project_dir / "output",
            )


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_from_temp_dir(self, temp_project_dir: Path, monkeypatch):
        """Test loading configuration from temporary directory."""
        # Set environment variables for the test
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-12345")
        monkeypatch.setenv("SHOW_FOLDER", "test_show")

        # Change to temp dir and load config
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_project_dir)
            config = load_config(show_folder="test_show")

            assert config.llm.provider == "anthropic"
            assert config.show.show_folder == "test_show"
            assert "Test Show" in config.show.show_bible
            assert "tech support" in config.show.creative_prompt.lower()
        finally:
            os.chdir(original_cwd)

    def test_load_config_with_show_folder_override(self, temp_project_dir: Path, monkeypatch):
        """Test loading config with show_folder parameter override."""
        # Set environment variables for the test
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-12345")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_project_dir)
            config = load_config(show_folder="test_show")
            assert config.show.show_folder == "test_show"
        finally:
            os.chdir(original_cwd)

    def test_load_config_nonexistent_show_raises_error(self, temp_project_dir: Path, monkeypatch):
        """Test that nonexistent show folder raises error."""
        # Set environment variables for the test
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-12345")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_project_dir)
            with pytest.raises(ConfigurationError, match="Show folder not found"):
                load_config(show_folder="nonexistent_show")
        finally:
            os.chdir(original_cwd)

    def test_load_config_missing_env_raises_error(self):
        """Test that missing environment variables raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "pyproject.toml").write_text("[project]\nname = 'test'\n")
            # Create Shows directory with test folder and required files
            show_dir = root / "Shows" / "test"
            show_dir.mkdir(parents=True)
            (show_dir / "show_bible.md").write_text("# Test Bible")
            (show_dir / "creative_prompt.md").write_text("# Test Prompt")
            # No .env file, no API key

            # Mock _get_project_root to return our temp directory
            with patch("src.utils.config._get_project_root", return_value=root):
                # Clear any environment variables that might be set
                env_vars_to_clear = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
                original_env = {k: os.environ.pop(k, None) for k in env_vars_to_clear}
                try:
                    with pytest.raises(ConfigurationError, match="No LLM provider"):
                        load_config(show_folder="test")
                finally:
                    # Restore original environment
                    for k, v in original_env.items():
                        if v is not None:
                            os.environ[k] = v

    def test_load_config_debug_mode(self, temp_project_dir: Path, monkeypatch):
        """Test loading config with debug mode enabled."""
        # Set environment variables for the test
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-12345")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_project_dir)
            config = load_config(show_folder="test_show", debug=True)
            assert config.debug is True
        finally:
            os.chdir(original_cwd)


class TestGetAgentPromptsPath:
    """Tests for get_agent_prompts_path function."""

    def test_get_agent_prompts_path_exists(self, mock_config: Config):
        """Test getting agent prompts path when file exists."""
        # Create the file
        prompts_path = mock_config.project_root / "Docs" / "agent-prompts.md"
        prompts_path.parent.mkdir(parents=True, exist_ok=True)
        prompts_path.write_text("# Agent Prompts")

        result = get_agent_prompts_path(mock_config)
        assert result == prompts_path

    def test_get_agent_prompts_path_missing_raises_error(self, temp_project_dir: Path):
        """Test that missing prompts file raises error."""
        # Remove the prompts file
        prompts_path = temp_project_dir / "Docs" / "agent-prompts.md"
        if prompts_path.exists():
            prompts_path.unlink()

        mock_config = Config(
            llm=LLMConfig(
                provider="anthropic",
                api_key="test",
                creative_model="test",
                support_model="test",
            ),
            workflow=WorkflowConfig(),
            show=ShowConfig(
                show_folder="test",
                show_bible="content",
                creative_prompt="content",
                output_dir=temp_project_dir / "output",
            ),
            project_root=temp_project_dir,
        )

        with pytest.raises(ConfigurationError, match="not found"):
            get_agent_prompts_path(mock_config)


class TestConfigIntegration:
    """Integration tests for configuration system."""

    def test_full_config_object(self, mock_config: Config):
        """Test that Config object has all required attributes."""
        assert hasattr(mock_config, "llm")
        assert hasattr(mock_config, "workflow")
        assert hasattr(mock_config, "show")
        assert hasattr(mock_config, "project_root")
        assert hasattr(mock_config, "debug")

    def test_config_immutability(self, mock_config: Config):
        """Test that config values are accessible."""
        # Config should provide access to all nested values
        assert mock_config.llm.provider in ["anthropic", "openai"]
        assert mock_config.workflow.max_revision_cycles > 0
        assert len(mock_config.show.show_bible) > 0

    def test_output_directory_creation(self, mock_config: Config):
        """Test that output directory path is valid."""
        output_dir = mock_config.show.output_dir
        assert isinstance(output_dir, Path)
        # Directory should exist or be creatable
        output_dir.mkdir(parents=True, exist_ok=True)
        assert output_dir.exists()
