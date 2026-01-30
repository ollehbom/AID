# Design Specification: Foundational Frontend (test-auto-fix-8)

## Overview
This specification details the user flow, states, and microcopy for the initial React application setup, including Google login and a basic dashboard.

## User Flow

### Flow 1: New User Login & Dashboard Access

1.  **User arrives at application URL.**
    *   **State:** `LoginScreen_Initial`
    *   **UI:** Displays "Welcome" heading and "Sign in with Google" button.
    *   **Copy:**
        *   Heading: "Welcome"
        *   Button: "Sign in with Google"
        *   Optional sub-text: "To get started, please sign in."

2.  **User clicks "Sign in with Google" button.**
    *   **State:** `LoginScreen_Authenticating`
    *   **UI:** Button becomes disabled, displays a loading indicator.
    *   **Copy:**
        *   Button: "Signing in..."
    *   **Transition:** Initiates Google OAuth flow (external browser/popup).

3.  **Google OAuth completes.**

    *   **3a. Successful Authentication:**
        *   **State:** `Dashboard_Loading`
        *   **UI:** Redirects to `/dashboard`. A full-screen or prominent loading indicator is shown.
        *   **Copy:** "Loading your dashboard..."
        *   **Transition:** After successful data load, transitions to `Dashboard_Content`.

    *   **3b. Failed Authentication:**
        *   **State:** `LoginScreen_Error`
        *   **UI:** Returns to `LoginScreen_Initial` with an error message displayed prominently.
        *   **Copy:** "Login failed. Please try again." (or specific error if available from Google)
        *   **Error Handling:** User can retry by clicking "Sign in with Google" again.

4.  **Dashboard Loads Data.**
    *   **State:** `Dashboard_Content`
    *   **UI:** Displays a header, a greeting, and mock content within a card.
    *   **Copy:**
        *   Header: "Dashboard"
        *   Greeting: "Hello, [User Name]!" (e.g., "Hello, Jane Doe!")
        *   Card Title: "Your Overview"
        *   Card Body: "Welcome to your dashboard. This is where your key information and quick actions will appear."
    *   **Edge Cases:**
        *   **Empty State:** If for some reason initial dashboard data is unavailable or intentionally empty for new users.
            *   **State:** `Dashboard_Empty`
            *   **UI:** Displays header, greeting, and a message indicating no content yet.
            *   **Copy:** "Hello, [User Name]! Your dashboard is currently empty. Start by doing X or Y to see data here." (For this MVP, `Dashboard_Content` with mock data is sufficient.)

## States Summary

1.  `LoginScreen_Initial`: User sees login prompt.
2.  `LoginScreen_Authenticating`: Google login process in progress.
3.  `LoginScreen_Error`: Login failed, error message displayed.
4.  `Dashboard_Loading`: Dashboard content is being fetched/prepared.
5.  `Dashboard_Content`: Dashboard with mock content displayed.
6.  `Dashboard_Empty` (Future consideration/MVP simplification): Dashboard with no content, prompt to add.

## Copy / Microcopy

*   **Login Screen:**
    *   Heading: "Welcome"
    *   Button: "Sign in with Google"
    *   Button (Authenticating): "Signing in..."
    *   Error Message: "Login failed. Please try again."
*   **Dashboard Screen:**
    *   Header: "Dashboard"
    *   Greeting: "Hello, [User Name]!"
    *   Card Title: "Your Overview"
    *   Card Body: "Welcome to your dashboard. This is where your key information and quick actions will appear."
    *   Loading: "Loading your dashboard..."

## Transitions & Animations
*   **Login to Dashboard:** Standard page redirect. No complex custom animations required.
*   **Loading States:** Simple loading spinners or skeleton loaders as provided by shadcn UI.
