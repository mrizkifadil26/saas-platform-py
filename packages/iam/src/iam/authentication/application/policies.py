from datetime import timedelta


class AuthenticationPolicy:
    MAX_FAILURES = 5
    TIME_WINDOW_MINUTES = 15

    def ensure_not_locked(
        self,
        *,
        recent_failures: int,
    ) -> None:
        if recent_failures >= self.MAX_FAILURES:
            # TODO: raise too many authentication attempts error
            # raise TooManyAuthenticationAttemptsError()
            raise

    def failure_window(self) -> timedelta:
        return timedelta(minutes=self.TIME_WINDOW_MINUTES)
