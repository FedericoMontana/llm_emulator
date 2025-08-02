# llm_emulator/exceptions.py


class EmulatorError(Exception):
    """Base exception class for all custom errors in this library."""

    pass


class LLMConnectionError(EmulatorError):
    """Raised when there is an issue connecting to the LLM service."""

    pass


class LLMResponseError(EmulatorError):
    """Raised when the LLM returns an unexpected or invalid response."""

    pass


class ProtocolDiscoveryError(EmulatorError):
    """Raised when the LLM fails to provide necessary protocol details."""

    pass


class NetworkError(EmulatorError):
    """Raised for general network-related issues within the emulator."""

    pass
