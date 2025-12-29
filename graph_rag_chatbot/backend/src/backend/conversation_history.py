from interfaces.models import ChatMessage

class ConversationHistory:
    def __init__(self) -> None:
        self._histories: dict[str, list[ChatMessage]] = {}
        
    def add_message(self, conversation_id: str, message: ChatMessage) -> None:
        """Add a message to the conversation history."""
        if conversation_id not in self._histories:
            self._histories[conversation_id] = []
        self._histories[conversation_id].append(message)

    def get_history(self, conversation_id: str) -> list[ChatMessage]:
        """Retrieve the conversation history for a given conversation ID."""
        return self._histories.get(conversation_id, [])

conversation_history = ConversationHistory()