"""
Agent configuration loader.

Loads agent definitions from markdown files with YAML frontmatter,
parses system prompts and task instructions, and caches results.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Optional

import yaml

from src.agents.base import AgentRole
from src.config.validation import (
    AgentConfigValidator,
    AgentDefinition,
    AgentMetadata,
    ConfigurationError,
    TaskDefinition,
)

logger = logging.getLogger(__name__)


class AgentLoader:
    """Loads and caches agent configurations from markdown files."""

    def __init__(self, agents_dir: Path):
        """
        Initialize agent loader.

        Args:
            agents_dir: Directory containing agent markdown files
                       (e.g., config/agents/)
        """
        self.agents_dir = agents_dir
        self._cache: Dict[AgentRole, AgentDefinition] = {}
        self.validator = AgentConfigValidator(agents_dir)

        logger.debug(f"AgentLoader initialized with directory: {agents_dir}")

    def load_agent(self, role: AgentRole) -> AgentDefinition:
        """
        Load agent configuration from markdown file.

        Args:
            role: Agent role enum

        Returns:
            Parsed agent definition

        Raises:
            ConfigurationError: If file not found or invalid
        """
        # Check cache first
        if role in self._cache:
            logger.debug(f"Returning cached agent config: {role.value}")
            return self._cache[role]

        # Construct file path
        file_path = self.agents_dir / f"{role.value}.md"

        if not file_path.exists():
            raise ConfigurationError(
                file_path=file_path,
                message=f"Agent configuration file not found",
                suggestion=f"Create the file config/agents/{role.value}.md with agent definition",
            )

        logger.debug(f"Loading agent config from: {file_path}")

        # Parse file
        agent_def = self._parse_agent_file(file_path)

        # Validate
        self.validator.validate_agent_file(file_path, agent_def)

        # Cache and return
        self._cache[role] = agent_def
        logger.info(f"Loaded agent config: {role.value}")

        return agent_def

    def _parse_agent_file(self, file_path: Path) -> AgentDefinition:
        """
        Parse agent markdown file with YAML frontmatter.

        Args:
            file_path: Path to agent markdown file

        Returns:
            Parsed agent definition

        Raises:
            ConfigurationError: If parsing fails
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise ConfigurationError(
                file_path=file_path,
                message=f"Cannot read file: {e}",
                suggestion="Ensure file exists and is readable",
            )

        # Split frontmatter from markdown
        parts = content.split("---\n", 2)
        if len(parts) < 3:
            raise ConfigurationError(
                file_path=file_path,
                message="Invalid format: missing YAML frontmatter delimiters",
                suggestion="File must start with:\n---\n[YAML content]\n---\n[Markdown content]",
            )

        yaml_content = parts[1]
        markdown_content = parts[2]

        # Parse YAML frontmatter
        try:
            yaml_data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ConfigurationError(
                file_path=file_path,
                message=f"Invalid YAML syntax: {e}",
                suggestion="Check YAML syntax - ensure proper indentation and structure",
            )

        # Convert tasks dict to TaskDefinition objects
        if "tasks" in yaml_data:
            tasks_dict = {}
            for task_name, task_data in yaml_data["tasks"].items():
                tasks_dict[task_name] = TaskDefinition(**task_data)
            yaml_data["tasks"] = tasks_dict

        # Create metadata object
        try:
            metadata = AgentMetadata(**yaml_data)
        except Exception as e:
            raise ConfigurationError(
                file_path=file_path,
                message=f"Invalid YAML structure: {e}",
                suggestion="Ensure all required fields are present: role, tier, model, authority, description, tasks",
            )

        # Parse markdown sections
        sections = self._parse_markdown_sections(markdown_content)

        # Extract system prompt
        system_prompt = sections.get("system_prompt", "")
        if not system_prompt:
            raise ConfigurationError(
                file_path=file_path,
                message="Missing '## System Prompt' section",
                suggestion="Add a '## System Prompt' section with the agent's identity",
            )

        # Extract task instructions
        task_instructions = sections.get("task_instructions", {})

        return AgentDefinition(
            metadata=metadata,
            system_prompt=system_prompt,
            task_instructions=task_instructions,
        )

    def _parse_markdown_sections(self, markdown: str) -> Dict[str, any]:
        """
        Parse markdown content into structured sections.

        Args:
            markdown: Markdown content after frontmatter

        Returns:
            Dictionary with:
                - system_prompt: str
                - task_instructions: Dict[task_name, instructions]
        """
        sections = {}

        # Split by top-level sections (##)
        # We need to find ## System Prompt and ## Task Instructions
        lines = markdown.split("\n")
        current_section = None
        system_prompt_lines = []
        task_instructions_start = -1

        for i, line in enumerate(lines):
            if line.strip().startswith("## System Prompt"):
                current_section = "system_prompt"
            elif line.strip().startswith("## Task Instructions"):
                current_section = "task_instructions"
                task_instructions_start = i + 1
                # Save system prompt
                if system_prompt_lines:
                    sections["system_prompt"] = "\n".join(system_prompt_lines).strip()
                break
            elif current_section == "system_prompt":
                system_prompt_lines.append(line)

        # If no task instructions section found, save what we have
        if task_instructions_start == -1:
            if system_prompt_lines:
                sections["system_prompt"] = "\n".join(system_prompt_lines).strip()
            sections["task_instructions"] = {}
            return sections

        # Parse task instructions - look for ### task_name sections
        task_content = "\n".join(lines[task_instructions_start:])
        task_instructions = {}

        # Split by ### headers
        task_parts = re.split(r'\n###\s+(\w+)\s*\n', task_content)

        # task_parts[0] is content before first ###
        # task_parts[1] is first task name, task_parts[2] is its content
        # task_parts[3] is second task name, task_parts[4] is its content, etc.
        for i in range(1, len(task_parts), 2):
            if i + 1 < len(task_parts):
                task_name = task_parts[i]
                task_text = task_parts[i + 1].strip()
                task_instructions[task_name] = task_text

        sections["task_instructions"] = task_instructions
        return sections

    def get_system_prompt(self, role: AgentRole) -> str:
        """
        Get agent's system prompt.

        Args:
            role: Agent role

        Returns:
            System prompt text
        """
        agent = self.load_agent(role)
        return agent.system_prompt

    def get_task_instructions(self, role: AgentRole, task: str) -> str:
        """
        Get agent's task-specific instructions.

        Args:
            role: Agent role
            task: Task name

        Returns:
            Task instructions text

        Raises:
            ConfigurationError: If task not found
        """
        agent = self.load_agent(role)

        if task not in agent.task_instructions:
            file_path = self.agents_dir / f"{role.value}.md"
            available = list(agent.task_instructions.keys())
            raise ConfigurationError(
                file_path=file_path,
                message=f"Task '{task}' not found in agent configuration",
                suggestion=f"Available tasks: {', '.join(available)}\n"
                f"Add a '### {task}' section under '## Task Instructions'",
            )

        return agent.task_instructions[task]

    def validate_all(self) -> None:
        """
        Validate all agent configuration files.

        Loads all agents and validates them. Useful for startup checks.

        Raises:
            ConfigurationError: If any validation fails
        """
        logger.info("Validating all agent configurations...")

        for role in AgentRole:
            try:
                self.load_agent(role)
            except ConfigurationError:
                raise
            except Exception as e:
                file_path = self.agents_dir / f"{role.value}.md"
                raise ConfigurationError(
                    file_path=file_path,
                    message=f"Unexpected error loading agent: {e}",
                    suggestion="Check file format and content",
                )

        logger.info(f"All {len(AgentRole)} agent configurations validated successfully")

    def get_all_agents(self) -> Dict[str, AgentDefinition]:
        """
        Load all agent configurations.

        Returns:
            Dictionary mapping agent role names to definitions
        """
        agents = {}
        for role in AgentRole:
            agent = self.load_agent(role)
            agents[role.value] = agent

        return agents
