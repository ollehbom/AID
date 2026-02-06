# Design Specification: Core UI Foundation (feature-2)

## 1. User Flow

### A. Unauthenticated User Access & Login
1.  **User Access**: User navigates to the application URL (e.g., `app.example.com`).
2.  **Redirect to Login**: If the user is not authenticated, they are automatically redirected to the `/login` route.
3.  **Login Page Display**: The login page (`/login`) is displayed.
4.  **Initiate Google Login**: User clicks the "Sign in with Google" button.
5.  **Google Authentication**: A Google authentication flow is initiated (e.g., a popup window or full-page redirect to Google's OAuth consent screen).
6.  **Authentication Callback**: Upon successful authentication with Google, the user is redirected back to the application's callback URL.
7.  **Session Establishment**: The application processes the Google authentication token, establishes a user session, and stores necessary user information.
8.  **Redirect to Dashboard**: Upon successful session establishment, the user is redirected to the `/dashboard` route.

### B. Authenticated User Dashboard & Logout
1.  **Dashboard Display**: The dashboard page (`/dashboard`) is displayed, showing initial mock content.
2.  **Interaction**: User can view the mock content and see their logged-in status (e.g., via a profile icon or name in the header).
3.  **Initiate Logout**: User clicks a "Logout" button (typically located in the header or a user profile menu).
4.  **Session Termination**: The application terminates the user's session (e.g., clears local storage, invalidates session token).
5.  **Redirect to Login**: User is redirected back to the `/login` route.

## 2. All Possible States, Copy & Microcopy

### A. Login Page (`/login`)
*   **Initial State (Unauthenticated)**:
    *   **Headline**: "Welcome!"
    *   **Body Text (Optional)**: "Sign in to access your dashboard."
    *   **Button**: `Sign in with Google` (with Google logo icon)
*   **Loading State (During Google Auth)**:
    *   **Headline**: "Welcome!"
    *   **Button**: `Logging in...` (disabled, with a small spinner icon)
*   **Error State (Google Auth Failed/Cancelled)**:
    *   **Headline**: "Welcome!"
    *   **Button**: `Sign in with Google` (with Google logo icon)
    *   **Error Message**: `Login failed. Please try again.` (displayed below the button, in a subtle error style)
    *   **Specific Error (if applicable)**: `Google authentication cancelled.`

### B. Dashboard Page (`/dashboard`)
*   **Loading State (Initial Data Fetch)**:
    *   **Header**: `Dashboard`
    *   **Body Content**: `Loading dashboard...` (with a central spinner)
*   **Empty State (No Content Yet)**:
    *   **Header**: `Dashboard`
    *   **Welcome Message**: `Welcome, [User Name]!`
    *   **Body Content**: `No items to display yet. Get started by exploring new features.` (or similar prompt for future functionality)
*   **Content Displayed State (Mock Content)**:
    *   **Header**: `Dashboard`
    *   **Welcome Message**: `Welcome, [User Name]!`
    *   **Body Content**: Display of Shadcn-styled mock cards or data tables, demonstrating the design system.
*   **Error State (Dashboard Data Fetch Failed)**:
    *   **Header**: `Dashboard`
    *   **Welcome Message**: `Welcome, [User Name]!`
    *   **Body Content**: `Oops! Something went wrong loading your dashboard. Please refresh.` (with a 'Refresh' button)

### C. Global Elements
*   **Header (Authenticated)**:
    *   `Dashboard` (as page title)
    *   `[User Avatar/Name]` (clickable, leading to a small dropdown menu)
    *   **Dropdown Menu Item**: `Logout`

## 3. Error Handling and Edge Cases

*   **Google Authentication Failure**: If Google authentication fails (e.g., network error, user declines permissions, invalid credentials), the user is returned to the login page, and an error message (`Login failed. Please try again.`) is displayed.
*   **Network Issues**: Any network request failures (e.g., during dashboard data loading) should display a user-friendly error message within the affected section, optionally with a retry mechanism.
*   **Session Expiration**: If an authenticated session expires or becomes invalid, any subsequent protected API request should trigger a redirect back to the `/login` page. The user should be informed if possible (e.g., "Your session has expired. Please log in again.").
*   **Unauthorized Access**: If an unauthenticated user attempts to access a protected route directly (e.g., `/dashboard`), they must be redirected to `/login`.
*   **User Cancellation**: If the user cancels the Google authentication flow, they should be returned to the initial login page with a message like `Google authentication cancelled.`

## 4. Transitions and Animations

*   **Loading Indicators**: Subtle spinners should be used for any asynchronous operations (e.g., during Google login, dashboard data fetch). These should be centrally aligned or replace the content being loaded.
*   **Page Transitions**: Standard browser navigation for redirects. No complex custom page transitions are required at this foundational stage.
*   **Button States**: Hover, active, and disabled states for buttons should follow Shadcn UI conventions, providing clear visual feedback.
*   **Error Message Appearance**: Error messages should appear smoothly (e.g., fade-in) without being jarring, and be styled clearly as warnings.