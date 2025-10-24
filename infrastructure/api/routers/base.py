from fastapi import APIRouter
from typing import Dict
import logging


class RouterManager:
    """
    Manages all API routers for Progresser.
    
    This class provides centralized management of FastAPI routers, allowing
    for organized registration and mounting of API endpoints. It maintains
    a registry of routers with their associated prefixes and handles the
    mounting process to the main FastAPI application.
    
    Attributes:
        _routers (Dict[str, APIRouter]): Dictionary mapping router prefixes
            to their corresponding APIRouter instances
        logger (logging.Logger): Logger instance for this class
    
    Example:
        >>> manager = RouterManager()
        >>> manager.register_router(tasks_router, prefix="/tasks")
        >>> manager.register_router(users_router, prefix="/users")
        >>> manager.mount_all(app, api_prefix="/api/v1")
    """

    def __init__(self):
        """
        Initialize the router manager.
        
        Creates an empty router registry and sets up logging.
        """
        self._routers: Dict[str, APIRouter] = {}
        self.logger = logging.getLogger(__name__)

    def register_router(self, router: APIRouter, prefix: str = "") -> None:
        """
        Register a router with an optional prefix.
        
        This method adds a router to the internal registry with its associated
        prefix. The prefix will be used when mounting the router to the main
        FastAPI application.
        
        Args:
            router (APIRouter): The FastAPI router instance to register
            prefix (str, optional): URL prefix for the router. If empty string,
                the router will be mounted at the root level. Defaults to "".
        
        Example:
            >>> from fastapi import APIRouter
            >>> tasks_router = APIRouter()
            >>> manager.register_router(tasks_router, prefix="/tasks")
            
        Note:
            If a router with the same prefix already exists, it will be
            overwritten. Use unique prefixes to avoid conflicts.
        """
        self._routers[prefix] = router
        self.logger.info(f"Registered router with prefix: '{prefix}'")

    def mount_all(self, app, api_prefix: str = "") -> None:
        """
        Mount all registered routers to the FastAPI application.
        
        This method iterates through all registered routers and mounts them
        to the main FastAPI application with their configured prefixes.
        The final URL path for each router will be the combination of
        api_prefix and the router's individual prefix.
        
        Args:
            app: The FastAPI application instance to mount routers to
            api_prefix (str, optional): Global API prefix to prepend to all
                router prefixes. Defaults to "".
        
        Example:
            >>> # With api_prefix="/api/v1" and router prefix="/tasks"
            >>> # Final URL will be "/api/v1/tasks"
            >>> manager.mount_all(app, api_prefix="/api/v1")
            
        Note:
            This method should be called after all routers have been
            registered and before the application is started.
        """
        for prefix, router in self._routers.items():
            full_prefix = f"{api_prefix}{prefix}" if api_prefix else prefix
            app.include_router(router, prefix=full_prefix)
            self.logger.debug(f"Mounted router at prefix: {full_prefix}")

    @property
    def count(self) -> int:
        """
        Get the number of registered routers.
        
        Returns:
            int: The total number of routers currently registered
            
        Example:
            >>> manager = RouterManager()
            >>> manager.register_router(router1, "/tasks")
            >>> manager.register_router(router2, "/users")
            >>> print(manager.count)
            2
        """
        return len(self._routers)