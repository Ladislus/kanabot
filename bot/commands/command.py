from discord import Message, TextChannel, Client
from .commandelement import Element
from .commandoptions import Option
from .logger import Logger
from .utils import isCommand, is_owner
from config.globalconfig import GlobalConfig
from .commandlist import commandlist


class Command:
    _logger: Logger = Logger('COMMAND EXECUTION')
    _commands: dict = commandlist

    def __init__(self,
                 client: Client,
                 rawCommand: str,
                 name: str,
                 author: str,
                 channel: TextChannel,
                 argCount: int,
                 optionalArgCount: int,
                 args: dict):
        self._client: Client = client
        self._rawCommand: str = rawCommand
        self._name: str = name
        self._author: str = author
        self._channel: TextChannel = channel
        self._argCount: int = argCount
        self._optionalArgCount: int = optionalArgCount
        self._args: dict = args

    def __repr__(self) -> str:
        return f'Command: \n\
            \tRaw: {self._rawCommand}\n\
            \tName: {self._name}\n\
            \tAuthor: {self._author}\n\
            \tChannel: {self._channel.name}\n\
            \tArgCount: {str(self._argCount)}\n\
            \tOptionalArgCount: {str(self._optionalArgCount)}\n\
            \tArgs: {self._args}\n'

    async def execute(self):
        # TODO more tests
        # TODO Split into smaller methods
        if self._name not in Command._commands:
            Command._logger.log(f'Command "{self._name}" dosen\'t exist')
        else:
            command_infos: dict = Command._commands[self._name]

            if self._argCount < command_infos[Option.ARGUMENT_REQUIRED]:
                Command._logger.log(f'Command "{self._name}" requires {str(command_infos[Option.ARGUMENT_REQUIRED])}, only {str(self._argCount)} given')
            elif self._argCount > command_infos[Option.ARGUMENT_REQUIRED] and not command_infos[Option.VARARGS_SUPPORTED]:
                Command._logger.log(f'Command "{self._name}" requires {str(command_infos[Option.ARGUMENT_REQUIRED])}, but {str(self._argCount)} were given ({self._args})')
            else:
                # TODO Check named args
                elements: dict[Element, object] = self._retrieve_elements(command_infos[Option.ELEMENT_REQUIRED])
                await Command._commands[self._name][Option.FUNCTION](self._args, elements)
                Command._logger.log(f'{self._rawCommand} executed')

    def _retrieve_elements(self, command_elements: list[Element]) -> dict[Element, object]:
        elements: dict[Element, object] = {}
        # TODO check for other elements
        if Element.CHANNEL in command_elements:
            elements[Element.CHANNEL] = self._channel
        if Element.USERS in command_elements:
            elements[Element.USERS] = self._client.config.guild.members
        return elements

    @staticmethod
    def isValidCommand(msg: Message, globalCfg: GlobalConfig) -> bool:
        """
        Function to check if a message is a command, and if it's authorized
        :param msg: The message to check
        :param globalCfg: The configuration file
        :return: True if the message should be interpreted as a command, False otherwise
        """
        return globalCfg.activated and \
            isCommand(msg.content) and \
            msg.channel.name in globalCfg.channels and \
            (not globalCfg.adminRequired or (msg.author.id in globalCfg.admins or is_owner(msg.author)))
