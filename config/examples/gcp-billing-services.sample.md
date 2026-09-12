# Sample: Google Cloud billing services rollup

Synthetic **USD** fixture with **real Google Cloud service names and public service IDs**.
Monetary amounts are transformed for privacy; product names/IDs are public catalog values.

## File

- `gcp-billing-services.sample.csv`

## Privacy

- Costs / savings / MoM values are synthetic (scaled from a private export).
- Service description + Service ID match Google Cloud billing catalog labels.
- Safe to commit for demos and portfolio screenshots.

## Intended use

- Seed the v1 Pages showcase and Grafana evidence pack.
- Google-first only (AWS/Azure → v3).
- No region/project line items in this rollup (deferred until richer export / v1.1+).

```bash
./scripts/local_dashboard_stack.sh inject-csv
```
