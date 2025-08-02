# llm_emulator/utils/subscribers.py
import logging
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.connection import Session

log = logging.getLogger(__name__)


def create_logging_subscriber(truncate_limit: int | None = 100) -> Callable:
    """Factory to create a configurable logging subscriber."""

    def _log_event(event_name: str, *args, **kwargs):
        details = []
        for key, value in kwargs.items():
            if key == "session" and value is not None:
                session: "Session" = value
                details.append(f"session={session.session_id[:8]}")
            else:
                s_val = str(value)
                if truncate_limit and len(s_val) > truncate_limit:
                    s_val = s_val[:truncate_limit] + "..."
                details.append(f"{key}={s_val}")
        log.info(f"[{event_name.upper()}] - {', '.join(details)}")

    return _log_event
