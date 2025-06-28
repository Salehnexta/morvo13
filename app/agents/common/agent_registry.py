"""
Registry for AI agents in the system.
"""

from app.agents.common.base_agent import BaseAgent


class AgentRegistry:
    """
    Registry for managing and accessing AI agents.
    """

    def __init__(self) -> None:
        """Initialize the agent registry."""
        self.agents: dict[str, BaseAgent] = {}

    def register(self, agent_id: str, agent: BaseAgent) -> None:
        """
        Register an agent in the registry.

        Args:
            agent_id: Unique identifier for the agent
            agent: The agent instance to register
        """
        self.agents[agent_id] = agent

    def get_agent(self, agent_id: str) -> BaseAgent | None:
        """
        Get an agent by its ID.

        Args:
            agent_id: ID of the agent to retrieve

        Returns:
            BaseAgent or None: The requested agent if found, None otherwise
        """
        return self.agents.get(agent_id)

    def list_agents(self) -> dict[str, BaseAgent]:
        """
        List all registered agents.

        Returns:
            Dict[str, BaseAgent]: Dictionary of agent IDs to agent instances
        """
        return self.agents


# Singleton instance for dependency injection
_agent_registry: AgentRegistry | None = None


def get_agent_registry() -> AgentRegistry:
    """
    Get the agent registry singleton.

    Returns:
        AgentRegistry: The agent registry instance
    """
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
        # TODO: Initialize and register all agents here
    return _agent_registry
