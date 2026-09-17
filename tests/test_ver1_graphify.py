import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from qgraph.adapter import QGraph, is_secret_path, build_safe_inventory
from graphify_boundary import GraphifyBoundary

def test_graph_boundary():
    assert GraphifyBoundary().validate() is True
    g=QGraph(); a=g.add_node('Agent','Q4','src/q4.py'); b=g.add_node('Skill','Quant','src/quant.py',trust='INFERRED'); g.add_edge(a,b,'USES')
    assert len(g.nodes)==2 and g.edges[0].trust=='EXTRACTED'

def test_secrets_never_enter_inventory(tmp_path):
    (tmp_path/'.env').write_text('secret'); (tmp_path/'broker_API_KEY.txt').write_text('secret'); (tmp_path/'README.md').write_text('safe')
    inv=build_safe_inventory(str(tmp_path)); assert 'README.md' in inv and '.env' not in inv and 'broker_API_KEY.txt' not in inv
    assert is_secret_path('.env') and is_secret_path('broker_API_KEY.txt')

def test_invalid_trust_rejected():
    try: QGraph().add_node('Agent','Q1','x','UNKNOWN'); assert False
    except ValueError: pass
