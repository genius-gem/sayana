from chatbot.memory import ConversationMemory
from chatbot.rag import RAG
from chatbot.similarity import SimilarityChecker
from services.llm import call_llm


memory = ConversationMemory()

similarity = SimilarityChecker()

rag = RAG()


# ==========================================
# GREETING CHECK
# ==========================================

def is_greeting(question):

    greetings = [

        "hello",
        "hi",
        "hey",

        "good morning",
        "good afternoon",
        "good evening",

        "thanks",
        "thank you"
    ]

    return question.lower().strip() in greetings


# ==========================================
# GREETING RESPONSE
# ==========================================

def greeting_response():

    return """
Hello 👋

I'm SayanaBot.

I can help you with:

• Sayana Press
• Side Effects
• Self Injection
• Missed Injections
• Pregnancy
• Breastfeeding
• Family Planning

How can I help you today?
"""


# ==========================================
# MAIN CHAT FUNCTION
# ==========================================

def get_response(question):

    if not question.strip():

        return "Please enter a question."

    if is_greeting(question):

        return greeting_response()

    last_question = memory.last_user_question()

    if last_question:

        if similarity.is_similar(
            question,
            last_question
        ):

            return (
                "It looks like you're asking a very similar question.\n\n"
                "Could you ask about a different aspect of Sayana Press, "
                "or let me know what additional information you'd like?"
            )

    # Save user message

    memory.add_user_message(question)

    # Retrieve context

    rag_response = rag.generate_context(question)

    prompt = rag_response["prompt"]

    # Add conversation history

    history = memory.build_history()

    final_prompt = f"""
You are SayanaBot.

You are a trusted reproductive health assistant specializing in Sayana Press.

Use ONLY the provided context to answer.

If the answer is not in the knowledge base, say:

"I could not find that information in my knowledge base."

Avoid repeating the exact same wording when answering similar questions.

Conversation History:

{history}

--------------------------------------------------

{prompt}
"""

    answer = call_llm(final_prompt)

    memory.add_assistant_message(answer)

    return answer