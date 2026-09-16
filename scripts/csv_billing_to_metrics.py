#!/usr/bin/env python3
"""Convert anonymized billing CSV into Prometheus metrics + demo messages (v1.1)."""

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
    negotiated_savings: float
    savings_programs: float
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
                    negotiated_savings=_parse_money(raw.get("Negotiated savings (USD)") or "0"),
                    savings_programs=_parse_money(raw.get("Savings programs (USD)") or "0"),
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


def build_alerts(
    services: list[ServiceRow],
    opportunities: list[dict],
    allocation: dict | None = None,
) -> dict[str, int]:
    high_growth = any(s.mom_ratio is not None and s.mom_ratio >= 0.5 and s.subtotal >= 100 for s in services)
    label_drift = 0
    if allocation and allocation.get("compliance_ratio", 1.0) < 0.85:
        label_drift = 1
    return {
        "spend_spike": 1 if high_growth else 0,
        "service_growth": 1 if high_growth else 0,
        "open_actions": 1 if opportunities else 0,
        "label_compliance_drift": label_drift,
    }


def build_pareto(services: list[ServiceRow], invoice_total: float) -> dict:
    """D — concentration / Pareto from service subtotals."""
    cumulative = 0.0
    rows: list[dict] = []
    services_for_50 = None
    services_for_80 = None
    for idx, svc in enumerate(services, start=1):
        share = (svc.subtotal / invoice_total) if invoice_total else 0.0
        cumulative += share
        rows.append(
            {
                "rank": idx,
                "name": svc.name,
                "service_id": svc.service_id,
                "subtotal_usd": svc.subtotal,
                "share": round(share, 4),
                "cumulative_share": round(cumulative, 4),
            }
        )
        if services_for_50 is None and cumulative >= 0.5:
            services_for_50 = idx
        if services_for_80 is None and cumulative >= 0.8:
            services_for_80 = idx

    top5_share = round(sum(r["share"] for r in rows[:5]), 4)
    return {
        "top5_share": top5_share,
        "services_for_50_pct": services_for_50 or len(services),
        "services_for_80_pct": services_for_80 or len(services),
        "rows": rows[:10],
    }


def build_savings(services: list[ServiceRow]) -> dict:
    """E — discount / savings program lines from CSV columns."""
    negotiated = round(sum(s.negotiated_savings for s in services), 2)
    programs = round(sum(s.savings_programs for s in services), 2)
    other = round(sum(s.other_savings for s in services), 2)
    list_total = round(sum(s.list_cost for s in services), 2)
    realized = round(abs(negotiated) + abs(programs) + abs(other), 2)
    lines = []
    for svc in services:
        line_total = abs(svc.negotiated_savings) + abs(svc.savings_programs) + abs(svc.other_savings)
        if line_total < 1:
            continue
        lines.append(
            {
                "name": svc.name,
                "service_id": svc.service_id,
                "negotiated_usd": svc.negotiated_savings,
                "programs_usd": svc.savings_programs,
                "other_usd": svc.other_savings,
                "total_savings_usd": round(
                    svc.negotiated_savings + svc.savings_programs + svc.other_savings, 2
                ),
            }
        )
    lines.sort(key=lambda r: abs(r["total_savings_usd"]), reverse=True)
    coverage = round(realized / list_total, 4) if list_total else 0.0
    return {
        "list_cost_usd": list_total,
        "negotiated_usd": negotiated,
        "programs_usd": programs,
        "other_usd": other,
        "realized_savings_usd": round(negotiated + programs + other, 2),
        "coverage_ratio": coverage,
        "lines": lines[:6],
    }


