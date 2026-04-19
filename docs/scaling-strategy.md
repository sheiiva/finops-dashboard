# Scaling Strategy: Data Ingestion and Dashboards

## Capacity assumptions

| Dimension | Baseline | Growth trigger |
|-----------|----------|----------------|
| Monthly billing rows ingested | ≤ 5M | Partition by month + provider |
| Collector runtime per scope | &lt; 15 min | Split scope, parallel workers |
| Prometheus series for FinOps KPIs | ≤ 50k active | Recording rules, label cardinality caps |
| Grafana dashboard refresh | 30s–5m | Raise interval before adding panels |

## Ingestion bottlenecks

- **API rate limits** (cloud billing, resource manager): backoff, quota request, regional fan-out.
- **Large JSON exports**: stream parse; avoid loading full month in memory.
- **Normalization CPU**: batch `normalize()`; profile hot paths.

## Query and dashboard bottlenecks

- **High-cardinality labels** on `resource_id`: aggregate by service/team before UI; keep drill-down on-demand.
- **Slow PromQL**: precompute weekly rollups into recording rules or metric export job.

## Mitigations

| Risk | Mitigation |
|------|------------|
| Ingestion backlog | Queue + DLQ; alert on lag &gt; SLA |
| Dashboard timeout | Grafana query timeout, summarized tables |
| State file growth | Remote state + workspace split for Terraform |
| Multi-region duplication | Single writer region for normalized store; read replicas later |

## Evolution path

1. Single-process collectors + file artifacts.  
2. Scheduled workers per provider scope.  
3. Optional message bus between raw landing and normalize (only if backlog sustained).
