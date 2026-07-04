from collections import deque


class ConversationMemory:

    def __init__(self, max_messages=10):

        self.messages = deque(maxlen=max_messages)

    # ------------------------------------

    def add_user_message(self, message):

        self.messages.append({
            "role": "user",
            "content": message.strip()
        })

    # ------------------------------------

    def add_assistant_message(self, message):

        self.messages.append({
            "role": "assistant",
            "content": message.strip()
        })

    # ------------------------------------

    def get_messages(self):

        return list(self.messages)

    # ------------------------------------

    def get_last_message(self):

        if self.messages:
            return self.messages[-1]

        return None

    # ------------------------------------

    def last_user_question(self):

        for message in reversed(self.messages):

            if message["role"] == "user":

                return message["content"]

        return None

    # ------------------------------------

    def build_history(self):

        if not self.messages:

            return ""

        history = []

        for message in self.messages:

            history.append(
                f"{message['role'].capitalize()}: {message['content']}"
            )

        return "\n".join(history)

    # ------------------------------------

    def clear(self):

        self.messages.clear()

    # ------------------------------------

    def __len__(self):

        return len(self.messages)