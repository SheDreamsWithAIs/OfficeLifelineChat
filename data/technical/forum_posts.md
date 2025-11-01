# Technical Forum Posts

## Q: How do I handle pagination in API responses?
**Answer**: Use the `page` and `per_page` query parameters. Default is 20 items per page, maximum is 100. Response includes `total`, `page`, `per_page`, and `total_pages` metadata.

**Example**:
```
GET /api/v1/users?page=2&per_page=50
```

## Q: Why am I getting 429 errors?
**Answer**: You're exceeding your rate limit. Check your plan limits and implement exponential backoff. Consider upgrading if consistently hitting limits. Use the `X-RateLimit-Remaining` header to track remaining requests.

## Q: Can I filter API responses?
**Answer**: Yes, most endpoints support filtering with query parameters. For example:
```
GET /api/v1/users?role=admin&status=active
```

Check individual endpoint documentation for available filters.

## Q: How do I test webhooks locally?
**Answer**: Use a service like ngrok to expose your local server. Then configure the webhook URL in your dashboard. Alternatively, use the webhook testing tool in the developer dashboard.

## Q: What's the best way to handle errors in my integration?
**Answer**: Always check HTTP status codes. Implement retry logic with exponential backoff for 5xx errors and 429 rate limit errors. Log error responses for debugging. Never retry on 4xx client errors except 429.

