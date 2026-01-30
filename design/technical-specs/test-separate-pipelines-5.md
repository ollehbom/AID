# Technical Specification: Foundational UI (test-separate-pipelines-5)

## Architecture Overview

The architecture for the foundational UI will adopt a modern client-server pattern, leveraging a static frontend and a serverless backend for authentication. Google OAuth will serve as the external Identity Provider (IdP). All communication will be secured via HTTPS.

```mermaid
graph TD
    User[User's Browser] -- 1. Navigate to App --> CDN
    CDN -- 2. Serve React App (Next.js) --> User
    User -- 3. Click 'Sign in with Google' --> ReactApp
    ReactApp -- 4. Initiate Google OAuth Flow --> GoogleOAuth[Google OAuth Service]
    GoogleOAuth -- 5. Redirect with Code/Token --> ReactAppCallback[React App Callback URL]
    ReactAppCallback -- 6. Send Code/Token --> BackendAuthAPI[Backend Auth API (Serverless Function)]
    BackendAuthAPI -- 7. Validate Code/Token --> GoogleOAuth
    GoogleOAuth -- 8. Validation Response --> BackendAuthAPI
    BackendAuthAPI -- 9. Create Session (e.g., HTTP-only Cookie) --> User
    User -- 10. Access Protected Routes --> ReactApp
    ReactApp -- 11. API Calls with Session --> BackendAuthAPI
    BackendAuthAPI -- 12. Return Data --> ReactApp
```

## Components

### Frontend (React Application, Next.js)
-   **Purpose**: User interface, handles client-side routing, renders UI components, initiates OAuth flow, and makes API calls.
-   **Responsibilities**: 
    -   Display Login Screen.
    -   Handle Google OAuth redirect and token forwarding.
    -   Render Dashboard Screen.
    -   Manage client-side session state (minimal).
    -   Display loading and error states.
-   **Key Technologies**: React, Next.js (for routing, SSR/SSG, API routes), shadcn/ui (for components), Tailwind CSS.

### Backend Authentication API (Serverless Function)
-   **Purpose**: Securely handle Google OAuth token validation and user session management.
-   **Responsibilities**: 
    -   Receive Google OAuth authorization code/ID token from the frontend.
    -   Verify the token's authenticity with Google.
    -   Create and manage secure user sessions (e.g., sign JWT, set HTTP-only cookie).
    -   Respond with session information or errors.
-   **Key Technologies**: Node.js/Python/Go (runtime), AWS Lambda/Google Cloud Functions/Azure Functions (platform), API Gateway, potentially a simple database for user profiles (future).

### External Services
-   **Google OAuth Service**: Provides identity verification and authorization.
-   **Content Delivery Network (CDN)**: Serves static frontend assets globally for performance and availability (e.g., CloudFront, Vercel, Netlify).

## Data Models

### User Session (Backend-managed)
```json
{
  "sessionId": "uuid-v4-string",
  "userId": "google-user-id-string",
  "email": "user@example.com",
  "name": "User Name",
  "avatarUrl": "https://example.com/avatar.jpg",
  "issuedAt": "2024-01-01T12:00:00Z",
  "expiresAt": "2024-01-01T13:00:00Z"
}
```
-   **Note**: This session data will primarily be stored server-side or encoded within a secure, signed HTTP-only cookie, not directly exposed to the client-side JavaScript.

## APIs

### 1. `POST /api/auth/google/callback`
-   **Purpose**: Exchange Google's authorization code/ID token for an application session.
-   **Request**: `application/json`
    ```json
    {
      "code": "<google_authorization_code>",
      "state": "<oauth_state_parameter>"
    }
    ```
    or for direct ID token flow:
    ```json
    {
      "idToken": "<google_id_token>"
    }
    ```
