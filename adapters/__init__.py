from .base import BaseAdapter, Prospect
from .github import GitHubAdapter
from .hn import HackerNewsAdapter
from .x_twitter import XTwitterAdapter
from .bootcamps import BootcampAdapter
from .gaming_platforms import GamingPlatformAdapter

ADAPTERS = {
    "github": GitHubAdapter,
    "hackernews": HackerNewsAdapter,
    "x_twitter": XTwitterAdapter,
    "bootcamps": BootcampAdapter,
    "gaming_platforms": GamingPlatformAdapter,
}
