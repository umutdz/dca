import base64
from typing import Any, Dict, Literal, Optional, TypeVar

import requests

from app.core.error_codes import ErrorCode
from app.core.exceptions import ExceptionBase
from app.middleware.logging import default_logger
from app.schemas.base import BaseAPISerializer
from app.services.base import BaseAPIService

RequestType = TypeVar("RequestType", bound=BaseAPISerializer)
AuthType = Literal["basic", "bearer", "api_key"]


class APIService(BaseAPIService):
    """
    Generic API service implementation that can be used for different providers.
    Each provider should extend this class and override the necessary properties.
    """

    def __init__(
        self,
        base_url: str,
        auth_type: AuthType = "basic",
        auth_username: Optional[str] = None,
        auth_password: Optional[str] = None,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        """
        Initialize the API service.

        Args:
            base_url (str): Base URL for the API
            auth_type (AuthType): Type of authentication to use
            auth_username (Optional[str]): Username for basic auth
            auth_password (Optional[str]): Password for basic auth
            api_key (Optional[str]): API key for api_key auth
            bearer_token (Optional[str]): Token for bearer auth
            timeout (int): Request timeout in seconds
            extra_headers (Optional[Dict[str, str]]): Additional headers to include
        """
        self._base_url = base_url
        self._auth_type = auth_type
        self._auth_username = auth_username
        self._auth_password = auth_password
        self._api_key = api_key
        self._bearer_token = bearer_token
        self._timeout = timeout

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[RequestType] = None,
        params: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
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

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self.headers(extra_headers)
        request_data = data.model_dump() if data else {}

        # Log outgoing request
        default_logger.info(
            "Outgoing API request",
            method=method,
            url=url,
            path=endpoint,
            headers=headers,
            query_params=params,
            body=request_data,
        )

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data.model_dump_json() if data else None,
                params=params,
                timeout=self._timeout,
            )

            # Log response
            default_logger.info(
                "API response received",
                method=method,
                url=url,
                path=endpoint,
                status_code=response.status_code,
                response=response.json(),
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            error_response = response.json() if response.content else {}
            error_message = error_response.get("error", str(e))

            default_logger.error(
                "API request failed",
                method=method,
                url=url,
                path=endpoint,
                status_code=response.status_code,
                error=error_message,
                response=error_response,
            )

            if error_response.get("error"):
                raise ExceptionBase(ErrorCode.API_ERROR, description=error_message)
            raise ExceptionBase(ErrorCode.API_ERROR, description=str(e))

    @property
    def base_url(self) -> str:
        return self._base_url

    def headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get headers based on auth type and extra headers"""
        headers = {
            "Content-Type": "application/json",
        }

        # Add auth header based on auth type
        if self._auth_type == "basic" and self._auth_username and self._auth_password:
            auth_value = f"{self._auth_username}:{self._auth_password}"
            encoded_auth = base64.b64encode(auth_value.encode("utf-8")).decode("utf-8")
            headers["Authorization"] = f"Basic {encoded_auth}"
        elif self._auth_type == "bearer" and self._bearer_token:
            headers["Authorization"] = f"Bearer {self._bearer_token}"
        elif self._auth_type == "api_key" and self._api_key:
            headers["X-API-Key"] = self._api_key

        # Add extra headers
        if extra_headers:
            headers.update(extra_headers)

        return headers
