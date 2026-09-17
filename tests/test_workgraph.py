import pytest
from src.workgraph import WorkNode,Workgraph

def test_dependency_order():
    g=Workgraph((WorkNode("data"),WorkNode("replay",("data",)),WorkNode("oos",("replay",))))
    assert g.ready()==("data",)

def test_cycle_rejected():
    with pytest.raises(ValueError,match="cycle"):
        Workgraph((WorkNode("a",("b",)),WorkNode("b",("a",))))
