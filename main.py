# main.py
import asyncio
import os
import argparse


from llm_emulator import (
    Emulator,
    EmulatorConfig,
    LiteLLMGateway,
    HookEvents,
)
from llm_emulator.utils.logger import setup_logger
from llm_emulator.utils.subscribers import create_logging_subscriber

# Configure logging
log = setup_logger()


async def main(service_name: str, instructions: str | None):
    """Main function to set up and run the emulator."""
    log.info(f"Starting LLM Emulator for service '{service_name}'.")

    # --- Configuration ---
    api_key = os.getenv("API_KEY")
    model_name = os.getenv("MODEL_NAME")

    if not api_key or not model_name:
        log.error("API_KEY or MODEL_NAME environment variable not set. Exiting.")
        return

    # Only create a config object if custom instructions are provided.
    config = None
    if instructions:
        config = EmulatorConfig(custom_instructions=instructions)

    # --- Emulator Setup ---
    llm_gateway = LiteLLMGateway(api_key=api_key, model=model_name)
    emulator = Emulator(
        service_name=service_name, llm_interface=llm_gateway, config=config
    )

    # --- Event Hook Subscriptions ---
    logging_subscriber = create_logging_subscriber(truncate_limit=200)

    def on_emulator_started(event_name, host, port, service):
        log.info(f"✨ Emulator started for service '{service}' on port {port}")
        log.info("Press Ctrl+C to stop.")

    emulator.hooks.subscribe(HookEvents.EMULATOR_STARTED, on_emulator_started)
    emulator.hooks.subscribe(
        HookEvents.EMULATOR_STOPPED, lambda event_name: log.info("🛑 Emulator stopped.")
    )
    for event_name in [
        HookEvents.CONNECTION_OPENED,
        HookEvents.CONNECTION_CLOSED,
        HookEvents.LLM_RESPONSE,
    ]:
        emulator.hooks.subscribe(event_name, logging_subscriber)

    # --- Run the Emulator ---
    try:
        await emulator.start()
        while True:
            await asyncio.sleep(3600)
    finally:
        await emulator.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the Universal LLM-Driven Service Emulator."
    )
    parser.add_argument(
        "service",
        type=str,
        help="The name of the service to emulate (e.g., 'http', 'shell').",
    )
    parser.add_argument(
        "-i",
        "--instructions",
        type=str,
        help="Optional custom instructions for the LLM.",
    )
    args = parser.parse_args()

    try:
        asyncio.run(main(service_name=args.service, instructions=args.instructions))
    except KeyboardInterrupt:
        log.info("\nShutdown requested by user.")
