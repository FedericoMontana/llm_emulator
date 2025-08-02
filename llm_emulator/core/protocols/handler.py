# llm_emulator/protocols/handler.py

import string
from typing import List, Dict, TYPE_CHECKING
from ...core.config import EmulatorConfig
from ...llm.roles import LLMRole

if TYPE_CHECKING:
    from ..protocols.service import ServiceDefinition
    from ...core.connection import Session


class ChatProtocolHandler:
    """
    A "Prompt Formatter" responsible for translating the state of a session
    into a structured list of messages suitable for an LLM, and for formatting
    the LLM's response before it's sent to the client.
    """

    # Centralized constant for the initial connection message.
    _INITIAL_DEFAULT_USER_MESSAGE = "[A client has just connected]"

    def __init__(self, service_def: "ServiceDefinition", config: EmulatorConfig):
        self.service_def = service_def
        self.config = config

    def _build_system_prompt(self) -> str:
        """Constructs the system prompt from the service definition and user config."""
        prompt_parts = [
            f"You are an expert system emulating a '{self.service_def.name}' network server.",
            f"Protocol Description: {self.service_def.description}.",
            "Your primary directive is to behave exactly like a real server for this protocol.",
            "Follow these rules strictly:",
            "1. **Protocol Compliance:** Your responses must be 100% compliant with the "
            f"'{self.service_def.name}' protocol. Generate only the raw server response, "
            "including all necessary headers, status lines, and body content.",
            "2. **No Explanations:** Do not add any commentary or text outside of the protocol's "
            "mandated response. Under no circumstances should you break character.",
            "3. **Maintain Coherence:** Ensure the session is coherent. For example, if emulating a "
            "shell, file listings must be consistent. If emulating HTTP, generate an initial page "
            "and then subsequent content that logically follows user interaction.",
            f"4. **Initial Connection:** The first user message you receive will be "
            f"'{self._INITIAL_DEFAULT_USER_MESSAGE}'. This is your signal to generate the initial "
            "welcome message a real server would provide.",
            "5. **Character Encoding:** Your entire response must consist only of standard, "
            "printable ASCII or UTF-8 characters.",
        ]

        if self.config.custom_instructions:
            prompt_parts.extend(
                [
                    "\n---",
                    "# User-Provided Instructions",
                    str(self.config.custom_instructions),
                    "---",
                ]
            )

        return "\n".join(prompt_parts)

    def create_messages_for_llm(self, session: "Session") -> List[Dict[str, str]]:
        """
        Creates the list of messages to be sent to the LLM. It always includes
        the system prompt and an initial user message, followed by the
        rest of the conversation history.
        """
        system_prompt = self._build_system_prompt()
        messages = [
            {"role": LLMRole.SYSTEM.value, "content": system_prompt},
            # Always include the initial user message, as you instructed.
            {"role": LLMRole.USER.value, "content": self._INITIAL_DEFAULT_USER_MESSAGE},
        ]

        history = session.get_history()

        # Truncate and add the rest of the actual conversation history.
        if (
            self.config.max_history_tokens
            and len(history) > self.config.max_history_tokens
        ):
            history = history[-self.config.max_history_tokens :]

        messages.extend(history)

        return messages

    def format_response_from_llm(self, response: str) -> str:
        """
        Formats the raw response from the LLM before it is sent to the
        client or added to the history.
        """
        # First, remove any non-printable characters.
        printable_chars = set(string.printable)
        sanitized_response = "".join(filter(lambda x: x in printable_chars, response))

        # For interactive protocols, enforce the prompt format intelligently.
        if self.service_def.communication_type == "interactive-stream":
            # 1. Normalize the response by stripping trailing whitespace.
            content = sanitized_response.rstrip()

            # 2. If the LLM included a prompt character, remove it for clean processing.
            if content.endswith("$"):
                content = content[:-1].rstrip()

            # 3. Build the final response.
            if content:
                # If there's content, ensure it ends with a newline before the prompt.
                return content + "\n$ "
            else:
                # If there's no content, just send the prompt.
                return "$ "

        return sanitized_response
