"""TradingView Pine v6 export templates driven by AI-QUANTUM final decisions.

The exporter is deliberately snapshot-based: Pine receives a signed decision matrix
produced by AI-QUANTUM; it does not make or mutate the platform's final decision.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping

TIMEFRAMES = ("1M", "5M", "15M", "30M", "1H", "2H", "4H", "1D", "1W")
VALID_DECISIONS = {"APPROVE", "APPROVE_REDUCED_SIZE", "WAIT", "NO_TRADE"}
VALID_DIRECTIONS = {"LONG", "SHORT", "FLAT"}

@dataclass(frozen=True)
class TFDecision:
    decision: str
    direction: str = "FLAT"
    probability: float = 0.0
    agreement: float = 0.0
    entry: float | None = None
    stop: float | None = None
    tp1: float | None = None
    tp2: float | None = None
    tp3: float | None = None
    rationale: str = ""

    def validate(self) -> None:
        if self.decision not in VALID_DECISIONS:
            raise ValueError(f"invalid_decision:{self.decision}")
        if self.direction not in VALID_DIRECTIONS:
            raise ValueError(f"invalid_direction:{self.direction}")
        if not 0 <= self.probability <= 1 or not 0 <= self.agreement <= 1:
            raise ValueError("probability_or_agreement_out_of_range")

@dataclass(frozen=True)
class PineExport:
    variant: str
    symbol: str
    generated_at: str
    content: str
    checksum: str

class PineExporter:
    """Generate two non-executing TradingView indicators from a final AQ decision matrix."""
    def __init__(self, *, symbol: str, generated_at: str):
        self.symbol = symbol
        self.generated_at = generated_at

    def _normalize(self, decisions: Mapping[str, TFDecision]) -> dict[str, TFDecision]:
        missing = [tf for tf in TIMEFRAMES if tf not in decisions]
        if missing:
            raise ValueError("missing_timeframes:" + ",".join(missing))
        out = {tf: decisions[tf] for tf in TIMEFRAMES}
        for d in out.values(): d.validate()
        return out

    @staticmethod
    def _num(v: float | None) -> str:
        return "na" if v is None else f"{v:.10g}"

    def _header(self, title: str, variant: str) -> str:
        return f'''//@version=6
indicator("{title}", "AQ-QUANTUM {variant}", overlay=true, max_labels_count=100)
// AI-QUANTUM FINAL DECISION SNAPSHOT
// Symbol: {self.symbol}
// Generated: {self.generated_at}
// This script visualizes a platform conclusion. It does NOT place orders and does NOT change Q1-Q9/Q8 decisions.
'''

    def _matrix_constants(self, d: dict[str, TFDecision]) -> str:
        lines = ["// Final decision matrix supplied by AI-QUANTUM", "string[] AQ_TF = array.from(" + ",".join('"'+tf+'"' for tf in TIMEFRAMES) + ")"]
        for tf in TIMEFRAMES:
            x=d[tf]
            key=tf.replace("M","m").replace("H","h").replace("1D","1d").replace("1W","1w")
            lines.append(f'const string D_{key} = "{x.decision}"')
            lines.append(f'const string DIR_{key} = "{x.direction}"')
            lines.append(f'const float P_{key} = {x.probability:.6f}')
            lines.append(f'const float A_{key} = {x.agreement:.6f}')
            for k,val in (("E",x.entry),("SL",x.stop),("TP1",x.tp1),("TP2",x.tp2),("TP3",x.tp3)):
                lines.append(f'const float {k}_{key} = {self._num(val)}')
        return "\n".join(lines)+"\n"

    def variant_1(self, decisions: Mapping[str, TFDecision]) -> PineExport:
        d=self._normalize(decisions)
        code=self._header("AI-QUANTUM Final Decision | Signal Matrix", "V1 SIGNAL MATRIX")
        code += self._matrix_constants(d)
        code += r'''
string tf = timeframe.period
string decision = tf == "1" ? D_1m : tf == "5" ? D_5m : tf == "15" ? D_15m : tf == "30" ? D_30m : tf == "60" ? D_1h : tf == "120" ? D_2h : tf == "240" ? D_4h : tf == "1D" ? D_1d : tf == "1W" ? D_1w : "NO_TRADE"
string direction = tf == "1" ? DIR_1m : tf == "5" ? DIR_5m : tf == "15" ? DIR_15m : tf == "30" ? DIR_30m : tf == "60" ? DIR_1h : tf == "120" ? DIR_2h : tf == "240" ? DIR_4h : tf == "1D" ? DIR_1d : tf == "1W" ? DIR_1w : "FLAT"
float prob = tf == "1" ? P_1m : tf == "5" ? P_5m : tf == "15" ? P_15m : tf == "30" ? P_30m : tf == "60" ? P_1h : tf == "120" ? P_2h : tf == "240" ? P_4h : tf == "1D" ? P_1d : tf == "1W" ? P_1w : 0.0
float agree = tf == "1" ? A_1m : tf == "5" ? A_5m : tf == "15" ? A_15m : tf == "30" ? A_30m : tf == "60" ? A_1h : tf == "120" ? A_2h : tf == "240" ? A_4h : tf == "1D" ? A_1d : tf == "1W" ? A_1w : 0.0
float entry = tf == "1" ? E_1m : tf == "5" ? E_5m : tf == "15" ? E_15m : tf == "30" ? E_30m : tf == "60" ? E_1h : tf == "120" ? E_2h : tf == "240" ? E_4h : tf == "1D" ? E_1d : tf == "1W" ? E_1w : na
float stop = tf == "1" ? SL_1m : tf == "5" ? SL_5m : tf == "15" ? SL_15m : tf == "30" ? SL_30m : tf == "60" ? SL_1h : tf == "120" ? SL_2h : tf == "240" ? SL_4h : tf == "1D" ? SL_1d : tf == "1W" ? SL_1w : na
float tp1 = tf == "1" ? TP1_1m : tf == "5" ? TP1_5m : tf == "15" ? TP1_15m : tf == "30" ? TP1_30m : tf == "60" ? TP1_1h : tf == "120" ? TP1_2h : tf == "240" ? TP1_4h : tf == "1D" ? TP1_1d : tf == "1W" ? TP1_1w : na
float tp2 = tf == "1" ? TP2_1m : tf == "5" ? TP2_5m : tf == "15" ? TP2_15m : tf == "30" ? TP2_30m : tf == "60" ? TP2_1h : tf == "120" ? TP2_2h : tf == "240" ? TP2_4h : tf == "1D" ? TP2_1d : tf == "1W" ? TP2_1w : na
float tp3 = tf == "1" ? TP3_1m : tf == "5" ? TP3_5m : tf == "15" ? TP3_15m : tf == "30" ? TP3_30m : tf == "60" ? TP3_1h : tf == "120" ? TP3_2h : tf == "240" ? TP3_4h : tf == "1D" ? TP3_1d : tf == "1W" ? TP3_1w : na
bool longOk = direction == "LONG" and (decision == "APPROVE" or decision == "APPROVE_REDUCED_SIZE")
bool shortOk = direction == "SHORT" and (decision == "APPROVE" or decision == "APPROVE_REDUCED_SIZE")
plot(entry, "AQ Entry", color=color.orange, linewidth=2, style=plot.style_linebr)
plot(stop, "AQ Stop", color=color.red, linewidth=2, style=plot.style_linebr)
plot(tp1, "AQ TP1", color=color.lime, style=plot.style_linebr)
plot(tp2, "AQ TP2", color=color.lime, style=plot.style_linebr)
plot(tp3, "AQ TP3", color=color.lime, style=plot.style_linebr)
plotshape(longOk, "AQ LONG", shape.labelup, location.belowbar, color=color.lime, text="AQ LONG", textcolor=color.black)
plotshape(shortOk, "AQ SHORT", shape.labeldown, location.abovebar, color=color.red, text="AQ SHORT", textcolor=color.white)
bgcolor(decision == "WAIT" ? color.new(color.orange, 88) : decision == "NO_TRADE" ? color.new(color.red, 90) : na)
var table dash = table.new(position.top_right, 2, 5)
if barstate.islast
    table.cell(dash,0,0,"AI-QUANTUM")
    table.cell(dash,1,0,"FINAL")
    table.cell(dash,0,1,"TF")
    table.cell(dash,1,1,tf)
    table.cell(dash,0,2,"Decision")
    table.cell(dash,1,2,decision)
    table.cell(dash,0,3,"Direction")
    table.cell(dash,1,3,direction)
    table.cell(dash,0,4,"P / Agreement")
    table.cell(dash,1,4,str.tostring(prob*100,"#.0")+"% / "+str.tostring(agree*100,"#.0")+"%")
alertcondition(longOk, "AI-QUANTUM LONG", "AI-QUANTUM final decision: LONG")
alertcondition(shortOk, "AI-QUANTUM SHORT", "AI-QUANTUM final decision: SHORT")
'''
        return self._pack("V1_SIGNAL_MATRIX", code)

    def variant_2(self, decisions: Mapping[str, TFDecision]) -> PineExport:
        d=self._normalize(decisions)
        code=self._header("AI-QUANTUM Final Decision | Institutional Confluence", "V2 INSTITUTIONAL CONFLUENCE")
        code += self._matrix_constants(d)
        code += r'''
int srLen = input.int(130, "S&R Reference Length", minval=20)
float srHigh = ta.highest(high, srLen)
float srLow = ta.lowest(low, srLen)
float srMid = math.avg(srHigh, srLow)
plot(srHigh, "AQ S&R Resistance", color=color.fuchsia, linewidth=1)
plot(srLow, "AQ S&R Support", color=color.lime, linewidth=1)
plot(srMid, "AQ S&R Mid", color=color.gray, linewidth=1)
int pivotLen = input.int(5, "OB Pivot Lookback", minval=2)
float ph = ta.pivothigh(high, pivotLen, pivotLen)
float pl = ta.pivotlow(low, pivotLen, pivotLen)
var float obTop = na
var float obBottom = na
var bool obBull = false
if not na(pl)
    obBottom := low[pivotLen]
    obTop := high[pivotLen]
    obBull := true
if not na(ph)
    obBottom := low[pivotLen]
    obTop := high[pivotLen]
    obBull := false
float obMid = math.avg(obTop, obBottom)
plot(obTop, "AQ Institutional OB Top", color=obBull ? color.new(color.lime,35) : color.new(color.red,35), style=plot.style_linebr)
plot(obBottom, "AQ Institutional OB Bottom", color=obBull ? color.new(color.lime,35) : color.new(color.red,35), style=plot.style_linebr)
plot(obMid, "AQ Institutional OB Median", color=color.new(color.white,20), linewidth=2, style=plot.style_linebr)
string tf = timeframe.period
string decision = tf == "1" ? D_1m : tf == "5" ? D_5m : tf == "15" ? D_15m : tf == "30" ? D_30m : tf == "60" ? D_1h : tf == "120" ? D_2h : tf == "240" ? D_4h : tf == "1D" ? D_1d : tf == "1W" ? D_1w : "NO_TRADE"
string direction = tf == "1" ? DIR_1m : tf == "5" ? DIR_5m : tf == "15" ? DIR_15m : tf == "30" ? DIR_30m : tf == "60" ? DIR_1h : tf == "120" ? DIR_2h : tf == "240" ? DIR_4h : tf == "1D" ? DIR_1d : tf == "1W" ? DIR_1w : "FLAT"
float prob = tf == "1" ? P_1m : tf == "5" ? P_5m : tf == "15" ? P_15m : tf == "30" ? P_30m : tf == "60" ? P_1h : tf == "120" ? P_2h : tf == "240" ? P_4h : tf == "1D" ? P_1d : tf == "1W" ? P_1w : 0.0
float agree = tf == "1" ? A_1m : tf == "5" ? A_5m : tf == "15" ? A_15m : tf == "30" ? A_30m : tf == "60" ? A_1h : tf == "120" ? A_2h : tf == "240" ? A_4h : tf == "1D" ? A_1d : tf == "1W" ? A_1w : 0.0
bool approved = decision == "APPROVE" or decision == "APPROVE_REDUCED_SIZE"
bool longOk = approved and direction == "LONG"
bool shortOk = approved and direction == "SHORT"
bool confluenceLong = longOk and close > srMid and obBull
bool confluenceShort = shortOk and close < srMid and not obBull
bgcolor(confluenceLong ? color.new(color.lime, 90) : confluenceShort ? color.new(color.red, 90) : decision == "WAIT" ? color.new(color.orange, 92) : decision == "NO_TRADE" ? color.new(color.red, 94) : na)
plotshape(confluenceLong, "AQ Institutional LONG", shape.labelup, location.belowbar, color=color.lime, text="AQ I-LONG", textcolor=color.black)
plotshape(confluenceShort, "AQ Institutional SHORT", shape.labeldown, location.abovebar, color=color.red, text="AQ I-SHORT", textcolor=color.white)
var table dash = table.new(position.top_right, 2, 6)
if barstate.islast
    table.cell(dash,0,0,"AQ INSTITUTIONAL")
    table.cell(dash,1,0,"FINAL")
    table.cell(dash,0,1,"TF / Decision")
    table.cell(dash,1,1,tf+" / "+decision)
    table.cell(dash,0,2,"Direction")
    table.cell(dash,1,2,direction)
    table.cell(dash,0,3,"P / Agreement")
    table.cell(dash,1,3,str.tostring(prob*100,"#.0")+"% / "+str.tostring(agree*100,"#.0")+"%")
    table.cell(dash,0,4,"S/R Mid")
    table.cell(dash,1,4,str.tostring(srMid,format.mintick))
    table.cell(dash,0,5,"OB Bias")
    table.cell(dash,1,5,obBull ? "BULLISH" : "BEARISH")
alertcondition(confluenceLong, "AI-QUANTUM Institutional LONG", "AI-QUANTUM institutional confluence: LONG")
alertcondition(confluenceShort, "AI-QUANTUM Institutional SHORT", "AI-QUANTUM institutional confluence: SHORT")
'''
        return self._pack("V2_INSTITUTIONAL_CONFLUENCE", code)

    def _pack(self, variant: str, code: str) -> PineExport:
        digest=sha256(code.encode()).hexdigest()
        return PineExport(variant,self.symbol,self.generated_at,code,digest)

    def export_both(self, decisions: Mapping[str, TFDecision]) -> tuple[PineExport, PineExport]:
        return self.variant_1(decisions), self.variant_2(decisions)
