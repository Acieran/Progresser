from contextlib import asynccontextmanager

from fastapi import FastAPI
import logging
import uvicorn

from .config import api_config
from .routers import *
from .middlewhere import *


class FastAPIApp:
    """
     FastAPI wrapper for Progresser using composition.
     Integrates with your existing architecture.
     """

    def __init__(self, config=None):
        self.config = config or api_config

        # Compose managers
        self.routers = RouterManager()
        self.middleware = MiddlewareManager()

        # FastAPI instance (created on demand)
        self._app: FastAPI | None = None
        self.logger = logging.getLogger(__name__)


    def setup(self) -> None:
        """Set up the application with routers and middleware."""
        # Register your routers
        self.routers.register_router(tasks_router, prefix="/tasks")
        self.routers.register_router(users_router, prefix="/users")

        # Configure middleware
        self.middleware.add_cors(
            allow_origins=self.config.cors_origins,
            allow_methods=self.config.cors_methods,
            allow_credentials=False
        )

        if self.config.enable_request_logging:
            self.middleware.add_custom_middleware(LoggingMiddleware)


    @property
    def app(self) -> FastAPI:
        """Get or create the FastAPI instance."""
        if self._app is None:
            self._create_app()
        return self._app


    def _create_app(self) -> None:
        """Create FastAPI instance with lifespan."""

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup - you can initialize your existing services here
            self.logger.info(f"Starting {self.config.title}")

            # Your existing service initialization could go here
            # from core.application.tasks.task_manager import TaskManager
            # app.state.task_manager = TaskManager()

            yield

            # Shutdown
            self.logger.info(f"Shutting down {self.config.title}")

        self._app = FastAPI(
            title=self.config.title,
            version=self.config.version,
            description=self.config.description,
            debug=self.config.debug,
            lifespan=lifespan,
        )

        # Apply configurations
        self.middleware.apply_all(self._app)
        self.routers.mount_all(self._app, self.config.api_prefix)

        self.logger.info("Progresser API app created and configured")


    def start(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """Start the API server."""

        self.logger.info(f"Starting Progresser API on {host}:{port}")
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            **kwargs
        )


