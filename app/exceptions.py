# exceptions.py: Custom application exceptions and handlers
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str):
        self.message = message

class EntityNotFoundException(AppException):
    """Raised when a database record is not found."""
    pass

class AccessDeniedException(AppException):
    """Raised when a user tries to access a resource they do not own."""
    pass

class AuthenticationFailedException(AppException):
    """Raised when authentication credentials are invalid or missing."""
    pass

class DuplicateEntityException(AppException):
    """Raised when creating an entity that violates uniqueness constraints."""
    pass


# Global handlers to translate custom Python exceptions into standard HTTP responses

def register_exception_handlers(app: FastAPI):
    """
    Registers global exception handlers with the FastAPI app instance.
    This demonstrates exception customization and middleware-like intercepts.
    """
    
    @app.exception_handler(EntityNotFoundException)
    async def entity_not_found_handler(request: Request, exc: EntityNotFoundException):
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "NOT_FOUND", "message": exc.message},
        )

    @app.exception_handler(AccessDeniedException)
    async def access_denied_handler(request: Request, exc: AccessDeniedException):
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "FORBIDDEN", "message": exc.message},
        )

    @app.exception_handler(AuthenticationFailedException)
    async def authentication_failed_handler(request: Request, exc: AuthenticationFailedException):
        return JSONResponse(
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
            content={"success": False, "error": "UNAUTHORIZED", "message": exc.message},
        )

    @app.exception_handler(DuplicateEntityException)
    async def duplicate_entity_handler(request: Request, exc: DuplicateEntityException):
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "BAD_REQUEST", "message": exc.message},
        )
