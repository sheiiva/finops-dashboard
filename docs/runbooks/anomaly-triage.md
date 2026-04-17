# Runbook: Anomaly Triage

## Trigger

- `FinOpsSpendAnomalyHigh` or manual review of spend dashboard

## Steps

1. **Confirm signal**  
   - Compare current window to baseline in Prometheus / billing export.  
   - Rule out ingestion delay, duplicate charge, or FX noise.

2. **Classify**  
   - **Expected**: new workload, seasonality, marketing campaign → document in week notes.  
   - **Investigate**: unknown spike → open task with owner from resource tags.

3. **Scope**  
   - Provider, account/subscription, region, service, resource IDs where available.

4. **Escalate**  
   - No owner tag or no response in **2 business days** → FinOps lead assigns owner.  
   - Suspected security or data exfil pattern → Security / Gov per RACI.

5. **Close loop**  
   - Record outcome: false positive, expected, or remediation ticket opened.

## Evidence to attach

- Query screenshot or exported metrics range  
- Billing line item or cost table reference if available  
