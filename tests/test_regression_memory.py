import pytest
from src.regression_memory import RegressionMemory,RegressionRecord

def test_hash_chain():
    m=RegressionMemory(); a=RegressionRecord("c1","DEGRADED",-0.2); m.append(a); b=RegressionRecord("c2","REVIEW",-0.1,a.digest()); m.append(b)
    assert len(m.all())==2

def test_broken_chain_rejected():
    m=RegressionMemory(); m.append(RegressionRecord("c1","DEGRADED",-0.2))
    with pytest.raises(ValueError): m.append(RegressionRecord("c2","PASS",0.1,"bad"))
