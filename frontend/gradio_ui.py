"""Gradio-based temporary front-end for local development.

This module is **NOT** meant for production use. It can be safely deleted
once a proper front-end (e.g. React/Next.js) replaces it.

Usage:
    poetry run python -m frontend.gradio_ui  # assumes FastAPI on localhost:8000

Environment variables:
    MORVO_BACKEND_URL   Override FastAPI chat endpoint (default: http://localhost:8000/v1/chat)
    MORVO_GRADIO_PORT   Port to expose the UI on (default: 3001)
    MORVO_GRADIO_HOST   Interface to bind to (default: 0.0.0.0)
"""
from __future__ import annotations

import os
import uuid

import gradio as gr
import httpx

# Base backend URL (e.g., http://localhost:8000/v1)
BACKEND_BASE_URL = os.getenv("MORVO_BACKEND_URL", "http://localhost:8000/v1")

# Chat endpoint path (v1/chat/message)
BACKEND_MESSAGE_ENDPOINT = f"{BACKEND_BASE_URL.rstrip('/')}/chat/message"

# Diagnostics endpoint path (v1/diagnostics)
BACKEND_DIAGNOSTICS_ENDPOINT = f"{BACKEND_BASE_URL.rstrip('/')}/diagnostics"

after_request_headers = {"Content-Type": "application/json"}


async def talk(message: str, history: list[tuple[str, str]]) -> str:  # noqa: ANN401
    """Send the user's message to the FastAPI backend and return the answer."""
    headers = {"x-correlation-id": str(uuid.uuid4())}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            BACKEND_MESSAGE_ENDPOINT,
            json={"client_id": str(uuid.uuid4()), "content": message},
            headers=headers | after_request_headers,  # type: ignore[operator]
        )
        response.raise_for_status()
        data = response.json()
        return data.get("content", "[No response text]")


def main() -> None:  # pragma: no cover – manual script
    with gr.Blocks(title="Morvo Prototype UI") as demo:
        gr.Markdown("""# Morvo Prototype UI

This temporary interface covers the *full* developer journey:

1. **Chat** with the AI assistant
2. **Diagnostics** – verify DB, OpenAI, and CrewAI connectivity

Delete this file once your production front-end is ready.
""")

        with gr.Tab("Chat"):
            gr.ChatInterface(
                fn=talk,
                title="Morvo Chat",
                description="Ask anything about Saudi marketing 👋",
            )

        with gr.Tab("Diagnostics"):
            run_button = gr.Button("Run Diagnostics", variant="primary")
            diag_output = gr.JSON(label="Diagnostics Result")

            async def run_diagnostics() -> dict:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get(BACKEND_DIAGNOSTICS_ENDPOINT)
                    resp.raise_for_status()
                    return resp.json()

            run_button.click(run_diagnostics, outputs=diag_output)

    demo.launch(
        server_port=int(os.getenv("MORVO_GRADIO_PORT", "3001")),
        server_name=os.getenv("MORVO_GRADIO_HOST", "0.0.0.0"),
        show_api=False,
        share=False,
    )


if __name__ == "__main__":  # pragma: no cover – manual launch
    main() 