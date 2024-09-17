let groupChatSocket;
let currentGroup = '';

// Function to start the WebSocket connection for group chat
function startGroupChat(groupName) {
    if (!groupName) {
        console.error('Group name is missing!');
        return;
    }

    if (groupChatSocket) {
        groupChatSocket.close();
    }

    groupChatSocket = new WebSocket(
        `ws://${window.location.host}/ws/chat/group/${groupName}/`
    );

    groupChatSocket.onopen = function(e) {
        console.log('WebSocket connection opened with', groupName);
    };

    groupChatSocket.onmessage = function(e) {
        try {
            const data = JSON.parse(e.data);
            console.log('Message received:', data);
            displayMessage(data.sender, data.message, data.timestamp);
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    };

    groupChatSocket.onclose = function(e) {
        console.error('WebSocket closed:', e);
        if (e.code !== 1000) {
            console.log('Attempting to reconnect in 5 seconds...');
            setTimeout(() => startGroupChat(currentGroup), 5000);
        }
    };

    groupChatSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };

    currentGroup = groupName;
}

// Ensure WebSocket connection is established before sending messages
function sendMessage() {
    const messageInput = document.querySelector('#chat-message-input');
    const message = messageInput.value.trim();

    if (message && groupChatSocket && groupChatSocket.readyState === WebSocket.OPEN) {
        groupChatSocket.send(JSON.stringify({
            'message': message,
            'group': currentGroup
        }));
        messageInput.value = ''; // Clear the input after sending the message
    } else {
        console.error('WebSocket is not open or message is empty.');
        if (groupChatSocket && groupChatSocket.readyState !== WebSocket.OPEN) {
            startGroupChat(currentGroup); // Attempt to reconnect if WebSocket is not open
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Handle group clicks to initiate group chat
    document.querySelectorAll('#group-list a').forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const groupName = this.dataset.roomName;
            if (groupName) {
                startGroupChat(groupName);  // Start WebSocket for the selected group
                loadGroupChatHistory(groupName); // Load group chat history for the selected group
            } else {
                console.error('Group name is missing!');
            }
        });
    });

    // Attach event listener to the send button
    document.querySelector('#send-button').addEventListener('click', function () {
        sendMessage(); // Send the message when the send button is clicked
    });

    // Allow sending messages by pressing "Enter"
    document.getElementById('chat-message-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage(); // Send the message when "Enter" is pressed
            e.preventDefault(); // Prevent form submission
        }
    });

    // Handle group creation form submission
    document.getElementById('create-group-form').addEventListener('submit', function(event) {
        event.preventDefault();

        const groupName = document.getElementById('group-name').value;
        const members = $('#group-members').val(); // Select2 for multiple selection

        if (!groupName) {
            alert("Group name is required!");
            return;
        }

        fetch('/chatcenter/groupchat/create-group/', {  // Ensure URL matches your Django URL
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Function to get CSRF token
            },
            body: JSON.stringify({
                name: groupName,
                members: members
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'An error occurred.');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                window.location.reload(); // Handle success
            } else {
                document.getElementById('create-group-message').innerText = data.error; // Handle error
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('create-group-message').innerText = error.message || 'An unexpected error occurred.'; // Display error message
        });
    });
});

// Function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Load group chat history
function loadGroupChatHistory(groupName) {
    fetch(`/chatcenter/group-chat-history/${groupName}/`)
        .then(response => response.json())
        .then(data => {
            if (data.messages) {
                document.querySelector('#chat-log').innerHTML = data.messages.map(msg => `
                    <div><strong>${msg.sender}:</strong> ${msg.message}</div>
                `).join('');
            }
        })
        .catch(err => console.error('Error loading chat history:', err));
}

// Define the displayMessage function
function displayMessage(sender, message, timestamp) {
    const chatLog = document.querySelector('#chat-log');
    const notificationDropdown = document.querySelector('#notificationDropdown');
    const notificationBadge = document.querySelector('#notificationBadge');
    const notificationMenu = document.querySelector('#notificationMenu');

    if (chatLog) {
        // Add message to chat log
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

        if (notificationDropdown && notificationBadge && notificationMenu) {
            // Add notification to dropdown menu
            const newNotification = `
                <a class="dropdown-item" href="#">${sender}: ${message}</a>
            `;
            notificationMenu.insertAdjacentHTML('afterbegin', newNotification);

            // Update badge count
            notificationBadge.textContent = parseInt(notificationBadge.textContent) + 1;
        } else {
            console.error('Notification elements not found.');
        }
    } else {
        console.error('Chat log element not found.');
    }
}


document.addEventListener('DOMContentLoaded', function() {
    const notificationDropdown = document.querySelector('#notificationDropdown');

    // Reset notification count when dropdown is clicked
    if (notificationDropdown) {
        notificationDropdown.addEventListener('click', function() {
            const notificationCount = this.querySelector('.badge');
            notificationCount.textContent = '0'; // Reset count
        });
    }
});
