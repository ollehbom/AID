## Design Specification: Foundational Application (test-single-workflow-3)

### 1. User Flow

**Flow Name**: Initial Login & Dashboard Access

1.  **User arrives at the application's root URL (e.g., `app.product.com/login`)**.
    *   **State**: Login Page (initial).
2.  **User sees the "Sign in with Google" button.**
    *   **Action**: User clicks "Sign in with Google".
3.  **Application initiates Google OAuth flow.**
    *   **State**: Loading/Redirecting (brief).
    *   *(External to our UI: User interacts with Google's authentication consent screen if not already logged in/consented.)*
4.  **Upon successful authentication, Google redirects back to the application.**
    *   **State**: Loading/Authenticating (brief).
5.  **User is redirected to the main Dashboard.**
    *   **State**: Dashboard (initial load).
6.  **Dashboard displays mock content.**
    *   **State**: Dashboard (content displayed).

### 2. All Possible States & Copy

#### A. Login Page
*   **State**: `login_initial`
    *   **Headline**: "Welcome to [Product Name]"
    *   **Subtitle**: "Your AI-powered workflow"
    *   **Button**: "Sign in with Google"
    *   **Error Message (if applicable)**: (Hidden by default, see Error Handling)

*   **State**: `login_loading` (after button click, before Google redirect)
    *   **Display**: "Redirecting to Google for authentication..." (subtle spinner or text below the button)

#### B. Dashboard Page
*   **State**: `dashboard_loading` (after successful Google redirect, before content loads)
    *   **Headline**: "Dashboard"
    *   **Display**: "Loading your workspace..." (with a subtle spinner)

*   **State**: `dashboard_content` (after mock content loads)
    *   **Navigation (Top Bar/Sidebar - conceptual)**: "Dashboard"
    *   **Main Headline**: "Welcome, [User Name]!"
    *   **Section Title 1**: "Your Projects"
        *   **Content**: 
            *   "Project Alpha: Initial setup complete."
            *   "Project Beta: Awaiting next steps."
            *   "Project Gamma: Explore new features."
    *   **Section Title 2**: "Quick Actions"
        *   **Content**: 
            *   "Create New Project"
            *   "View Documentation"

### 3. Error Handling and Edge Cases

*   **Google Authentication Failure**: 
    *   **Scenario**: User denies consent, Google account issue, network error during OAuth.
    *   **State**: `login_error`
    *   **Display**: Return to `login_initial` state with an inline error message.
    *   **Error Copy**: "Authentication failed. Please try again or contact support if the issue persists." (Displayed prominently near the "Sign in with Google" button).
*   **Network Error (Dashboard Load)**:
    *   **Scenario**: After successful login, dashboard data fails to load.
    *   **State**: `dashboard_error`
    *   **Display**: Dashboard layout with a central error message.
    *   **Error Copy**: "Failed to load dashboard content. Please check your internet connection and refresh, or contact support."

### 4. Transitions and Animations

*   **Login to Google OAuth**: Standard browser redirect.
*   **Google OAuth to Dashboard**: Standard browser redirect.
*   **Loading States**: Subtle spinners or progress indicators for brief loading periods (e.g., 500ms+). No complex animations are required for this foundational stage. Focus on speed and directness.