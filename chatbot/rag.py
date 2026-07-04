"""
rag.py

Retrieval-Augmented Generation (RAG) Pipeline
"""

from chatbot.retriever import Retriever
from chatbot.prompt_templates import PromptTemplates


class RAG:

    def __init__(self):

        self.retriever = Retriever()

    # ----------------------------------------------------

    def retrieve_context(self, question, top_k=5):
        """
        Retrieve relevant chunks from the knowledge base.
        """

        results = self.retriever.retrieve(
            query=question,
            top_k=top_k
        )

        return results

    # ----------------------------------------------------

    def build_context(self, retrieved_chunks):
        """
        Convert retrieved chunks into a single context string.
        """

        context = []

        for chunk in retrieved_chunks:

            context.append(
                f"""
Category: {chunk['category']}

Title: {chunk['title']}

Content:
{chunk['content']}
"""
            )

        return "\n\n".join(context)

    # ----------------------------------------------------

    def build_prompt(self, question, retrieved_chunks):
        """
        Build the final prompt sent to the LLM.
        """

        context = self.build_context(retrieved_chunks)

        prompt = PromptTemplates.build_prompt(
            context=context,
            question=question
        )

        return prompt

    # ----------------------------------------------------

    def generate_context(self, question):
        """
        Complete RAG pipeline before calling the LLM.
        """

        chunks = self.retrieve_context(question)

        prompt = self.build_prompt(
            question,
            chunks
        )

        return {
            "question": question,
            "chunks": chunks,
            "prompt": prompt
        }


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    rag = RAG()

    response = rag.generate_context(
        "Can breastfeeding mothers use Sayana Press?"
    )

    print("=" * 80)
    print(response["prompt"])