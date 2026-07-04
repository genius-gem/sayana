document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("chat-form");
    const input = document.getElementById("question");
    const messages = document.getElementById("messages");

    function addMessage(sender, text) {

        const div = document.createElement("div");

        div.className = sender;

        div.innerHTML = `
            <strong>${sender === "user" ? "You" : "SayanaBot"}:</strong><br>
            ${text}
        `;

        messages.appendChild(div);

        messages.scrollTop = messages.scrollHeight;
    }

    form.addEventListener("submit", async (e) => {

        e.preventDefault();

        const question = input.value.trim();

        if (!question) return;

        addMessage("user", question);

        input.value = "";

        try {

            const response = await fetch("/chatbot/ask", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    message: question
                })

            });

            const data = await response.json();

            addMessage("assistant", data.answer);

        }

        catch (error) {

            console.error(error);

            addMessage(
                "assistant",
                "Sorry, I am unable to connect to the server."
            );

        }

    });

});