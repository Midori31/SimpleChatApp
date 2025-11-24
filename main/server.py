import socket
import threading
import time

online_users = {}
user_lock = threading.Lock()
SERVER_ADDR = ("0.0.0.0", 9000)
BUFFER_SIZE = 1024
EXIT_MARKER = "__EXIT__"
CHAT_SEPARATOR = "|||"

def broadcast_chat_message(sender, msg, is_private=False, target_user=None):
    with user_lock:
        if is_private:
            if target_user in online_users:
                try:
                    private_msg = f"[私聊][{sender}] {msg}{CHAT_SEPARATOR}".encode("utf-8")
                    online_users[target_user].send(private_msg)
                except Exception as e:
                    print(f"私聊转发失败（{target_user}）：{e}")
        else:
            group_msg = f"[{sender}] {msg}{CHAT_SEPARATOR}".encode("utf-8")
            for username, client_socket in online_users.items():
                if username != sender:
                    try:
                        client_socket.send(group_msg)
                    except Exception as e:
                        print(f"群聊转发失败（{username}）：{e}")

def send_response(client_socket, msg):
    """发送响应消息（含系统通知和登录响应）"""
    try:
        client_socket.settimeout(5.0)
        client_socket.sendall(f"{msg}{CHAT_SEPARATOR}".encode("utf-8"))
    except Exception as e:
        print(f"发送响应失败：{e}")

def get_online_list_str():
    """获取在线列表字符串"""
    with user_lock:
        if not online_users:
            return "无"
        return ",".join(online_users.keys())

def broadcast_system_message(msg):
    """广播系统消息给所有在线用户"""
    with user_lock:
        online_snapshot = list(online_users.values())
    
    for client_socket in online_snapshot:
        send_response(client_socket, f"【系统通知】{msg}")
        time.sleep(0.05)

def send_online_list_to_client(client_socket):
    """单独向指定客户端发送当前在线列表"""
    online_list = get_online_list_str()
    send_response(client_socket, f"【当前在线】{online_list}")

def handle_client(client_socket, client_addr):
    username = None
    try:
        # 接收用户名
        username = client_socket.recv(BUFFER_SIZE).decode("utf-8").strip()
        if not username:
            send_response(client_socket, "【错误】用户名不能为空")
            client_socket.close()
            return

        # 检查用户名重复
        with user_lock:
            if username in online_users:
                send_response(client_socket, "【错误】用户名已被占用")
                client_socket.close()
                return
            online_users[username] = client_socket

        # 1. 发送登录成功响应
        send_response(client_socket, "【成功】登录成功")
        # 2. 单独向当前客户端发送在线列表（登录后必看）
        send_online_list_to_client(client_socket)
        print(f"用户{username}（{client_addr}）登录成功，当前在线：{get_online_list_str()}")

        # 3. 向其他用户广播上线通知
        broadcast_system_message(f"{username}已上线")
        # 4. 向其他用户广播更新后的在线列表
        broadcast_system_message(f"当前在线：{get_online_list_str()}")

        # 接收聊天消息
        while True:
            client_socket.settimeout(300.0)
            try:
                data = client_socket.recv(BUFFER_SIZE).decode("utf-8").strip()
            except socket.timeout:
                send_response(client_socket, "【系统】连接超时，请发送消息保持在线")
                continue
            except Exception as e:
                print(f"用户{username}断开连接：{e}")
                break

            if data == EXIT_MARKER:
                print(f"用户{username}主动退出")
                break

            if not data:
                break

            # 处理私聊/群聊
            if data.startswith("@"):
                if " " not in data[1:]:
                    send_response(client_socket, "【错误】私聊格式：@用户名 消息内容")
                    continue
                target_user, private_msg = data[1:].split(" ", 1)
                broadcast_chat_message(sender=username, msg=private_msg, is_private=True, target_user=target_user)
            else:
                broadcast_chat_message(sender=username, msg=data, is_private=False)

    except Exception as e:
        print(f"用户{username}处理异常：{e}")
        send_response(client_socket, "【错误】登录失败，请重试")
    finally:
        # 下线清理
        if username and username in online_users:
            with user_lock:
                del online_users[username]
            # 广播下线通知和更新列表
            broadcast_system_message(f"{username}已下线")
            broadcast_system_message(f"当前在线：{get_online_list_str()}")
            print(f"用户{username}已下线，当前在线：{get_online_list_str()}")
        try:
            client_socket.close()
        except:
            pass

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(SERVER_ADDR)
    server_socket.listen(10)
    print(f"聊天服务器启动成功，监听端口{SERVER_ADDR[1]}...")
    print("等待客户端连接...")

    while True:
        client_socket, client_addr = server_socket.accept()
        print(f"新客户端连接：{client_addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_addr), daemon=True)
        client_thread.start()

if __name__ == "__main__":
    start_server()