"""Version-keyed cache invalidation for public-page fragments.

Public pages are read-heavy and change only when staff edit content. Rather
than track per-fragment keys, every cached fragment is keyed on a single
integer ``cache_version``. Saving or deleting any content model bumps the
version (see :mod:`apps.core.signals`), so the next request misses the old
fragments and rebuilds them — an instant, global "cache-bust on dashboard
save" (BS §403) with no stale content.
"""

from django.core.cache import cache

CACHE_VERSION_KEY = "public:cache_version"


def get_cache_version() -> int:
    """Current content version (initialised to 1 on first read)."""
    return cache.get_or_set(CACHE_VERSION_KEY, 1, None)


def bump_cache_version() -> int:
    """Invalidate all version-keyed fragments by advancing the version."""
    try:
        return cache.incr(CACHE_VERSION_KEY)
    except ValueError:
        # Key not initialised yet — set it past the default so any fragment
        # cached under version 1 is abandoned.
        cache.set(CACHE_VERSION_KEY, 2, None)
        return 2
