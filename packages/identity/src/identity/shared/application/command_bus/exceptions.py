from .contracts import Command


class CommandHandlerNotFound(Exception):
    def __init__(
        self,
        command_type: type[Command],
    ) -> None:
        super().__init__(
            f"No handler registered for command {command_type.__name__}",
        )

        self.command_type = command_type


class CommandHandlerAlreadyRegistered(Exception):
    def __init__(
        self,
        command_type: type[Command],
    ) -> None:
        super().__init__(
            f"A handler is already registered for command {command_type.__name__}",
        )

        self.command_type = command_type
