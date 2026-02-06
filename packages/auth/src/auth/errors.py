class AuthError(Exception): ...


class EmailAlreadyRegistered(AuthError):
    pass


class InvalidCredentials(AuthError):
    pass


class UserInactive(AuthError):
    pass


class SessionNotFound(AuthError):
    pass


class SessionRevoked(AuthError):
    pass


class SessionExpired(AuthError):
    pass
