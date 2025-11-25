import socket
from PyQt6.QtCore import QThread, pyqtSignal
from config import BUFFER_SIZE, CHAT_SEPARATOR

class ReceiveThread(QThread):
    """后台接收消息线程（不阻塞UI）"""
    # 信号定义：传递不同类型消息到UI
    normal_msg_signal = pyqtSignal(str)  # 普通聊天消息
    system_msg_signal = pyqtSignal(str)  # 系统通知消息
    error_signal = pyqtSignal(str)       # 错误消息
    login_result_signal = pyqtSignal(bool, str)  # 登录结果（成功状态，在线列表）

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.is_running = True

    def run(self):
        """线程核心逻辑：持续接收并解析服务器消息"""
        try:
            # 第一步：接收登录阶段的响应（登录结果+初始在线列表）
            self._handle_login_response()
            # 第二步：持续接收聊天阶段的消息
            self._handle_chat_messages()
        except Exception as e:
            self.error_signal.emit(f"接收消息异常：{str(e)}")
        finally:
            self.client_socket.close()

    def _handle_login_response(self):
        """处理登录阶段的服务器响应"""
        login_data = b""
        # 接收足够数据（至少包含登录结果和在线列表）
        while len(login_data.split(CHAT_SEPARATOR.encode("utf-8"))) < 3 and self.is_running:
            chunk = self.client_socket.recv(BUFFER_SIZE)
            if not chunk:
                self.error_signal.emit("服务器连接中断")
                return
            login_data += chunk

        # 解析响应内容
        responses = [m.strip() for m in login_data.decode("utf-8").split(CHAT_SEPARATOR) if m.strip()]
        login_success = False
        online_list = ""
        for resp in responses:
            if resp.startswith("【成功】"):
                login_success = True
            elif resp.startswith("【当前在线】"):
                online_list = resp.replace("【当前在线】", "").strip()
            elif resp.startswith("【错误】"):
                self.error_signal.emit(resp)
            elif resp.startswith("【系统通知】"):
                self.system_msg_signal.emit(resp)

        # 发送登录结果信号给UI
        self.login_result_signal.emit(login_success, online_list)

    def _handle_chat_messages(self):
        """处理聊天阶段的服务器消息"""
        while self.is_running:
            # 接收数据并解码
            data = self.client_socket.recv(BUFFER_SIZE).decode("utf-8", errors="ignore")
            if not data:
                break
            # 按分隔符拆分多条消息
            msgs = [m.strip() for m in data.split(CHAT_SEPARATOR) if m.strip()]
            for msg in msgs:
                if msg.startswith("【系统通知】"):
                    self.system_msg_signal.emit(msg)
                else:
                    self.normal_msg_signal.emit(msg)

    def stop(self):
        """停止线程（安全退出）"""
        self.is_running = False