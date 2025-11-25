import socket
import threading
from config import BUFFER_SIZE, EXIT_MARKER
from server.user_manager import (add_user, remove_user, is_username_exist,
                                 get_online_list_str)
from server.system_notify import (send_response, broadcast_system_message,
                                  send_online_list_to_client)
from server.message_handler import send_private_message, broadcast_group_message

def handle_single_client(client_socket, client_addr):
    """处理单个客户端的完整生命周期（登录→聊天→下线）"""
    username = None
    try:
        # 1. 接收并验证用户名
        username = client_socket.recv(BUFFER_SIZE).decode("utf-8").strip()
        if not username:
            send_response(client_socket, "【错误】用户名不能为空")
            return

        if is_username_exist(username):
            send_response(client_socket, "【错误】用户名已被占用")
            return

        # 2. 登录成功：添加用户、发送响应
        add_user(username, client_socket)
        send_response(client_socket, "【成功】登录成功")
        send_online_list_to_client(client_socket)
        print(f"用户{username}（{client_addr}）登录成功，当前在线：{get_online_list_str()}")

        # 3. 广播上线通知
        broadcast_system_message(f"{username}已上线")
        broadcast_system_message(f"当前在线：{get_online_list_str()}")

        # 4. 持续接收消息
        while True:
            client_socket.settimeout(300.0)  # 5分钟超时
            try:
                data = client_socket.recv(BUFFER_SIZE).decode("utf-8").strip()
            except socket.timeout:
                send_response(client_socket, "【系统】连接超时，请发送消息保持在线")
                continue
            except Exception as e:
                print(f"用户{username}断开连接：{e}")
                break

            # 处理退出/空消息
            if data == EXIT_MARKER or not data:
                if data == EXIT_MARKER:
                    print(f"用户{username}主动退出")
                break

            # 处理私聊/群聊
            if data.startswith("@"):
                if " " not in data[1:]:
                    send_response(client_socket, "【错误】私聊格式：@用户名 消息内容")
                    continue
                target_user, private_msg = data[1:].split(" ", 1)
                send_private_message(sender=username, target_user=target_user, msg=private_msg)
            else:
                broadcast_group_message(sender=username, msg=data)

    except Exception as e:
        print(f"用户{username}处理异常：{e}")
        send_response(client_socket, "【错误】登录失败，请重试")
    finally:
        # 5. 下线清理
        if username:
            remove_user(username)
            broadcast_system_message(f"{username}已下线")
            broadcast_system_message(f"当前在线：{get_online_list_str()}")
            print(f"用户{username}已下线，当前在线：{get_online_list_str()}")
        try:
            client_socket.close()
        except:
            pass