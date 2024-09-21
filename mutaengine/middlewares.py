import logging
from time import time

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        logger.info(f"Incoming request: {request.method} {request.path}")

        start_time = time()
        response = self.get_response(request)
        end_time = time()
        logger.info(f"Outgoing response: {response.status_code} for {request.method} {request.path}\nProcess Time: {end_time-start_time} seconds")

        return response
