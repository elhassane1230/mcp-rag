# Data retention and deletion

## Retention windows
By default, Nimbus retains event data for 90 days on the Team plan and 30 days on
the Free plan. Enterprise customers can configure retention from 7 days to 7 years.
Aggregated metrics are retained for 13 months regardless of plan.

## Deleting data
You can delete a single record via the API, or request bulk deletion of a project's
data from Settings → Data. Deletion is irreversible. When you delete data, it is
removed from primary storage immediately and purged from encrypted backups within 35
days.

## GDPR and data subject requests
Nimbus is GDPR compliant. To satisfy a data-subject erasure request ("right to be
forgotten"), use the `/v1/gdpr/erase` endpoint with the subject identifier; Nimbus
removes all personal data associated with that subject and returns a signed
certificate of deletion. Data residency can be pinned to the EU or US region at
project creation.
