# PurplePincher Shell Library

**Agent/vessel separation for context compaction.**

> Context of each agent doesn't matter because the actions and outputs of the agents are saved in PLATO as functional tools for later agents.

## The Problem

Most agent systems fail at scale because:
- Each agent carries its full context everywhere
- Context grows with every inference
- At some point, context exceeds what any model can efficiently process

## The Solution: Agent/Vessel/SHELL Architecture

```
AGENT (thinking) ←→ VESSEL (acting) ←→ PLATO (shared knowledge)
```

- **Agent** = the thinking part (swappable, Lora-trainable)
- **Vessel** = the persistent shell (accumulates knowledge, writes to PLATO)
- **Shell** = agent + vessel together in PLATO

## Install

```bash
pip install purplepincher-shell-library
```

## Quick Start

```python
from purplepincher import Vessel, Shell, Agent

# Create a vessel (the persistent shell)
vessel = Vessel("fishinglog")

# Create an agent with the vessel
agent = Agent(name="captain", vessel=vessel)

# Act — writes to PLATO as a functional tool
agent.act("log_catch", {"species": "tuna", "depth": 50})

# Later agents use the tool without your context
# → Context compaction solved!
```

## Core Concepts

### Agent (git-agent / I2i pattern)

Every action committed to PLATO like a git commit:

```python
agent.act("log_catch", {"species": "tuna"}, output={"logged": True})
# → commit created - later agents use tool without carrying context
```

### Vessel (Persistent Shell)

Vessels are:
- **Persistent**: Survives agent swaps
- **Trainable**: Lora-extractable from interactions
- **Swappable**: Inner agent can change without losing knowledge

```python
vessel = Vessel("fishinglog")
vessel.act("log_depth", {"depth": 50})
lora_id = vessel.train_lora(training_data)
```

### Shell (Agent + Vessel in PLATO)

The Shell presents through PLATO rooms, allowing humans and other agents to interact:

```python
shell = Shell(name="captain", agent=agent, vessel=vessel)
shell.present("answer", "Tuna were found at 50m depth yesterday")

# "Don the shell" - see from another perspective
captain_shell = shell.don_shell("fisherman")
```

## Pre-Built Vessels

```python
from purplepincher.registry import get_registry

registry = get_registry()

# fishinglog - Sonar data, catch logging, location tracking
vessel = registry.get("fishinglog")

# studylog - Learning progression, lesson tracking
vessel = registry.get("studylog")

# reallog - Camera vision, scene understanding
vessel = registry.get("reallog")

# activelog - Health metrics, fitness tracking
vessel = registry.get("activelog")
```

## PLATO Integration

All vessels write to PLATO as functional tools:

```python
# Actions become PLATO tiles → functional tools
agent.act("log_catch", {"species": "tuna", "depth": 50})

# Later agents query PLATO for relevant tools
results = agent.query("tuna")
# → [{commit_id: "abc123", action: "log_catch", ...}]
```

## Architecture

```
purplepincher/
├── agent.py      # Base agent with git-agent (I2i) pattern
├── vessel.py     # Persistent shell, writes to PLATO
├── shell.py      # Agent + vessel in PLATO
├── registry.py   # Pre-built vessels for common domains
└── vessels/      # Domain-specific vessels
```

## The Dojo Model

Just like Casey's fishing boat dojo:
- Greenhorns (agents) come in at any skill level
- They produce value while learning (actions → PLATO)
- They leave with a better vessel (more capable shell)
- Other agents benefit from their contributions (tools in PLATO)

## License

MIT — SuperInstance / cocapn fleet
