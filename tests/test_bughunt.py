import math
from src.bughunt import scan_metrics

def test_nonfinite_found(): assert scan_metrics({"brier":math.nan})[0].code=="NONFINITE"
def test_lineage_found(): assert scan_metrics({"prediction_id":""})[0].code=="MISSING_LINEAGE"
def test_clean_metrics(): assert scan_metrics({"brier":0.2,"prediction_id":"p1"})==()
