# WaveText - Messaging App

**WaveText** is a web-based messaging application designed to offer real-time chat functionality with user authentication, group chats, private messaging, and notifications. It also includes REST API endpoints for retrieving notifications.

## Features

- **Real-time Messaging**: Users can send and receive messages in real-time using WebSockets (via Django Channels).
- **Private Chats**: One-on-one messaging between users.
- **Group Chats**: Create and participate in group chats.
- **Notifications**: Retrieve notifications using API endpoints.
- **User Authentication**: Sign up, log in, and user session management.
- **Simple UI**: Designed with a clean and user-friendly interface using Bootstrap.

## Technology Stack

- **Frontend**: Bootstrap 4, HTML5, CSS3, JavaScript
- **Backend**: Django, Django Channels
- **Database**: SQLite3
- **Real-Time**: WebSockets, Django Channels
- **API**: Django REST Framework 
- **Version Control**: GitHub

## Setup Instructions

### Prerequisites

Ensure you have the following installed on your machine:
- Python 3.8+

### Installation Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/wavetext.git
   cd wavetext
   ```

2. Create a virtual environment:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:

   ```bash
   python manage.py migrate
   ```

5. Run the development server:

   ```bash
   python manage.py runserver
   ```

### WebSockets Integration
WaveText leverages WebSockets via Django Channels to implement real-time communication for both private and group chats. WebSockets allow the server to push updates to the client without needing to continuously poll for new data.

WebSocket Routes
Private Chats: WebSocket connections for private chats are established via the route /ws/chat/private/<username>/.
Group Chats: WebSocket connections for group chats are established via the route /ws/chat/group/<group_name>/.
This enables users to instantly see messages as soon as they are sent, without needing to refresh the page.

### API Endpoints

- **Notification Retrieval**: Retrieve notifications using the API endpoint `/api/notifications/`.
  
  Example request:
  ```bash
  GET /api/notifications/
  ```

### License

This project is licensed under the MIT License.

### Developer details
SUPRIYO BHATTACHARYA
ELECTRICAL ENGINEERING
IIT JAMMU


---
