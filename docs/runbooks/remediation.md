# Runbook: Remediation

## Trigger

- Confirmed optimization opportunity, compliance breach, or anomaly triage outcome

## Steps

1. **Plan**  
   - Change type: rightsize, delete, reschedule, tag fix, reservation change.  
   - Blast radius: HA, backups, dependencies.

2. **Approve**  
   - Production change: use standard change approval for the platform.  
   - Destructive delete: require backup or snapshot confirmation where applicable.

3. **Execute**  
   - Apply change in maintenance window if needed.  
   - Link change ticket ID to FinOps finding.

4. **Verify**  
   - Resource state matches intent (inventory, utilization).  
   - Follow [Savings verification](savings-verification.md) for cost proof.

## Escalation

- Blocked dependency on another team → FinOps lead coordinates.  
- Policy exception needed → governance queue per `docs/tag-policy.md`.
