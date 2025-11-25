import socket
from PyQt6.QtCore import QThread, pyqtSignal
from config import BUFFER_SIZE, CHAT_SEPARATOR

class ReceiveThread(QThread):
    """后台接收消息线程"""
    normal_msg_signal = pyqtSignal(str)  # 群聊消息
    system_msg_signal = pyqtSignal(str)  # 系统通知消息
    error_signal = pyqtSignal(str)       # 错误消息
    login_result_signal = pyqtSignal(bool, str)  # 登录结果（成功状态，在线列表）
    online_list_update_signal = pyqtSignal(str)  # 在线列表更新信号
    private_msg_signal = pyqtSignal(str, str)  # 私聊消息信号（发送者，消息内容）

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.is_running = True

    def run(self):
        """线程核心逻辑：持续接收并解析服务器消息"""
        try:
            self._handle_login_response()
            self._handle_chat_messages()
        except Exception as e:
            self.error_signal.emit(f"接收消息异常：{str(e)}")
        finally:
            self.client_socket.close()

    def _handle_login_response(self):
        """处理登录阶段的服务器响应"""
        login_data = b""
        while len(login_data.split(CHAT_SEPARATOR.encode("utf-8"))) < 3 and self.is_running:
            chunk = self.client_socket.recv(BUFFER_SIZE)
            if not chunk:
                self.error_signal.emit("服务器连接中断")
                return
            login_data += chunk

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

        self.login_result_signal.emit(login_success, online_list)

    def _handle_chat_messages(self):
        """处理聊天阶段的服务器消息（修复私聊解析）"""
        while self.is_running:
            data = self.client_socket.recv(BUFFER_SIZE).decode("utf-8", errors="ignore")
            if not data:
                break
            msgs = [m.strip() for m in data.split(CHAT_SEPARATOR) if m.strip()]
            for msg in msgs:
                if msg.startswith("【系统通知】"):
                    self.system_msg_signal.emit(msg)
                    if "当前在线：" in msg:
                        online_list = msg.split("当前在线：")[-1].strip()
                        self.online_list_update_signal.emit(online_list)
                elif msg.startswith("[私聊]"):
                    try:
                        # 解析格式：[私聊][发送者] 消息内容（无服务器时间戳）
                        sender_part = msg.split("[私聊][")[1].split("]")[0]
                        content_part = msg.split(f"[私聊][{sender_part}] ")[1].strip()
                        self.private_msg_signal.emit(sender_part, content_part)
                    except Exception as e:
                        print(f"解析私聊消息失败：{e}，原始消息：{msg}")
                        self.normal_msg_signal.emit(f"【解析失败】{msg}")
                else:
                    self.normal_msg_signal.emit(msg)

    def stop(self):
        """停止线程"""
        self.is_running = False