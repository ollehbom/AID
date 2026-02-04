# Technical Specification: Foundational UI (gh-vs-7)

## Architecture Overview
The foundational UI will be a single-page application (SPA) built with React, leveraging `shadcn/ui` and TailwindCSS for a modern and consistent design system. User authentication will be handled via Google OAuth 2.0 (Authorization Code Flow with PKCE), orchestrated between the client-side application and a dedicated backend authentication service. The frontend will be deployed as a static site, served globally via a Content Delivery Network (CDN).

```mermaid
graph TD
    A[User Browser] -->|1. Request app.yourdomain.com| B(CDN/Static Host)
    B -->|2. Serve index.html + JS/CSS| A
    A -->|3. Init Google Login| C{Google OAuth Server}
    C -->|4. Auth Code (PKCE)| A
    A -->|5. Send Auth Code to Backend| D(Backend Auth Service)
    D -->|6. Verify Code, Get Tokens| C
    C -->|7. Return ID/Access Tokens| D
    D -->|8. Validate ID Token, Create/Retrieve User, Issue Session Cookie| A
    A -->|9. Redirect to /dashboard| A
    A -->|10. Request Dashboard Data (with session cookie)| D
    D -->|11. Return User Data| A
    A -->|12. Render Dashboard| A
```

## Components

-   **`App`**: The root React component, responsible for routing, global state management (e.g., authentication status), and layout. Uses `react-router-dom` for client-side routing.
-   **`LoadingSpinner`**: A full-screen or contextual spinner component (from `shadcn/ui`) to indicate data loading or processing states.
-   **`LoginPage`**: Displays the product branding and a prominent "Sign in with Google" button. Handles initiating the Google OAuth flow.
-   **`AuthCallbackHandler`**: A dedicated route/component that receives the redirect from Google OAuth, processes the authorization code, and communicates with the backend authentication service.
-   **`DashboardPage`**: The primary authenticated view, displaying a welcome message, user-specific information (e.g., name), and placeholder content for future features.
-   **`TopNavigationBar`**: Contains product logo/name, and a user avatar with a dropdown menu including a "Logout" option.
-   **`ErrorAlert` / `Toast`**: `shadcn/ui` components for displaying ephemeral or persistent error and success messages to the user.

## Data Models

### Client-side User Session (Example)
```json
{
  "isAuthenticated": true,
  "userId": "usr_abc123",
  "userName": "John Doe",
  "userEmail": "john.doe@example.com",
  "userAvatarUrl": "https://lh3.googleusercontent.com/a/...
}
```
*Note: The actual session token (e.g., JWT) will be stored securely in an `HttpOnly` cookie or similar mechanism, not directly in client-side JavaScript state.*

### Backend User Profile (Example)
```json
{
  "id": "usr_abc123",
  "googleId": "google_id_12345",
  "email": "john.doe@example.com",
  "name": "John Doe",
  "avatarUrl": "https://lh3.googleusercontent.com/a/...
  "createdAt": "2023-01-01T12:00:00Z",
  "updatedAt": "2023-01-01T12:00:00Z"
}
```

## APIs

### Authentication Service Endpoints
-   **`POST /api/auth/google/login`**
    -   **Description**: Initiates the Google OAuth 2.0 Authorization Code Flow. The client sends a request, and the backend generates a `state` and `code_verifier` (for PKCE), then redirects the user's browser to Google's consent screen.
    -   **Request**: `GET /api/auth/google/login` (or `POST` to initiate redirect)
    -   **Response**: HTTP 302 Redirect to `accounts.google.com/o/oauth2/v2/auth`.

-   **`GET /api/auth/google/callback`**
    -   **Description**: Handles the callback from Google after user consent. The client-side application receives the `code` and `state` parameters from Google's redirect URL and forwards them to this backend endpoint.
    -   **Request**: `GET /api/auth/google/callback?code=...&state=...&code_verifier=...`
    -   **Response (Success)**: HTTP 200 OK. Sets an `HttpOnly` session cookie (e.g., containing a JWT) and redirects the client to `/dashboard`.
        ```json
        // (On successful authentication, typically redirects client or sets cookies)
        // Example: { "message": "Authentication successful", "redirect": "/dashboard" }
        ```
    -   **Response (Failure)**: HTTP 400 Bad Request / 401 Unauthorized. Returns an error message and redirects the client to `/login` with an error parameter.
        ```json
        { "error": "Authentication failed", "details": "Invalid code or state" }
        ```

