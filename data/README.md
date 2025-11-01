# Data Directory Structure

This directory contains mock documents organized by domain for the specialized AI agents.

## Structure

### `/billing`
Documents related to billing, pricing, and invoices:
- `pricing_tiers.md` - Plan pricing and features
- `invoice_policy.md` - Invoice generation and payment policies
- `billing_faq.md` - Frequently asked billing questions

### `/technical`
Documents for technical support and troubleshooting:
- `api_documentation.md` - API endpoints and usage
- `bug_reports.md` - Known issues and bug tracking
- `forum_posts.md` - Common technical questions and answers
- `troubleshooting_guides.md` - Step-by-step troubleshooting instructions

### `/policy`
Static policy documents:
- `terms_of_service.md` - Terms and conditions
- `privacy_policy.md` - Privacy and data handling policies
- `compliance_guidelines.md` - GDPR, SOC 2, and compliance information

## Usage

These documents will be:
1. Ingested into ChromaDB for RAG retrieval (technical and billing documents)
2. Loaded into memory for CAG retrieval (policy documents)
3. Used with Hybrid RAG/CAG strategy (billing documents - initial RAG, then cached)

## Document Format

All documents are in Markdown format for easy processing and readability. Documents should be:
- Well-structured with clear headings
- Concise but comprehensive
- Factual and accurate
- Properly formatted for markdown parsing

