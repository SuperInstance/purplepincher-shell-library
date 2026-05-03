"""
Agent — Base agent class with git-agent (I2i) pattern.

The git-agent pattern: every action committed to PLATO like a git commit.
Each commit = functional tool for future agents.
Later agents use tools without carrying old agent's context.
"""

from __future__ import annotations
import time
import hashlib
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class AgentCommit:
    """
    A commit in the git-agent (I2i) pattern.
    Like a git commit, but for agent actions and outputs.
    """
    commit_id: str
    action: str
    input_data: Dict[str, Any]
    output_data: Any
    timestamp: float = field(default_factory=time.time)
    parent_commits: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def message(self) -> str:
        """Commit message for readability."""
        return f"{self.action}: {str(self.input_data)[:50]}"


class Agent:
    """
    Base agent with git-agent (I2i) pattern.
    
    The I2i (Intent-to-Inference) pattern:
    1. Intent comes in
    2. Agent acts and creates a commit (action + output)
    3. Commit is written to PLATO as a functional tool
    4. Later agents use the tool without needing context
    
    Usage:
        agent = Agent(name="fishing_captain")
        agent.act("log_catch", {"species": "tuna"}, output={"logged": True})
        # → commit created and written to PLATO
    """
    
    def __init__(
        self,
        name: str,
        vessel: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.vessel = vessel
        self.metadata = metadata or {}
        self.commits: List[AgentCommit] = []
    
    def _make_commit_id(self, action: str, data: Dict[str, Any]) -> str:
        """Generate deterministic commit ID from action + data."""
        content = f"{action}:{str(data)}:{time.time()}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def act(
        self,
        action: str,
        input_data: Dict[str, Any],
        output_data: Any = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentCommit:
        """
        Execute an action and create a commit.
        
        The commit is the core unit of the git-agent pattern.
        It captures the action, input, and output in a traceable way.
        
        Args:
            action: Name of the action (e.g., "log_catch", "answer_question")
            input_data: What the action was given
            output_data: What the action produced
            metadata: Optional metadata (tags, priority, etc.)
            
        Returns:
            The created AgentCommit
        """
        commit_id = self._make_commit_id(action, input_data)
        
        commit = AgentCommit(
            commit_id=commit_id,
            action=action,
            input_data=input_data,
            output_data=output_data,
            parent_commits=[c.commit_id for c in self.commits[-3:]] if self.commits else [],
            metadata={
                "agent": self.name,
                **(metadata or {})
            }
        )
        
        self.commits.append(commit)
        
        # If vessel attached, write to PLATO as functional tool
        if self.vessel:
            self.vessel.act(action, {
                "commit_id": commit.commit_id,
                "input": input_data,
                "output": output_data,
                "agent": self.name,
                "timestamp": commit.timestamp,
            })
        
        return commit
    
    def query(self, intent: str) -> List[Dict[str, Any]]:
        """
        Query for commits relevant to an intent.
        
        Used by later agents to find relevant tools without carrying context.
        """
        relevant = []
        for commit in reversed(self.commits):
            if intent.lower() in commit.action.lower():
                relevant.append({
                    "commit_id": commit.commit_id,
                    "action": commit.action,
                    "input": commit.input_data,
                    "output": commit.output_data,
                    "timestamp": commit.timestamp,
                })
        return relevant
    
    def get_commits(self, limit: int = 50) -> List[AgentCommit]:
        """Get recent commits."""
        return self.commits[-limit:]
    
    def log(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> AgentCommit:
        """
        Convenience method for logging without output.
        
        Like `git commit -m "message"` with no files changed.
        """
        return self.act("log", {"message": message}, output=None, metadata=metadata)
    
    def __repr__(self) -> str:
        return f"Agent({self.name}, commits={len(self.commits)}, vessel={self.vessel.name if self.vessel else None})"
