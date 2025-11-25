from config import CHAT_SEPARATOR
from server.user_manager import get_online_list, get_user_socket

def send_response(client_socket, msg):
    """发送单个响应消息（系统通知/登录响应）"""
    try:
        client_socket.settimeout(5.0)
        client_socket.sendall(f"{msg}{CHAT_SEPARATOR}".encode("utf-8"))
    except Exception as e:
        print(f"发送响应失败：{e}")

def broadcast_system_message(msg):
    """广播系统消息给所有在线用户"""
    online_list = get_online_list()
    for username in online_list:
        client_socket = get_user_socket(username)
        if client_socket:
            send_response(client_socket, f"【系统通知】{msg}")

def send_online_list_to_client(client_socket):
    """向指定客户端发送当前在线列表"""
    from server.user_manager import get_online_list_str
    online_list_str = get_online_list_str()
    send_response(client_socket, f"【当前在线】{online_list_str}")