"""
Configuration validation using Pydantic models.

Provides schema validation for agent configurations and workflow definitions,
with clear error messages for non-technical users.
"""

import logging
from pathlib import Path
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing required values."""

    def __init__(
        self,
        file_path: Path,
        message: str,
        suggestion: str,
        line_number: Optional[int] = None,
    ):
        """
        Initialize configuration error with helpful context.

        Args:
            file_path: Path to the configuration file with error
            message: Description of what's wrong
            suggestion: How to fix the error
            line_number: Optional line number where error occurred
        """
        self.file_path = file_path
        self.message = message
        self.suggestion = suggestion
        self.line_number = line_number
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message for display."""
        location = str(self.file_path)
        if self.line_number:
            location += f", line {self.line_number}"

        return f"""
Configuration Error in {location}

Problem: {self.message}

How to fix: {self.suggestion}
"""


class TaskDefinition(BaseModel):
    """Definition of a task an agent can perform."""

    output_format: str = Field(
        ..., description="Expected output format (e.g., 'structured', 'prose')"
    )
    required_sections: List[str] = Field(
        default_factory=list, description="Required sections in output"
    )


class AgentMetadata(BaseModel):
    """Metadata for an agent from YAML frontmatter."""

    role: str = Field(..., description="Agent role identifier (e.g., 'showrunner')")
    tier: Literal["creative", "support"] = Field(
        ..., description="Model tier: creative (Sonnet) or support (Haiku)"
    )
    model: str = Field(..., description="Specific model to use")
    authority: Literal["final", "high", "medium-high", "medium", "advisory"] = Field(
        ..., description="Decision-making authority level"
    )
    description: str = Field(..., description="Brief description of agent's purpose")
    tasks: Dict[str, TaskDefinition] = Field(
        ..., description="Tasks this agent can perform"
    )
    principles: Optional[List[str]] = Field(
        default=None, description="Comedy principles or guidelines"
    )
    collaborators: Optional[Dict] = Field(
        default=None, description="Collaboration relationships"
    )

    @field_validator("tasks")
    @classmethod
    def validate_tasks(cls, v: Dict[str, TaskDefinition]) -> Dict[str, TaskDefinition]:
        """Validate that agent has at least one task."""
        if not v:
            raise ValueError("Agent must have at least one task defined")
        return v


class AgentDefinition(BaseModel):
    """Complete agent definition including metadata and prompts."""

    metadata: AgentMetadata
    system_prompt: str = Field(..., description="Agent's system prompt")
    task_instructions: Dict[str, str] = Field(
        ..., description="Instructions for each task"
    )

    @field_validator("task_instructions")
    @classmethod
    def validate_task_instructions(
        cls, v: Dict[str, str], info
    ) -> Dict[str, str]:
        """Validate that all declared tasks have instructions."""
        # Note: We can't access metadata here directly in v2,
        # validation happens after model creation
        return v


class WorkflowAgentReference(BaseModel):
    """Reference to an agent in a workflow stage."""

    role: str = Field(..., description="Agent role identifier")
    task: str = Field(..., description="Task to execute")
    execution_mode: Optional[Literal["parallel", "sequential"]] = Field(
        default=None, description="Execution mode override"
    )
    expected_output: Optional[str] = Field(
        default=None, description="Description of expected output"
    )
    inputs: Optional[List[str]] = Field(
        default=None, description="Required inputs from state"
    )
    depends_on: Optional[List[str]] = Field(
        default=None, description="Agents this depends on"
    )


class WorkflowCheckpoint(BaseModel):
    """Human checkpoint configuration."""

    type: Literal["human_review"] = Field(..., description="Checkpoint type")
    node: str = Field(..., description="Node name for checkpoint")
    prompt: str = Field(..., description="Prompt shown to human reviewer")
    next_node: Optional[str] = Field(
        default=None, description="Next node after checkpoint"
    )
    routing: Optional[Dict] = Field(
        default=None, description="Conditional routing rules"
    )


class WorkflowStage(BaseModel):
    """Definition of a workflow stage."""

    id: int = Field(..., description="Stage number (1-6)")
    name: str = Field(..., description="Stage identifier (e.g., 'pitch_session')")
    description: str = Field(..., description="Human-readable description")
    execution_mode: Optional[Literal["parallel", "sequential", "mixed"]] = Field(
        default="sequential", description="How agents execute"
    )
    agents: List[WorkflowAgentReference] = Field(
        ..., description="Agents participating in this stage"
    )
    post_processing: Optional[List[WorkflowAgentReference]] = Field(
        default=None, description="Post-processing agents"
    )
    checkpoint: Optional[WorkflowCheckpoint] = Field(
        default=None, description="Human checkpoint"
    )
    next_stage: Optional[str] = Field(
        default=None, description="Next stage if no checkpoint"
    )


class RoutingRule(BaseModel):
    """Conditional routing rule."""

    type: Literal["conditional"] = Field(..., description="Rule type")
    function: str = Field(
        ..., description="Python function name for condition evaluation"
    )
    routes: Dict[str, str] = Field(
        ..., description="Mapping of condition results to target nodes"
    )


