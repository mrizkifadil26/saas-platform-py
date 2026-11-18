from __future__ import annotations

from dataclasses import dataclass

from .password import PasswordHasher, PasswordPolicy
from .password.hasher import Argon2PasswordHasher
from .settings import Settings
from .tokens import JWTDecoder, JWTEncoder, SecureTokenGenerator, TokenHasher


@dataclass(frozen=True, slots=True)
class Container:
    token_generator: SecureTokenGenerator
    token_hasher: TokenHasher

    jwt_encoder: JWTEncoder
    jwt_decoder: JWTDecoder

    password_hasher: PasswordHasher
    password_policy: PasswordPolicy

    @classmethod
    def build(
        cls,
        settings: Settings,
    ) -> Container:
        token_generator = SecureTokenGenerator(
            default_bytes=settings.opaque_token_bytes,
        )

        token_hasher = TokenHasher(
            secret=settings.token_hash_secret.get_secret_value().encode(),
        )

        jwt_encoder = JWTEncoder(
            secret=settings.jwt_secret.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        )

        jwt_decoder = JWTDecoder(
            secret=settings.jwt_secret.get_secret_value(),
            algorithm=settings.jwt_algorithm,
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )

        password_hasher = Argon2PasswordHasher()
        password_policy = PasswordPolicy(
            min_length=settings.password.min_length,
            max_length=settings.password.max_length,
        )

        return cls(
            token_generator=token_generator,
            token_hasher=token_hasher,
            jwt_encoder=jwt_encoder,
            jwt_decoder=jwt_decoder,
            password_hasher=password_hasher,
            password_policy=password_policy,
        )
