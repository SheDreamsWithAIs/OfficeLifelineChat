# API Documentation

## Authentication
All API requests require authentication using an API key in the header:
```
Authorization: Bearer YOUR_API_KEY
```

## Rate Limits
- Basic Plan: 10 requests per second
- Professional Plan: 50 requests per second
- Enterprise Plan: 200 requests per second

## Endpoints

### GET /api/v1/users
Retrieve list of users.
- Response: JSON array of user objects
- Status Codes: 200 (success), 401 (unauthorized), 429 (rate limit exceeded)

### POST /api/v1/users
Create a new user.
- Request Body: JSON object with name, email, role
- Response: Created user object
- Status Codes: 201 (created), 400 (bad request), 401 (unauthorized)

### PUT /api/v1/users/{id}
Update user information.
- Request Body: JSON object with fields to update
- Response: Updated user object
- Status Codes: 200 (success), 404 (not found), 401 (unauthorized)

## Error Handling
All errors return JSON in the format:
```json
{
  "error": "Error code",
  "message": "Human-readable error message",
  "details": {}
}
```

## Webhooks
Configure webhooks in your dashboard to receive notifications for:
- User creation
- Plan changes
- Payment failures
- API limit warnings