def build_allocation(services: list[ServiceRow], invoice_total: float) -> dict:
    """H — demo allocation hygiene (CSV has no tags; heuristics stand in)."""
    # Demo ownership map: large spend → Platform/FinOps; new/long-tail → unowned.
    owned_rows: list[dict] = []
    unowned_rows: list[dict] = []
    for svc in services:
        if svc.is_new or svc.subtotal < 25:
            owner = None
            status = "unowned"
            unowned_rows.append(
                {
                    "name": svc.name,
                    "service_id": svc.service_id,
                    "subtotal_usd": svc.subtotal,
                    "status": status,
                    "owner_label": None,
                }
            )
        elif svc.subtotal >= 500:
            owner = "Platform"
            owned_rows.append(
                {
                    "name": svc.name,
                    "service_id": svc.service_id,
                    "subtotal_usd": svc.subtotal,
                    "status": "tagged",
                    "owner_label": owner,
                }
            )
        else:
            owner = "FinOps"
            owned_rows.append(
                {
                    "name": svc.name,
                    "service_id": svc.service_id,
                    "subtotal_usd": svc.subtotal,
                    "status": "tagged",
                    "owner_label": owner,
                }
            )

    unowned_spend = round(sum(r["subtotal_usd"] for r in unowned_rows), 2)
    owned_spend = round(invoice_total - unowned_spend, 2) if invoice_total else 0.0
    compliance = round(owned_spend / invoice_total, 4) if invoice_total else 1.0
    return {
        "compliance_ratio": compliance,
        "owned_spend_usd": owned_spend,
        "unowned_spend_usd": unowned_spend,
        "unowned_service_count": len(unowned_rows),
        "tagged_service_count": len(owned_rows),
        "gaps": sorted(unowned_rows, key=lambda r: r["subtotal_usd"], reverse=True)[:6],
    }


def build_forecast(
    invoice_total: float,
    invoice_mom_ratio: float | None,
    opportunity_total: float,
) -> dict:
    """I — simple runway / next-period projection from MoM."""
    mom = invoice_mom_ratio if invoice_mom_ratio is not None else 0.0
    # Dampen extreme MoM for a demo projection.
    dampened = max(-0.25, min(0.35, mom * 0.6))
    next_invoice = round(invoice_total * (1.0 + dampened), 2)
    delta = round(next_invoice - invoice_total, 2)
    # Months of growth offset if addressable savings are realized next period.
    if delta > 0 and opportunity_total > 0:
        runway_months = round(opportunity_total / delta, 1)
    elif opportunity_total > 0:
        runway_months = 12.0
    else:
        runway_months = 0.0
    recovered = round(max(0.0, next_invoice - opportunity_total), 2)
    return {
        "next_invoice_usd": next_invoice,
        "projected_delta_usd": delta,
        "assumption_mom_ratio": round(dampened, 4),
        "runway_months_if_recovered": min(runway_months, 24.0),
        "next_invoice_if_recovered_usd": recovered,
    }


def build_governance() -> dict:
    """K — engagement-kit cadence / RACI snippet."""
    return {
        "cadence": "Weekly 30-min FinOps triage · monthly exec spend review",
        "roles": [
            {"role": "FinOps", "owns": "Prioritize queue, validate savings estimates"},
            {"role": "Platform", "owns": "Remediate idle / new-service ownership"},
            {"role": "Cloud Economics", "owns": "Discount / CUD coverage reviews"},
            {"role": "Finance", "owns": "Invoice sign-off and forecast check"},
        ],
        "verify": "After each action: re-export CSV → regenerate snapshot → confirm MoM and opportunity delta.",
    }


def _invoice_mom(services: list[ServiceRow]) -> tuple[float, float, float | None]:
    prior_total = 0.0
    comparable_current = 0.0
    for svc in services:
        if svc.is_new or svc.mom_ratio is None or svc.mom_ratio <= -0.999:
            continue
        prior_total += svc.subtotal / (1.0 + svc.mom_ratio)
        comparable_current += svc.subtotal
    ratio = None
    if prior_total > 0:
        ratio = round((comparable_current - prior_total) / prior_total, 4)
    return prior_total, comparable_current, ratio


