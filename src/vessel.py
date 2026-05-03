"""Minimal Agent/Vessel Separation — persistent shell that survives context compaction.
A vessel is a persistent directory. An agent is ephemeral. Agents eject → merge into
vessel. New agents attach → inherit accumulated state.  python src/vessel.py"""
from __future__ import annotations
import json, hashlib, time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass(frozen=True)
class Charter:
    purpose: str
    created_at: float = field(default_factory=time.time)

@dataclass
class Identity:
    name: str = ""
    role: str = ""
    notes: str = ""
    last_agent: str = ""
    updated_at: float = field(default_factory=time.time)

@dataclass
class Memory:
    long_term: dict[str, Any] = field(default_factory=dict)
    session: dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentState:
    agent_id: str
    identity_delta: dict[str, Any]
    session_memory: dict[str, Any]
    skills_added: list[str]
    ejected_at: float = field(default_factory=time.time)

class Vessel:
    def __init__(self, root: str, purpose: str):
        self.root = Path(root)
        self.charter = Charter(purpose=purpose)
        self.identity = Identity()
        self.memory = Memory()
        self.skills: set[str] = set()
        self.ejected: list[AgentState] = []
        self._attached: str | None = None
        self._save()
    def _save(self):
        self.root.mkdir(parents=True, exist_ok=True)
        data = {
            "charter.json": asdict(self.charter),
            "identity.json": asdict(self.identity),
            "memory.json": asdict(self.memory),
            "skills.json": {"skills": list(self.skills)},
            "ejected.json": {"ejected": [asdict(e) for e in self.ejected]},
        }
        for name, payload in data.items():
            with open(self.root / name, "w") as f:
                json.dump(payload, f, indent=2, default=str)
    @classmethod
    def load(cls, root: str) -> "Vessel":
        v = cls.__new__(cls)
        v.root = Path(root)
        v.charter = Charter(**json.load(open(v.root / "charter.json")))
        v.identity = Identity(**json.load(open(v.root / "identity.json")))
        m = json.load(open(v.root / "memory.json"))
        v.memory = Memory(long_term=m.get("long_term", {}), session=m.get("session", {}))
        v.skills = set(json.load(open(v.root / "skills.json")).get("skills", []))
        v.ejected = [AgentState(**e) for e in json.load(open(v.root / "ejected.json")).get("ejected", [])]
        v._attached = None
        return v
    def attach(self, agent_config: dict) -> "Agent":
        agent = Agent(self, agent_config)
        self._attached = agent.agent_id
        return agent
    def __repr__(self) -> str:
        return (f"Vessel({self.root.name}, charter={self.charter.purpose!r}, "
                f"agents={len(self.ejected)}, skills={len(self.skills)})")

class Agent:
    def __init__(self, vessel: Vessel, config: dict):
        self.vessel = vessel
        self.api_key = config.get("api_key", "")
        self.agent_id = config.get("agent_id", "anon_" + _token()[:8])
        self.identity = Identity(**asdict(vessel.identity))
        self.skills = set(vessel.skills)
        self.memory = vessel.memory
    def work(self, task: str, result: Any):
        self.memory.session[task] = result
        if ":" in task:
            self.skills.add(task.split(":", 1)[0])
    def remember(self, key: str, value: Any):
        self.memory.long_term[key] = value
    def eject(self) -> AgentState:
        state = AgentState(
            agent_id=self.agent_id,
            identity_delta={k: v for k, v in asdict(self.identity).items()
                            if v != getattr(self.vessel.identity, k, None)},
            session_memory=dict(self.memory.session),
            skills_added=list(self.skills - self.vessel.skills),
        )
        self.vessel.identity = self.identity
        self.vessel.skills |= self.skills
        self.vessel.memory = self.memory
        self.vessel.ejected.append(state)
        self.vessel._attached = None
        self.vessel._save()
        return state
    def __repr__(self) -> str:
        return f"Agent({self.agent_id}, vessel={self.vessel.root.name})"

def _token() -> str:
    return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]

if __name__ == "__main__":
    import tempfile, shutil
    tmpdir = tempfile.mkdtemp(prefix="vessel_demo_")
    try:
        v = Vessel(tmpdir, purpose="Explore PLATO rooms and report findings")
        print("\n1. Created:", v)
        alice = v.attach({"agent_id": "Alice", "api_key": "sk-alice"})
        print("\n2. Attached:", alice, "skills:", alice.skills, "memory:", alice.memory.long_term)
        alice.work("scout:room_1", {"exits": ["n", "e"], "objects": 3})
        alice.work("scout:room_2", {"exits": ["s"], "objects": 1})
        alice.remember("map_complete", True)
        alice.identity.name = "Alice the Scout"
        alice.identity.notes = "Found 2 rooms, 4 objects"
        print("\n3. Alice worked. session:", alice.memory.session)
        print("   long_term:", alice.memory.long_term)
        state = alice.eject()
        print("\n4. Ejected Alice — skills_added:", state.skills_added,
              "id_delta:", state.identity_delta)
        print("   vessel skills:", v.skills, "memory:", v.memory.long_term)
        bob = v.attach({"agent_id": "Bob", "api_key": "sk-bob"})
        print("\n5. Attached:", bob, "skills:", bob.skills, "memory:", bob.memory.long_term)
        assert "scout" in bob.skills and v.memory.long_term.get("map_complete")
        assert v.identity.name == "Alice the Scout"
        print("\n6. ✓ Bob sees Alice's skills, memory, and identity.")
        bob.work("report:summary", "4 objects across 2 rooms")
        bob.remember("object_count", 4)
        bob.eject()
        print("\n7. Bob ejected. Vessel has", len(v.ejected), "agents.")
        print("   final memory:", v.memory.long_term)
        print("\n   --- Vessel survived ---")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
