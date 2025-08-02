# llm_emulator/llm/litellm_gateway.py

import logging
from typing import List, Dict, Any, Optional
import litellm

from .base import LLMInterface
from ..exceptions import LLMConnectionError, LLMResponseError

log = logging.getLogger("llm_emulator")

# To prevent litellm from logging too verbosely by default
# litellm.set_verbose = False


class LiteLLMGateway(LLMInterface):
    """
    The production-ready LLM gateway that uses the litellm library.
    It accepts optional keyword arguments to control completion parameters like temperature.
    """

    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs: Any):
        """
        Initializes the gateway.

        Args:
            model: The model name to use for completions (e.g., 'gpt-4o').
            api_key: The API key, if required. Often set via environment variables.
            **kwargs: Any other keyword arguments (e.g., temperature, max_tokens)
                      to be passed directly to the litellm.acompletion call.
        """
        self.model = model
        self.api_key = api_key
        # Store all other keyword arguments to be passed to the completion call
        self.completion_params = kwargs
        log.debug(
            f"Initialized LiteLLMGateway with model '{self.model}' "
            f"and completion params: {self.completion_params}"
        )

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        log.debug(f"Sending request to litellm with model '{self.model}'.")
        try:
            # Unpack the stored completion params directly into the call
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                api_key=self.api_key,
                **self.completion_params,
            )

            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content

            raise LLMResponseError("LLM response was empty or malformed.")

        except Exception as e:
            log.error(f"An error occurred while communicating with litellm: {e}")
            raise LLMConnectionError(
                f"Failed to get a response from litellm: {e}"
            ) from e
