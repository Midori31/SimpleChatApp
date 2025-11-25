from config import EXIT_MARKER, CHAT_SEPARATOR

class MessageSender:
    """消息发送工具类（封装群聊、私聊、退出逻辑）"""
    def __init__(self, client_socket, username, ui_callback):
        self.client_socket = client_socket
        self.username = username
        self.ui_callback = ui_callback  # UI回调（用于更新本地消息显示）

    def send_group_message(self, msg):
        """发送群聊消息"""
        try:
            self.client_socket.send(f"{msg}{CHAT_SEPARATOR}".encode("utf-8"))
            self.ui_callback(f"[我] {msg}")  # 本地显示自己的消息
            return True
        except Exception as e:
            self.ui_callback(f"【发送失败】群聊消息发送失败：{str(e)}")
            return False

    def send_private_message(self, target_user, msg):
        """发送私聊消息"""
        if not target_user or not msg:
            self.ui_callback(f"[我（私聊）] 格式错误：@用户名 内容")
            return False

        try:
            private_msg = f"@{target_user} {msg}"
            self.client_socket.send(f"{private_msg}{CHAT_SEPARATOR}".encode("utf-8"))
            self.ui_callback(f"[我（私聊）] {msg}")  # 本地显示自己的消息
            return True
        except Exception as e:
            self.ui_callback(f"【发送失败】私聊消息发送失败：{str(e)}")
            return False

    def send_exit_signal(self):
        """发送退出信号给服务器"""
        try:
            self.client_socket.send(EXIT_MARKER.encode("utf-8"))
        except:
            pass