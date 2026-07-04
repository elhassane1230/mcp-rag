# Incident response runbook

## Severity levels
- SEV1: full outage or data loss. Page the on-call engineer immediately.
- SEV2: major feature degraded for many customers.
- SEV3: minor or cosmetic issue affecting few users.

## On-call and escalation
The on-call engineer acknowledges a page within 5 minutes. If unacknowledged after
10 minutes, the alert escalates to the secondary on-call, then to the engineering
manager. For SEV1 incidents, open a war room and post updates to the status page
every 30 minutes.

## Recovery steps
1. Acknowledge and declare severity.
2. Mitigate first (roll back the last deploy, or fail over to the standby region).
3. Identify root cause only after the bleeding stops.
4. Write a blameless post-mortem within 48 hours.

## Failover
Nimbus runs active-passive across two regions. Failover to the standby region is
triggered with `nimbus ops failover --region standby` and takes about 3 minutes,
during which writes are queued and replayed.
