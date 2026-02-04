## Design Specification for Feature: gh-vs-7 (Foundational UI)

### 1. Complete User Flow: Onboarding & Dashboard Access

**Objective**: Enable new and returning users to securely log in via Google and access a basic dashboard, establishing the product's core interactive layer.

**Flow Steps**:

1.  **Initial Application Load**
    *   **User Action**: Navigates to `app.yourdomain.com` (or similar base URL).
    *   **System Action**: Application initiates a check for existing authentication tokens/session.
    *   **UI State (Loading)**:
        *   **Visual**: Full-screen centered spinner (e.g., `shadcn/ui` `Spinner` or `Loader` component).
        *   **Copy**: "Loading..."
    *   **Validation**: Provides immediate feedback that the application is active.

2.  **Authentication Check & Login Prompt**
    *   **System Action**: If no valid session is found, displays the login page.
    *   **UI State (Login Page)**:
        *   **Visual**: A centered card or modal containing product branding (placeholder logo/name), a main heading, a sub-heading, and a prominent "Sign in with Google" button.
        *   **Copy**:
            *   **Header**: "Welcome to [Product Name]"
            *   **Sub-header**: "Sign in to continue"
            *   **Button**: "Sign in with Google"
        *   **Interaction**: User clicks the "Sign in with Google" button.
    *   **Validation**: "Can a new user predict what happens next?" – Yes, the intent to log in is explicit. "Does the UI match the intent?" – Clearly guides the user to authenticate.

3.  **Google Authentication Redirection & Consent**
    *   **System Action**: Redirects the user's browser to Google's OAuth consent screen.
    *   **UI State**: (External to application) User interacts with Google's standard authentication flow to select an account and grant permissions.
    *   **Validation**: Relies on Google's established UX for authentication clarity.

4.  **Post-Authentication Callback & Processing**
    *   **User Action**: Completes Google authentication and is redirected back to the application (e.g., `app.yourdomain.com/auth/callback`).
    *   **System Action**: The application backend/frontend processes the authentication token received from Google.
    *   **UI State (Processing/Loading)**:
        *   **Visual**: Full-screen centered spinner.
        *   **Copy**: "Signing you in..." or "Loading your workspace..."
    *   **Validation**: Provides crucial feedback during a potentially brief but critical technical step.

5.  **Successful Login & Dashboard Display**
    *   **System Action**: If authentication is successful, the user is redirected to the `/dashboard` route.
    *   **UI State (Dashboard)**:
        *   **Visual**: A clean, minimal layout using `shadcn/ui` components. Includes a top navigation bar (Product Name/Logo on the left, User Avatar/Name with a dropdown menu on the right). The main content area displays a welcome message and placeholder content.
        *   **Copy**:
            *   **Page Title (Browser tab)**: "Dashboard | [Product Name]"
            *   **Header (on page)**: "Dashboard"
            *   **Welcome Message**: "Welcome back, [User's Name]!" (Dynamically inserts authenticated user's name).
            *   **Placeholder Content**: "This is your central hub. Future features will appear here."
            *   **User Menu Item**: "Logout"
        *   **Interaction**: User can click on their avatar/name to reveal a dropdown with "Logout".
    *   **Validation**: "The product must feel obvious without documentation." – The dashboard clearly indicates successful login and provides a starting point. "Users value speed over configurability." – Direct access to the core functionality.

### 2. All Possible States

*   **Initial Application Load (Unauthenticated)**
    *   **Visual**: Centered full-screen spinner.
    *   **Copy**: "Loading..."
*   **Login Page (Unauthenticated)**
    *   **Visual**: Centered card with "Welcome to [Product Name]", "Sign in to continue", "Sign in with Google" button.
*   **Authentication Processing (Post-Google Redirect)**
    *   **Visual**: Centered full-screen spinner.
    *   **Copy**: "Signing you in..."
*   **Dashboard (Authenticated - Initial/Empty)**
    *   **Visual**: Top navigation bar, "Dashboard" header, "Welcome back, [User's Name]!", and placeholder text in the main content area.
*   **Dashboard (Authenticated - Loading Content - *Future State*)**
    *   **Visual**: Dashboard layout with specific content sections (e.g., card for "Projects") showing individual loading spinners within their boundaries.
    *   **Copy**: Contextual loading messages (e.g., "Loading your projects...").

### 3. Exact Copy/Microcopy

*   **Login Page:**
    *   Header: "Welcome to [Product Name]"
    *   Sub-header: "Sign in to continue"
    *   Button: "Sign in with Google"
*   **Authentication Processing:**
    *   Spinner Text: "Signing you in..."
*   **Dashboard:**
    *   Page Title (browser): "Dashboard | [Product Name]"
    *   Header (on page): "Dashboard"
    *   Welcome Message (Authenticated): "Welcome back, [User's Name]!"
    *   Placeholder Content: "This is your central hub. Future features will appear here."
    *   Logout Button/Menu Item: "Logout"

### 4. Error Handling and Edge Cases

*   **Google Login Failure (e.g., user cancels, network issue during redirect, Google API error)**
    *   **Trigger**: Google redirects back with an error parameter, or the internal API call to validate the token fails.
    *   **UI State**: Returns to the Login Page, displaying an error message.
    *   **Copy**: "Sign-in failed. Please try again." (Displayed prominently, e.g., in a `shadcn/ui` `Alert` component near the button).
    *   **Action**: The "Sign in with Google" button remains active, allowing the user to retry.
    *   **Validation**: "Is anything explained too late?" – No, the error is immediate and actionable. "Does the UI match the intent?" – Yes, guides the user to resolve the issue.
*   **Authentication Token Invalid/Expired (on subsequent visits)**
    *   **Trigger**: An API request is made with an expired or invalid authentication token, or the token validation fails on application load.
    *   **System Action**: The application clears the invalid token and redirects the user to the Login Page.
    *   **UI State**: Login Page with an ephemeral (briefly displayed) message.
    *   **Copy (ephemeral message)**: "Your session has expired. Please sign in again." (Displayed as a `Toast` or temporary `Alert`.)
    *   **Validation**: Clearly communicates the reason for redirection and guides the user to re-authenticate.
*   **Network Offline (Initial Load or during Auth/Dashboard Load)**
    *   **Trigger**: Browser's network status API indicates offline, or API requests consistently fail due to network.
    *   **UI State**: Full-screen message over the application content.
    *   **Copy**: "You appear to be offline. Please check your internet connection and try again."
    *   **Action**: A "Retry" button to attempt reloading the application or re-checking the connection.

### 5. Transitions and Animations

*   **Loading States**: Subtle, quick fade-ins/outs (e.g., 200ms duration) for content appearing after a load. Spinners should animate smoothly.
*   **Button Interactions**: Standard `shadcn/ui` button feedback (slight background change on hover, subtle press effect on click) for responsiveness.
*   **Page Transitions**: For redirects (e.g., Login to Dashboard), transitions should be instant to align with the belief that "Users value speed over configurability." No elaborate full-page animations are required for this foundational MVP.