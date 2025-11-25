from config import CHAT_SEPARATOR
from datetime import datetime

def get_current_time():
    """获取时间戳：hh:mm:ss"""
    return datetime.now().strftime("%H:%M:%S")

def send_login_response(client_socket, success, online_list):
    time_str = get_current_time()
    online_str = ','.join(online_list) if online_list else '无'
    if success:
        response = f"【成功】{time_str}\n登录成功！{CHAT_SEPARATOR}【当前在线】{online_str}{CHAT_SEPARATOR}"
    else:
        response = f"【错误】{time_str}\n登录失败！{CHAT_SEPARATOR}【当前在线】{online_str}{CHAT_SEPARATOR}"
    client_socket.send(response.encode("utf-8"))

def send_response(client_socket, success, online_list):
    """兼容旧代码的登录响应"""
    send_login_response(client_socket, success, online_list)

def broadcast_system_message(all_client_sockets, msg):
    """广播系统消息"""
    for client_socket in all_client_sockets.values():
        try:
            client_socket.send(f"{msg}{CHAT_SEPARATOR}".encode("utf-8"))
        except:
            pass

def send_online_list_to_client(client_socket, online_list):
    """发送在线列表"""
    time_str = get_current_time()
    online_str = ','.join(online_list) if online_list else '无'
    msg = f"【系统通知】{time_str}\n当前在线：{online_str}"
    try:
        client_socket.send(f"{msg}{CHAT_SEPARATOR}".encode("utf-8"))
    except Exception as e:
        print(f"❌ 发送在线列表失败：{e}")

def send_online_notify(username, all_client_sockets):
    """上线通知"""
    time_str = get_current_time()
    online_str = ','.join(all_client_sockets.keys()) if all_client_sockets else '无'
    notify_msg = f"【系统通知】{time_str}\n用户 {username} 已上线！当前在线：{online_str}"
    broadcast_system_message(all_client_sockets, notify_msg)

def send_offline_notify(username, all_client_sockets):
    """下线通知"""
    time_str = get_current_time()
    online_str = ','.join(all_client_sockets.keys()) if all_client_sockets else '无'
    notify_msg = f"【系统通知】{time_str}\n用户 {username} 已下线！当前在线：{online_str}"
    broadcast_system_message(all_client_sockets, notify_msg)