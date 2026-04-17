# Team Action Queue and Ownership Views

## Artifacts

- Dashboard JSON: `dashboards/grafana/team-action-queue.dashboard.json`
- Queue builder script: `scripts/build_action_queue.py`
- Sample queue input: `config/examples/action-queue.sample.json`

## Team-Level Views

- Table view: actionable findings with owner and priority score.
- Aggregate view: open action count per owner.
- Hygiene view: unassigned action count.

## Owner Field Policy

- Each action requires an `owner` value.
- Missing owner values are normalized to `unassigned`.
- `unassigned` items are tracked as operational debt.

## Priority Sorting

Queue items are sorted descending on `priority_score` to ensure teams execute highest-value actions first.

## Run

```bash
python scripts/build_action_queue.py \
  --input config/examples/action-queue.sample.json \
  --output tmp/dashboard/action-queue.json
```
