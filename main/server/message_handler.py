from config import CHAT_SEPARATOR
from server.user_manager import get_user_socket, get_online_list

def send_private_message(sender, target_user, msg):
    """发送私聊消息"""
    target_socket = get_user_socket(target_user)
    if not target_socket:
        print(f"私聊失败：目标用户{target_user}不在线")
        return False

    try:
        private_msg = f"[私聊][{sender}] {msg}{CHAT_SEPARATOR}".encode("utf-8")
        target_socket.send(private_msg)
        return True
    except Exception as e:
        print(f"私聊转发失败（{target_user}）：{e}")
        return False

def broadcast_group_message(sender, msg):
    """广播群聊消息给所有在线用户（排除发送者）"""
    online_list = get_online_list()
    group_msg = f"[{sender}] {msg}{CHAT_SEPARATOR}".encode("utf-8")
    for username in online_list:
        if username != sender:
            client_socket = get_user_socket(username)
            if client_socket:
                try:
                    client_socket.send(group_msg)
                except Exception as e:
                    print(f"群聊转发失败（{username}）：{e}")