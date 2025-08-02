# llm_emulator/llm/base.py

from abc import ABC, abstractmethod
from typing import List, Dict


class LLMInterface(ABC):
    """
    Abstract base class for LLM gateways.
    Defines the contract for how the emulator interacts with an LLM.
    """

    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Generates a response from the LLM based on a structured list of messages.

        Args:
            messages: A list of message dictionaries, where each dictionary
                      has a "role" and "content" key.

        Returns:
            The LLM's response as a string.
        """
        pass