-   **`GET /api/auth/user`**
    -   **Description**: Retrieves the profile of the currently authenticated user.
    -   **Authentication**: Requires a valid session cookie.
    -   **Request**: `GET /api/auth/user`
    -   **Response (Success)**:
        ```json
        {
          "userId": "usr_abc123",
          "userName": "John Doe",
          "userEmail": "john.doe@example.com",
          "userAvatarUrl": "https://lh3.googleusercontent.com/a/...
        }
        ```
    -   **Response (Failure)**: HTTP 401 Unauthorized if no valid session.

-   **`POST /api/auth/logout`**
    -   **Description**: Invalidates the current user session.
    -   **Authentication**: Requires a valid session cookie.
    -   **Request**: `POST /api/auth/logout`
    -   **Response (Success)**: HTTP 204 No Content. Clears the session cookie and redirects the client to `/login`.

## Infrastructure

-   **Frontend Hosting**: 
    -   **Service**: Managed static site hosting platform (e.g., Vercel, Netlify, AWS S3 + CloudFront).
    -   **Configuration**: Global CDN, automatic HTTPS, custom domain mapping.
-   **Backend Authentication Service**: 
    -   **Service**: Cloud-agnostic (e.g., Node.js/Express, Python/FastAPI) deployed to a scalable environment (e.g., AWS Lambda/API Gateway, Google Cloud Run, Kubernetes/ECS).
    -   **Configuration**: Secure environment variables for Google OAuth client ID/secret, database credentials. Rate limiting for API endpoints.
-   **Database**: 
    -   **Service**: Managed relational database (e.g., AWS RDS PostgreSQL, Google Cloud SQL) or NoSQL database (e.g., DynamoDB, MongoDB Atlas) for storing user profiles linked to Google IDs.
    -   **Configuration**: Secure network access (VPC, private endpoints), regular backups, encryption at rest.

## Testing Strategy

-   **Unit Tests**: 
    -   **Scope**: Individual React components (e.g., `LoginPage`, `TopNavigationBar`), utility functions (e.g., for OAuth state management, token decoding). 
    -   **Tools**: Jest, React Testing Library.
-   **Integration Tests**: 
    -   **Scope**: Interaction between React components and local state/props. Frontend-to-backend authentication flow (mocking Google OAuth). 
    -   **Tools**: Jest, Supertest (for backend API). 
-   **End-to-End (E2E) Tests**: 
    -   **Scope**: Full user journey from application load, Google login, dashboard access, and logout.
    -   **Tools**: Cypress or Playwright.
-   **Security Testing**: 
    -   **Scope**: Verification of OAuth flow implementation against common vulnerabilities (CSRF, XSS, redirect manipulation). Input validation on all forms. 
    -   **Tools**: OWASP ZAP, manual penetration testing.

## Deployment

-   **CI/CD Pipeline**: Automated build, test, and deployment on every push to the `main` branch (or via pull request merges).
-   **Frontend Deployment**: 
    -   **Strategy**: Atomic deployments to static site host. New versions are deployed to a new directory/hash, and the CDN pointer is updated. Rollback capabilities.
    -   **Feature Flags**: Not strictly required for this foundational MVP, but will be integrated for future feature rollouts to enable controlled releases.
-   **Backend Deployment**: 
    -   **Strategy**: Containerized deployment (e.g., Docker) to a managed service with blue/green or rolling updates for zero-downtime deployments.
    -   **Rollback**: Automated rollback to previous stable versions upon failure detection.
-   **Monitoring and Alerts**: 
    -   **Frontend**: Client-side error reporting (e.g., Sentry), performance monitoring (e.g., Google Analytics, Lighthouse CI).
    -   **Backend**: API request/response logging, error rates, latency, resource utilization (CPU, memory), and custom metrics for authentication events. Alerts for critical failures or performance degradation.
    -   **Uptime Monitoring**: External checks for frontend and backend service availability.
