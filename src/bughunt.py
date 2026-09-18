from dataclasses import dataclass
import math
@dataclass(frozen=True)
class BugFinding:
    code:str; severity:str; detail:str
def scan_metrics(metrics:dict)->tuple[BugFinding,...]:
    out=[]
    for k,v in metrics.items():
        if isinstance(v,(int,float)) and not math.isfinite(v): out.append(BugFinding("NONFINITE","CRITICAL",k))
    if "prediction_id" in metrics and not metrics["prediction_id"]: out.append(BugFinding("MISSING_LINEAGE","CRITICAL","prediction_id"))
    return tuple(out)
