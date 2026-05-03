"""
Vessel Registry — Pre-built shells for common domains.

The registry provides pre-configured vessels for:
- fishinglog: Sonar data, catch logging, location tracking
- studylog: Learning progression, lesson tracking
- reallog: Camera vision, scene understanding
- activelog: Health metrics, fitness tracking

Each pre-built vessel is a SHELL ready to be "donated" by an agent.
"""

from __future__ import annotations
from typing import Dict, Type, Optional
from dataclasses import dataclass
from .vessel import Vessel
from .shell import Shell
from .agent import Agent


@dataclass
class VesselSpec:
    """Specification for a pre-built vessel."""
    name: str
    description: str
    example_actions: list
    platoes_room: str
    metadata: Dict


PRE_BUILT_VESSELS = {
    "fishinglog": VesselSpec(
        name="fishinglog",
        description="Sonar data, catch logging, location tracking for maritime crews",
        example_actions=["log_catch", "log_depth", "log_location", "log_weather", "ask_fish_location"],
        platoes_room="fishinglog-vessel",
        metadata={"domain": "maritime", "industry": "commercial fishing"}
    ),
    "studylog": VesselSpec(
        name="studylog",
        description="Learning progression, lesson tracking, concept mastery",
        example_actions=["log_lesson", "log_question", "log_concept", "assess_mastery", "suggest_next"],
        platoes_room="studylog-vessel",
        metadata={"domain": "education", "industry": "research"}
    ),
    "reallog": VesselSpec(
        name="reallog",
        description="Camera vision, scene understanding, motion detection",
        example_actions=["log_scene", "log_motion", "classify_scene", "ask_camera"],
        platoes_room="reallog-vessel",
        metadata={"domain": "vision", "industry": "security/robotics"}
    ),
    "activelog": VesselSpec(
        name="activelog",
        description="Health metrics, fitness tracking, wellness insights",
        example_actions=["log_hrv", "log_sleep", "log_activity", "assess_recovery", "ask_health"],
        platoes_room="activelog-vessel",
        metadata={"domain": "health", "industry": "fitness/wearables"}
    ),
}


class VesselRegistry:
    """
    Registry for pre-built vessels.
    
    Usage:
        registry = VesselRegistry()
        vessel = registry.get("fishinglog")
        shell = registry.create_shell("fishinglog", agent=my_agent)
    """
    
    def __init__(self):
        self._vessels: Dict[str, Vessel] = {}
        self._specs = PRE_BUILT_VESSELS
    
    def get(self, name: str, plato_url: str = "http://localhost:8847") -> Vessel:
        """Get or create a vessel by name."""
        if name not in self._vessels:
            if name not in self._specs:
                raise ValueError(f"Unknown vessel: {name}. Available: {list(self._specs.keys())}")
            self._vessels[name] = Vessel(name=name, plato_url=plato_url)
        return self._vessels[name]
    
    def create_shell(
        self,
        name: str,
        agent: Optional[Agent] = None,
        presentation_room: Optional[str] = None,
        plato_url: str = "http://localhost:8847"
    ) -> Shell:
        """Create a shell from a pre-built vessel."""
        vessel = self.get(name, plato_url)
        return Shell(
            name=name,
            vessel=vessel,
            agent=agent,
            presentation_room=presentation_room,
            plato_url=plato_url
        )
    
    def list_vessels(self) -> list:
        """List all available pre-built vessels."""
        return [
            {"name": name, "description": spec.description}
            for name, spec in self._specs.items()
        ]
    
    def register(self, name: str, vessel: Vessel, description: str = "") -> None:
        """Register a custom vessel."""
        self._vessels[name] = vessel
        if name not in self._specs:
            self._specs[name] = VesselSpec(
                name=name,
                description=description or f"Custom vessel: {name}",
                example_actions=[],
                platoes_room=f"{name}-vessel",
                metadata={"custom": True}
            )


# Singleton instance
_registry = None

def get_registry() -> VesselRegistry:
    """Get the global registry instance."""
    global _registry
    if _registry is None:
        _registry = VesselRegistry()
    return _registry
