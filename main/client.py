import socket
import threading
import sys
import time
from queue import Queue

SERVER_IP = "101.76.246.151"
SERVER_PORT = 9000
BUFFER_SIZE = 1024
EXIT_CMD = ".exit"
EXIT_MARKER = "__EXIT__"
CHAT_SEPARATOR = "|||"

msg_queue = Queue()
current_username = ""
prompt = ""
prompt_displayed = False
client_socket = None
login_completed = False

def receive_login_response():
    """同步接收登录响应和初始在线列表"""
    global login_completed
    try:
        client_socket.settimeout(15.0)
        data = b""
        # 接收所有登录相关响应（成功提示+在线列表）
        while len(data.split(CHAT_SEPARATOR.encode("utf-8"))) < 3:  # 至少接收2条消息（成功+在线列表）
            chunk = client_socket.recv(BUFFER_SIZE)
            if not chunk:
                break
            data += chunk
        # 处理所有响应消息
        responses = [m.strip() for m in data.decode("utf-8").split(CHAT_SEPARATOR) if m.strip()]
        for resp in responses:
            if resp.startswith("【成功】"):
                print(f"\n{resp}\n")
                login_completed = True
            
            elif resp.startswith("【错误】"):
                print(f"\n{resp}\n")
                login_completed = False
    except socket.timeout:
        print(f"\n登录超时（15秒），未收到响应\n")
        login_completed = False
    except Exception as e:
        print(f"\n接收登录响应失败：{e}\n")
        login_completed = False
    finally:
        client_socket.settimeout(None)

def receive_chat_messages():
    """接收聊天消息和系统通知"""
    global client_socket
    while login_completed:
        try:
            data = client_socket.recv(BUFFER_SIZE).decode("utf-8", errors="ignore")
            if not data:
                break
            msgs = [m.strip() for m in data.split(CHAT_SEPARATOR) if m.strip()]
            for msg in msgs:
                if msg:
                    msg_queue.put(msg)
        except Exception as e:
            if "10054" not in str(e) and "远程主机" not in str(e):
                msg_queue.put(f"【错误】接收消息失败：{e}")
            break

def print_messages():
    """打印所有消息（含系统通知和聊天消息）"""
    global prompt_displayed
    while True:
        if not msg_queue.empty():
            msg = msg_queue.get()
            
            # 清空当前行提示，避免错位
            if prompt_displayed:
                sys.stdout.write("\r")
                sys.stdout.write(" " * len(prompt))
                sys.stdout.write("\r")
                sys.stdout.flush()

            # 打印消息（系统通知和聊天消息统一格式）
            print(msg)
            sys.stdout.flush()

            # 重新显示输入提示
            if current_username:
                sys.stdout.write(prompt)
                sys.stdout.flush()
                prompt_displayed = True
        time.sleep(0.05)

def start_client(port):
    global current_username, prompt, client_socket, login_completed
    # 创建socket连接
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, port))
        print(f"✅ 成功连接到聊天服务器（{SERVER_IP}:{port}）")
    except Exception as e:
        print(f"❌ 连接服务器失败：{e}")
        sys.exit(1)

    # 输入用户名（仅一次）
    username = input("\n请输入你的用户名：").strip()
    while not username:
        print("❌ 用户名不能为空！")
        username = input("请输入你的用户名：").strip()
    
    # 发送用户名并登录
    try:
        client_socket.sendall(username.encode("utf-8"))
        print(f"🔄 正在登录...")
    except Exception as e:
        print(f"❌ 发送用户名失败：{e}")
        sys.exit(1)

    # 同步接收登录响应和初始在线列表
    receive_login_response()
    if not login_completed:
        print("❌ 登录失败，程序即将退出...")
        client_socket.close()
        sys.exit(1)

    # 登录成功初始化
    current_username = username
    prompt = f"\n[{current_username}] "

    # 启动消息接收和打印线程
    chat_thread = threading.Thread(target=receive_chat_messages, daemon=True)
    print_thread = threading.Thread(target=print_messages, daemon=True)
    chat_thread.start()
    print_thread.start()

    # 显示初始输入提示
    time.sleep(0.5)
    sys.stdout.write(prompt)
    sys.stdout.flush()
    prompt_displayed = True

    # 处理用户输入
    while True:
        try:
            msg = input().strip()
        except KeyboardInterrupt:
            print("\n\n🔌 正在退出聊天...")
            break

        if msg.lower() == EXIT_CMD:
            print("\n\n🔌 正在退出聊天...")
            try:
                client_socket.send(EXIT_MARKER.encode("utf-8"))
                time.sleep(0.5)
                client_socket.close()
            except:
                pass
            sys.exit(0)

        # 重新显示输入提示
        sys.stdout.write(prompt)
        sys.stdout.flush()

        if not msg:
            continue
        try:
            client_socket.send(f"{msg}{CHAT_SEPARATOR}".encode("utf-8"))
        except Exception as e:
            print(f"\n❌ 发送消息失败：{e}")
            client_socket.close()
            break

if __name__ == "__main__":
    port = 9000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            print("❌ 端口参数错误，使用默认端口9000")
    start_client(port)