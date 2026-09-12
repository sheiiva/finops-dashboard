"""Tests for CSV billing → metrics converter (v1 slim)."""

from pathlib import Path

from scripts.csv_billing_to_metrics import (
    build_alerts,
    build_messages,
    build_opportunities,
    build_site_snapshot,
    load_services,
    render_prom,
)

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "config/examples/gcp-billing-services.sample.csv"


def test_load_services_parses_invoice_and_rows() -> None:
    services, invoice = load_services(CSV)
    assert len(services) == 25
    assert invoice == 7335.08
    assert services[0].name == "Cloud Composer"
    assert services[0].service_id == "1992-3666-B975"
    assert services[0].subtotal > services[-1].subtotal


def test_opportunities_and_prom_contain_v1_sections() -> None:
    services, invoice = load_services(CSV)
    opportunities = build_opportunities(services, invoice)
    alerts = build_alerts(services, opportunities)
    messages = build_messages(services, invoice, opportunities, alerts)
    prom = render_prom(services, invoice, opportunities, alerts, messages)

    assert messages["pack"] == "v1-slim"
    assert messages["sections_included"] == ["A", "B", "C", "F", "G", "J"]
    assert "finops_gcp_cost_total_usd" in prom
    assert "Cloud Composer" in prom
    assert opportunities
    assert all(0 <= o["priority_score"] <= 100 for o in opportunities)
    assert "owner:" in opportunities[0]["message"]


def test_site_snapshot_has_showcase_fields() -> None:
    services, invoice = load_services(CSV)
    opportunities = build_opportunities(services, invoice)
    alerts = build_alerts(services, opportunities)
    messages = build_messages(services, invoice, opportunities, alerts)
    snap = build_site_snapshot(services, invoice, opportunities, alerts, messages)
    assert snap["version"] == "v1"
    assert snap["cloud"] == "Google Cloud"
    assert snap["invoice_total_usd"] == invoice
    assert snap["open_actions"] == len(opportunities)
    assert snap["top_services"][0]["name"] == "Cloud Composer"
    assert snap["top_services"][0]["service_id"]
    assert snap["actions"]
    assert max(a["priority_score"] for a in snap["actions"]) <= 100
    assert snap["messages"]["A"]["message"]
