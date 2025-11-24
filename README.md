[TOC]

**English** | [中文](./README.zh-CN.md)

# Simple GUI Chat App

A lightweight TCP-based chat application with PyQt6 GUI, supporting group chat, private chat, and online status notifications.

## Features

- Graphical login interface
- Real-time group chat message sync
- Private chat (format: `@username message`)
- Auto-updating online user list
- User online/offline notifications
- Graceful exit mechanism

## Tech Stack

- Python 3.8+
- PyQt6 (GUI)
- TCP Socket (network communication)
- Multithreading (concurrency)

## Quick Start

### 1. Install Dependencies

```Bash
pip install pyqt6
```

### 2. Run Server

```Bash
python server.py
```

### 3. Run Client (multiple clients supported)

#### GUI Client

```Bash
python client_gui.py
```

#### Command-Line Client (optional)

```Bash
python client.py
```

### 4. Usage

1. Enter a username to log in (no duplicates allowed)
2. Group chat: Type a message and send directly
3. Private chat: Use the format `@target_username your_message`
4. Exit: Type `exit` or close the window

## File Structure

```Plain
chat-app/
├── server.py          # Backend server code
├── client_gui.py      # GUI client code
├── client.py          # Command-line client code
└── README.md          # Project documentation
```

## Notes

- Default server port: 9000 (modify in `server.py` if needed)
- Manually update `SERVER_IP` in `client.py` and `client_gui.py` to the server's address
- For local testing, set `SERVER_IP` to `127.0.0.1`
- Ensure the server and clients are on the same network
- Firewall may need to allow the port for network access