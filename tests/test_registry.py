"""Tests for VesselRegistry."""

import pytest
from purplepincher.registry import VesselRegistry, get_registry


class TestVesselRegistry:
    def test_list_vessels(self):
        r = VesselRegistry()
        vessels = r.list_vessels()
        assert len(vessels) >= 4
        names = [v["name"] for v in vessels]
        assert "fishinglog" in names
        assert "studylog" in names
    
    def test_get_vessel(self):
        r = VesselRegistry()
        v = r.get("fishinglog")
        assert v.name == "fishinglog"
    
    def test_get_registry_singleton(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2
