# llm_emulator/protocols/discovery.py

import logging
import json
from typing import Dict, List

from .service import ServiceDefinition
from ...llm.base import LLMInterface
from ...llm.roles import LLMRole
from ...exceptions import ProtocolDiscoveryError

log = logging.getLogger("llm_emulator")


class ProtocolDiscoverer:
    """
    Responsible for discovering the details of a service by querying an LLM.
    """

    def __init__(self, llm_interface: LLMInterface):
        self.llm_interface = llm_interface

    def _build_discovery_prompt(self, service_name: str) -> List[Dict[str, str]]:
        """Builds the prompt to ask the LLM for service details."""
        system_prompt = (
            "You are a network protocol expert. Your task is to provide the "
            "standard details for a given network service name. Respond ONLY with a "
            "JSON object containing the following keys: 'port' (integer), "
            "'transport_protocol' (string, e.g., 'tcp' or 'udp'), "
            "'communication_type' (string, e.g., 'request-response' or 'interactive-stream'), "
            "and 'description' (a brief one-sentence description of the protocol). "
            "Do not include any other text, explanations, or markdown."
        )
        user_prompt = f"Provide the details for the '{service_name}' service."

        return [
            {"role": LLMRole.SYSTEM, "content": system_prompt},
            {"role": LLMRole.USER, "content": user_prompt},
        ]

    async def discover(self, service_name: str) -> ServiceDefinition:
        """
        Queries the LLM to discover protocol details and returns a
        ServiceDefinition object. Raises ProtocolDiscoveryError if discovery fails.
        """
        log.info(f"Discovering protocol details for '{service_name}'...")
        messages = self._build_discovery_prompt(service_name)

        raw_response = await self.llm_interface.generate_response(messages)

        try:
            # Clean the response to ensure it's valid JSON
            json_str = raw_response.strip().replace("```json", "").replace("```", "")
            llm_json = json.loads(json_str)

            # Strict check: Ensure a port was returned by the LLM.
            if "port" not in llm_json or not isinstance(llm_json.get("port"), int):
                raise ProtocolDiscoveryError(
                    f"LLM failed to provide a valid port for the '{service_name}' service. Response: {raw_response}"
                )

            return ServiceDefinition.from_llm_response(service_name, llm_json)
        except json.JSONDecodeError as e:
            log.error(
                f"Failed to decode JSON from LLM response for protocol discovery: {raw_response}"
            )
            raise ProtocolDiscoveryError(
                f"LLM returned invalid JSON for '{service_name}' discovery."
            ) from e
        except ProtocolDiscoveryError:
            # Re-raise the specific error to be caught by the caller
            raise
        except Exception as e:
            log.error(f"An unexpected error occurred during protocol discovery: {e}")
            raise ProtocolDiscoveryError(
                f"Could not create ServiceDefinition for '{service_name}'."
            ) from e
