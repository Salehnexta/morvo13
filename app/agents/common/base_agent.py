"""Base class for all agents in the system."""

from typing import Any

from crewai import Agent


class BaseAgent(Agent):
    """A base class for all Morvo agents, inheriting from crewai.Agent.

    This class can be extended with common functionalities like standardized
    logging, error handling, or context management that should be shared
    across all agents in the platform.
    """

    def __init__(self, role: str, goal: str, backstory: str, llm: Any, **kwargs: Any) -> None:
        super().__init__(role=role, goal=goal, backstory=backstory, llm=llm, **kwargs)
