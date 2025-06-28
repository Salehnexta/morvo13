"""
Example usage of error tracking in Morvo13.
"""

from app.core.error_tracking import (
    add_breadcrumb,
    capture_exception,
    capture_message,
    set_tag,
    set_user_context,
    track_errors,
)


# Example 1: Using the decorator for automatic error tracking
@track_errors("user_registration")
def register_user(email: str, password: str) -> None:  # type: ignore
    """Example function with automatic error tracking."""
    # This will automatically capture any exceptions
    if not email:
        raise ValueError("Email is required")

    # Add breadcrumbs for debugging
    add_breadcrumb(f"Registering user with email: {email}", category="auth")

    # Simulate registration logic
    print(f"User {email} registered successfully")


# Example 2: Manual error capturing
def process_payment(user_id: str, amount: float) -> None:
    """Example function with manual error tracking."""
    try:
        # Set user context for better error tracking
        set_user_context(user_id=user_id)

        # Set tags for filtering
        set_tag("operation", "payment")
        set_tag("amount_range", "high" if amount > 1000 else "low")

        # Add breadcrumb
        add_breadcrumb(f"Processing payment of ${amount}", category="payment")

        if amount < 0:
            raise ValueError("Amount cannot be negative")

        # Simulate payment processing
        print(f"Payment of ${amount} processed for user {user_id}")

    except Exception as e:
        # Manually capture the exception with extra context
        capture_exception(
            e, {"user_id": user_id, "amount": amount, "payment_method": "credit_card"}
        )
        raise


# Example 3: Capturing custom messages
def monitor_ai_agent_performance(agent_name: str, response_time: float) -> None:
    """Example of capturing performance metrics."""
    set_tag("agent", agent_name)

    if response_time > 10.0:
        # Capture a warning message
        capture_message(
            f"Agent {agent_name} slow response: {response_time}s",
            level="warning",
            extra_data={
                "agent_name": agent_name,
                "response_time": response_time,
                "threshold": 10.0,
            },
        )

    add_breadcrumb(f"Agent {agent_name} responded in {response_time}s", category="ai")


# Example 4: FastAPI endpoint with error tracking
from fastapi import HTTPException


def api_endpoint_example(user_id: str) -> dict[str, str]:
    """Example API endpoint with comprehensive error tracking."""
    try:
        # Set user context
        set_user_context(user_id=user_id)

        # Add operation breadcrumb
        add_breadcrumb("Starting API operation", category="api")

        # Simulate some business logic
        if user_id == "invalid":
            raise HTTPException(status_code=400, detail="Invalid user ID")

        # Success breadcrumb
        add_breadcrumb("API operation completed successfully", category="api")

        return {"status": "success", "user_id": user_id}

    except HTTPException:
        # Don't capture HTTP exceptions as errors (they're expected)
        add_breadcrumb("HTTP exception occurred", category="api", level="warning")
        raise

    except Exception as e:
        # Capture unexpected errors
        capture_exception(e, {"endpoint": "api_endpoint_example", "user_id": user_id})
        raise


# Example usage in your actual code:
if __name__ == "__main__":
    # These examples show how to use error tracking

    # Example 1: Automatic tracking
    try:
        register_user("test@example.com", "password123")
    except Exception as e:
        print(f"Caught: {e}")

    # Example 2: Manual tracking
    try:
        process_payment("user123", 500.0)
    except Exception as e:
        print(f"Caught: {e}")

    # Example 3: Performance monitoring
    monitor_ai_agent_performance("content_strategist", 12.5)

    # Example 4: API endpoint
    try:
        result = api_endpoint_example("user456")
        print(result)
    except Exception as e:
        print(f"Caught: {e}")
 