-   **Response**: `application/json`
    -   **Success (200 OK)**:
        ```json
        {
          "message": "Authentication successful",
          "user": {
            "userId": "google-user-id-string",
            "email": "user@example.com",
            "name": "User Name",
            "avatarUrl": "https://example.com/avatar.jpg"
          }
        }
        ```
        *   **Note**: A secure, HTTP-only cookie containing the session token will be set by the server in the response headers.
    -   **Error (400 Bad Request / 401 Unauthorized / 500 Internal Server Error)**:
        ```json
        {
          "error": "Authentication failed",
          "details": "Invalid token or internal server error"
        }
        ```
-   **Authentication Requirements**: None on this endpoint directly; token validation happens server-side.

### 2. `GET /api/user/me` (Example Protected Endpoint)
-   **Purpose**: Retrieve details of the currently authenticated user.
-   **Request**: No body.
-   **Authentication Requirements**: Valid session cookie (automatically sent by browser).
-   **Response**: `application/json`
    -   **Success (200 OK)**:
        ```json
        {
          "userId": "google-user-id-string",
          "email": "user@example.com",
          "name": "User Name",
          "avatarUrl": "https://example.com/avatar.jpg"
        }
        ```
    -   **Error (401 Unauthorized)**:
        ```json
        {
          "error": "Unauthorized",
          "message": "No active session or invalid credentials."
        }
        ```

## Infrastructure

-   **Frontend Hosting**: 
    -   **Provider**: Vercel or Netlify (recommended for Next.js) or AWS S3 + CloudFront.
    -   **Configuration**: Static site hosting, CDN for global distribution, HTTPS enabled by default.
-   **Backend (Authentication API)**:
    -   **Provider**: AWS Lambda + API Gateway, Google Cloud Functions + API Gateway, or Next.js API Routes (if using Next.js for the entire app).
    -   **Configuration**: Serverless function for cost-efficiency and auto-scaling, integrated with an API Gateway for secure endpoint exposure. Environment variables for Google OAuth client ID/secret.
-   **DNS**: Configured to point application URL to the frontend hosting provider.
-   **Google Cloud Project/Console**: OAuth 2.0 Client ID and Client Secret configured for the application, authorized redirect URIs set.

## Testing Strategy

-   **Unit Tests**: 
    -   **Frontend**: React components (e.g., Login, Dashboard) using Jest/React Testing Library.
    -   **Backend**: Authentication API logic (token validation, session creation) using Jest/Mocha.
-   **Integration Tests**: 
    -   **Frontend-Backend Auth Flow**: Simulate user clicking login, backend token exchange, and session establishment.
    -   **API Endpoints**: Verify correct responses and error handling for `/api/auth/google/callback` and `/api/user/me`.
-   **End-to-End (E2E) Tests**: 
    -   **User Login Journey**: Simulate a full user login from navigating to the app, clicking Google login, completing OAuth, and landing on the dashboard using tools like Cypress or Playwright.
    -   **Error Scenarios**: Test various login failure cases (e.g., user cancellation, invalid token).
-   **Security Testing**: 
    -   **Penetration Testing (Manual/Automated)**: Identify common web vulnerabilities (OWASP Top 10) on the authentication flow and exposed APIs.
    -   **Dependency Scanning**: Regularly scan for known vulnerabilities in all libraries (e.g., Snyk, npm audit).

## Deployment

-   **CI/CD Pipeline**: Automated pipeline (e.g., GitHub Actions, GitLab CI, Vercel/Netlify built-in) for:
    -   Running tests.
    -   Building frontend assets.
    -   Deploying frontend to static hosting.
    -   Deploying backend serverless functions.
-   **Rollout Strategy**: 
    -   **Initial Deployment**: Direct deployment to production for internal testing.
    -   **Future Features**: Utilize feature flags for new features to enable canary deployments or staged rollouts.
-   **Monitoring and Alerts**: 
    -   **Frontend**: Error tracking (e.g., Sentry), performance monitoring (e.g., Lighthouse CI, Web Vitals), analytics (e.g., Google Analytics).
    -   **Backend**: Logs (e.g., CloudWatch Logs, Stackdriver Logging), metrics (e.g., API request rates, error rates, latency), alerts for critical failures.
-   **Environment Management**: Separate environments for development, staging, and production, with distinct OAuth credentials and API endpoints.
