# infrastructure/api/middleware/base.py
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging


class MiddlewareManager:
    """
    Manages all middleware for Progresser API.
    
    This class provides a centralized way to configure and apply middleware
    to the FastAPI application. It supports both built-in middleware (like CORS)
    and custom middleware classes.
    
    Attributes:
        _middleware_stack (List[Tuple]): Internal stack storing middleware
            configurations. Each tuple contains middleware type and configuration.
        logger (logging.Logger): Logger instance for this class
    
    Example:
        >>> manager = MiddlewareManager()
        >>> manager.add_cors(allow_origins=["http://localhost:3000"])
        >>> manager.add_custom_middleware(MyCustomMiddleware)
        >>> manager.apply_all(app)
    """

    def __init__(self):
        """
        Initialize the middleware manager.
        
        Creates an empty middleware stack and sets up logging.
        """
        self._middleware_stack = []
        self.logger = logging.getLogger(__name__)

    def add_cors(
            self,
            allow_origins: List[str] = None,
            allow_methods: List[str] = None,
            allow_headers: List[str] = None,
            allow_credentials: bool = False
    ) -> None:
        """
        Add CORS (Cross-Origin Resource Sharing) middleware.
        
        This method configures CORS middleware to handle cross-origin requests
        from web browsers. It allows the API to be accessed from different
        domains, which is essential for frontend applications.
        
        Args:
            allow_origins (List[str], optional): List of allowed origin URLs.
                Use ["*"] to allow all origins (not recommended for production).
                Defaults to ["*"].
            allow_methods (List[str], optional): List of allowed HTTP methods.
                Use ["*"] to allow all methods. Defaults to ["*"].
            allow_headers (List[str], optional): List of allowed request headers.
                Use ["*"] to allow all headers. Defaults to ["*"].
            allow_credentials (bool, optional): Whether to allow credentials
                (cookies, authorization headers) in cross-origin requests.
                Defaults to False.
        
        Note:
            CORS middleware is essential for web applications that need to
            make requests to the API from a different domain than the API server.
        """
        cors_config = {
            "allow_origins": allow_origins or ["*"],
            "allow_methods": allow_methods or ["*"],
            "allow_headers": allow_headers or ["*"],
            "allow_credentials": allow_credentials,
        }
        self._middleware_stack.append(("cors", cors_config))
        self.logger.info("CORS middleware configured")

    def add_custom_middleware(self, middleware_class: callable, **options) -> None:
        """
        Add custom middleware to the application.
        
        This method allows adding custom middleware classes that implement
        the ASGI middleware interface. Custom middleware can be used for
        authentication, logging, rate limiting, and other cross-cutting concerns.
        
        Args:
            middleware_class (callable): The middleware class to add. Must
                implement the ASGI middleware interface (accept app, return
                new ASGI app).
            **options: Additional keyword arguments to pass to the middleware
                constructor.
        
        Example:
            >>> manager.add_custom_middleware(
            ...     AuthenticationMiddleware,
            ...     secret_key="my-secret-key",
            ...     token_expiry=3600
            ... )
        
        Note:
            Middleware is applied in the order it's added. The first middleware
            added will be the outermost layer.
        """
        self._middleware_stack.append(("custom", middleware_class, options))
        self.logger.info(f"Custom middleware added: {middleware_class.__name__}")

    def apply_all(self, app) -> None:
        """
        Apply all configured middleware to the FastAPI application.
        
        This method iterates through the middleware stack and applies each
        middleware to the FastAPI application instance. It handles both
        built-in middleware (like CORS) and custom middleware.
        
        Args:
            app: The FastAPI application instance to apply middleware to.
        
        Note:
            This method should be called after all middleware has been
            configured and before the application is started. The middleware
            will be applied in the order they were added to the stack.
        """
        for middleware in self._middleware_stack:
            if middleware[0] == "cors":
                app.add_middleware(CORSMiddleware, **middleware[1])
            elif middleware[0] == "custom":
                app.add_middleware(middleware[1], **middleware[2])

        self.logger.info(f"Applied {len(self._middleware_stack)} middleware")