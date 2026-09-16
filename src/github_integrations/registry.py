"""Registry and provenance contract for public GitHub research integrations."""

from .midas_adapter import SOURCE_REPO as MIDAS_REPO, SOURCE_LICENSE as MIDAS_LICENSE, council_contract
from .pine_reference import SOURCE_REPO as PINE_REPO, SOURCE_LICENSE as PINE_LICENSE, ROUTES
from .xau_research import SOURCE_REPOS as XAU_REPOS


def integration_registry() -> dict[str, object]:
    return {
        "pine_v6": {
            "source": PINE_REPO,
            "license": PINE_LICENSE,
            "role": "knowledge_rag_and_static_validator",
            "execution": False,
            "routes": sorted(ROUTES),
        },
        "midas": {
            "source": MIDAS_REPO,
            "license": MIDAS_LICENSE,
            "role": "multi_agent_research_council",
            "execution": False,
            "contract": council_contract(),
        },
        "xau_research": {
            "sources": list(XAU_REPOS),
            "role": "Q1_Q2_Q7_feature_research",
            "execution": False,
            "models": ["EMA", "RSI", "ATR", "structure", "FVG", "regime_proxy"],
        },
        "xauusd_market_data": {
            "sources": ["GOLD_API", "YAHOO_FINANCE"],
            "gold_api_symbol": "XAU",
            "yahoo_symbol": "XAUUSD=X",
            "role": "independent_spot_and_ohlc_validation",
            "execution": False,
            "research_only": True,
            "weight_update": False,
            "live_execution": False,
        },
        "policy": {
            "live_orders": False,
            "paper_only": True,
            "human_approval_required": True,
            "external_source_is_not_execution_authority": True,
        },
    }
