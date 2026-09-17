import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class RegressionRecord:
    change_id:str; outcome:str; metric_delta:float; previous_hash:str=""
    def digest(self)->str:
        raw=json.dumps({"change_id":self.change_id,"outcome":self.outcome,"metric_delta":self.metric_delta,"previous_hash":self.previous_hash},sort_keys=True,separators=(",",":"))
        return hashlib.sha256(raw.encode()).hexdigest()
class RegressionMemory:
    def __init__(self): self._records=[]
    def append(self,record):
        if self._records and record.previous_hash!=self._records[-1].digest(): raise ValueError("broken_chain")
        self._records.append(record)
    def all(self): return tuple(self._records)
