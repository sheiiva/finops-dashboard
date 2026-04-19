# Spend Forecasting Baseline

## Model

- **Method**: trailing `N`-month moving average (`N` default `3`).
- **Next period forecast**: mean of last `N` observed monthly totals (`amount_usd`).
- **Error metric**: **MAPE (%)** on walk-forward one-step predictions: for each month `t` from `N` onward, predict `t` using months `t-N..t-1`, compare to actual at `t`.

## Script

- `scripts/forecast_spend.py`
- Input: `config/examples/spend-history.sample.json`

## Run

```bash
python scripts/forecast_spend.py \
  --input config/examples/spend-history.sample.json \
  --output tmp/forecast-output.json
```

## Dashboard

- Grafana panel definitions: `dashboards/grafana/spend-forecast-baseline.dashboard.json`
- Typical queries (after exporting metrics to Prometheus):

  - Actual: `finops_monthly_spend_usd`
  - Forecast: `finops_monthly_spend_forecast_usd`

## Interpretation

- Lower MAPE = more stable spend; re-fit window when MAPE drifts above agreed threshold (e.g. 15%).
