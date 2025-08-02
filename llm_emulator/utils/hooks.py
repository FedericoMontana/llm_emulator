# llm_emulator/utils/hooks.py

from collections import defaultdict
import logging

log = logging.getLogger("llm_emulator")


class HookManager:
    """
    A simple hook (publish-subscribe) system for event handling.
    Allows parts of the system to be decoupled by subscribing to named events.
    """

    def __init__(self):
        self._callbacks = defaultdict(list)

    def subscribe(self, event_name: str, callback):
        """
        Subscribe a callback to a given event hook.

        Args:
            event_name (str): The name of the event (e.g., 'connection_opened').
            callback (callable): The function to call when the event is emitted.
                                 It will receive `event_name` as its first argument.
        """
        self._callbacks[event_name].append(callback)
        log.debug(f"Subscribed callback to hook '{event_name}'")

    def emit(self, event_name: str, *args, **kwargs):
        """
        Emit an event, calling all subscribed callbacks for that hook.

        Args:
            event_name (str): The name of the event to emit.
            *args, **kwargs: Arguments to pass to the callback functions.
        """
        log.debug(
            f"Emitting event for hook '{event_name}' with args: {args}, kwargs: {kwargs}"
        )
        for callback in self._callbacks[event_name]:
            try:
                # Pass the event_name as the first argument to the callback.
                # This enables the creation of generic subscribers.
                callback(event_name, *args, **kwargs)
            except Exception as e:
                log.error(
                    f"Error in hook subscriber for '{event_name}': {e}", exc_info=True
                )
