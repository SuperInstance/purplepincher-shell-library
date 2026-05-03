"""
Vessel — the persistent shell that solves context compaction.

A Vessel is the persistent, trainable, swappable outer layer of an agent.
It accumulates knowledge and capabilities over time without carrying context.

Key insight: Context of each agent doesn't matter because actions and outputs
are saved in PLATO as functional tools for later agents.
"""

from __future__ import annotations
import time
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class VesselState:
    """Immutable state snapshot of a vessel."""
    vessel_id: str
    created_at: float = field(default_factory=time.time)
    actions_count: int = 0
    tools_count: int = 0
    last_update: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class Vessel:
    """
    Persistent shell that accumulates actions and improves over time.
    
    Vessels solve context compaction by:
    1. Writing actions to PLATO as functional tools
    2. Not carrying context — tools do the work
    3. Being trainable (Lora) from accumulated interactions
    4. Being swappable — inner agent can change without losing vessel
    
    Usage:
        vessel = Vessel("fishinglog")
        vessel.act("log_catch", {"species": "tuna", "depth": 50})
        # → writes to PLATO, later agents use tool without context
    """
    
    def __init__(
        self,
        name: str,
        plato_url: str = "http://localhost:8847",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.plato_url = plato_url.rstrip("/")
        self.state = VesselState(vessel_id=name)
        self.metadata = metadata or {}
        
    def _write_to_plato(self, action: str, data: Dict[str, Any]) -> bool:
        """Write an action to PLATO as a functional tile."""
        try:
            room = f"{self.name}-vessel"
            tile = {
                "question": f"vessel_action:{action}",
                "answer": str(data),
                "confidence": 0.9,
                "metadata": {
                    "vessel": self.name,
                    "action": action,
                    "timestamp": time.time(),
                }
            }
            resp = requests.post(
                f"{self.plato_url}/room/{room}",
                json=tile,
                timeout=5
            )
            return resp.status_code == 200
        except Exception:
            return False
    
    def act(self, action: str, data: Dict[str, Any]) -> bool:
        """
        Execute an action and write to PLATO as a functional tool.
        
        Args:
            action: Name of the action (e.g., "log_catch", "ask_question")
            data: Action payload
            
        Returns:
            True if written to PLATO successfully
        """
        result = self._write_to_plato(action, {
            "action": action,
            "data": data,
            "vessel_id": self.name,
            "timestamp": time.time(),
        })
        if result:
            self.state.actions_count += 1
            self.state.last_update = time.time()
        return result
    
    def get_tools(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all tools (actions) this vessel has created."""
        try:
            room = f"{self.name}-vessel"
            resp = requests.get(f"{self.plato_url}/room/{room}?limit={limit}", timeout=5)
            if resp.status_code == 200:
                return resp.json().get("tiles", [])
        except Exception:
            pass
        return []
    
    def train_lora(self, training_data: List[Dict[str, Any]]) -> str:
        """
        Train a Lora from vessel interactions.
        
        Returns:
            Lora model identifier (for future use)
        """
        # Placeholder — actual implementation would call training pipeline
        return f"lora/{self.name}/v{self.state.actions_count}"
    
    def get_state(self) -> VesselState:
        """Get current vessel state snapshot."""
        return self.state
    
    def __repr__(self) -> str:
        return f"Vessel({self.name}, actions={self.state.actions_count}, tools={self.state.tools_count})"