def build_messages(
    services: list[ServiceRow],
    invoice_total: float,
    opportunities: list[dict],
    alerts: dict[str, int],
    pareto: dict,
    savings: dict,
    allocation: dict,
    forecast: dict,
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
    prior_est, comparable, mom_invoice = _invoice_mom(services)
    if prior_est > 0 and mom_invoice is not None:
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
    pareto_msg = (
        f"Top 5 services are {pareto['top5_share']:.0%} of the invoice. "
        f"{pareto['services_for_80_pct']} services cover 80% of spend — "
        f"ownership reviews should start there."
    )
    realized = savings["realized_savings_usd"]
    savings_msg = (
        f"List cost ${savings['list_cost_usd']:,.0f} with "
        f"${abs(realized):,.0f} in recorded savings/discounts "
        f"({savings['coverage_ratio']:.1%} of list). "
        f"Largest lines shown below."
        if realized
        else f"List cost ${savings['list_cost_usd']:,.0f}; little discount coverage in this demo export."
    )
    alloc_msg = (
        f"{allocation['compliance_ratio']:.0%} of spend has a demo owner tag. "
        f"{allocation['unowned_service_count']} services "
        f"(${allocation['unowned_spend_usd']:,.0f}) still need allocation."
    )
    forecast_msg = (
        f"Next period projects ~${forecast['next_invoice_usd']:,.0f} "
        f"({forecast['projected_delta_usd']:+,.0f}) using a dampened MoM. "
        f"Recovering ${sum(o['est_monthly_savings_usd'] for o in opportunities):,.0f}/mo "
        f"addressable offsets ~{forecast['runway_months_if_recovered']:.1f} months of that growth."
    )
    gov_msg = (
        "Weekly triage with FinOps + Platform; monthly finance review. "
        "Each fix is verified by regenerating the snapshot from a fresh export."
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
            "D": {"title": "Concentration / Pareto", "message": pareto_msg},
            "E": {"title": "Savings & discounts", "message": savings_msg},
            "F": {
                "title": "Waste & opportunities",
                "message": (
                    f"{len(opportunities)} opportunities totaling "
                    f"${sum(o['est_monthly_savings_usd'] for o in opportunities):,.0f}/mo addressable — "
                    f"ranked below by estimated recovery, then owned in the action queue."
                ),
            },
            "G": {"title": "Action queue", "message": action_msg},
            "H": {"title": "Allocation hygiene", "message": alloc_msg},
            "I": {"title": "Forecast & runway", "message": forecast_msg},
            "J": {"title": "Alerts & messages", "message": alert_msg},
            "K": {"title": "Governance", "message": gov_msg},
        },
        "pack": "v1.1",
        "sections_included": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"],
    }


def render_prom(
    services: list[ServiceRow],
    invoice_total: float,
    opportunities: list[dict],
    alerts: dict[str, int],
    messages: dict,
    pareto: dict,
    savings: dict,
    allocation: dict,
    forecast: dict,
) -> str:
    lines: list[str] = [
        "# HELP finops_demo_info Synthetic FinOps demo metrics from billing CSV",
        "# TYPE finops_demo_info gauge",
        'finops_demo_info{pack="v1.1",source="gcp-billing-services.sample.csv"} 1',
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

    lines += [
        "# HELP finops_pareto_top5_share_ratio Top 5 services share of invoice",
        "# TYPE finops_pareto_top5_share_ratio gauge",
        f"finops_pareto_top5_share_ratio {pareto['top5_share']}",
        "# HELP finops_pareto_services_for_80 Count of services covering 80% spend",
        "# TYPE finops_pareto_services_for_80 gauge",
        f"finops_pareto_services_for_80 {pareto['services_for_80_pct']}",
        "# HELP finops_savings_realized_usd Recorded discounts/savings USD (negative = credit)",
        "# TYPE finops_savings_realized_usd gauge",
        f"finops_savings_realized_usd {savings['realized_savings_usd']}",
        "# HELP finops_allocation_compliance_ratio Demo tagged spend ratio",
        "# TYPE finops_allocation_compliance_ratio gauge",
        f"finops_allocation_compliance_ratio {allocation['compliance_ratio']}",
        "# HELP finops_forecast_next_invoice_usd Projected next invoice USD",
        "# TYPE finops_forecast_next_invoice_usd gauge",
        f"finops_forecast_next_invoice_usd {forecast['next_invoice_usd']}",
    ]

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
    pareto: dict,
    savings: dict,
    allocation: dict,
    forecast: dict,
    governance: dict,
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
        "version": "v1.1",
        "pack": messages.get("pack", "v1.1"),
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
        "pareto": pareto,
        "savings": savings,
        "allocation": allocation,
        "forecast": forecast,
        "governance": governance,
        "actions": opportunities,
        "alerts": alerts,
        "sections_included": messages.get("sections_included", []),
    }


