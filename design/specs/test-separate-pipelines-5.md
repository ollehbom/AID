## Design Specification: Foundational UI (test-separate-pipelines-5)

### Complete User Flow
1.  **Access Application**: User navigates to the application URL (e.g., `app.yourproduct.com`).
2.  **Authentication Check**: The application immediately checks for an existing, active user session.
3.  **Display Login Screen**: If no active session is found, the **Login Screen** is displayed.
4.  **Initiate Google Login**: User clicks the "Sign in with Google" button.
5.  **OAuth Redirect**: The user's browser is redirected to Google's OAuth consent screen.
6.  **Grant Permissions**: User reviews and grants the necessary permissions to the application.
7.  **Return to Application**: Google redirects the user's browser back to the application with an authorization token.
8.  **Authentication Processing**: The application's backend validates the Google token and establishes a session.
9.  **Display Dashboard**: If authentication is successful, the user is redirected to the **Dashboard Screen**.
10. **Handle Login Error**: If authentication fails at any point (e.g., token invalid, network error), the user is returned to the **Login Screen (Error State)** with an appropriate message.

### All Possible States

#### 1. Login Screen (Initial)
*   **Purpose**: Provide a clear and familiar entry point for new and returning users.
*   **Elements**: 
    *   Application Logo/Name (prominently displayed)
    *   Welcome message
    *   "Sign in with Google" button (prominently styled)
*   **Copy**: 
    *   `Header`: "Welcome to [Product Name]"
    *   `Subtitle (Optional)`: "Your journey starts here."
    *   `Button`: "Sign in with Google"

#### 2. Login Screen (Error State)
*   **Purpose**: Inform the user of an authentication failure and provide guidance.
*   **Elements**: Same as Initial Login Screen, with an added error message component.
*   **Copy**: 
    *   `Error Message`: "Login failed. Please try again. If the issue persists, contact support." (Displayed in a clear, contrasting color like red).

#### 3. Loading/Redirecting State
*   **Purpose**: Acknowledge ongoing processes during the OAuth redirect and authentication.
*   **Elements**: Full-screen overlay with a spinner or a small inline spinner near the button.
*   **Copy**: 
    *   `Message`: "Connecting..." or "Authenticating..." (Briefly displayed, if full-screen).

#### 4. Dashboard Screen (Initial/Empty)
*   **Purpose**: Serve as the primary landing page post-login, confirming successful access and indicating readiness for future features.
*   **Elements**: 
    *   Top Bar with Welcome message and potentially user avatar/settings (minimal).
    *   Main content area with a primary information card.
    *   Placeholder for future features.
*   **Copy**: 
    *   `Top Bar Header`: "Welcome, [User Name]!"
    *   `Card Title`: "Your Dashboard"
    *   `Card Body Text`: "This is your foundational dashboard. We're busy building powerful features for you. Stay tuned!"
    *   `Placeholder Label`: "More features coming soon..."
    *   `Call to Action (Optional)`: "Learn More" (button on the card, leads to a simple info page if implemented)

### Error Handling and Edge Cases
*   **Google OAuth Failure**: If the user cancels the Google login, or Google returns an error (e.g., invalid scope, network issue on Google's side), the application should redirect back to the **Login Screen (Error State)** with the generic "Login failed. Please try again." message. Internal logs should capture the specific Google error code.
*   **Backend Authentication Failure**: If the backend fails to validate the Google token or create a user session, the application should redirect back to the **Login Screen (Error State)**. Again, specific errors should be logged server-side.
*   **Network Issues (Client-side)**: If the client-side cannot reach the application server during the initial load, a browser-level network error will occur. For interactions post-load, a generic toast notification or inline message "Network connection lost. Please check your internet connection." should appear.
*   **Unauthorized Access**: If a user attempts to access a protected route without a valid session, they should be immediately redirected to the **Login Screen**.

### Transitions and Animations
*   **Screen Transitions**: Subtle fade-in/fade-out animations for full-page transitions (e.g., Login to Dashboard) to provide a smooth experience. (Leverage shadcn/ui defaults).
*   **Loading States**: Small, unobtrusive spinners or progress indicators for asynchronous operations (e.g., during OAuth redirect, button clicks).
*   **Error Messages**: Error messages should appear promptly and clearly, possibly with a subtle slide-in animation.