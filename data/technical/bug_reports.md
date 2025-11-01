# Known Issues and Bug Reports

## High Priority Issues

### Issue #1234: API Rate Limiting Not Enforcing
**Status**: Fixed in v2.3.1
**Description**: Rate limits were not being properly enforced for some enterprise accounts.
**Workaround**: Contact support to manually set rate limits until patch deployed.

### Issue #1156: Webhook Delivery Failures
**Status**: Investigating
**Description**: Some webhook deliveries failing for customers using Cloudflare.
**Affected**: ~5% of webhook deliveries
**Workaround**: Retry mechanism added, manual webhook resend available in dashboard.

## Medium Priority Issues

### Issue #1123: Dashboard Loading Slowly
**Status**: Fixed in v2.3.0
**Description**: Dashboard page load times exceeded 5 seconds for accounts with >1000 users.
**Fix**: Optimized database queries and added caching layer.

### Issue #1089: Invoice PDF Generation Errors
**Status**: Fixed
**Description**: PDF generation failing for invoices with special characters in company names.
**Fix**: Updated PDF library to handle UTF-8 encoding properly.

## Feature Requests

### Feature Request #987: Bulk User Import
**Status**: In Development
**Expected Release**: Q2 2025
**Description**: Ability to import users from CSV file.

### Feature Request #865: Custom Webhook Retry Logic
**Status**: Planned
**Description**: Allow customers to configure webhook retry attempts and intervals.

