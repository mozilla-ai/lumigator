from backend.settings import settings
from backend.tracking.mlflow import MLflowClientManager
from backend.tracking.tracking_interface import TrackingClientManager


class TrackingClientFactory:
    """Factory class to create tracking clients based on settings."""

    @staticmethod
    def get_tracking_client_manager() -> TrackingClientManager:
        if settings.TRACKING_BACKEND == settings.TrackingBackendType.MLFLOW:
            return MLflowClientManager(settings.TRACKING_BACKEND_URI)
        else:
            raise ValueError(f"Unsupported tracking backend: {settings.TRACKING_BACKEND}")


tracking_client_manager = TrackingClientFactory.get_tracking_client_manager()
