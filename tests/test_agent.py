"""Tests for Agent class."""

import pytest
from purplepincher.agent import Agent, AgentCommit


class TestAgent:
    def test_create_agent(self):
        a = Agent("test")
        assert a.name == "test"
        assert len(a.commits) == 0
    
    def test_act_creates_commit(self):
        a = Agent("test")
        commit = a.act("log_catch", {"species": "tuna"}, output={"logged": True})
        assert isinstance(commit, AgentCommit)
        assert len(a.commits) == 1
        assert commit.action == "log_catch"
    
    def test_query_finds_relevant(self):
        a = Agent("test")
        a.act("log_catch", {"species": "tuna"})
        a.act("log_depth", {"depth": 50})
        results = a.query("catch")
        assert len(results) == 1
        assert results[0]["action"] == "log_catch"
    
    def test_log_creates_commit(self):
        a = Agent("test")
        commit = a.log("test message")
        assert commit.action == "log"
        assert commit.output_data is None
