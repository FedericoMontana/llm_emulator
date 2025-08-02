# llm_emulator/llm/roles.py
from enum import Enum


class LLMRole(str, Enum):
    """
    Defines the standard roles in a chat conversation for an LLM.
    Using a proper Enum provides type safety and clarity.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
