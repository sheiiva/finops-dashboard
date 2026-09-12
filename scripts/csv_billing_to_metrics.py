#!/usr/bin/env python3
"""Convert anonymized billing CSV into Prometheus metrics + demo messages (v1 slim)."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ServiceRow:
    name: str
    service_id: str
    list_cost: float
    other_savings: float
    subtotal: float
    mom_raw: str
    mom_ratio: float | None
    is_new: bool


def _parse_money(value: str) -> float:
    return float(value) if value.strip() else 0.0


def _parse_mom(raw: str) -> tuple[float | None, bool]:
    text = (raw or "").strip()
    if not text:
        return None, False
    if text.lower() == "new":
        return None, True
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)%", text)
    if not match:
        return None, False
    return float(match.group(1)) / 100.0, False


def _prom_label(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("\n", " ").replace('"', '\\"')
    return escaped[:180]


def _service_slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")


def load_services(csv_path: Path) -> tuple[list[ServiceRow], float]:
    rows: list[ServiceRow] = []
    invoice_total = 0.0
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            label = (raw.get("Service description") or "").strip()
            # Footer rows park the label under "Other savings (USD)" in this sample shape.
            if not label:
                footer_label = (raw.get("Other savings (USD)") or "").strip()
                if footer_label == "Invoice total":
                    invoice_total = _parse_money(raw.get("Subtotal (USD)") or "0")
                continue

            mom_ratio, is_new = _parse_mom(raw.get("Percent change in subtotal compared to previous period") or "")
            rows.append(
                ServiceRow(
                    name=label,
                    service_id=(raw.get("Service ID") or "").strip(),
                    list_cost=_parse_money(raw.get("List cost (USD)") or "0"),
                    other_savings=_parse_money(raw.get("Other savings (USD)") or "0"),
                    subtotal=_parse_money(raw.get("Subtotal (USD)") or "0"),
                    mom_raw=(raw.get("Percent change in subtotal compared to previous period") or "").strip(),
                    mom_ratio=mom_ratio,
                    is_new=is_new,
                )
            )

    if not invoice_total:
        invoice_total = round(sum(r.subtotal for r in rows), 2)
    rows.sort(key=lambda r: r.subtotal, reverse=True)
    return rows, invoice_total


OWNER_LABELS = {
    "team-finops": "FinOps",
    "team-platform": "Platform",
    "team-cloud-econ": "Cloud Economics",
}


def _owner_label(owner_id: str) -> str:
    return OWNER_LABELS.get(owner_id, owner_id)


def _score_100(*parts: float) -> float:
    return round(min(100.0, max(0.0, sum(parts))), 1)


def build_opportunities(services: list[ServiceRow], invoice_total: float) -> list[dict]:
    """Demo heuristics for opportunities/action queue — not production recommendations."""
    opportunities: list[dict] = []
    for svc in services:
        if svc.is_new and svc.subtotal >= 40:
            owner = "team-platform"
            opportunities.append(
                {
                    "service": svc.name,
                    "service_id": svc.service_id,
                    "type": "new_service_review",
                    "owner": owner,
                    "owner_label": _owner_label(owner),
                    "priority_score": _score_100(35, min(svc.subtotal / 25, 40)),
                    "est_monthly_savings_usd": round(svc.subtotal * 0.15, 2),
                    "message": (
                        f"Assign an owner for new service {svc.name} "
                        f"({svc.service_id}) — owner: {_owner_label(owner)}"
                    ),
                }
            )
        if svc.mom_ratio is not None and svc.mom_ratio >= 0.5 and svc.subtotal >= 100:
            owner = "team-finops"
            opportunities.append(
                {
                    "service": svc.name,
                    "service_id": svc.service_id,
                    "type": "growth_anomaly",
                    "owner": owner,
                    "owner_label": _owner_label(owner),
                    "priority_score": _score_100(
                        40,
                        min(svc.mom_ratio * 45, 45),
                        min(svc.subtotal / 80, 15),
                    ),
                    "est_monthly_savings_usd": round(
                        svc.subtotal * min(0.25, svc.mom_ratio * 0.2), 2
                    ),
                    "message": (
                        f"Investigate {svc.mom_raw} MoM spike on {svc.name} "
                        f"— owner: {_owner_label(owner)}"
                    ),
                }
            )
        if svc.other_savings < -20:
            owner = "team-cloud-econ"
            opportunities.append(
                {
                    "service": svc.name,
                    "service_id": svc.service_id,
                    "type": "discount_gap",
                    "owner": owner,
                    "owner_label": _owner_label(owner),
                    "priority_score": _score_100(30, min(abs(svc.other_savings) / 3, 50)),
                    "est_monthly_savings_usd": round(abs(svc.other_savings) * 0.5, 2),
                    "message": (
                        f"Review discount coverage on {svc.name} "
                        f"— owner: {_owner_label(owner)}"
                    ),
                }
            )

    long_tail = [s for s in services if 0 < s.subtotal < 25]
    if long_tail:
        target = long_tail[0]
        owner = "team-platform"
        opportunities.append(
            {
                "service": target.name,
                "service_id": target.service_id,
                "type": "idle_candidate",
                "owner": owner,
                "owner_label": _owner_label(owner),
                "priority_score": 48.0,
                "est_monthly_savings_usd": round(target.subtotal * 0.8, 2),
                "message": (
                    f"Check whether {target.name} is still needed "
                    f"— owner: {_owner_label(owner)}"
                ),
            }
        )

    opportunities.sort(key=lambda o: o["priority_score"], reverse=True)
    return opportunities[:8]


def build_alerts(services: list[ServiceRow], opportunities: list[dict]) -> dict[str, int]:
    high_growth = any(s.mom_ratio is not None and s.mom_ratio >= 0.5 and s.subtotal >= 100 for s in services)
    return {
        "spend_spike": 1 if high_growth else 0,
        "service_growth": 1 if high_growth else 0,
        "open_actions": 1 if opportunities else 0,
        "label_compliance_drift": 0,
    }


def build_messages(
    services: list[ServiceRow],
    invoice_total: float,
    opportunities: list[dict],
    alerts: dict[str, int],
) -> dict:
    top = services[0] if services else None
    top_share = (top.subtotal / invoice_total) if top and invoice_total else 0.0
    risers = [s for s in services if s.mom_ratio is not None]
    risers.sort(key=lambda s: s.mom_ratio or 0.0, reverse=True)
    top_riser = risers[0] if risers else None
    new_services = [s for s in services if s.is_new]

    headline = (
        f"Demo invoice ${invoice_total:,.2f} across {len(services)} services. "
        f"Top driver: {top.name} (${top.subtotal:,.2f}, {top_share:.0%} of total)."
        if top
        else f"Demo invoice ${invoice_total:,.2f}."
    )
    # Prior-period estimate from MoM ratios (services with measurable change).
    prior_est = 0.0
    comparable = 0.0
    for svc in services:
        if svc.mom_ratio is None or svc.is_new or svc.mom_ratio <= -0.999:
            continue
        prior_est += svc.subtotal / (1.0 + svc.mom_ratio)
        comparable += svc.subtotal
    if prior_est > 0:
        mom_invoice = (comparable - prior_est) / prior_est
        direction = "up" if mom_invoice >= 0 else "down"
        headline += (
            f" Comparable spend is {direction} {abs(mom_invoice):.0%} vs prior period "
            f"(~${prior_est:,.0f} → ${comparable:,.0f})."
        )
    growth_msg = (
        f"Fastest riser: {top_riser.name} ({top_riser.mom_raw}). "
        f"{len(new_services)} service(s) marked New."
        if top_riser
        else f"{len(new_services)} service(s) marked New."
    )
    action_msg = (
        f"{len(opportunities)} actions queued; top: {opportunities[0]['message']}"
        if opportunities
        else "No demo actions generated."
    )
    alert_on = [k for k, v in alerts.items() if v == 1]
    alert_msg = (
        f"Active demo alerts: {', '.join(alert_on)}."
        if alert_on
        else "No demo alerts active."
    )

    return {
        "disclaimer": "Synthetic anonymized demo data — not a real customer invoice.",
        "period_label": "Demo window 2025-01-01 → 2025-02-28",
        "sections": {
            "A": {"title": "Executive summary", "message": headline},
            "B": {
                "title": "Spend by service",
                "message": f"Ranked {len(services)} services by subtotal; focus top 5 for ownership reviews.",
            },
            "C": {"title": "Growth & anomalies", "message": growth_msg},
            "F": {
                "title": "Waste & opportunities",
                "message": f"{len(opportunities)} heuristic opportunities from MoM growth, new services, and savings pressure.",
            },
            "G": {"title": "Action queue", "message": action_msg},
            "J": {"title": "Alerts & messages", "message": alert_msg},
        },
        "pack": "v1-slim",
        "sections_included": ["A", "B", "C", "F", "G", "J"],
    }


def render_prom(
    services: list[ServiceRow],
    invoice_total: float,
    opportunities: list[dict],
    alerts: dict[str, int],
    messages: dict,
) -> str:
    lines: list[str] = [
        "# HELP finops_demo_info Synthetic FinOps demo metrics from billing CSV",
        "# TYPE finops_demo_info gauge",
        'finops_demo_info{pack="v1-slim",source="gcp-billing-services.sample.csv"} 1',
        "# HELP finops_gcp_cost_total_usd Invoice total USD",
        "# TYPE finops_gcp_cost_total_usd gauge",
        f"finops_gcp_cost_total_usd {invoice_total}",
        "# HELP finops_gcp_service_count Number of billed services",
        "# TYPE finops_gcp_service_count gauge",
        f"finops_gcp_service_count {len(services)}",
        "# HELP finops_gcp_cost_service_usd Cost by service USD",
        "# TYPE finops_gcp_cost_service_usd gauge",
    ]
    for svc in services:
        slug = _service_slug(svc.name)
        lines.append(
            f'finops_gcp_cost_service_usd{{service="{_prom_label(svc.name)}",service_id="{_prom_label(svc.service_id)}",slug="{slug}"}} {svc.subtotal}'
        )

    lines += [
        "# HELP finops_gcp_service_share_ratio Service share of invoice",
        "# TYPE finops_gcp_service_share_ratio gauge",
    ]
    for svc in services:
        share = (svc.subtotal / invoice_total) if invoice_total else 0.0
        lines.append(
            f'finops_gcp_service_share_ratio{{service="{_prom_label(svc.name)}"}} {share:.6f}'
        )

    lines += [
        "# HELP finops_gcp_service_mom_change_ratio MoM subtotal change ratio",
        "# TYPE finops_gcp_service_mom_change_ratio gauge",
        "# HELP finops_gcp_service_is_new Service first seen this period",
        "# TYPE finops_gcp_service_is_new gauge",
    ]
    for svc in services:
        if svc.mom_ratio is not None:
            lines.append(
                f'finops_gcp_service_mom_change_ratio{{service="{_prom_label(svc.name)}"}} {svc.mom_ratio:.6f}'
            )
        lines.append(
            f'finops_gcp_service_is_new{{service="{_prom_label(svc.name)}"}} {1 if svc.is_new else 0}'
        )

    lines += [
        "# HELP finops_gcp_recommendation_savings_usd Estimated monthly savings USD",
        "# TYPE finops_gcp_recommendation_savings_usd gauge",
        "# HELP finops_action_queue Priority score for action queue",
        "# TYPE finops_action_queue gauge",
    ]
    for opp in opportunities:
        svc = _prom_label(opp["service"])
        typ = _prom_label(opp["type"])
        owner = _prom_label(opp["owner"])
        lines.append(
            f'finops_gcp_recommendation_savings_usd{{service="{svc}",type="{typ}",owner="{owner}"}} {opp["est_monthly_savings_usd"]}'
        )
        lines.append(
            f'finops_action_queue{{service="{svc}",type="{typ}",owner="{owner}"}} {opp["priority_score"]}'
        )

    lines += [
        "# HELP finops_gcp_alert_flag Demo alert flags (1=active)",
        "# TYPE finops_gcp_alert_flag gauge",
    ]
    for name, value in alerts.items():
        lines.append(f'finops_gcp_alert_flag{{alert="{name}"}} {value}')

    # Message metrics for Grafana table panels (label carries text).
    lines += [
        "# HELP finops_demo_message Section narrative for dashboard text/table panels",
        "# TYPE finops_demo_message gauge",
    ]
    for section, payload in messages["sections"].items():
        text = _prom_label(payload["message"])
        lines.append(
            f'finops_demo_message{{section="{section}",title="{_prom_label(payload["title"])}",text="{text}"}} 1'
        )
    lines.append(
        f'finops_demo_message{{section="meta",title="Disclaimer",text="{_prom_label(messages["disclaimer"])}"}} 1'
    )

    opportunity_total = round(sum(o["est_monthly_savings_usd"] for o in opportunities), 2)
    lines += [
        "# HELP finops_opportunity_monthly_usd Addressable demo opportunity USD",
        "# TYPE finops_opportunity_monthly_usd gauge",
        f"finops_opportunity_monthly_usd {opportunity_total}",
    ]
    return "\n".join(lines) + "\n"


def build_site_snapshot(
    services: list[ServiceRow],
    invoice_total: float,
    opportunities: list[dict],
    alerts: dict[str, int],
    messages: dict,
) -> dict:
    """Structured payload for the GitHub Pages product showcase."""
    top = services[0] if services else None
    opportunity_total = round(sum(o["est_monthly_savings_usd"] for o in opportunities), 2)

    prior_total = 0.0
    comparable_current = 0.0
    top_services = []
    for svc in services:
        if svc.is_new or svc.mom_ratio is None:
            prior = 0.0 if svc.is_new else None
        elif svc.mom_ratio <= -0.999:
            prior = svc.subtotal
        else:
            prior = round(svc.subtotal / (1.0 + svc.mom_ratio), 2)
            prior_total += prior
            comparable_current += svc.subtotal

        share = (svc.subtotal / invoice_total) if invoice_total else 0.0
        if len(top_services) < 8:
            top_services.append(
                {
                    "name": svc.name,
                    "service_id": svc.service_id,
                    "subtotal_usd": svc.subtotal,
                    "prior_usd": prior,
                    "share": round(share, 4),
                    "mom_raw": svc.mom_raw,
                    "mom_ratio": svc.mom_ratio,
                    "is_new": svc.is_new,
                }
            )

    invoice_mom_ratio = None
    if prior_total > 0:
        invoice_mom_ratio = round((comparable_current - prior_total) / prior_total, 4)

    risers = sorted(
        [s for s in services if s.mom_ratio is not None],
        key=lambda s: s.mom_ratio or 0.0,
        reverse=True,
    )[:5]
    fallers = sorted(
        [s for s in services if s.mom_ratio is not None and s.mom_ratio < 0],
        key=lambda s: s.mom_ratio or 0.0,
    )[:5]

    def _trend_row(svc: ServiceRow) -> dict:
        prior = None
        if svc.is_new:
            prior = 0.0
        elif svc.mom_ratio is not None and svc.mom_ratio > -0.999:
            prior = round(svc.subtotal / (1.0 + svc.mom_ratio), 2)
        return {
            "name": svc.name,
            "service_id": svc.service_id,
            "subtotal_usd": svc.subtotal,
            "prior_usd": prior,
            "mom_raw": svc.mom_raw,
            "mom_ratio": svc.mom_ratio,
            "is_new": svc.is_new,
        }

    return {
        "product": "FinOps Dashboard",
        "cloud": "Google Cloud",
        "version": "v1",
        "pack": messages.get("pack", "v1-slim"),
        "period_label": messages["period_label"],
        "disclaimer": messages["disclaimer"],
        "invoice_total_usd": invoice_total,
        "prior_invoice_usd": round(prior_total, 2),
        "invoice_mom_ratio": invoice_mom_ratio,
        "service_count": len(services),
        "opportunity_total_usd": opportunity_total,
        "open_actions": len(opportunities),
        "new_service_count": sum(1 for s in services if s.is_new),
        "top_driver": {
            "name": top.name if top else None,
            "service_id": top.service_id if top else None,
            "subtotal_usd": top.subtotal if top else 0.0,
            "share": round((top.subtotal / invoice_total), 4) if top and invoice_total else 0.0,
        },
        "messages": messages["sections"],
        "top_services": top_services,
        "risers": [_trend_row(s) for s in risers],
        "fallers": [_trend_row(s) for s in fallers],
        "actions": opportunities,
        "alerts": alerts,
        "sections_included": messages.get("sections_included", []),
    }


def build_dashboard(messages: dict) -> dict:
    """Grafana dashboard for v1 slim sections A B C F G J."""
    ds = {"type": "prometheus", "uid": "prometheus-local"}

    def text_panel(panel_id: int, title: str, body: str, x: int, y: int, w: int = 24, h: int = 3) -> dict:
        return {
            "id": panel_id,
            "type": "text",
            "title": title,
            "gridPos": {"h": h, "w": w, "x": x, "y": y},
            "options": {
                "mode": "markdown",
                "content": body,
            },
        }

    a = messages["sections"]["A"]["message"]
    b = messages["sections"]["B"]["message"]
    c = messages["sections"]["C"]["message"]
    f = messages["sections"]["F"]["message"]
    g = messages["sections"]["G"]["message"]
    j = messages["sections"]["J"]["message"]
    disclaimer = messages["disclaimer"]
    period = messages["period_label"]

    panels: list[dict] = [
        text_panel(
            100,
            "FinOps v1 slim · demo pack",
            f"**{period}**  \n{disclaimer}  \n\nNarrative: **Spend → Drivers → Risks → Actions → Alerts**  \nSections: A · B · C · F · G · J *(D/E/H/I/K deferred to v1.1)*",
            0,
            0,
            24,
            3,
        ),
        # A
        text_panel(101, "A · Executive summary", a, 0, 3, 24, 2),
        {
            "id": 1,
            "type": "stat",
            "title": "Invoice total (USD)",
            "gridPos": {"h": 4, "w": 6, "x": 0, "y": 5},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": "finops_gcp_cost_total_usd"}],
            "fieldConfig": {"defaults": {"unit": "currencyUSD", "decimals": 2}},
        },
        {
            "id": 2,
            "type": "stat",
            "title": "Services billed",
            "gridPos": {"h": 4, "w": 6, "x": 6, "y": 5},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": "finops_gcp_service_count"}],
        },
        {
            "id": 3,
            "type": "stat",
            "title": "Addressable opportunity (USD)",
            "gridPos": {"h": 4, "w": 6, "x": 12, "y": 5},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": "finops_opportunity_monthly_usd"}],
            "fieldConfig": {"defaults": {"unit": "currencyUSD", "decimals": 2}},
        },
        {
            "id": 4,
            "type": "stat",
            "title": "Top service share",
            "gridPos": {"h": 4, "w": 6, "x": 18, "y": 5},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": "topk(1, finops_gcp_service_share_ratio)"}],
            "fieldConfig": {"defaults": {"unit": "percentunit", "decimals": 1}},
        },
        # B
        text_panel(102, "B · Spend by service", b, 0, 9, 24, 2),
        {
            "id": 5,
            "type": "bargauge",
            "title": "Cost by service (USD)",
            "gridPos": {"h": 10, "w": 14, "x": 0, "y": 11},
            "datasource": ds,
            "options": {"orientation": "horizontal", "displayMode": "gradient", "showUnfilled": True},
            "targets": [
                {
                    "refId": "A",
                    "expr": "topk(12, finops_gcp_cost_service_usd)",
                    "legendFormat": "{{service}}",
                }
            ],
            "fieldConfig": {"defaults": {"unit": "currencyUSD", "decimals": 2}},
        },
        {
            "id": 6,
            "type": "table",
            "title": "Service share of invoice",
            "gridPos": {"h": 10, "w": 10, "x": 14, "y": 11},
            "datasource": ds,
            "targets": [
                {
                    "refId": "A",
                    "expr": "finops_gcp_service_share_ratio",
                    "format": "table",
                    "instant": True,
                }
            ],
            "transformations": [
                {"id": "labelsToFields", "options": {}},
                {
                    "id": "organize",
                    "options": {
                        "excludeByName": {"Time": True, "__name__": True},
                        "renameByName": {"service": "Service", "Value": "Share"},
                    },
                },
            ],
            "fieldConfig": {
                "defaults": {},
                "overrides": [
                    {
                        "matcher": {"id": "byName", "options": "Share"},
                        "properties": [{"id": "unit", "value": "percentunit"}, {"id": "decimals", "value": 1}],
                    }
                ],
            },
        },
        # C
        text_panel(103, "C · Growth & anomalies", c, 0, 21, 24, 2),
        {
            "id": 7,
            "type": "bargauge",
            "title": "MoM change by service",
            "gridPos": {"h": 8, "w": 14, "x": 0, "y": 23},
            "datasource": ds,
            "options": {"orientation": "horizontal", "displayMode": "gradient"},
            "targets": [
                {
                    "refId": "A",
                    "expr": "finops_gcp_service_mom_change_ratio",
                    "legendFormat": "{{service}}",
                }
            ],
            "fieldConfig": {"defaults": {"unit": "percentunit", "decimals": 0}},
        },
        {
            "id": 8,
            "type": "table",
            "title": "New services this period",
            "gridPos": {"h": 8, "w": 10, "x": 14, "y": 23},
            "datasource": ds,
            "targets": [
                {
                    "refId": "A",
                    "expr": 'finops_gcp_service_is_new == 1',
                    "format": "table",
                    "instant": True,
                }
            ],
            "transformations": [
                {"id": "labelsToFields", "options": {}},
                {
                    "id": "organize",
                    "options": {
                        "excludeByName": {"Time": True, "__name__": True, "Value": True},
                        "renameByName": {"service": "Service"},
                    },
                },
            ],
        },
        # F
        text_panel(104, "F · Waste & opportunities (demo heuristics)", f, 0, 31, 24, 2),
        {
            "id": 9,
            "type": "bargauge",
            "title": "Estimated savings by opportunity",
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 33},
            "datasource": ds,
            "options": {"orientation": "horizontal", "displayMode": "gradient"},
            "targets": [
                {
                    "refId": "A",
                    "expr": "finops_gcp_recommendation_savings_usd",
                    "legendFormat": "{{type}} · {{service}}",
                }
            ],
            "fieldConfig": {"defaults": {"unit": "currencyUSD", "decimals": 2}},
        },
        {
            "id": 10,
            "type": "piechart",
            "title": "Opportunity mix by type",
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 33},
            "datasource": ds,
            "targets": [
                {
                    "refId": "A",
                    "expr": "sum by (type) (finops_gcp_recommendation_savings_usd)",
                    "legendFormat": "{{type}}",
                }
            ],
        },
        # G
        text_panel(105, "G · Action queue", g, 0, 41, 24, 2),
        {
            "id": 11,
            "type": "table",
            "title": "Prioritized actions",
            "gridPos": {"h": 9, "w": 24, "x": 0, "y": 43},
            "datasource": ds,
            "targets": [
                {
                    "refId": "A",
                    "expr": "finops_action_queue",
                    "format": "table",
                    "instant": True,
                },
                {
                    "refId": "B",
                    "expr": "finops_gcp_recommendation_savings_usd",
                    "format": "table",
                    "instant": True,
                },
            ],
            "transformations": [
                {"id": "labelsToFields", "options": {}},
                {
                    "id": "merge",
                    "options": {},
                },
                {
                    "id": "organize",
                    "options": {
                        "excludeByName": {"Time": True, "__name__": True},
                        "renameByName": {
                            "service": "Service",
                            "type": "Type",
                            "owner": "Owner",
                            "Value #A": "Priority score",
                            "Value #B": "Est. savings USD",
                        },
                    },
                },
                {
                    "id": "sortBy",
                    "options": {
                        "sort": [{"field": "Priority score", "desc": True}],
                    },
                },
            ],
        },
        # J
        text_panel(106, "J · Alerts & messages", j, 0, 52, 24, 2),
        {
            "id": 12,
            "type": "stat",
            "title": "Spend spike",
            "gridPos": {"h": 4, "w": 6, "x": 0, "y": 54},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": 'finops_gcp_alert_flag{alert="spend_spike"}'}],
            "fieldConfig": {
                "defaults": {
                    "mappings": [
                        {"type": "value", "options": {"0": {"text": "OK", "color": "green"}, "1": {"text": "ACTIVE", "color": "red"}}}
                    ],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [{"color": "green", "value": None}, {"color": "red", "value": 1}],
                    },
                }
            },
        },
        {
            "id": 13,
            "type": "stat",
            "title": "Service growth",
            "gridPos": {"h": 4, "w": 6, "x": 6, "y": 54},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": 'finops_gcp_alert_flag{alert="service_growth"}'}],
            "fieldConfig": {
                "defaults": {
                    "mappings": [
                        {"type": "value", "options": {"0": {"text": "OK", "color": "green"}, "1": {"text": "ACTIVE", "color": "orange"}}}
                    ]
                }
            },
        },
        {
            "id": 14,
            "type": "stat",
            "title": "Open actions",
            "gridPos": {"h": 4, "w": 6, "x": 12, "y": 54},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": 'finops_gcp_alert_flag{alert="open_actions"}'}],
            "fieldConfig": {
                "defaults": {
                    "mappings": [
                        {"type": "value", "options": {"0": {"text": "Clear", "color": "green"}, "1": {"text": "Queue", "color": "blue"}}}
                    ]
                }
            },
        },
        {
            "id": 15,
            "type": "stat",
            "title": "Label compliance drift",
            "gridPos": {"h": 4, "w": 6, "x": 18, "y": 54},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": 'finops_gcp_alert_flag{alert="label_compliance_drift"}'}],
            "fieldConfig": {
                "defaults": {
                    "mappings": [
                        {"type": "value", "options": {"0": {"text": "OK", "color": "green"}, "1": {"text": "DRIFT", "color": "red"}}}
                    ]
                }
            },
        },
    ]

    return {
        "id": None,
        "uid": "finops-local",
        "title": "FinOps v1 Slim (CSV demo)",
        "description": "Evidence layer for v1 — sections A B C F G J. v1.1 adds D E H I K. Pages is the product front door.",
        "tags": ["finops", "gcp", "v1-slim", "csv-demo"],
        "timezone": "browser",
        "schemaVersion": 39,
        "version": 3,
        "refresh": "30s",
        "editable": True,
        "panels": panels,
        "templating": {"list": []},
        "annotations": {"list": []},
        "time": {"from": "now-1h", "to": "now"},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("config/examples/gcp-billing-services.sample.csv"),
    )
    parser.add_argument(
        "--metrics-out",
        type=Path,
        default=Path("config/examples/finops-csv-metrics.prom"),
    )
    parser.add_argument(
        "--messages-out",
        type=Path,
        default=Path("config/examples/finops-csv-messages.json"),
    )
    parser.add_argument(
        "--dashboard-out",
        type=Path,
        default=Path("ops/grafana/dashboards/finops-local-validation.dashboard.json"),
    )
    parser.add_argument(
        "--site-snapshot-out",
        type=Path,
        default=Path("site/data/snapshot.json"),
    )
    parser.add_argument("--skip-dashboard", action="store_true")
    parser.add_argument("--skip-site-snapshot", action="store_true")
    args = parser.parse_args()

    services, invoice_total = load_services(args.csv)
    if not services:
        raise SystemExit(f"ERROR: no service rows parsed from {args.csv}")

    opportunities = build_opportunities(services, invoice_total)
    alerts = build_alerts(services, opportunities)
    messages = build_messages(services, invoice_total, opportunities, alerts)
    prom = render_prom(services, invoice_total, opportunities, alerts, messages)

    args.metrics_out.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_out.write_text(prom, encoding="utf-8")
    args.messages_out.write_text(json.dumps(messages, indent=2) + "\n", encoding="utf-8")

    if not args.skip_dashboard:
        dashboard = build_dashboard(messages)
        args.dashboard_out.parent.mkdir(parents=True, exist_ok=True)
        args.dashboard_out.write_text(json.dumps(dashboard, indent=2) + "\n", encoding="utf-8")

    if not args.skip_site_snapshot:
        snapshot = build_site_snapshot(services, invoice_total, opportunities, alerts, messages)
        args.site_snapshot_out.parent.mkdir(parents=True, exist_ok=True)
        args.site_snapshot_out.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")

    print(f"OK: wrote {args.metrics_out}")
    print(f"OK: wrote {args.messages_out}")
    if not args.skip_dashboard:
        print(f"OK: wrote {args.dashboard_out}")
    if not args.skip_site_snapshot:
        print(f"OK: wrote {args.site_snapshot_out}")
    print(f"services={len(services)} invoice_usd={invoice_total} opportunities={len(opportunities)}")


if __name__ == "__main__":
    main()
