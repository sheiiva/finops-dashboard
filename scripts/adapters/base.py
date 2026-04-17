"""Base provider adapter contract."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ProviderAdapter(ABC):
    """Abstract contract implemented by each cloud provider adapter."""

    provider: str

    @abstractmethod
    def fetch_inventory(self, scope: dict) -> list[dict]:
        """Collect inventory metadata from provider APIs."""

    @abstractmethod
    def fetch_utilization(self, scope: dict) -> list[dict]:
        """Collect utilization metrics/signals from provider APIs."""

    @abstractmethod
    def fetch_costs(self, scope: dict) -> list[dict]:
        """Collect billing/cost data from provider APIs."""

    @abstractmethod
    def normalize(self, records: list[dict]) -> list[dict]:
        """Normalize provider records to common output contract."""

    @abstractmethod
    def healthcheck(self) -> dict:
        """Return adapter health state."""
