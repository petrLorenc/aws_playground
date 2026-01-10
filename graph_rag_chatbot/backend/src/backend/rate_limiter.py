import time

from fastapi import HTTPException, Request, status

from backend.config import get_settings


class RateLimiter:
    """
    Simple in-memory global rate limiter using sliding window.
    Limits total requests to the backend regardless of client.
    For production, consider using Redis-based rate limiting.
    """

    def __init__(self):
        # Store all request timestamps globally
        self._requests: list[float] = []

    def _cleanup_old_requests(self, window_start: float) -> None:
        """Remove requests outside the current window."""
        self._requests = [ts for ts in self._requests if ts > window_start]

    async def check_rate_limit(self, request: Request) -> None:
        """
        Check if the request is within global rate limits.

        Args:
            request: The FastAPI request object

        Raises:
            HTTPException: If rate limit is exceeded
        """
        settings = get_settings()
        current_time = time.time()
        window_start = current_time - settings.rate_limit_window_seconds

        # Cleanup old requests
        self._cleanup_old_requests(window_start)

        # Check if limit exceeded
        request_count = len(self._requests)
        if request_count >= settings.rate_limit_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {settings.rate_limit_requests} requests per {settings.rate_limit_window_seconds} seconds.",
                headers={"Retry-After": str(settings.rate_limit_window_seconds)},
            )

        # Record this request
        self._requests.append(current_time)

    def get_remaining_requests(self) -> int:
        """Get the number of remaining requests in the current window."""
        settings = get_settings()
        current_time = time.time()
        window_start = current_time - settings.rate_limit_window_seconds

        # Cleanup old requests
        self._cleanup_old_requests(window_start)

        used_requests = len(self._requests)
        return max(0, settings.rate_limit_requests - used_requests)


# Global rate limiter instance
# No need for Sigleton pattern here as state is shared in this instance
rate_limiter = RateLimiter()