def build_dashboard(messages: dict) -> dict:
    """Grafana dashboard for v1.1 sections A–K."""
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
    d = messages["sections"]["D"]["message"]
    e = messages["sections"]["E"]["message"]
    f = messages["sections"]["F"]["message"]
    g = messages["sections"]["G"]["message"]
    h = messages["sections"]["H"]["message"]
    i = messages["sections"]["I"]["message"]
    j = messages["sections"]["J"]["message"]
    k = messages["sections"]["K"]["message"]
    disclaimer = messages["disclaimer"]
    period = messages["period_label"]

    panels: list[dict] = [
        text_panel(
            100,
            "FinOps v1.1 · demo pack",
            f"**{period}**  \n{disclaimer}  \n\nNarrative: **Spend → Drivers → Trend → Concentration → Savings → Opportunities → Actions → Allocation → Forecast → Alerts → Governance**  \nSections: A · B · C · D · E · F · G · H · I · J · K",
            0,
            0,
            24,
            3,
        ),
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
                    "expr": "finops_gcp_service_is_new == 1",
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
        text_panel(110, "D · Concentration / Pareto", d, 0, 31, 24, 2),
        {
            "id": 20,
            "type": "stat",
            "title": "Top 5 share",
            "gridPos": {"h": 4, "w": 12, "x": 0, "y": 33},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": "finops_pareto_top5_share_ratio"}],
            "fieldConfig": {"defaults": {"unit": "percentunit", "decimals": 0}},
        },
        {
            "id": 21,
            "type": "stat",
            "title": "Services for 80% spend",
            "gridPos": {"h": 4, "w": 12, "x": 12, "y": 33},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": "finops_pareto_services_for_80"}],
        },
        text_panel(111, "E · Savings & discounts", e, 0, 37, 24, 2),
        {
            "id": 22,
            "type": "stat",
            "title": "Recorded savings (USD)",
            "gridPos": {"h": 4, "w": 24, "x": 0, "y": 39},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": "finops_savings_realized_usd"}],
            "fieldConfig": {"defaults": {"unit": "currencyUSD", "decimals": 2}},
        },
        text_panel(104, "F · Waste & opportunities (demo heuristics)", f, 0, 43, 24, 2),
        {
            "id": 9,
            "type": "bargauge",
            "title": "Estimated savings by opportunity",
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 45},
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
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 45},
            "datasource": ds,
            "targets": [
                {
                    "refId": "A",
                    "expr": "sum by (type) (finops_gcp_recommendation_savings_usd)",
                    "legendFormat": "{{type}}",
                }
            ],
        },
        text_panel(105, "G · Action queue", g, 0, 53, 24, 2),
        {
            "id": 11,
            "type": "table",
            "title": "Prioritized actions",
            "gridPos": {"h": 9, "w": 24, "x": 0, "y": 55},
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
                {"id": "merge", "options": {}},
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
                    "options": {"sort": [{"field": "Priority score", "desc": True}]},
                },
            ],
        },
        text_panel(112, "H · Allocation hygiene", h, 0, 64, 24, 2),
        {
            "id": 23,
            "type": "stat",
            "title": "Tagged spend ratio",
            "gridPos": {"h": 4, "w": 24, "x": 0, "y": 66},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": "finops_allocation_compliance_ratio"}],
            "fieldConfig": {"defaults": {"unit": "percentunit", "decimals": 0}},
        },
        text_panel(113, "I · Forecast & runway", i, 0, 70, 24, 2),
        {
            "id": 24,
            "type": "stat",
            "title": "Projected next invoice",
            "gridPos": {"h": 4, "w": 24, "x": 0, "y": 72},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": "finops_forecast_next_invoice_usd"}],
            "fieldConfig": {"defaults": {"unit": "currencyUSD", "decimals": 0}},
        },
        text_panel(106, "J · Alerts & messages", j, 0, 76, 24, 2),
        {
            "id": 12,
            "type": "stat",
            "title": "Spend spike",
            "gridPos": {"h": 4, "w": 6, "x": 0, "y": 78},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": 'finops_gcp_alert_flag{alert="spend_spike"}'}],
            "fieldConfig": {
                "defaults": {
                    "mappings": [
                        {
                            "type": "value",
                            "options": {
                                "0": {"text": "OK", "color": "green"},
                                "1": {"text": "ACTIVE", "color": "red"},
                            },
                        }
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
            "gridPos": {"h": 4, "w": 6, "x": 6, "y": 78},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": 'finops_gcp_alert_flag{alert="service_growth"}'}],
            "fieldConfig": {
                "defaults": {
                    "mappings": [
                        {
                            "type": "value",
                            "options": {
                                "0": {"text": "OK", "color": "green"},
                                "1": {"text": "ACTIVE", "color": "orange"},
                            },
                        }
                    ]
                }
            },
        },
        {
            "id": 14,
            "type": "stat",
            "title": "Open actions",
            "gridPos": {"h": 4, "w": 6, "x": 12, "y": 78},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": 'finops_gcp_alert_flag{alert="open_actions"}'}],
            "fieldConfig": {
                "defaults": {
                    "mappings": [
                        {
                            "type": "value",
                            "options": {
                                "0": {"text": "Clear", "color": "green"},
                                "1": {"text": "Queue", "color": "blue"},
                            },
                        }
                    ]
                }
            },
        },
        {
            "id": 15,
            "type": "stat",
            "title": "Label compliance drift",
            "gridPos": {"h": 4, "w": 6, "x": 18, "y": 78},
            "datasource": ds,
            "targets": [{"refId": "A", "expr": 'finops_gcp_alert_flag{alert="label_compliance_drift"}'}],
            "fieldConfig": {
                "defaults": {
                    "mappings": [
                        {
                            "type": "value",
                            "options": {
                                "0": {"text": "OK", "color": "green"},
                                "1": {"text": "DRIFT", "color": "red"},
                            },
                        }
                    ]
                }
            },
        },
        text_panel(114, "K · Governance", k, 0, 82, 24, 3),
    ]

    return {
        "id": None,
        "uid": "finops-local",
        "title": "FinOps v1.1 (CSV demo)",
        "description": "Evidence layer for v1.1 — sections A–K. Pages is the product front door.",
        "tags": ["finops", "gcp", "v1.1", "csv-demo"],
        "timezone": "browser",
        "schemaVersion": 39,
        "version": 4,
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
    pareto = build_pareto(services, invoice_total)
    savings = build_savings(services)
    allocation = build_allocation(services, invoice_total)
    _, _, invoice_mom = _invoice_mom(services)
    opportunity_total = round(sum(o["est_monthly_savings_usd"] for o in opportunities), 2)
    forecast = build_forecast(invoice_total, invoice_mom, opportunity_total)
    governance = build_governance()
    alerts = build_alerts(services, opportunities, allocation)
    messages = build_messages(
        services,
        invoice_total,
        opportunities,
        alerts,
        pareto,
        savings,
        allocation,
        forecast,
    )
    prom = render_prom(
        services,
        invoice_total,
        opportunities,
        alerts,
        messages,
        pareto,
        savings,
        allocation,
        forecast,
    )

    args.metrics_out.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_out.write_text(prom, encoding="utf-8")
    args.messages_out.write_text(json.dumps(messages, indent=2) + "\n", encoding="utf-8")

    if not args.skip_dashboard:
        dashboard = build_dashboard(messages)
        args.dashboard_out.parent.mkdir(parents=True, exist_ok=True)
        args.dashboard_out.write_text(json.dumps(dashboard, indent=2) + "\n", encoding="utf-8")

    if not args.skip_site_snapshot:
        snapshot = build_site_snapshot(
            services,
            invoice_total,
            opportunities,
            alerts,
            messages,
            pareto,
            savings,
            allocation,
            forecast,
            governance,
        )
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
