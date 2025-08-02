# llm_emulator/llm/mocks/mock_gateway.py

import logging
from typing import List, Dict

from ..base import LLMInterface
from ...exceptions import LLMResponseError

log = logging.getLogger("llm_emulator")


class MockLLMGateway(LLMInterface):
    """
    A mock LLM gateway for testing. It now handles both discovery and chat.
    This mock is designed to emulate an HTTP server.
    """

    def _get_discovery_response(self) -> str:
        """Returns the JSON response for the discovery phase."""
        return """
        {
            "port": 8080,
            "transport_protocol": "tcp",
            "communication_type": "request-response",
            "description": "A standard HTTP server."
        }
        """

    def _get_chat_response(self) -> str:
        """Returns the HTML response for the chat phase."""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>LLM Mock Server</title>
</head>
<body>
    <h1>Hello World from the Mock LLM!</h1>
    <p>This is an interactive page.</p>
    <input type="text" id="myText" value="Initial Text">
    <button onclick="updateContent('Button 1')">Button 1</button>
    <button onclick="updateContent('Button 2')">Button 2</button>
    <button onclick="updateContent('Button 3')">Button 3</button>
    <div id="output"></div>
    <script>
        function updateContent(buttonName) {
            const text = document.getElementById('myText').value;
            const output = document.getElementById('output');
            output.innerHTML = `You clicked <strong>${buttonName}</strong> and the textbox contained: <em>${text}</em>`;
        }
    </script>
</body>
</html>
"""
        # Construct a well-formed HTTP response
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(html_content)}\r\n"
            "Connection: close\r\n\r\n"
            f"{html_content}"
        )
        return response

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        if not messages:
            raise LLMResponseError("Received an empty message list.")

        # Check if this is a discovery request
        system_prompt = messages[0].get("content", "").lower()
        if "network protocol expert" in system_prompt:
            log.info("MockLLMGateway: Detected discovery request. Returning JSON.")
            return self._get_discovery_response()

        # Otherwise, assume it's a chat request
        log.info("MockLLMGateway: Detected chat request. Returning HTML page.")
        return self._get_chat_response()
