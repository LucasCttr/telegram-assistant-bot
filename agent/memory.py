from langchain_classic.memory import ConversationBufferWindowMemory

memories = {}

def get_memory(user_id: int):
    if user_id not in memories:
        memories[user_id] = ConversationBufferWindowMemory(
            k=5,
            memory_key="chat_history",
            return_messages=True
        )
    return memories[user_id]