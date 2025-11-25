from config import CHAT_SEPARATOR
from server.user_manager import get_user_socket, get_online_list
from datetime import datetime

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def send_private_message(sender, target_user, msg):
    """发送私聊消息（修复：仅拼接用户名，不包含时间戳）"""
    target_socket = get_user_socket(target_user)
    if not target_socket:
        print(f"❌ 私聊失败：{target_user} 不在线")
        return False

    try:
        private_msg = f"[私聊][{sender}] {msg}{CHAT_SEPARATOR}".encode("utf-8")
        target_socket.send(private_msg)
        return True
    except Exception as e:
        print(f"❌ 私聊转发失败（{target_user}）：{e}")
        return False

def broadcast_group_message(sender, msg):
    """广播群聊消息（保持不变，群聊仍由服务器添加时间戳）"""
    online_list = get_online_list()
    time_str = get_current_time()
    group_msg = f"[{sender}] {time_str}\n{msg}{CHAT_SEPARATOR}".encode("utf-8")
    for username in online_list:
        if username != sender:
            client_socket = get_user_socket(username)
            if client_socket:
                try:
                    client_socket.send(group_msg)
                except Exception as e:
                    print(f"❌ 群聊转发失败（{username}）：{e}")