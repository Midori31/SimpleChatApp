from config import EXIT_MARKER, CHAT_SEPARATOR

class MessageSender:
    """消息发送工具类（修复群聊自己消息格式）"""
    def __init__(self, client_socket, username, group_ui_callback):
        self.client_socket = client_socket
        self.username = username
        self.group_ui_callback = group_ui_callback  # 仅用于群聊消息显示

    def send_group_message(self, msg):
        """发送群聊消息（修复：只传递纯消息内容，不包含[我]前缀）"""
        try:
            self.client_socket.send(f"{msg}{CHAT_SEPARATOR}".encode("utf-8"))
            self.group_ui_callback(msg)  # 只传递纯消息内容
            return True
        except Exception as e:
            self.group_ui_callback(f"【发送失败】群聊消息发送失败：{str(e)}")
            return False

    def send_private_message(self, target_user, msg):
        """发送私聊消息（仅支持对话框调用）"""
        if not target_user or not msg:
            return False

        try:
            private_msg = f"@{target_user} {msg}"
            self.client_socket.send(f"{private_msg}{CHAT_SEPARATOR}".encode("utf-8"))
            return True
        except Exception as e:
            print(f"私聊发送失败：{e}")
            return False

    def send_exit_signal(self):
        """发送退出信号"""
        try:
            self.client_socket.send(EXIT_MARKER.encode("utf-8"))
        except:
            pass