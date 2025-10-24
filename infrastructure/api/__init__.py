from .app import FastAPIApp
from .config import api_config

def create_progresser_api() -> FastAPIApp:
    """Factory function to create Progresser API."""
    app_manager = FastAPIApp(api_config)
    app_manager.setup()
    return app_manager

# Convenience instance
progresser_api = create_progresser_api()
app = progresser_api.app

__all__ = ["FastAPIApp", "create_progresser_api", "app", "api_config"]