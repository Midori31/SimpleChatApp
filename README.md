[TOC]

**English** | [中文](./README.zh-CN.md)

# Simple GUI Chat App

A lightweight TCP-based chat application with PyQt6 GUI, supporting group chat, private chat, timestamp display, and Chinese username compatibility.

## Features

- Graphical login interface (configurable IP/port)
- Real-time group chat message sync
- Private chat (double-click online user to start)
- Auto-updating online user list
- User online/offline notifications
- Message timestamps (format: `username hh:mm:ss`)
- Chinese username support (1-20 characters)
- Graceful exit mechanism (logout button)
- Configuration persistence (saves last server IP/port)

## Tech Stack

- Python 3.8+
- PyQt6 (GUI)
- TCP Socket (network communication)
- Multithreading (concurrency)
- JSON (configuration storage)

## Quick Start

### 1. Install Dependencies

```Bash
pip install pyqt6
```

### 2. Run Server

```Bash
python -m server.main
```

### 3. Run Client (multiple clients supported)

```Bash
python -m client.main
```

### 4. Usage

1. Enter server IP, port (default: 9000) and username (supports Chinese) to log in
2. Group chat: Type message and send directly
3. Private chat: Double-click a username in the online list
4. Exit: Click "Logout" button, send `.exit` or close the window

## File Structure

```Plain
SimpleChatApp/
├── main/
│   ├── client/
│   │   ├── chat_ui.py           # Main group chat window
│   │   ├── private_chat_ui.py   # Private chat dialog
│   │   ├── login_ui.py          # Login window
│   │   ├── message_sender.py    # Message sending logic
│   │   └── message_receiver.py  # Background receive thread
│   ├── server/
│   │   ├── main.py              # Server entry
│   │   ├── connection.py        # Client connection handler
│   │   ├── user_manager.py      # Online user management
│   │   ├── message_handler.py   # Message forwarding
│   │   └── system_notify.py     # Status notifications
│   └── config.py                # Global configuration
├── .gitignore
├── README.md                    # English documentation
├── README.zh-CN.md              # Chinese documentation
└── requirements.txt             # Dependencies list
```

## Notes

- Server auto-displays local LAN IP for client connection
- Configuration file (`config.json`) is auto-generated to save last used IP/port
- For local testing, set server IP to `127.0.0.1`
- Ensure server and clients are on the same network
- Firewall may need to allow the port (default: 9000)
- Usernames are unique (no duplicates allowed)
- Chinese usernames support 1-20 characters (no illegal symbols)