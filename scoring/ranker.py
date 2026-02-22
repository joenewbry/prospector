from adapters.base import Prospect

MEMEX_WEIGHTS = {
    "trust_gap": 0.45,
    "reachability": 0.25,
    "relevance": 0.30,
}

OPENARCADE_WEIGHTS = {
    "trust_gap": 0.35,   # influence score for gaming
    "reachability": 0.30,
    "relevance": 0.35,
}


class Ranker:
    """Compute final scores and rank prospects."""

    def __init__(self, weights: dict = None):
        self.weights = weights or MEMEX_WEIGHTS.copy()

    def rank(self, prospects: list[Prospect], campaign: str = "memex") -> list[Prospect]:
        # Use campaign-specific defaults if no custom weights were set
        if campaign == "openarcade" and self.weights == MEMEX_WEIGHTS:
            weights = OPENARCADE_WEIGHTS
        else:
            weights = self.weights

        for p in prospects:
            p.final_score = (
                p.trust_gap_score * weights["trust_gap"]
                + p.reachability_score * weights["reachability"]
                + p.relevance_score * weights["relevance"]
            )
        prospects.sort(key=lambda p: p.final_score, reverse=True)
        return prospects
