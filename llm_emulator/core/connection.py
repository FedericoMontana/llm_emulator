# llm_emulator/core/connection.py
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, TYPE_CHECKING

from ..events import HookEvents
from ..llm.roles import LLMRole

if TYPE_CHECKING:
    from ..llm.base import LLMInterface
    from ..protocols.service import ServiceDefinition
    from ..core.config import EmulatorConfig
    from ..protocols.handler import ChatProtocolHandler
    from ..utils.hooks import HookManager

log = logging.getLogger(__name__)


class Session:
    """A data container for a single client connection's state."""

    def __init__(self, client_address: tuple, service_name: str):
        self.session_id = str(uuid.uuid4())
        self.client_address = client_address
        self.service_name = service_name
        self.history: List[Dict[str, Any]] = []
        self.is_active = True
        self.start_time = datetime.now(timezone.utc)

    def __repr__(self):
        return (
            f"<Session id={self.session_id} client={self.client_address} "
            f"service='{self.service_name}'>"
        )

    def get_history(self) -> List[Dict[str, Any]]:
        """Returns the full conversation history."""
        return self.history

    def add_to_history(self, role: LLMRole, content: str):
        """Adds a new message to the session's history."""
        self.history.append(
            {
                "role": role.value,
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )


class ConnectionHandler:
    """
    A "Session Conductor" that manages the active lifecycle of a single
    client connection.
    """

    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        llm_interface: "LLMInterface",
        service_def: "ServiceDefinition",
        config: "EmulatorConfig",
        hooks: "HookManager",
        protocol_handler: "ChatProtocolHandler",
    ):
        self.reader = reader
        self.writer = writer
        self.llm_interface = llm_interface
        self.service_def = service_def
        self.config = config
        self.hooks = hooks
        self.protocol_handler = protocol_handler
        self.session: Session | None = None

    async def manage_connection(self):
        """Manages the read/write loop for the client connection."""
        addr = self.writer.get_extra_info("peername")
        self.session = Session(client_address=addr, service_name=self.service_def.name)
        self.hooks.emit(HookEvents.CONNECTION_OPENED, session=self.session)

        try:
            # --- Initial Server-First Interaction ---
            initial_messages = self.protocol_handler.create_messages_for_llm(
                session=self.session
            )
            self.hooks.emit(
                HookEvents.LLM_REQUEST, session=self.session, messages=initial_messages
            )

            raw_llm_response = await self.llm_interface.generate_response(
                initial_messages
            )
            llm_response = self.protocol_handler.format_response_from_llm(
                raw_llm_response
            )

            self.hooks.emit(
                HookEvents.LLM_RESPONSE, session=self.session, response=llm_response
            )

            self.writer.write(llm_response.encode())
            await self.writer.drain()
            self.hooks.emit(
                HookEvents.MESSAGE_SENT,
                session=self.session,
                data=llm_response.encode(),
            )

            # Add the assistant's first message to the history.
            self.session.add_to_history(role=LLMRole.ASSISTANT, content=llm_response)

            # --- Main Loop for Subsequent Client Messages ---
            while self.session.is_active:
                data = await self.reader.read(4096)
                if not data:
                    break

                client_message = data.decode(errors="ignore")
                self.hooks.emit(
                    HookEvents.MESSAGE_RECEIVED, session=self.session, data=data
                )
                self.session.add_to_history(role=LLMRole.USER, content=client_message)

                messages = self.protocol_handler.create_messages_for_llm(
                    session=self.session
                )
                self.hooks.emit(
                    HookEvents.LLM_REQUEST, session=self.session, messages=messages
                )

                raw_llm_response = await self.llm_interface.generate_response(messages)
                llm_response = self.protocol_handler.format_response_from_llm(
                    raw_llm_response
                )

                self.hooks.emit(
                    HookEvents.LLM_RESPONSE, session=self.session, response=llm_response
                )

                self.session.add_to_history(
                    role=LLMRole.ASSISTANT, content=llm_response
                )
                self.writer.write(llm_response.encode())
                await self.writer.drain()
                self.hooks.emit(
                    HookEvents.MESSAGE_SENT,
                    session=self.session,
                    data=llm_response.encode(),
                )

        except (ConnectionResetError, BrokenPipeError) as e:
            log.warning(f"Connection lost for {self.session.client_address}: {e}")
        except Exception as e:
            log.error(
                f"An error occurred in connection handler for {self.session.client_address}: {e}",
                exc_info=True,
            )
        finally:
            log.info(f"Closing connection for {self.session.client_address}")
            self.writer.close()
            await self.writer.wait_closed()
            if self.session:
                self.session.is_active = False
            self.hooks.emit(HookEvents.CONNECTION_CLOSED, session=self.session)
