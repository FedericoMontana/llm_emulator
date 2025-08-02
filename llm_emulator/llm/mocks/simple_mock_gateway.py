# llm_emulator/llm/mocks/simple_mock_gateway.py

import logging
import random
from typing import List, Dict

from ..base import LLMInterface
from ...exceptions import LLMResponseError
from ..roles import LLMRole

log = logging.getLogger("llm_emulator")


class SimpleMockGateway(LLMInterface):
    """
    A very simple mock gateway that now handles both discovery and chat.
    It returns one of three random messages during chat.
    """

    def _get_discovery_response(self) -> str:
        """Returns the JSON response for the discovery phase."""
        return """
        {
            "port": 9999,
            "transport_protocol": "tcp",
            "communication_type": "interactive-stream",
            "description": "A simple echo and random message server."
        }
        """

    def _get_chat_response(self, messages: List[Dict[str, str]]) -> str:
        """Returns a random response for the chat phase."""
        last_user_message = "nothing"
        for msg in reversed(messages):
            if msg.get("role") == LLMRole.USER:
                last_user_message = msg.get("content", "nothing").strip()
                break

        options = [
            f"You said: {last_user_message}. That's interesting!",
            f"I see you wrote '{last_user_message}'. Acknowledged.",
            f"Why did you send '{last_user_message}'? I am pondering this.",
        ]
        return random.choice(options)

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        print(messages)
        if not messages:
            raise LLMResponseError("Received an empty message list.")

        # Check if this is a discovery request
        system_prompt = messages[0].get("content", "").lower()
        if "network protocol expert" in system_prompt:
            log.info("SimpleMockGateway: Detected discovery request. Returning JSON.")
            return self._get_discovery_response()

        # Otherwise, assume it's a chat request
        log.info("SimpleMockGateway: Detected chat request. Returning random message.")
        return self._get_chat_response(messages)
