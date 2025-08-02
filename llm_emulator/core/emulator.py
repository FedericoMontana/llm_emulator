# llm_emulator/core/emulator.py
import asyncio
import logging
from typing import Optional, TYPE_CHECKING

from ..events import HookEvents
from ..llm.base import LLMInterface
from .protocols.discovery import ProtocolDiscoverer
from .protocols.handler import ChatProtocolHandler
from ..core.config import EmulatorConfig
from ..utils.hooks import HookManager
from .connection import ConnectionHandler

if TYPE_CHECKING:
    from .protocols.service import ServiceDefinition


log = logging.getLogger(__name__)


class Emulator:
    """The main emulator class that orchestrates the service."""

    def __init__(
        self,
        service_name: str,
        llm_interface: LLMInterface,
        config: Optional[EmulatorConfig] = None,
    ):
        """
        Initializes the Emulator.

        Args:
            service_name: The name of the service to emulate (e.g., 'http').
            llm_interface: An instance of a class that implements LLMInterface.
            config: An optional configuration object. If None, default settings are used.
        """
        if not service_name:
            raise ValueError("service_name cannot be empty.")
        self.service_name = service_name
        self.llm_interface = llm_interface
        # If no config is provided, create a default one.
        self.config = config or EmulatorConfig()
        self.server: asyncio.Server | None = None
        self.hooks = HookManager()
        self.service_def: "ServiceDefinition" | None = None

    async def start(self):
        """Starts the emulator server."""
        log.info(f"Discovering protocol details for '{self.service_name}'...")
        discoverer = ProtocolDiscoverer(self.llm_interface)
        self.service_def = await discoverer.discover(self.service_name)
        log.info(f"Discovered service details: {self.service_def}")

        port = self.config.port or self.service_def.port
        host = "0.0.0.0"

        protocol_handler = ChatProtocolHandler(
            service_def=self.service_def, config=self.config
        )

        async def handle_connection(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ):
            """Callback to handle a new client connection."""
            handler = ConnectionHandler(
                reader=reader,
                writer=writer,
                llm_interface=self.llm_interface,
                service_def=self.service_def,
                config=self.config,
                hooks=self.hooks,
                protocol_handler=protocol_handler,
            )
            await handler.manage_connection()

        self.server = await asyncio.start_server(handle_connection, host, port)
        self.hooks.emit(
            HookEvents.EMULATOR_STARTED,
            host=host,
            port=port,
            service=self.service_def.name,
        )

    async def stop(self):
        """Stops the emulator server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.hooks.emit(HookEvents.EMULATOR_STOPPED)
