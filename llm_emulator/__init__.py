# llm_emulator/__init__.py

"""
Universal LLM-Driven Service Emulator

This __init__.py file exposes the core, user-facing components of the library,
allowing for cleaner and more convenient imports.
"""

# Core components for running the emulator
from .core.emulator import Emulator
from .core.config import EmulatorConfig

# Main LLM gateway for production use
from .llm.litellm_gateway import LiteLLMGateway

# Mock gateways for testing and development
from .llm.mocks.mock_gateway import MockLLMGateway
from .llm.mocks.simple_mock_gateway import SimpleMockGateway

# Event constants for subscribing to hooks
from .events import HookEvents

# Expose custom exceptions
from .exceptions import (
    EmulatorError,
    LLMConnectionError,
    LLMResponseError,
    ProtocolDiscoveryError,
    NetworkError,
)

# Define what gets imported with 'from llm_emulator import *'
__all__ = [
    "Emulator",
    "EmulatorConfig",
    "LiteLLMGateway",
    "MockLLMGateway",
    "SimpleMockGateway",
    "HookEvents",
    "EmulatorError",
    "LLMConnectionError",
    "LLMResponseError",
    "ProtocolDiscoveryError",
    "NetworkError",
]
