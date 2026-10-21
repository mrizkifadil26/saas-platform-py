from datetime import datetime

from pydantic import BaseModel, EmailStr, SecretStr, field_validator

from iam.registration.domain.enums import RegistrationMethod, RegistrationStep
from iam.registration.domain.value_objects import RegistrationId


class StartEmailRegistrationBody(BaseModel):
    email: EmailStr
    password: SecretStr | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        password = value.get_secret_value()

        # TODO: add policy stuff here, can be tune up in the settings

        return value


class StartGoogleRegistrationBody(BaseModel):
    authorization_code: SecretStr


class VerifyEmailBody(BaseModel):
    verification_token: SecretStr


class RegistrationStartedResponse(BaseModel):
    registration_id: RegistrationId
    method: RegistrationMethod
    step: RegistrationStep
    expires_at: datetime
