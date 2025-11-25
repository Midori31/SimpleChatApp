[TOC]

[中文] | [English](./README.md)

# 简易图形化聊天应用

一款基于 TCP 协议的轻量级聊天应用，采用 PyQt6 构建图形界面，支持群聊、私聊、时间戳显示及中文用户名兼容。

## 核心功能

- 图形化登录界面（支持配置 IP 和端口）
- 实时群聊消息同步
- 私聊功能（双击在线用户发起）
- 在线用户列表自动更新
- 用户上线/下线通知
- 消息时间戳（格式：`用户名 时:分:秒`）
- 中文用户名支持（1-20 个字符）
- 优雅退出机制（退出按钮）
- 配置持久化（保存上次使用的服务器 IP 和端口）

## 技术栈

- Python 3.8+
- PyQt6（图形界面）
- TCP Socket（网络通信）
- 多线程（并发处理）
- JSON（配置存储格式）

## 快速开始

### 1. 安装依赖

```Bash
pip install pyqt6
```



### 2. 启动服务器

```Bash
python -m server.main
```

### 3. 启动客户端

```Bash
python -m client.main
```

### 4. 使用说明

1. 输入服务器IP、端口（默认：9000）及用户名（支持中文）进行登录
2. 群聊：输入消息后直接发送
3. 私聊：双击在线用户列表中的用户名
4. 退出：点击“退出”按钮、在对话框中输入`.exit`或关闭窗口

## 文件结构

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

## 注意事项

- 服务器会自动显示本地局域网IP，供客户端连接

- 配置文件（`config.json`）会自动生成，用于保存上次使用的IP和端口

- 本地测试时，需将服务器IP设为`127.0.0.1`

- 确保服务器与客户端处于同一网络环境

- 可能需要配置防火墙，允许对应端口（默认：9000）的通信

- 用户名具有唯一性，不允许重复登录

- 中文用户名支持1-20个字符，且不包含非法符号

  