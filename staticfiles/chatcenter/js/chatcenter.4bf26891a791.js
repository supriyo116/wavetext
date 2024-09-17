let chatSocket;
let currentReceiver = '';

// Function to start the WebSocket connection for private chat
function startChat(receiverUsername) {
    if (!receiverUsername) {
        console.error('Receiver username is missing!');
        return;
    }

    if (chatSocket) {
        chatSocket.close();
    }

    chatSocket = new WebSocket(
    `wss://${window.location.host}/ws/chat/private/${receiverUsername}/`
);


    chatSocket.onopen = function(e) {
        console.log('WebSocket connection opened with', receiverUsername);
    };

    chatSocket.onmessage = function(e) {
        try {
            const data = JSON.parse(e.data);
            console.log('Message received:', data);
            displayMessage(data.sender, data.message, data.timestamp);
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    };

    chatSocket.onclose = function(e) {
        console.error('WebSocket closed:', e);
        if (e.code !== 1000) {
            console.log('Attempting to reconnect in 5 seconds...');
            setTimeout(() => startChat(currentReceiver), 5000);
        }
    };

    chatSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };

    currentReceiver = receiverUsername;
}

// Ensure WebSocket connection is established before sending messages
function sendMessage() {
    const messageInput = document.querySelector('#chat-message-input');
    const message = messageInput.value.trim();

    if (!message) {
        console.error('Message is empty.');
        return;
    }

    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(JSON.stringify({
            'message': message,
            'receiver': currentReceiver
        }));
        messageInput.value = ''; // Clear the input after sending the message
    } else {
        console.error('WebSocket is not open or message is empty.');
        startChat(currentReceiver); // Attempt to reconnect if WebSocket is not open
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Handle contact clicks to initiate private chat
    document.querySelectorAll('#contact-list a').forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const receiverUsername = this.dataset.roomName;
            if (receiverUsername) {
                startChat(receiverUsername);  // Start WebSocket for the selected contact
                loadChatHistory(receiverUsername); // Load chat history for the selected contact
            } else {
                console.error('Receiver username is missing!');
            }
        });
    });

    // Attach event listener to the send button
    const sendButton = document.querySelector('#send-button');
    if (sendButton) {
        sendButton.addEventListener('click', function (e) {
            sendMessage(); // Send the message when the send button is clicked
        });
    } else {
        console.error('Send button not found.');
    }

    // Allow sending messages by pressing "Enter"
    const messageInput = document.querySelector('#chat-message-input');
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage(); // Send the message when "Enter" is pressed
                e.preventDefault(); // Prevent form submission
            }
        });
    } else {
        console.error('Message input field not found.');
    }
});

// Function to load private chat history from the server
function loadChatHistory(receiverUsername) {
    fetch(`/chatcenter/history/${receiverUsername}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const chatLog = document.querySelector('#chat-log');
            if (chatLog) {
                chatLog.innerHTML = ''; // Clear previous chat log

                data.messages.forEach(msg => {
                    displayMessage(msg.sender, msg.message, msg.timestamp); // Display each message
                });

                // Scroll to the bottom of the chat log
                chatLog.scrollTop = chatLog.scrollHeight;
            } else {
                console.error('Chat log element not found.');
            }
        })
        .catch(err => console.error('Error loading chat history:', err));
}

// Function to display a private message in the chat window
function displayMessage(sender, message, timestamp) {
    const chatLog = document.querySelector('#chat-log');
    if (chatLog) {
        const messageElement = `
            <div class="media mb-2">
                <div class="media-body">
                    <p class="bg-light p-2 rounded">${message}</p>
                    <small class="text-muted d-block">${sender}</small>
                    <small class="text-muted">${timestamp}</small>
                </div>
            </div>
        `;
        chatLog.innerHTML += messageElement;
        chatLog.scrollTop = chatLog.scrollHeight; // Scroll to the latest message
    } else {
        console.error('Chat log element not found.');
    }
}

function updateNotifications() {
    fetch('/chatcenter/notifications/recent-messages/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Fetched messages:', data); // Debug line to check data

            const dropdownMenu = document.querySelector('#notificationDropdown .dropdown-menu');
            if (!dropdownMenu) {
                console.error('Dropdown menu not found.');
                return;
            }

            dropdownMenu.innerHTML = ''; // Clear existing notifications

            // Loop through messages and add them to the dropdown
            data.messages.forEach(msg => {
                const messageElement = `
                    <a class="dropdown-item" href="#">
                        <strong>${msg.sender}</strong>: ${msg.message}
                        <small class="text-muted d-block">${msg.timestamp}</small>
                    </a>
                `;
                dropdownMenu.innerHTML += messageElement;
            });

            // Update the badge count
            const badge = document.querySelector('#notificationDropdown .badge');
            if (badge) {
                badge.textContent = data.messages.length;
            } else {
                console.error('Badge element not found.');
            }
        })
        .catch(error => console.error('Error fetching notifications:', error));
}

// Call this function on page load and when new messages are received
document.addEventListener('DOMContentLoaded', function() {
    updateNotifications();

    // Optionally, you can set an interval to update notifications periodically
    setInterval(updateNotifications, 60000); // Update every 60 seconds
});

