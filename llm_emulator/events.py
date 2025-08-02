# llm_emulator/events.py


class HookEvents:
    """
    Defines the constant names for all available events in the emulator.
    Using these constants prevents typos and makes the code more maintainable.
    """

    EMULATOR_STARTED = "emulator_started"
    EMULATOR_STOPPED = "emulator_stopped"
    CONNECTION_OPENED = "connection_opened"
    CONNECTION_CLOSED = "connection_closed"

    MESSAGE_RECEIVED = "message_received"

    MESSAGE_SENT = "message_sent"
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
