import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import AuthService
from app.schemas.user import (
    RegisterRequest,
    LoginRequest,
    ChangePasswordRequest,
)
from app.core.exceptions import ExceptionBase
from app.core.error_codes import ErrorCode
from app.core.jwt import JWTManager


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def auth_service(mock_db):
    return AuthService(mock_db)


@pytest.fixture
def mock_user_repository():
    with patch("app.services.auth.PostgresUserRepository") as mock:
        instance = mock.return_value
        instance.exists = AsyncMock()
        instance.create = AsyncMock()
        instance.filter_one = AsyncMock()
        instance.get = AsyncMock()
        instance.update = AsyncMock()
        yield instance


@pytest.fixture
def mock_jwt_manager():
    with patch("app.services.auth.JWTManager") as mock:
        instance = mock.return_value
        instance.create_access_token.return_value = "test_access_token"
        instance.create_refresh_token.return_value = "test_refresh_token"
        instance.verify_token.return_value = {"sub": "1", "email": "test@example.com", "is_active": True}
        yield instance


class TestAuthService:
    @pytest.mark.asyncio
    async def test_register_success(self, auth_service, mock_user_repository):
        # Arrange
        request = RegisterRequest(email="test@example.com", password="password123")
        mock_user_repository.exists.return_value = False
        mock_user_repository.create.return_value = MagicMock(
            id=1, email="test@example.com", is_active=True
        )

        # Act
        response = await auth_service.register(request)

        # Assert
        assert response.id == 1
        assert response.email == "test@example.com"
        assert response.is_active is True
        mock_user_repository.exists.assert_called_once_with(email=request.email)
        mock_user_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_exists(self, auth_service, mock_user_repository):
        # Arrange
        request = RegisterRequest(email="test@example.com", password="password123")
        mock_user_repository.exists.return_value = True

        # Act & Assert
        with pytest.raises(ExceptionBase) as exc_info:
            await auth_service.register(request)
        assert exc_info.value.code == ErrorCode.USER_ALREADY_EXISTS.code

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service, mock_user_repository):
        # Arrange
        request = LoginRequest(email="test@example.com", password="password123")
        mock_user = MagicMock(
            id=1,
            email="test@example.com",
            is_active=True,
            password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQNxKJxGqG8y"  # hashed "password123"
        )
        mock_user_repository.filter_one.return_value = mock_user

        # Create real JWT tokens
        jwt_manager = JWTManager()
        token_data = {
            "sub": str(mock_user.id),
            "email": mock_user.email,
            "is_active": mock_user.is_active
        }
        expected_access_token = jwt_manager.create_access_token(token_data)
        expected_refresh_token = jwt_manager.create_refresh_token(token_data)

        # Mock verify_password to return True
        with patch("app.services.auth.verify_password", return_value=True):
            # Act
            response = await auth_service.login(request)

            # Assert
            assert response.access_token == expected_access_token
            assert response.refresh_token == expected_refresh_token
            mock_user_repository.filter_one.assert_called_once_with(email=request.email)

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, auth_service, mock_user_repository):
        # Arrange
        request = LoginRequest(email="test@example.com", password="wrongpassword")
        mock_user_repository.filter_one.return_value = None

        # Act & Assert
        with pytest.raises(ExceptionBase) as exc_info:
            await auth_service.login(request)
        assert exc_info.value.code == ErrorCode.INVALID_CREDENTIALS.code

    @pytest.mark.asyncio
    async def test_get_user_success(self, auth_service, mock_user_repository):
        # Arrange
        jwt_manager = JWTManager()
        token_data = {
            "sub": "1",
            "email": "test@example.com",
            "is_active": True
        }
        token = jwt_manager.create_access_token(token_data)
        mock_user = MagicMock(id=1, email="test@example.com", is_active=True)
        mock_user_repository.get.return_value = mock_user

        # Act
        response = await auth_service.get_user(token)

        # Assert
        assert response.id == 1
        assert response.email == "test@example.com"
        assert response.is_active is True
        mock_user_repository.get.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_invalid_token(self, auth_service):
        # Arrange
        token = "invalid_token"

        # Act & Assert
        with pytest.raises(ExceptionBase) as exc_info:
            await auth_service.get_user(token)
        assert exc_info.value.code == ErrorCode.INVALID_CREDENTIALS.code

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, auth_service, mock_user_repository):
        # Arrange
        jwt_manager = JWTManager()
        token_data = {
            "sub": "1",
            "email": "test@example.com",
            "is_active": True
        }
        token = jwt_manager.create_refresh_token(token_data)
        mock_user = MagicMock(id=1, email="test@example.com", is_active=True)
        mock_user_repository.get.return_value = mock_user

        # Act
        response = await auth_service.refresh_token(token)

        # Assert
        assert response.access_token == jwt_manager.create_access_token(token_data)
        assert response.refresh_token == jwt_manager.create_refresh_token(token_data)
        mock_user_repository.get.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_change_password_success(self, auth_service, mock_user_repository):
        # Arrange
        jwt_manager = JWTManager()
        token_data = {
            "sub": "1",
            "email": "test@example.com",
            "is_active": True
        }
        token = jwt_manager.create_access_token(token_data)
        request = ChangePasswordRequest(old_password="oldpass123", new_password="newpass123")
        mock_user = MagicMock(
            id=1,
            email="test@example.com",
            password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQNxKJxGqG8y"  # hashed "oldpass123"
        )
        mock_user_repository.get.return_value = mock_user

        # Mock verify_password to return True
        with patch("app.services.auth.verify_password", return_value=True):
            # Act
            response = await auth_service.change_password(token, request)

            # Assert
            assert response.success is True
            mock_user_repository.get.assert_called_once_with(1)
            mock_user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_invalid_old_password(self, auth_service, mock_user_repository):
        # Arrange
        jwt_manager = JWTManager()
        token_data = {
            "sub": "1",
            "email": "test@example.com",
            "is_active": True
        }
        token = jwt_manager.create_access_token(token_data)
        request = ChangePasswordRequest(old_password="wrongpass", new_password="newpass123")
        mock_user = MagicMock(
            id=1,
            email="test@example.com",
            password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQNxKJxGqG8y"  # hashed "oldpass123"
        )
        mock_user_repository.get.return_value = mock_user

        # Mock verify_password to return False
        with patch("app.services.auth.verify_password", return_value=False):
            # Act & Assert
            with pytest.raises(ExceptionBase) as exc_info:
                await auth_service.change_password(token, request)
            assert exc_info.value.code == ErrorCode.INVALID_CREDENTIALS.code
