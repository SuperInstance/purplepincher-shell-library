"""Tests for Vessel class."""

import pytest
from purplepincher.vessel import Vessel, VesselState


class TestVessel:
    def test_create_vessel(self):
        v = Vessel("test")
        assert v.name == "test"
        assert v.state.vessel_id == "test"
        assert v.state.actions_count == 0
    
    def test_act_increments_count(self):
        v = Vessel("test")
        result = v.act("log_catch", {"species": "tuna"})
        assert v.state.actions_count == 1
    
    def test_repr(self):
        v = Vessel("fishinglog")
        assert "fishinglog" in repr(v)
    
    def test_train_lora_returns_id(self):
        v = Vessel("test")
        lora_id = v.train_lora([])
        assert "lora/test" in lora_id