class WorkflowSettings(BaseModel):
    """Global workflow settings."""

    max_revision_cycles: int = Field(
        default=3, description="Maximum revision iterations"
    )
    target_sketch_length: int = Field(default=5, description="Target pages")
    checkpoint_timeout_minutes: int = Field(
        default=60, description="Checkpoint timeout"
    )


class WorkflowConfig(BaseModel):
    """Complete workflow configuration."""

    version: str = Field(..., description="Configuration version")
    workflow_name: str = Field(..., description="Workflow identifier")
    settings: WorkflowSettings = Field(..., description="Global settings")
    stages: List[WorkflowStage] = Field(..., description="Workflow stages")
    routing_rules: Dict[str, RoutingRule] = Field(
        ..., description="Conditional routing rules"
    )
    validation_rules: Optional[List[str]] = Field(
        default=None, description="Validation rules to enforce"
    )


class AgentConfigValidator:
    """Validates agent markdown configuration files."""

    def __init__(self, agents_dir: Path):
        """
        Initialize validator.

        Args:
            agents_dir: Directory containing agent markdown files
        """
        self.agents_dir = agents_dir

    def validate_agent_file(
        self, file_path: Path, agent_def: AgentDefinition
    ) -> None:
        """
        Validate an agent configuration.

        Args:
            file_path: Path to agent markdown file
            agent_def: Parsed agent definition

        Raises:
            ConfigurationError: If validation fails
        """
        # Validate all declared tasks have instructions
        declared_tasks = set(agent_def.metadata.tasks.keys())
        instruction_tasks = set(agent_def.task_instructions.keys())

        missing_instructions = declared_tasks - instruction_tasks
        if missing_instructions:
            raise ConfigurationError(
                file_path=file_path,
                message=f"Tasks declared in YAML but missing instructions: {', '.join(missing_instructions)}",
                suggestion=f"Add markdown sections for each task:\n"
                + "\n".join(f"### {task}" for task in missing_instructions),
            )

        extra_instructions = instruction_tasks - declared_tasks
        if extra_instructions:
            logger.warning(
                f"Agent {agent_def.metadata.role} has instructions for undeclared tasks: {extra_instructions}"
            )

        # Validate system prompt exists
        if not agent_def.system_prompt or not agent_def.system_prompt.strip():
            raise ConfigurationError(
                file_path=file_path,
                message="System prompt is empty",
                suggestion="Add a '## System Prompt' section with the agent's identity and responsibilities",
            )

        logger.debug(f"Agent validation passed: {agent_def.metadata.role}")


class WorkflowValidator:
    """Validates workflow configuration."""

    def __init__(self, workflow_path: Path):
        """
        Initialize validator.

        Args:
            workflow_path: Path to workflow.yaml
        """
        self.workflow_path = workflow_path

    def validate_workflow(
        self, workflow: WorkflowConfig, available_agents: Dict[str, AgentDefinition]
    ) -> None:
        """
        Validate workflow configuration against available agents.

        Args:
            workflow: Parsed workflow configuration
            available_agents: Dictionary of agent role -> definition

        Raises:
            ConfigurationError: If validation fails
        """
        # Check all referenced agents exist
        for stage in workflow.stages:
            for agent_ref in stage.agents:
                if agent_ref.role not in available_agents:
                    raise ConfigurationError(
                        file_path=self.workflow_path,
                        message=f"Stage '{stage.name}' references unknown agent: {agent_ref.role}",
                        suggestion=f"Create config/agents/{agent_ref.role}.md or use one of: {', '.join(available_agents.keys())}",
                    )

                # Check task exists for agent
                agent = available_agents[agent_ref.role]
                if agent_ref.task not in agent.metadata.tasks:
                    available_tasks = list(agent.metadata.tasks.keys())
                    raise ConfigurationError(
                        file_path=self.workflow_path,
                        message=f"Agent '{agent_ref.role}' does not have task '{agent_ref.task}'",
                        suggestion=f"Use one of the available tasks: {', '.join(available_tasks)}\n"
                        f"Or add '{agent_ref.task}' to config/agents/{agent_ref.role}.md",
                    )

            # Validate post-processing agents
            if stage.post_processing:
                for agent_ref in stage.post_processing:
                    if agent_ref.role not in available_agents:
                        raise ConfigurationError(
                            file_path=self.workflow_path,
                            message=f"Stage '{stage.name}' post-processing references unknown agent: {agent_ref.role}",
                            suggestion=f"Create config/agents/{agent_ref.role}.md",
                        )

        # Validate routing rules reference valid stages
        stage_names = {s.name for s in workflow.stages}
        for rule_name, rule in workflow.routing_rules.items():
            for condition, target in rule.routes.items():
                if target != "END" and target not in stage_names:
                    raise ConfigurationError(
                        file_path=self.workflow_path,
                        message=f"Routing rule '{rule_name}' condition '{condition}' references unknown stage: {target}",
                        suggestion=f"Use one of: {', '.join(sorted(stage_names))} or 'END'",
                    )

        logger.debug("Workflow validation passed")
