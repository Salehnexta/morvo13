"""Site customisation for Morvo.

This module is imported automatically by the Python interpreter if it is
present on `PYTHONPATH`.  We use it to silence noisy third-party deprecation
warnings that do not affect runtime behaviour, keeping logs clean in
production and during tests.
"""

from __future__ import annotations

import warnings

# ---------------------------------------------------------------------------
# Suppress Pydantic V1/V2 mixing warnings emitted by CrewAI dependencies.
# ---------------------------------------------------------------------------
warnings.filterwarnings(
    "ignore",
    message=r"Mixing V1 models and V2 models",
    category=UserWarning,
)

# Suppress pkg_resources deprecation noise (to be removed ~2025)
warnings.filterwarnings(
    "ignore",
    message=r"pkg_resources is deprecated as an API",
    category=UserWarning,
) 