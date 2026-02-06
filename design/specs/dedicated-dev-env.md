### Design Specification: Dedicated Dev Environment

#### 1. User Flow

**1.1 Initial Access (Unauthenticated)**
*   **Action**: User navigates to the application URL.
*   **System Response**: User is redirected to the "Sign In" page.

**1.2 Google Login**
*   **Action**: User clicks the "Sign in with Google" button.
*   **System Response**:
    *   A loading state is displayed on the button/page.
    *   User is redirected to Google's authentication consent screen.
    *   Upon successful authentication with Google, user is redirected back to the application.
    *   Application processes the authentication token.
*   **Outcome**:
    *   **Success**: User is redirected to the "Dashboard" page.
    *   **Failure**: User remains on the "Sign In" page, with an error message displayed.

**1.3 Dashboard Access (Authenticated)**
*   **Action**: User successfully logs in or accesses the application with an active session.
*   **System Response**: The "Dashboard" page is displayed, showing relevant information.
*   **Action**: User navigates away and then back to the application (with active session).
*   **System Response**: User is directly taken to the "Dashboard" page.

#### 2. States

**2.1 Sign In Page States**

*   **Initial State**:
    *   **Layout**: Centered content block with a welcome message and a single login button.
    *   **Copy**:
        *   Header: "Welcome!"
        *   Body: "Please sign in to continue."
        *   Button: "Sign in with Google"
*   **Loading State (during Google Auth redirect)**:
    *   **Layout**: Same as initial, but login button is disabled and shows a loading spinner.
    *   **Copy**:
        *   Header: "Welcome!"
        *   Body: "Please sign in to continue."
        *   Button: "Signing in..." (with spinner)
*   **Error State (post-Google Auth failure)**:
    *   **Layout**: Same as initial, with an additional error message displayed prominently.
    *   **Copy**:
        *   Header: "Welcome!"
        *   Body: "Please sign in to continue."
        *   Button: "Sign in with Google"
        *   Error message: "Login failed. Please try again." (or specific error if possible, e.g., "Authentication cancelled by user.")

**2.2 Dashboard Page States**

*   **Loading State (initial dashboard data fetch)**:
    *   **Layout**: A central loading spinner or skeleton UI for the dashboard content.
    *   **Copy**: "Loading dashboard..."
*   **Success State (content displayed)**:
    *   **Layout**: Header with "Dashboard" title, user greeting, and a main content area with mock cards/sections.
    *   **Copy**:
        *   Header: "Dashboard"
        *   Greeting: "Welcome, [User Name]!" (e.g., "Welcome, Alex!")
        *   Card 1 Title: "Quick Actions"
        *   Card 1 Body: "Start your next project with ease."
        *   Card 2 Title: "Recent Activity"
        *   Card 2 Body: "No recent activity to display." (Example for empty state within a card)
*   **Empty State (for dynamic content areas within dashboard, if applicable)**:
    *   **Layout**: Specific section shows an empty state message.
    *   **Copy**: "No data to display yet." (e.g., within "Recent Activity" card)

#### 3. Copy/Microcopy

*   **Sign In Page**:
    *   "Welcome!"
    *   "Please sign in to continue."
    *   "Sign in with Google"
    *   "Signing in..."
    *   "Login failed. Please try again."
    *   "Authentication cancelled. Please try again."
*   **Dashboard Page**:
    *   "Dashboard"
    *   "Welcome, [User Name]!"
    *   "Quick Actions"
    *   "Start your next project with ease."
    *   "Recent Activity"
    *   "No recent activity to display."
    *   "Loading dashboard..."

#### 4. Error Handling and Edge Cases

*   **Google Authentication Failure**:
    *   If Google login fails (e.g., network error, Google service error, user declines permissions), the user is redirected back to the Sign In page with an appropriate error message (`"Login failed. Please try again."` or `"Authentication cancelled. Please try again."`).
*   **Session Expiration/Invalid Token**:
    *   If an authenticated user's session expires or their token becomes invalid, any attempt to access authenticated routes should automatically redirect them to the "Sign In" page. No explicit error message is needed beyond the general "Please sign in to continue." for a cleaner experience, as the user might not be aware their session expired.
*   **Unauthorized Access**:
    *   Attempting to access a protected route directly without being authenticated should always redirect to the "Sign In" page.
*   **Network Issues**:
    *   During initial page load or API calls, if network issues occur, a generic "Network error. Please check your connection and try again." message can be displayed, potentially with a retry button. For this foundational build, focus on login and dashboard display.

#### 5. Transitions and Animations

*   **Page Transitions**: Simple, instantaneous transitions between Sign In and Dashboard pages upon successful login/logout. No complex animations are required at this foundational stage.
*   **Loading Indicators**:
    *   A small spinner embedded within the "Sign in with Google" button during the authentication process.
    *   A full-page or central spinner/skeleton loader for the Dashboard during its initial data fetch (if any asynchronous data loading is introduced beyond static mock content).