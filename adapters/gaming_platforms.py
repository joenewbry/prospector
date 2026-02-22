from .base import BaseAdapter, Prospect


GAMING_PLATFORMS = [
    {
        "name": "itch.io",
        "url": "https://itch.io",
        "type": "Game Platform",
        "audience": "Indie game developers and players",
        "size": "500K+ games hosted, millions of monthly visitors",
        "contact_role": "Community team",
        "pitch_angle": "Featured collection of 100+ instant-play browser arcade games — fits perfectly alongside itch.io's existing web game catalog",
    },
    {
        "name": "Newgrounds",
        "url": "https://www.newgrounds.com",
        "type": "Game Platform",
        "audience": "Flash/HTML5 game enthusiasts, animators, indie creators",
        "size": "Active community of creators and players since 1999",
        "contact_role": "Content curation team",
        "pitch_angle": "Classic arcade games plus modern indie browser games — a natural fit for Newgrounds' legacy as the home of browser gaming",
    },
    {
        "name": "CrazyGames",
        "url": "https://www.crazygames.com",
        "type": "Game Portal",
        "audience": "Casual browser game players worldwide",
        "size": "30M+ monthly visitors",
        "contact_role": "Game submissions team",
        "pitch_angle": "Free HTML5 games playable instantly — no downloads, no login, just high-quality browser arcade games",
    },
    {
        "name": "Poki",
        "url": "https://poki.com",
        "type": "Game Portal",
        "audience": "Casual gamers, especially younger demographics",
        "size": "50M+ monthly players",
        "contact_role": "Developer relations",
        "pitch_angle": "High-quality collection of browser-playable arcade games with instant load times and no install required",
    },
    {
        "name": "GameJolt",
        "url": "https://gamejolt.com",
        "type": "Game Platform",
        "audience": "Indie game community, game jam participants",
        "size": "Millions of users, 300K+ games",
        "contact_role": "Community team",
        "pitch_angle": "Indie arcade collection with classic remakes and original games — community-friendly, free to play",
    },
    {
        "name": "Kongregate",
        "url": "https://www.kongregate.com",
        "type": "Game Portal",
        "audience": "Browser game enthusiasts",
        "size": "Legacy platform with loyal player base",
        "contact_role": "Publisher team",
        "pitch_angle": "100+ browser arcade games that would bring new life to the platform's classic web gaming roots",
    },
    {
        "name": "Armor Games",
        "url": "https://armorgames.com",
        "type": "Game Portal",
        "audience": "Strategy and arcade game players",
        "size": "Established community since 2004",
        "contact_role": "Game submissions",
        "pitch_angle": "Curated collection of arcade-style browser games — quality titles that match Armor Games' standards",
    },
    {
        "name": "FreeGamesAZ",
        "url": "https://www.freegamesaz.com",
        "type": "Aggregator",
        "audience": "Free game seekers",
        "size": "Large free games directory",
        "contact_role": "Site admin",
        "pitch_angle": "100+ completely free browser games — perfect directory listing for free game aggregation",
    },
    {
        "name": "Jay is Games",
        "url": "https://jayisgames.com",
        "type": "Review Site",
        "audience": "Curated browser game enthusiasts",
        "size": "Established review community",
        "contact_role": "Editor / reviewer",
        "pitch_angle": "Curated browser game arcade with retro classics and modern indie titles — ideal for a feature review",
    },
    {
        "name": "idev.games",
        "url": "https://idev.games",
        "type": "Developer Community",
        "audience": "Indie game developers",
        "size": "Growing indie dev community",
        "contact_role": "Community admin",
        "pitch_angle": "Open arcade showcasing what's possible with browser game tech — great resource for the dev community",
    },
    {
        "name": "Game Distribution",
        "url": "https://gamedistribution.com",
        "type": "Game Distribution",
        "audience": "Game publishers and portal operators",
        "size": "10K+ HTML5 games distributed",
        "contact_role": "Publisher relations",
        "pitch_angle": "Distribution opportunity for 100+ quality HTML5 arcade games with proven player engagement",
    },
    {
        "name": "Game Jolt (Game Jams)",
        "url": "https://jams.gamejolt.com",
        "type": "Game Jam Hub",
        "audience": "Game jam participants and organizers",
        "size": "Regular game jams with hundreds of participants",
        "contact_role": "Jam organizers",
        "pitch_angle": "Showcase game jam-style projects alongside polished arcade games — great inspiration for jammers",
    },
]


class GamingPlatformAdapter(BaseAdapter):
    name = "gaming_platforms"
    description = "Gaming platforms, portals, and directories to feature OpenArcade — curated list of submission targets"
    icon = "gamepad"
    categories = ["Gaming Platforms", "Game Portals", "Game Directories"]

    def get_config_schema(self):
        return {
            "include_all": {
                "type": "boolean",
                "label": "Include all gaming platforms",
                "default": True,
            },
        }

    async def fetch(self, config: dict) -> list[Prospect]:
        prospects = []
        for gp in GAMING_PLATFORMS:
            signals = ["gaming_platform", "gaming_submission_target"]
            gp_type = gp["type"].lower()
            if "portal" in gp_type:
                signals.append("game_portal")
            if "review" in gp_type:
                signals.append("game_review_site")
            if "aggregator" in gp_type:
                signals.append("game_aggregator")
            if "community" in gp_type or "jam" in gp_type:
                signals.append("gaming_community")

            prospects.append(Prospect(
                source="gaming_platforms",
                username=gp["name"].lower().replace(" ", "-").replace(".", "-"),
                display_name=gp["name"],
                profile_url=gp["url"],
                bio=f"{gp['type']}. {gp['audience']}. {gp['size']}.",
                category="Gaming Platform",
                signals=signals,
                raw_data={
                    "platform_type": gp["type"],
                    "audience": gp["audience"],
                    "size": gp["size"],
                    "contact_role": gp["contact_role"],
                    "pitch_angle": gp["pitch_angle"],
                },
            ))
        return prospects
