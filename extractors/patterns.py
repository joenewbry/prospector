from adapters.base import Prospect


TRUST_GAP_SIGNALS = {
    # High trust gap = screen history is very valuable
    "no_company": 0.3,
    "few_public_repos": 0.4,
    "low_followers": 0.2,
    "self_taught": 0.8,
    "career_changer": 0.7,
    "bootcamp_grad": 0.6,
    "junior_level": 0.5,
    "bio_mentions_looking_for": 0.3,
    "bio_mentions_open_to": 0.3,
    "bio_mentions_seeking": 0.3,
    "bio_mentions_available": 0.2,
    "bio_mentions_laid_off": 0.6,
    "freelance_available": 0.5,
    "build_in_public": 0.7,
    "100_days_of_code": 0.6,
    "ai_prompt_engineer": 0.8,
    "indie_hacker": 0.5,
    "web3": 0.4,
    "wants_remote": 0.3,
}

REACHABILITY_SIGNALS = {
    "has_github": 0.3,
    "has_linkedin": 0.4,
    "has_website": 0.5,
    "hireable_flag": 0.6,
    "bio_mentions_open_to": 0.4,
    "bio_mentions_available": 0.5,
    "freelance_available": 0.5,
    "build_in_public": 0.3,
}

# Gaming influence signals — used for openarcade campaign
# Repurposes trust_gap_score field as an "influence score"
GAMING_INFLUENCE_SIGNALS = {
    "gaming_youtuber": 0.9,
    "gaming_streamer": 0.8,
    "gaming_reviewer": 0.8,
    "gaming_blogger": 0.7,
    "gaming_retro": 0.6,
    "gaming_arcade": 0.7,
    "gaming_browser": 0.8,
    "gaming_indiedev": 0.5,
    "has_game_repos": 0.3,
    "active_in_gaming": 0.5,
    "show_hn_poster": 0.4,
    "high_engagement_post": 0.5,
    "gaming_platform": 0.8,
    "gaming_submission_target": 0.3,
    "game_portal": 0.6,
    "game_review_site": 0.7,
    "game_aggregator": 0.5,
    "gaming_community": 0.5,
}

GAMING_REACHABILITY_SIGNALS = {
    "has_github": 0.3,
    "has_website": 0.5,
    "gaming_platform": 0.6,
    "game_portal": 0.5,
    "gaming_submission_target": 0.6,
    "active_in_gaming": 0.3,
    "gaming_youtuber": 0.5,
    "gaming_streamer": 0.5,
    "gaming_reviewer": 0.4,
    "gaming_blogger": 0.4,
    "show_hn_poster": 0.3,
}

GAMING_RELEVANCE_CATEGORIES = {
    "Gaming YouTuber": 0.95,
    "Retro Gaming Streamer": 0.90,
    "Game Reviewer": 0.90,
    "Gaming Content Creator": 0.85,
    "Browser Game Enthusiast": 0.85,
    "Gaming Platform": 0.90,
    "Retro Enthusiast": 0.80,
    "Game Developer": 0.60,
    "Indie Game Dev": 0.65,
    "Game Jam Participant": 0.60,
}


class PatternExtractor:
    """Extract and enrich signals from prospects."""

    def extract(self, prospects: list[Prospect], campaign: str = "memex") -> list[Prospect]:
        for p in prospects:
            if campaign == "openarcade":
                p.trust_gap_score = self._score_gaming_influence(p)
                p.reachability_score = self._score_gaming_reachability(p)
                p.relevance_score = self._score_gaming_relevance(p)
            else:
                p.trust_gap_score = self._score_trust_gap(p)
                p.reachability_score = self._score_reachability(p)
                p.relevance_score = self._score_relevance(p)
        return prospects

    def _score_trust_gap(self, p: Prospect) -> float:
        score = 0.0
        for signal in p.signals:
            score += TRUST_GAP_SIGNALS.get(signal, 0.1)
        return min(score / 3.0, 1.0)

    def _score_reachability(self, p: Prospect) -> float:
        score = 0.0
        for signal in p.signals:
            score += REACHABILITY_SIGNALS.get(signal, 0.0)
        if p.raw_data.get("github_url"):
            score += 0.3
        if p.raw_data.get("linkedin_url"):
            score += 0.3
        if p.raw_data.get("website_url"):
            score += 0.2
        return min(score / 2.0, 1.0)

    def _score_relevance(self, p: Prospect) -> float:
        """How relevant is screen history for this person specifically."""
        high_relevance_categories = {
            "Self-Taught Developer": 0.9,
            "Career Changer": 0.85,
            "Bootcamp Graduate": 0.8,
            "Build in Public": 0.9,
            "AI/Prompt Engineer": 0.95,
            "100DaysOfCode": 0.85,
            "Recently Laid Off": 0.7,
            "Freelancer": 0.75,
            "Junior Developer": 0.7,
            "Job Seeker": 0.65,
            "Senior Developer": 0.5,
            "OSS Contributor": 0.7,
            "Developer": 0.5,
            "Startup Hiring": 0.6,
        }
        return high_relevance_categories.get(p.category, 0.5)

    # --- Gaming campaign scoring ---

    def _score_gaming_influence(self, p: Prospect) -> float:
        """Influence score for gaming campaign (stored in trust_gap_score field)."""
        score = 0.0
        for signal in p.signals:
            score += GAMING_INFLUENCE_SIGNALS.get(signal, 0.05)
        return min(score / 2.5, 1.0)

    def _score_gaming_reachability(self, p: Prospect) -> float:
        score = 0.0
        for signal in p.signals:
            score += GAMING_REACHABILITY_SIGNALS.get(signal, 0.0)
        if p.raw_data.get("story_url"):
            score += 0.2
        if p.raw_data.get("contact_role"):
            score += 0.4
        return min(score / 2.0, 1.0)

    def _score_gaming_relevance(self, p: Prospect) -> float:
        return GAMING_RELEVANCE_CATEGORIES.get(p.category, 0.5)
