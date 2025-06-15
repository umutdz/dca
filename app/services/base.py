from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar

from app.schemas.base import BaseAPISerializer

RequestType = TypeVar("RequestType", bound=BaseAPISerializer)


class BaseAPIService(ABC):
    """Base interface for API service implementations"""

    @abstractmethod
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[RequestType] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to the API.

        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint path
            data (Optional[RequestType], optional): Request body for POST/PUT requests
            params (Optional[Dict[str, Any]], optional): Query parameters for GET requests

        Returns:
            Dict[str, Any]: Response data as dictionary

        Raises:
            ExceptionBase: If the request fails
        """

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Get the base URL for the API"""

    @property
    @abstractmethod
    def headers(self) -> Dict[str, str]:
        """Get the default headers"""
