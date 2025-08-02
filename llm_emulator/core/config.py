# llm_emulator/core/config.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class EmulatorConfig:
    """
    Configuration for the emulator's behavior.
    """

    port: Optional[int] = None
    max_history_tokens: int = 20
    custom_instructions: Optional[str] = None
