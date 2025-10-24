from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI):
    """
    Set up CORS (Cross-Origin Resource Sharing) middleware for the FastAPI application.
    
    This function configures CORS middleware to allow cross-origin requests
    from web browsers. It's particularly useful for development environments
    where the frontend and backend are running on different ports.
    
    Args:
        app (FastAPI): The FastAPI application instance to configure CORS for
    
    Configuration:
        - Origins: Allows requests from localhost on various ports
        - Credentials: Disabled for security (set to False)
        - Methods: Allows all HTTP methods (*)
        - Headers: Allows all request headers (*)
    
    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> setup_cors(app)
        
    Note:
        This is a convenience function for quick CORS setup. For more
        complex CORS requirements, consider using the MiddlewareManager
        class with custom configuration.
    """
    origins = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods="*",
        allow_headers="*",
    )