from collections.abc import Mapping


class HTTPErrorRegistry:
    def __init__(
        self,
        *mappings: Mapping[type[Exception], HTTPError],
    ) -> None:
        errors: dict[type[Exception], HTTPError] = {}

        for mapping in mappings:
            for exception_type, error in mapping.items():
                if exception_type in errors:
                    raise ValueError(f"Duplicate HTTP error mapping for {exception_type.__name__}")

                errors[exception_type] = error

        self._errors = MappingProxyType(errors)

    def resolve(
        self,
        exc: Exception,
    ) -> HTTPError | None:
        for exception_type in type(exc).__mro__:
            error = self._errors.get(exception_type)

            if error is not None:
                return error

        return None
