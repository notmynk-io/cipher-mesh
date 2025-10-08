document.addEventListener("DOMContentLoaded", () => {
    const messagesContainer = document.getElementById("messagesContainer");
    const messageInput = document.getElementById("messageInput");
    const sendButton = document.querySelector(".send-btn");

    const encryptionStatusEl = document.getElementById("encryptionStatus");
    const readReceiptEl = document.getElementById("readReceipt");
    const deleteAtEl = document.getElementById("deleteAt");

        const API_URL = "https://ciphermesh-backend.onrender.com"; // TODO: Replace this with your actual Render backend URL

    let messagesMap = new Map();

    async function fetchMessages() {
        try {
            const response = await fetch(`${API_URL}/messages/`);
            if (!response.ok) {
                throw new Error("Failed to fetch messages");
            }
            const messages = await response.json();
            messagesMap.clear();
            messages.forEach(msg => messagesMap.set(msg.id, msg));
            renderMessages(messages);
        } catch (error) {
            console.error("Error fetching messages:", error);
        }
    }

    function renderMessages(messages) {
        messagesContainer.innerHTML = "";
        messages.forEach(message => {
            const messageElement = createMessageElement(message);
            messagesContainer.appendChild(messageElement);
        });
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function createMessageElement(message) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message");
        messageDiv.dataset.messageId = message.id;

        messageDiv.innerHTML = `
            <img class="message-avatar" src="https://randomuser.me/api/portraits/women/5.jpg" />
            <div class="message-content">
                <div class="message-user">${message.author} <span class="message-time">${new Date(message.timestamp).toLocaleTimeString()}</span></div>
                <div class="message-text">${message.content}</div>
            </div>
        `;

        messageDiv.addEventListener("click", () => {
            displayMessageDetails(message.id);
        });

        return messageDiv;
    }

    function displayMessageDetails(messageId) {
        const message = messagesMap.get(messageId);
        if (message) {
            encryptionStatusEl.textContent = message.is_encrypted ? "On" : "Off";
            readReceiptEl.textContent = message.read_receipt || "Not read";
            deleteAtEl.textContent = message.delete_at ? new Date(message.delete_at).toLocaleString() : "Never";
        }
    }

    async function sendMessage() {
        const content = messageInput.value.trim();
        if (!content) {
            return;
        }

        const author = "Alice";

        try {
            const response = await fetch(`${API_URL}/messages/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ author, content, is_encrypted: false, read_receipt: null, delete_at: null }),
            });

            if (!response.ok) {
                throw new Error("Failed to send message");
            }

            const newMessage = await response.json();
            messagesMap.set(newMessage.id, newMessage);
            const messageElement = createMessageElement(newMessage);
            messagesContainer.appendChild(messageElement);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            messageInput.value = "";
        } catch (error) {
            console.error("Error sending message:", error);
        }
    }

    sendButton.addEventListener("click", sendMessage);
    messageInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    fetchMessages();
});
