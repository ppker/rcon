"""BattlEye RCon client."""

from ipaddress import IPv4Address
from logging import getLogger
from socket import SOCK_DGRAM
from typing import Callable, Union

from rcon.battleye.proto import RESPONSE_TYPES
from rcon.battleye.proto import Command
from rcon.battleye.proto import Header
from rcon.battleye.proto import LoginRequest
from rcon.battleye.proto import Request
from rcon.battleye.proto import Response
from rcon.battleye.proto import ServerMessage
from rcon.client import BaseClient
from rcon.exceptions import WrongPassword


__all__ = ['Client']


Host = Union[str, IPv4Address]
MessageHandler = Callable[[ServerMessage], None]


def log_message(server_message: ServerMessage) -> None:
    """Default handler, logging the server message."""

    getLogger('Server message').info(server_message.message)


class Client(BaseClient, socket_type=SOCK_DGRAM):
    """BattlEye RCon client."""

    def __init__(
            self, *args,
            message_handler: MessageHandler = log_message,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._handle_server_message = message_handler

    def _receive(self, max_length: int) -> Response:
        """Receives a packet."""
        data = self._socket.recv(max_length)[:7]
        header = Header.from_bytes(data)
        return RESPONSE_TYPES[header.type].from_bytes(header, data[7:])

    def receive(self, max_length: int = 4096) -> Response:
        """Receives a message."""
        while isinstance(response := self._receive(max_length), ServerMessage):
            self._handle_server_message(response)

        return response

    def communicate(self, request: Request) -> Response:
        """Logs the user in."""
        with self._socket.makefile('wb') as file:
            file.write(bytes(request))

        return self.receive()

    def login(self, passwd: str) -> bool:
        """Logs the user in."""
        if not self.communicate(LoginRequest.from_passwd(passwd)).success:
            raise WrongPassword()

        return True

    def run(self, command: str, *args: str) -> str:
        """Executes a command."""
        return self.communicate(Command.from_command(command, *args)).message
