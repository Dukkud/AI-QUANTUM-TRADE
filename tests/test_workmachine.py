import pytest
from src.workmachine import WorkMachine
from src.workgraph import NodeState

def test_valid_lifecycle():
    m=WorkMachine(); m.transition(NodeState.RUNNING); m.transition(NodeState.VALIDATION); m.transition(NodeState.COMPLETED)
    assert m.state==NodeState.COMPLETED

def test_invalid_transition_blocked():
    m=WorkMachine()
    with pytest.raises(ValueError): m.transition(NodeState.COMPLETED)

def test_retry_bound():
    m=WorkMachine(max_retries=1); m.transition(NodeState.RUNNING); m.transition(NodeState.WAITING); m.transition(NodeState.RUNNING)
    assert m.retries==1
