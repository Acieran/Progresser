# infrastructure/api/middleware/logging.py
from fastapi import Request
import time
import logging


class LoggingMiddleware:
    """
    ASGI middleware for logging HTTP requests and responses.
    
    This middleware intercepts all HTTP requests and logs information about
    the request method, URL path, response status code, and processing time.
    It follows the ASGI middleware pattern and can be used with any ASGI
    application, including FastAPI.
    
    Attributes:
        app: The ASGI application instance being wrapped
        logger (logging.Logger): Logger instance for this middleware
    
    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> app.add_middleware(LoggingMiddleware)
    """
    def __init__(self, app):
        """
        Initialize the logging middleware.
        
        Args:
            app: The ASGI application instance to wrap with logging
        """
        self.app = app
        self.logger = logging.getLogger(__name__)

    async def __call__(self, request: Request, call_next):
        """
        Process the request and log information about it.
        
        This method implements the ASGI middleware interface. It:
        1. Records the start time of the request
        2. Calls the next middleware/handler in the chain
        3. Calculates the processing time
        4. Logs the request details and response information
        
        Args:
            request (Request): The incoming HTTP request object
            call_next: The next middleware/handler in the ASGI chain
            
        Returns:
            Response: The HTTP response from the application
            
        Note:
            The middleware logs information in the format:
            "METHOD /path - STATUS_CODE - PROCESSING_TIME" (e.g.,
            "GET /api/v1/tasks - 200 - 0.045s")
        """
        # Your existing logging logic
        start_time = time.time()

        # Call next middleware/route handler
        response = await call_next(request)

        process_time = time.time() - start_time
        self.logger.info(
            f"{request.method} {request.url.path} - {response.status_code} "
            f"- {process_time:.3f}s"
        )

        return response