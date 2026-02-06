# Technical Specification: 'dev-as-a-service' Application Foundation

## Architecture Overview
The 'dev-as-a-service' foundational UI will be implemented as a Single-Page Application (SPA) using React.js, bundled with Vite for optimal development and production performance. The UI will be styled using shadcn/ui components, providing a modern and consistent aesthetic. User authentication will be handled externally via Google OAuth, with a dedicated backend service responsible for validating Google ID tokens and issuing application-specific session tokens. The frontend will consume data from this backend API to populate the basic dashboard.

## Components

-   **`AuthLayout`**: Encapsulates the login screen, including the main heading, description, and the `GoogleAuthButton`. Handles redirect logic post-authentication or on session expiry.
-   **`DashboardLayout`**: Provides the main application shell after successful login, including a top navigation bar (with logo, user avatar/name, and logout button) and the main content area for dashboard widgets.
-   **`GoogleAuthButton`**: A reusable button component that initiates the Google OAuth flow. Manages loading states during the authentication process.
-   **`LoadingIndicator`**: A generic component to display loading states across the application, used during authentication redirects and dashboard data fetching.
-   **`ToastNotification`**: A small, temporary banner component for displaying success, error, or informational messages (e.g., 