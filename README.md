### Short Documentation

#### Overview
This Django application handles the registration and payment process for courses using the Thawani payment gateway. It includes views for registering for a course, handling successful and canceled payments, and creating checkout sessions with the Thawani API.

#### Views

1. **register(request)**
    - Renders a registration form for available courses.
    - Handles form submission, saves the registration details, and initiates a payment session with Thawani.
    - Redirects the user to the Thawani payment URL or shows an error message if the session creation fails.

2. **cancel(request)**
    - Renders a cancellation page in case the payment process is unsuccessful or canceled.

3. **succeed(request)**
    - Renders a success page upon successful payment completion.

#### Helper Functions

- **create_checkout_session(registration)**
    - Creates a new checkout session with the Thawani API using the registration details.
    - Returns the session ID if successful, otherwise returns `None`.

#### Models

- **Course**
    - Represents a course that users can register for.
    
- **CourseRegistration**
    - Represents a user's registration for a course, including personal details and selected course information.

#### Configuration

- **THAWANI_API_KEY**
    - Replace this with your actual Thawani API key.

#### Notes

- Ensure to update the `success_url` and `cancel_url` in `create_checkout_session` function with the actual URLs for your success and cancellation pages.
- Handle the Thawani API key securely, and do not hardcode it in the codebase for production environments. Use environment variables or Django settings.
