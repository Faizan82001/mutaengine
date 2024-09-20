import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)

class APILoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log incoming API requests, track API usage, and restrict access based on conditions.
    """

    def process_request(self, request):
        # Log request information
        logger.info(f"Incoming request: {request.method} {request.path} from IP: {self.get_client_ip(request)}")
        
        # Start time tracking to measure request processing time
        request.start_time = time.time()

    def process_response(self, request, response):
        # Calculate the duration of the request
        duration = time.time() - request.start_time

        # Log the request and response status
        logger.info(f"Request {request.method} {request.path} completed in {duration:.2f}s with status {response.status_code}")
        
        # Track API usage (simple example using session or token-based user identification)
        self.track_api_usage(request)
        
        return response

    def track_api_usage(self, request):
        # Example: track API usage by user (you can use tokens, sessions, or IP for tracking)
        user = request.user if request.user.is_authenticated else None
        if user:
            # Update user API usage count or store in logs (or a database)
            logger.info(f"User {user.username} made an API request.")
        else:
            logger.info(f"Unauthenticated request from IP: {self.get_client_ip(request)}")
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Restrict access to certain views (you can apply any custom restrictions here)
        restricted_ips = getattr(settings, 'RESTRICTED_IPS', [])
        if self.get_client_ip(request) in restricted_ips:
            return JsonResponse({'error': 'Access forbidden from your IP address.'}, status=403)

    def get_client_ip(self, request):
        # Retrieve client IP address, considering headers like X-Forwarded-For
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
