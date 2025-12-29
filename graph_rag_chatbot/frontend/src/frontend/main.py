#!/usr/bin/env python3
import asyncio
import json
import httpx

from nicegui import ui

from interfaces.models import ChatMessage, ChatRequest, MessageRole, StreamChunk
from interfaces.endpoints import APIEndpoints
from config import get_settings

class BackendClient:
    """Client for communicating with the backend service."""
    
    def __init__(self, base_url: str = get_settings().backend_url, api_key: str = get_settings().api_key) -> None:
        print("Using BackendClient with URL:", base_url)
        self.base_url = base_url
        self.api_key = api_key
        self.conversation_id: str | None = None
    
    async def astream(self, question: str):
        """Stream responses from the backend."""
        request = ChatRequest(
            message=ChatMessage(role=MessageRole.USER, content=question),
            conversation_id=self.conversation_id,
            stream=True,
        )
        
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}{APIEndpoints.BACKEND_PREFIX}{APIEndpoints.BACKEND_CHAT_STREAM}",
                    json=request.model_dump(),
                    headers={"X-API-Key": self.api_key},
                    timeout=60.0,
                ) as response:
                    # Store conversation ID from response header
                    if "X-Conversation-ID" in response.headers:
                        self.conversation_id = response.headers["X-Conversation-ID"]
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        yield ChatMessage(
                            role=MessageRole.ASSISTANT,
                            content=f"Error: {response.status_code} - {error_text.decode()}"
                        )
                        return
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            chunk = StreamChunk(**data)
                            if chunk.error:
                                yield ChatMessage(
                                    role=MessageRole.ASSISTANT,
                                    content=f"Error: {chunk.error}"
                                )
                                return
                            if chunk.content:
                                yield ChatMessage(
                                    role=MessageRole.ASSISTANT,
                                    content=chunk.content
                                )
                            if chunk.done:
                                return
            except httpx.ConnectError:
                yield ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content="Error: Could not connect to backend. Is it running?"
                )
            except Exception as e:
                yield ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=f"Error: {str(e)}"
                )


class FakeLLMGenerator:
    """Fallback generator when backend is not available."""
    
    async def astream(self, question: str):
        chunks = [
            "Hello! ",
            "This is a simulated response ",
            "from a fake LLM generator. ",
            "How can I assist you today?"
        ]
        for chunk in chunks:
            await asyncio.sleep(0.4)
            yield ChatMessage(role=MessageRole.ASSISTANT, content=chunk)


def root():
    # Use BackendClient by default, can switch to FakeLLMGenerator for testing
    llm = BackendClient()

    async def send() -> None:
        question = text.value
        text.value = ''

        with message_container:
            ui.chat_message(text=question, name='You', sent=True)
            response_message = ui.chat_message(name='Bot', sent=False)
            spinner = ui.spinner(type='dots')

        response = ''
        async for chunk in llm.astream(question):
            response += chunk.content
            with response_message.clear():
                ui.html(response, sanitize=False)
            ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
        message_container.remove(spinner)

    message_container = ui.column().classes('w-full max-w-2xl mx-auto flex-grow items-stretch')

    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            placeholder = 'message'
            text = ui.input(placeholder=placeholder).props('rounded outlined input-class=mx-3') \
                .classes('w-full self-center').on('keydown.enter', send)
        ui.markdown('simple chat app built with [NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary') \
            .classes('[&_a]:text-inherit [&_a]:no-underline [&_a]:font-medium')


ui.run(root, title='Chat with Me...')