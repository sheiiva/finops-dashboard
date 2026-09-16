"""Tests for CSV billing → metrics converter (v1.1)."""

from pathlib import Path

from scripts.csv_billing_to_metrics import (
    _invoice_mom,
    build_alerts,
    build_allocation,
    build_forecast,
    build_governance,
    build_messages,
    build_opportunities,
    build_pareto,
    build_savings,
    build_site_snapshot,
    load_services,
    render_prom,
)

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "config/examples/gcp-billing-services.sample.csv"


def _pipeline():
    services, invoice = load_services(CSV)
    opportunities = build_opportunities(services, invoice)
    pareto = build_pareto(services, invoice)
    savings = build_savings(services)
    allocation = build_allocation(services, invoice)
    _, _, mom = _invoice_mom(services)
    opportunity_total = round(sum(o["est_monthly_savings_usd"] for o in opportunities), 2)
    forecast = build_forecast(invoice, mom, opportunity_total)
    governance = build_governance()
    alerts = build_alerts(services, opportunities, allocation)
    messages = build_messages(
        services,
        invoice,
        opportunities,
        alerts,
        pareto,
        savings,
        allocation,
        forecast,
    )
    return services, invoice, opportunities, alerts, messages, pareto, savings, allocation, forecast, governance


def test_load_services_parses_invoice_and_rows() -> None:
    services, invoice = load_services(CSV)
    assert len(services) == 25
    assert invoice == 7335.08
    assert services[0].name == "Cloud Composer"
    assert services[0].service_id == "1992-3666-B975"
    assert services[0].subtotal > services[-1].subtotal


def test_opportunities_and_prom_contain_v1_sections() -> None:
    (
        services,
        invoice,
        opportunities,
        alerts,
        messages,
        pareto,
        savings,
        allocation,
        forecast,
        _,
    ) = _pipeline()
    prom = render_prom(
        services,
        invoice,
        opportunities,
        alerts,
        messages,
        pareto,
        savings,
        allocation,
        forecast,
    )

    assert messages["pack"] == "v1.1"
    assert messages["sections_included"] == [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
    ]
    assert "finops_gcp_cost_total_usd" in prom
    assert "finops_pareto_top5_share_ratio" in prom
    assert "finops_forecast_next_invoice_usd" in prom
    assert "Cloud Composer" in prom
    assert opportunities
    assert all(0 <= o["priority_score"] <= 100 for o in opportunities)
    assert "owner:" in opportunities[0]["message"]


def test_site_snapshot_has_showcase_fields() -> None:
    (
        services,
        invoice,
        opportunities,
        alerts,
        messages,
        pareto,
        savings,
        allocation,
        forecast,
        governance,
    ) = _pipeline()
    snap = build_site_snapshot(
        services,
        invoice,
        opportunities,
        alerts,
        messages,
        pareto,
        savings,
        allocation,
        forecast,
        governance,
    )
    assert snap["version"] == "v1.1"
    assert snap["cloud"] == "Google Cloud"
    assert snap["invoice_total_usd"] == invoice
    assert snap["open_actions"] == len(opportunities)
    assert snap["top_services"][0]["name"] == "Cloud Composer"
    assert snap["top_services"][0]["service_id"]
    assert snap["actions"]
    assert max(a["priority_score"] for a in snap["actions"]) <= 100
    assert snap["messages"]["A"]["message"]
    assert snap["pareto"]["services_for_80_pct"] >= 1
    assert "lines" in snap["savings"]
    assert "gaps" in snap["allocation"]
    assert snap["forecast"]["next_invoice_usd"] > 0
    assert snap["governance"]["roles"]
