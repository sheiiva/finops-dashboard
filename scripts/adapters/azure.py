"""Azure adapter stub implementing ProviderAdapter contract."""

from __future__ import annotations

from .base import ProviderAdapter


class AzureAdapter(ProviderAdapter):
    provider = "azure"

    def fetch_inventory(self, scope: dict) -> list[dict]:
        return []

    def fetch_utilization(self, scope: dict) -> list[dict]:
        return []

    def fetch_costs(self, scope: dict) -> list[dict]:
        return []

    def normalize(self, records: list[dict]) -> list[dict]:
        return records

    def healthcheck(self) -> dict:
        return {"provider": self.provider, "status": "ok", "ready": True}
