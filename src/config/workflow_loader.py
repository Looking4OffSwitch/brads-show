"""
Workflow configuration loader.

Loads workflow definitions from YAML files, validates against agent configs,
and provides query methods for workflow structure.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from src.config.validation import (
    ConfigurationError,
    RoutingRule,
    WorkflowConfig,
    WorkflowStage,
    WorkflowValidator,
)

logger = logging.getLogger(__name__)


class WorkflowLoader:
    """Loads and validates workflow configuration from YAML."""

    def __init__(self, workflow_path: Path):
        """
        Initialize workflow loader.

        Args:
            workflow_path: Path to workflow.yaml file
        """
        self.workflow_path = workflow_path
        self.config: Optional[WorkflowConfig] = None
        self.validator = WorkflowValidator(workflow_path)

        logger.debug(f"WorkflowLoader initialized with: {workflow_path}")

    def load(self) -> WorkflowConfig:
        """
        Load workflow configuration from YAML file.

        Returns:
            Parsed workflow configuration

        Raises:
            ConfigurationError: If file not found or invalid
        """
        if self.config is not None:
            logger.debug("Returning cached workflow config")
            return self.config

        if not self.workflow_path.exists():
            raise ConfigurationError(
                file_path=self.workflow_path,
                message="Workflow configuration file not found",
                suggestion=f"Create {self.workflow_path} with workflow definition",
            )

        logger.debug(f"Loading workflow config from: {self.workflow_path}")

        try:
            content = self.workflow_path.read_text(encoding="utf-8")
        except Exception as e:
            raise ConfigurationError(
                file_path=self.workflow_path,
                message=f"Cannot read file: {e}",
                suggestion="Ensure file exists and is readable",
            )

        try:
            yaml_data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ConfigurationError(
                file_path=self.workflow_path,
                message=f"Invalid YAML syntax: {e}",
                suggestion="Check YAML syntax - ensure proper indentation and structure",
            )

        try:
            self.config = WorkflowConfig(**yaml_data)
        except Exception as e:
            raise ConfigurationError(
                file_path=self.workflow_path,
                message=f"Invalid workflow structure: {e}",
                suggestion="Ensure all required fields are present: version, workflow_name, settings, stages, routing_rules",
            )

        logger.info(f"Loaded workflow config: {self.config.workflow_name}")
        return self.config

    def validate(self, available_agents: Dict[str, any]) -> None:
        """
        Validate workflow against available agent configurations.

        Args:
            available_agents: Dictionary of agent role -> definition

        Raises:
            ConfigurationError: If validation fails
        """
        if self.config is None:
            self.load()

        logger.debug("Validating workflow configuration...")
        self.validator.validate_workflow(self.config, available_agents)
        logger.info("Workflow validation passed")

    def get_stages(self) -> List[WorkflowStage]:
        """
        Get all workflow stages in order.

        Returns:
            List of workflow stages sorted by ID
        """
        if self.config is None:
            self.load()

        return sorted(self.config.stages, key=lambda s: s.id)

    def get_stage(self, stage_name: str) -> Optional[WorkflowStage]:
        """
        Get a specific workflow stage by name.

        Args:
            stage_name: Name of the stage (e.g., 'pitch_session')

        Returns:
            WorkflowStage if found, None otherwise
        """
        if self.config is None:
            self.load()

        for stage in self.config.stages:
            if stage.name == stage_name:
                return stage

        return None

    def get_routing_rules(self) -> Dict[str, RoutingRule]:
        """
        Get all conditional routing rules.

        Returns:
            Dictionary mapping rule name to RoutingRule
        """
        if self.config is None:
            self.load()

        return self.config.routing_rules

    def get_routing_rule(self, rule_name: str) -> Optional[RoutingRule]:
        """
        Get a specific routing rule by name.

        Args:
            rule_name: Name of the routing rule

        Returns:
            RoutingRule if found, None otherwise
        """
        if self.config is None:
            self.load()

        return self.config.routing_rules.get(rule_name)

    def get_max_revision_cycles(self) -> int:
        """Get maximum revision cycles setting."""
        if self.config is None:
            self.load()

        return self.config.settings.max_revision_cycles

    def get_target_sketch_length(self) -> int:
        """Get target sketch length setting."""
        if self.config is None:
            self.load()

        return self.config.settings.target_sketch_length
