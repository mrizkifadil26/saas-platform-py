from datetime import timedelta
from typing import Final

from iam.shared.application.throttling.policy import ThrottleRule

from .contexts import EmailChallengeThrottleContext
from .util import hash_identifier

START_EMAIL_REGISTRATION_THROTTLE: Final = (
    ThrottleRule[EmailChallengeThrottleContext](
        namespace="registration.start.email",
        limit=5,
        window=timedelta(hours=1),
        key=lambda ctx: hash_identifier(ctx.email.value),
    ),
    ThrottleRule[EmailChallengeThrottleContext](
        namespace="registration.start.ip",
        limit=20,
        window=timedelta(hours=1),
        key=lambda ctx: hash_identifier(ctx.ip_address),
    ),
)

RESEND_EMAIL_VERIFICATION_THROTTLE: Final = (
    ThrottleRule[EmailChallengeThrottleContext](
        namespace="registration.resend.registration",
        limit=3,
        window=timedelta(minutes=15),
        key=lambda ctx: hash_identifier(str(ctx.registration_id)),
    ),
    ThrottleRule[EmailChallengeThrottleContext](
        namespace="registration.resend.email",
        limit=5,
        window=timedelta(hours=1),
        key=lambda ctx: hash_identifier(ctx.email.value),
    ),
    ThrottleRule[EmailChallengeThrottleContext](
        namespace="registration.resend.ip",
        limit=20,
        window=timedelta(hours=1),
        key=lambda ctx: hash_identifier(ctx.ip_address),
    ),
)

RESEND_EMAIL_VERIFICATION_COOLDOWN = timedelta(minutes=1)
