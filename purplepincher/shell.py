"""
Shell — agent + vessel together in PLATO.

The Shell is the combination of an inner agent (thinking) and a vessel (acting).
It presents through PLATO, allowing humans and other agents to interact.
"""

from __future__ import annotations
import time
import requests
from typing import Optional, Dict, Any, List
from .vessel import Vessel


@dataclass
class ShellConfig:
    """Configuration for a Shell."""
    name: str
    vessel: Vessel
    presentation_room: str = "shell-presentation"
    enable_tools: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ShellPresentation:
    """A presentation from a Shell to PLATO."""
    content: str
    type: str  # "question", "answer", "tool", "reflection"
    shell_name: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class Shell:
    """
    Shell = Agent + Vessel in PLATO.
    
    The Shell presents information through PLATO rooms.
    Humans and agents interact with the Shell through these presentations.
    
    Usage:
        vessel = Vessel("fishinglog")
        shell = Shell(agent=my_agent, vessel=vessel)
        shell.present("answer", "Tuna were found at 50m depth yesterday")
        # → writes to PLATO presentation room
    """
    
    def __init__(
        self,
        name: str,
        vessel: Vessel,
        agent: Optional[Any] = None,
        presentation_room: Optional[str] = None,
        plato_url: str = "http://localhost:8847"
    ):
        self.name = name
        self.vessel = vessel
        self.agent = agent
        self.plato_url = plato_url.rstrip("/")
        self.presentation_room = presentation_room or f"{name}-shell"
        self.config = ShellConfig(
            name=name,
            vessel=vessel,
            presentation_room=self.presentation_room,
        )
    
    def present(
        self,
        content_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Present something through PLATO.
        
        Args:
            content_type: Type of presentation ("question", "answer", "tool", "reflection")
            content: The content to present
            metadata: Optional metadata
            
        Returns:
            True if written to PLATO successfully
        """
        tile = {
            "question": f"shell:{content_type}",
            "answer": content,
            "confidence": 0.9,
            "metadata": {
                "shell": self.name,
                "content_type": content_type,
                "timestamp": time.time(),
                **(metadata or {})
            }
        }
        try:
            resp = requests.post(
                f"{self.plato_url}/room/{self.presentation_room}",
                json=tile,
                timeout=5
            )
            return resp.status_code == 200
        except Exception:
            return False
    
    def ask(self, question: str) -> str:
        """
        Ask the shell a question.
        
        If an agent is attached, it will answer.
        Otherwise, queries PLATO for relevant tools.
        """
        if self.agent:
            answer = self.agent.answer(question)
            self.present("answer", answer, {"question": question})
            return answer
        
        # Query PLATO for relevant tools
        return self._query_tools(question)
    
    def _query_tools(self, query: str) -> str:
        """Query PLATO for tools relevant to the query."""
        try:
            resp = requests.get(
                f"{self.plato_url}/room/{self.vessel.name}-vessel",
                timeout=5
            )
            if resp.status_code == 200:
                tiles = resp.json().get("tiles", [])
                relevant = [t for t in tiles if query.lower() in str(t).lower()]
                if relevant:
                    return f"Found {len(relevant)} relevant tools: {relevant[0].get('answer', '')}"
        except Exception:
            pass
        return "No relevant tools found in vessel."
    
    def don_shell(self, shell_name: str) -> Shell:
        """
        Don another shell's presentation to see from their perspective.
        
        Returns a new Shell configured to present as the target shell.
        """
        return Shell(
            name=f"{self.name}→{shell_name}",
            vessel=self.vessel,
            agent=self.agent,
            presentation_room=f"{shell_name}-shell",
            plato_url=self.plato_url
        )
    
    def __repr__(self) -> str:
        return f"Shell({self.name}, vessel={self.vessel.name})"
