# Billing and quotas

Nimbus bills monthly based on your plan tier plus metered usage.

## Plans
- Free: 1 project, 10k API calls/month, 1 GB storage.
- Team: 10 projects, 1M API calls/month, 100 GB storage, email support.
- Enterprise: unlimited projects, custom quotas, SSO, and a dedicated success manager.

## Quotas and overages
Each plan includes a monthly quota of API calls and storage. When you exceed your
included quota, Nimbus does not cut off your service; instead, additional usage is
billed as overage at the metered rate ($0.50 per extra 10k calls, $0.10 per extra
GB). You can set a hard spending cap in Settings → Billing to have requests rejected
with HTTP 402 once the cap is reached, instead of accruing overage charges.

## Invoices and payment
Invoices are issued on the first of each month and charged to your card on file.
Enterprise customers can pay by invoice with net-30 terms.
