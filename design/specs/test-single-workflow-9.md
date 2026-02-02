# Design Specification: Foundational UI (Google Login & Basic Dashboard)

## Purpose
To establish the product's initial user interface, providing a secure, intuitive entry point via Google Login, and a basic dashboard as the primary user hub. This design prioritizes immediate usability and clarity, aligning with the core belief that "the product must feel obvious without documentation" and testing the "onboarding flow is intuitive without guidance" hypothesis.

## 1. Complete User Flow

*   **Step 1: Initial Access**
    *   User navigates to the application's base URL (e.g., `app.product.com`).
    *   **System Action:** Checks for an active session. If none, redirects to the Login Page.
*   **Step 2: Login Page**
    *   User is presented with a clear option to "Sign in with Google".
    *   **User Action:** Clicks the "Sign in with Google" button.
*   **Step 3: Google Authentication (External)**
    *   **System Action:** Initiates the Google OAuth flow, redirecting the user to Google's authentication page.
    *   **User Action:** Selects their Google account and grants necessary permissions (if not previously granted).
    *   **System Action:** Google authenticates the user and redirects them back to the application with an authentication token.
*   **Step 4: Application Authentication & Redirect**
    *   **System Action:** The application backend verifies the Google token, creates/identifies the user session, and issues an internal session token.
    *   **System Action:** Redirects the user to the Dashboard Page.
*   **Step 5: Dashboard Page**
    *   User arrives at the main dashboard, displaying a welcome message and placeholder content.

## 2. All Possible States & Microcopy

### A. Login Page

*   **Default State:**
    *   **Header:** "Welcome to [Product Name]"
    *   **Call to Action:** "Sign in with Google" (Button)
*   **Loading State (Google Redirect):**
    *   *No explicit UI state within our application during the external Google OAuth redirect.* The browser will show typical loading indicators.
*   **Error State (Google Auth Failed / Generic Login Error):**
    *   **Toast/Banner Message:** "Sign-in failed. Please try again."
    *   **Call to Action:** "Sign in with Google" (Button, remains active)
*   **Error State (Unauthorized User / No Account):**
    *   **Toast/Banner Message:** "You don't have access to [Product Name]. Please contact support if you believe this is an error."
    *   **Call to Action:** "Sign in with Google" (Button, remains active)

### B. Dashboard Page

*   **Loading State (Initial Data Fetch):**
    *   **Content Area:** Placeholder "Loading your dashboard..." (with a subtle spinner or skeleton UI).
*   **Default/Success State (Empty Dashboard):**
    *   **Header:** "Welcome, [User Name]!" (e.g., "Welcome, Alex!")
    *   **Content Area:** "Your dashboard is empty. Start by exploring features or creating your first project." (Placeholder message for future expansion).
*   **Error State (Dashboard Data Load Failed):**
    *   **Toast/Banner Message:** "Couldn't load dashboard data. Please refresh the page or try again later."
    *   **Content Area:** May display partial content or the empty state message if no data is available.

## 3. Exact Copy/Microcopy

*   **Login Page Header:** "Welcome to [Product Name]"
*   **Login Button:** "Sign in with Google"
*   **Generic Login Error:** "Sign-in failed. Please try again."
*   **Unauthorized User Error:** "You don't have access to [Product Name]. Please contact support if you believe this is an error."
*   **Dashboard Loading:** "Loading your dashboard..."
*   **Dashboard Welcome:** "Welcome, [User Name]!"
*   **Empty Dashboard Message:** "Your dashboard is empty. Start by exploring features or creating your first project."
*   **Dashboard Data Load Error:** "Couldn't load dashboard data. Please refresh the page or try again later."
*   **Session Expired (if applicable, after login):** "Your session has expired. Please sign in again."

## 4. Error Handling & Edge Cases

*   **Google Authentication Failure:**
    *   **Mechanism:** Catch OAuth errors.
    *   **User Feedback:** Display the "Sign-in failed. Please try again." toast/banner. Log error internally.
*   **Unauthorized Google Account:**
    *   **Mechanism:** Backend checks if the authenticated Google email/ID is allowed access.
    *   **User Feedback:** Display "You don't have access to [Product Name]..." toast/banner. Log unauthorized attempt.
*   **Network Issues (Post-Login API Calls):**
    *   **Mechanism:** Implement standard API error handling (try/catch, fetch error).
    *   **User Feedback:** Display "Couldn't load dashboard data..." toast/banner.
*   **Session Expiration:**
    *   **Mechanism:** Backend invalidates tokens after a set period. Frontend detects 401/403 responses.
    *   **User Feedback:** Redirect to login page with "Your session has expired. Please sign in again." message (can be a query param).
*   **Browser Back/Forward Navigation:**
    *   **Mechanism:** Standard browser history management. Ensure login page redirects if session is active, and dashboard remains if session is active.
    *   **User Experience:** Seamless navigation without re-authentication if session is valid.

## 5. Transitions & Animations

*   **Login Button Click:** A subtle visual feedback (e.g., button state change to "Signing in...") before redirecting to Google.
*   **Post-Login Redirect:** Fast, seamless redirect to the Dashboard. No explicit animation needed, focus on speed.
*   **Loading States:**
    *   **Dashboard:** Use a subtle skeleton UI or a small, centered spinner with "Loading your dashboard..." text to indicate activity without blocking.
*   **Error/Success Messages:**
    *   **Toasts/Banners:** Slide in from top/bottom, remain visible for 3-5 seconds, then slide out. Should be dismissible by user. Utilize shadcn's `Toast` component for consistency and accessibility.