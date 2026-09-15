"""Controlled integrations inspired by audited public GitHub research sources.

These modules are adapters and research components. They do not place live orders.
"""

from .registry import integration_registry

__all__ = ["integration_registry"]
