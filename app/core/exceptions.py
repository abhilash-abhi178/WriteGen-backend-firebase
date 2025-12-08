"""
Custom authentication exceptions
Location: app/core/exceptions.py
"""

from fastapi import HTTPException, status


class AuthenticationException(HTTPException):
    """Base authentication exception"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class InvalidCredentialsException(AuthenticationException):
    """Raised when credentials are invalid"""
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(detail)


class UserNotFoundException(HTTPException):
    """Raised when user is not found"""
    def __init__(self, detail: str = "User not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class UserAlreadyExistsException(HTTPException):
    """Raised when trying to create user with existing email"""
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {email} already exists"
        )


class InvalidTokenException(AuthenticationException):
    """Raised when token is invalid"""
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(detail)


class TokenExpiredException(AuthenticationException):
    """Raised when token has expired"""
    def __init__(self):
        super().__init__("Token has expired")


class InsufficientPermissionsException(HTTPException):
    """Raised when user lacks required permissions"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class AccountInactiveException(AuthenticationException):
    """Raised when user account is inactive"""
    def __init__(self):
        super().__init__("User account is inactive")
