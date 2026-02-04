## Design Specification: gh-vs-3 - Foundational Frontend

### 1. Overview
This specification details the design for the initial React frontend, including user authentication via Google and a basic dashboard. The goal is a stable, intuitive, and modern platform, aligning with the belief: "The product must feel obvious without documentation."

### 2. User Flow

**A. Application Launch & Initial Load**
1.  **User Action**: User navigates to the application URL (e.g., `app.example.com`).
2.  **System Action**: React app loads and initializes.
3.  **State Transition**: `APP_LOADING`

**B. Authentication Check & Redirection**
1.  **System Action**: App checks for existing auth session (e.g., token).
2.  **Condition 1: Authenticated Session Found**
    *   **System Action**: Validates session, redirects to `/dashboard`.
    *   **State Transition**: `DASHBOARD_LOADING`
3.  **Condition 2: No Session / Invalid Session**
    *   **System Action**: Redirects to `/login`.
    *   **State Transition**: `LOGIN_PAGE_DISPLAY`

**C. User Login (via Google)**
1.  **User Action**: On `/login`, clicks "Sign in with Google".
2.  **State Transition**: `LOGIN_IN_PROGRESS`
3.  **System Action**: Initiates Google OAuth flow.
4.  **User Action**: Completes Google authentication.
5.  **System Action**: Google redirects back, app processes token.
    *   **Condition 1: Authentication Successful**
        *   **System Action**: Redirects to `/dashboard`.
        *   **State Transition**: `DASHBOARD_LOADING`
    *   **Condition 2: Authentication Failed**
        *   **System Action**: Displays error on `/login`.
        *   **State Transition**: `LOGIN_ERROR_DISPLAY`

**D. Dashboard Display**
1.  **System Action**: Upon reaching `/dashboard`, app loads mock content.
2.  **State Transition**: `DASHBOARD_LOADING`
3.  **System Action**: Renders dashboard.
4.  **State Transition**: `DASHBOARD_CONTENT_DISPLAY`

### 3. States and Copy

#### A. `APP_LOADING`
*   **Visual**: Full-screen overlay with central spinner.
*   **Copy**: "Loading application..."

#### B. `LOGIN_PAGE_DISPLAY`
*   **Visual**: Centered card (shadcn/ui style).
*   **Heading**: "Welcome to [Product Name]"
*   **Subheading**: "Sign in to continue."
*   **Button**: `[Google Icon]` "Sign in with Google"
*   **Legal Text (small)**: "By signing in, you agree to our [Terms of Service](link) and [Privacy Policy](link)."

#### C. `LOGIN_IN_PROGRESS`
*   **Visual**: "Sign in with Google" button disabled, with inline loading spinner.
*   **Button Copy**: "Signing in..."

#### D. `LOGIN_ERROR_DISPLAY`
*   **Visual**: Prominent, dismissible toast or inline error message (red text) on login page.
*   **Error Copy**: "Sign-in failed. Please try again. If the problem persists, contact support."
    *   *Edge Case Specific*: "Authentication cancelled by user." (if user closes Google popup)

#### E. `DASHBOARD_LOADING`
*   **Visual**: Basic dashboard layout with skeleton loaders or central spinner.
*   **Header Title**: "Dashboard"
*   **Main Content Area**: Central spinner with text "Loading your overview..."

#### F. `DASHBOARD_CONTENT_DISPLAY`
*   **Visual**: Clean, responsive dashboard (shadcn/ui components).
    *   **Header**: Fixed top bar: Product logo/name (left), User avatar/dropdown (right).
    *   **Main Content**: Grid/stacked cards.
*   **Header - User Avatar/Dropdown**: 
    *   Icon: User Avatar (e.g., `lucide-react/User`) or initials.
    *   Dropdown Items: "Settings", "Help", "Logout"
*   **Main Content - Card 1 (Getting Started)**:
    *   **Title**: "Getting Started"
    *   **Body**: "This is your dashboard. Explore features and manage your projects."
    *   **Action Button**: "View Documentation" (link to `docs.example.com`)
*   **Main Content - Card 2 (Recent Activity - Empty State)**:
    *   **Title**: "Recent Activity"
    *   **Body**: "No recent activity yet. Start interacting with the platform!"
    *   **Action Button**: "Create New Project" (placeholder)

### 4. Error Handling and Edge Cases
*   **Google Auth Rejection/Cancellation**: If the user closes the Google login popup or denies permissions, the application should return to the `LOGIN_PAGE_DISPLAY` state, potentially with a specific `LOGIN_ERROR_DISPLAY` message indicating cancellation.
*   **Network Errors**: For network-related failures during login or dashboard load, implement a generic error display (toast or banner). Copy: "A network error occurred. Please check your internet connection and try again."
*   **Invalid/Expired Session**: If an authenticated user tries to access a route with an expired or invalid token, the system should automatically clear the invalid session and redirect to `LOGIN_PAGE_DISPLAY`.

### 5. Transitions and Animations
*   **Page Transitions**: Subtle fade-in/fade-out animations for route changes to provide a smooth user experience.
*   **Loading States**: Smooth, non-distracting loading spinners for asynchronous operations (e.g., login, dashboard content load).
*   **Button States**: Visual feedback on button click (e.g., slight press animation, change to `LOGIN_IN_PROGRESS` state with spinner).