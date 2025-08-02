# Universal LLM-Driven Service Emulator

A powerful Python library that leverages Large Language Models (LLMs) to dynamically emulate a wide range of network services. Instead of hardcoding protocol logic, this library uses an LLM to understand and generate protocol-compliant responses on the fly, making it incredibly flexible for network testing, security research, and educational purposes.

## Core Features

* **Dynamic Service Emulation:** Emulate common network services like HTTP, SMTP, Shell, or FTP just by specifying their names.

* **LLM-Powered Protocol Discovery:** The library queries the LLM to discover the correct port and communication patterns for any given service.

* **Stateful Session Management:** Each client connection is managed in a separate, stateful session, allowing for coherent, multi-step conversations.

* **Configurable Behavior:** Easily configure internal behaviors, such as conversation history length, and inject custom instructions to guide the LLM's responses.

* **Extensible Event System:** Subscribe to hooks for key events (`CONNECTION_OPENED`, `MESSAGE_RECEIVED`, `LLM_RESPONSE`, etc.) to monitor and react to the emulator's internal state.

* **Provider Agnostic:** Uses `litellm` to connect to over 100 different LLM providers, ensuring maximum flexibility.

## How It Works

The emulator follows a simple but powerful workflow:

1. **Discovery:** When you start the emulator for a service (e.g., "smtp"), it first asks the LLM for the service's standard details, such as its default port and communication type.

2. **Listening:** It opens a server on the discovered port and waits for client connections.

3. **Session Handling:** For each connection, it creates a `Session` and manages the conversation.

4. **Prompt Generation:** The `ChatProtocolHandler` constructs a detailed prompt for the LLM, including a system message with instructions, the conversation history, and the latest client message.

5. **Response Formatting:** The handler formats the raw response from the LLM to ensure it is clean and protocol-compliant before sending it back to the client.

## Installation

```
pip install litellm
# Add other dependencies as needed

```

## Quick Start

The following example demonstrates how to start an emulator for a simple shell service.

```
# example.py
import asyncio
import os
from llm_emulator.core.emulator import Emulator
from llm_emulator.core.config import EmulatorConfig
from llm_emulator.llm.litellm_gateway import LiteLLMGateway
from llm_emulator.utils.logger import setup_logging

# Configure logging
log = setup_logging()

async def main():
    # Ensure your LLM provider's API key is set as an environment variable
    # For example: export OPENAI_API_KEY="your-key"
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        log.error("API key not found in environment variables.")
        return

    # 1. Configure the emulator's behavior
    config = EmulatorConfig(
        max_history_tokens=10,
        custom_instructions="Emulate a friendly, helpful Linux shell. The root filesystem should contain standard directories."
    )

    # 2. Choose and instantiate the LLM gateway
    llm_gateway = LiteLLMGateway(api_key=api_key, model="gpt-4-turbo")

    # 3. Create the Emulator instance
    emulator = Emulator(
        service_name="shell",
        llm_interface=llm_gateway,
        config=config
    )

    # 4. Start the emulator and run forever
    try:
        await emulator.start()
        while True:
            await asyncio.sleep(3600)
    finally:
        await emulator.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Shutdown requested by user.")

```

You can then connect to the running service using a client like `telnet` or `nc`:

```
telnet localhost 514

```

## Future Work

This library is under active development. The next major architectural improvement planned is:

* **Protocol Factory:** While the `ChatProtocolHandler` is excellent for generic services, we plan to introduce a factory pattern. This will allow for the creation of service-specific handlers (e.g., a dedicated `FTProtocolHandler`) that can manage complex, multi-port protocols like FTP more robustly, while still falling back to the universal handler for unknown or simple services.

## License

This project is licensed under the MIT License.