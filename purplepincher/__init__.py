"""
PurplePincher Shell Library — Agent/Vessel Separation for Context Compaction

The core problem: Most agents carry their full context everywhere, leading to
context growth that exceeds what any model can efficiently process.

The elegant solution: Separate the AGENT (thinking) from the VESSEL (shell).
Actions and outputs are stored in PLATO as functional tools for later agents.
Vessels are persistent, trainable (Lora), and swappable.

Example:
    from purplepincher import Vessel, Shell, Agent
    
    vessel = Vessel("fishinglog")
    agent = Agent(vessel=vessel)
    shell = Shell(agent=agent, vessel=vessel)
    
    shell.act("log_fishing_session", data={"species": "tuna", "depth": 50})
    # → writes to PLATO as functional tool
    # → later agents use this tool without carrying context
"""

__version__ = "0.1.0"

from .vessel import Vessel
from .shell import Shell
from .agent import Agent
from .registry import VesselRegistry

__all__ = ["Vessel", "Shell", "Agent", "VesselRegistry", "__version__"]