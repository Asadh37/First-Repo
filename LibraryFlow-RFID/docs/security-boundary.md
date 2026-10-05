# Prototype security boundary

This module deliberately provides a small, explicit demo-only authentication boundary. It is **not** a replacement for institutional SSO, MFA, secure deployment, or a security review.

- Authentication is disabled by default. Set `LIBRARYFLOW_DEMO_AUTH=1` to enable it for a local demonstration.
- Demo users and passwords are configured through environment variables; do not put credentials in source control.
- Sessions are signed with `SESSION_SECRET`; set a long random secret outside source control.
- Every write route and sensitive report requires an authenticated session and the `librarian` or `admin` role. The administration role is required for the admin-only demo endpoint.
- When demo authentication is disabled, the application emits a visible prototype warning and must be bound to localhost only.
- This implementation uses a same-origin session cookie and CSRF token for browser form/API writes. Do not expose it to a network or use real patron data.

The demo credentials are intentionally not shipped. Configure `LIBRARYFLOW_DEMO_USERS` as a JSON object mapping usernames to objects with `password` and `role`, for example:

```json
{"demo-admin":{"password":"set-a-long-demo-password","role":"admin"},"demo-librarian":{"password":"set-another-password","role":"librarian"}}
```

Use a different secret and passwords on your machine. This demo auth should be replaced with approved institutional identity management before any real deployment.
