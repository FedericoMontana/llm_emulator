# llm_emulator/protocols/service.py

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ServiceDefinition:
    """
    A structured representation of an emulated network service's properties.
    """

    name: str
    port: int
    transport_protocol: str = "tcp"
    communication_type: str = "unknown"
    description: str = ""
    raw_details: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_llm_response(
        cls, service_name: str, llm_json: Dict[str, Any]
    ) -> "ServiceDefinition":
        """
        Factory method to create a ServiceDefinition instance from a parsed
        LLM JSON response.
        """
        return cls(
            name=service_name,
            port=llm_json.get("port"),
            transport_protocol=llm_json.get("transport_protocol", "tcp"),
            communication_type=llm_json.get("communication_type", "unknown"),
            description=llm_json.get(
                "description", f"A standard {service_name} server."
            ),
            raw_details=llm_json,
        )
