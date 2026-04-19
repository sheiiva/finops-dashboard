#!/usr/bin/env python3
"""Baseline spend forecast from monthly series (moving average + walk-forward MAPE)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _mape(actual: list[float], predicted: list[float]) -> float:
    errs = []
    for a, p in zip(actual, predicted, strict=True):
        if a == 0:
            continue
        errs.append(abs(a - p) / a)
    return sum(errs) / len(errs) if errs else 0.0


def forecast_series(rows: list[dict], window: int = 3) -> dict:
    """Rows: {\"period\": str, \"amount_usd\": number}, sorted ascending by period."""
    amounts = [float(r["amount_usd"]) for r in rows]
    if len(amounts) < window + 1:
        raise ValueError("need at least window+1 points for walk-forward MAPE")

    preds: list[float] = []
    acts: list[float] = []
    for t in range(window, len(amounts)):
        pred = sum(amounts[t - window : t]) / window
        preds.append(pred)
        acts.append(amounts[t])

    mape = round(_mape(acts, preds) * 100, 2)
    next_forecast = round(sum(amounts[-window:]) / window, 2)
    return {
        "forecast_next_period_usd": next_forecast,
        "mape_percent_walk_forward": mape,
        "window": window,
        "points_used": len(amounts),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Baseline spend forecast")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--window", type=int, default=3)
    args = parser.parse_args()

    rows = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise SystemExit("ERROR: input must be JSON array")
    rows = sorted(rows, key=lambda r: r["period"])
    out = forecast_series(rows, window=args.window)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
