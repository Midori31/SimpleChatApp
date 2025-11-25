import socket
from config import BUFFER_SIZE, CHAT_SEPARATOR, EXIT_MARKER
from server.user_manager import (add_user, remove_user, get_all_users,
                                 is_username_exist, get_online_list)
from server.message_handler import broadcast_group_message, send_private_message
from server.system_notify import (send_response, broadcast_system_message,
                                  send_online_list_to_client, send_online_notify,
                                  send_offline_notify)

def handle_single_client(client_socket, client_address):
    """处理单个客户端连接（支持中文用户名）"""
    username = None
    try:
        print(f"📞 接收客户端 {client_address} 登录请求")
        
        # 1. 接收用户名（支持中文，指定utf-8编码）
        username = receive_username(client_socket)
        if not username:
            send_response(client_socket, success=False, online_list=get_online_list())
            return
        
        # 2. 验证用户名是否重复
        if is_username_exist(username):
            send_response(client_socket, success=False, online_list=get_online_list())
            print(f"❌ 用户名 {username} 已被占用，{client_address} 登录失败")
            return
        
        # 3. 添加在线用户（中文用户名正常存储）
        add_user(username, client_socket)
        online_list = get_online_list()
        
        # 4. 发送登录成功响应
        send_response(client_socket, success=True, online_list=online_list)
        
        # 5. 广播上线通知（中文用户名正常显示）
        send_online_notify(username, get_all_users())
        print(f"✅ 用户 {username} 登录成功，当前在线：{','.join(online_list)}")
        
        # 6. 持续接收消息（支持中文消息）
        while True:
            # 接收消息时强制utf-8编码，忽略错误字符
            data = client_socket.recv(BUFFER_SIZE).decode("utf-8", errors="replace")
            if not data or EXIT_MARKER in data:
                print(f"👋 用户 {username} 主动下线")
                break
            
            # 解析多条消息（中文消息正常分割）
            msgs = [msg.strip() for msg in data.split(CHAT_SEPARATOR) if msg.strip()]
            for msg in msgs:
                if msg.startswith("@"):
                    handle_private_message(username, msg)  # 中文私聊目标用户支持
                else:
                    broadcast_group_message(username, msg)  # 中文群聊消息支持
    
    except Exception as e:
        print(f"❌ 客户端 {client_address} 异常：{e}")
    finally:
        # 清理资源（中文用户名正常移除）
        if username and is_username_exist(username):
            remove_user(username)
            remaining_online = get_online_list()
            send_offline_notify(username, get_all_users())
            print(f"👋 用户 {username} 下线，当前在线：{','.join(remaining_online) if remaining_online else '无'}")
        client_socket.close()
        print(f"🔌 连接 {client_address} 已关闭")

def receive_username(client_socket):
    """接收用户名（支持中文，优化合法性验证）"""
    try:
        # 强制utf-8解码，确保中文正确接收
        username = client_socket.recv(BUFFER_SIZE).decode("utf-8", errors="replace").strip()
        
        # 验证用户名合法性：
        # 1. 非空
        # 2. 长度 1-20（中文算1个字符，符合直觉）
        # 3. 不包含非法字符（避免分割符冲突）
        illegal_chars = [CHAT_SEPARATOR, EXIT_MARKER, "@", "[", "]", "|||", "__EXIT__"]
        if not username:
            print("❌ 用户名不能为空")
            return None
        if len(username) > 20:
            print(f"❌ 用户名 {username} 过长（最大20个字符）")
            return None
        for char in illegal_chars:
            if char in username:
                print(f"❌ 用户名包含非法字符：{char}")
                return None
        
        return username
    except Exception as e:
        print(f"❌ 接收用户名失败：{e}")
        return None

def handle_private_message(sender, msg):
    """处理私聊消息（支持中文目标用户）"""
    try:
        if " " not in msg[1:]:
            return  # 无消息内容，忽略
        # 分割中文目标用户和消息内容
        target_user, content = msg[1:].split(" ", 1)
        if target_user and content:
            send_private_message(sender, target_user, content)
    except Exception as e:
        print(f"❌ 处理私聊消息失败：{e}")