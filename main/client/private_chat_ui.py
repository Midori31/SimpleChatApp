from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QLineEdit, QPushButton, QLabel, QMessageBox)
from PyQt6.QtGui import QFont, QColor, QTextCursor
from PyQt6.QtCore import Qt
from datetime import datetime

def get_current_time():
    """获取当前时间，格式：hh:mm:ss"""
    return datetime.now().strftime("%H:%M:%S")

class PrivateChatWindow(QDialog):
    """私聊对话框（修复：去掉重复时间戳）"""
    def __init__(self, parent, username, target_user, message_sender):
        super().__init__(parent)
        self.username = username
        self.target_user = target_user  # 对方用户名
        self.message_sender = message_sender
        self.init_ui()

    def init_ui(self):
        """初始化UI（不变）"""
        self.setWindowTitle(f"私聊 - {self.target_user}")
        self.setFixedSize(450, 400)
        self.setStyleSheet("background-color: #f5f5f5;")

        self.normal_font = QFont("微软雅黑", 10)
        self.bold_font = QFont("微软雅黑", 10, QFont.Weight.Bold)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel(f"与 {self.target_user} 的私聊")
        title_label.setFont(self.bold_font)
        title_label.setStyleSheet("color: #2c3e50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        self.msg_display = QTextEdit()
        self.msg_display.setReadOnly(True)
        self.msg_display.setFont(self.normal_font)
        self.msg_display.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
        """)
        main_layout.addWidget(self.msg_display, stretch=1)

        input_layout = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.msg_input.setFont(self.normal_font)
        self.msg_input.setPlaceholderText("输入私聊消息，输入 .close 关闭窗口")
        self.msg_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 8px;
        """)
        self.msg_input.returnPressed.connect(self.send_private_message)

        self.send_btn = QPushButton("发送")
        self.send_btn.setFont(self.normal_font)
        self.send_btn.setStyleSheet("""
            background-color: #2ecc71;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
        """)
        self.send_btn.clicked.connect(self.send_private_message)

        input_layout.addWidget(self.msg_input, stretch=1)
        input_layout.addWidget(self.send_btn)
        main_layout.addLayout(input_layout)

    def send_private_message(self):
        """发送私聊消息"""
        msg = self.msg_input.text().strip()
        if not msg:
            return

        if msg.lower() == ".close":
            self.close()
            return

        success = self.message_sender.send_private_message(
            target_user=self.target_user,
            msg=msg
        )

        if success:
            self._display_self_message(msg)
            self.msg_input.clear()
        else:
            self._display_system_message("【发送失败】消息发送失败，请重试！")

    def _display_self_message(self, msg):
        """[我] hh:mm:ss + 换行消息"""
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)
        self.msg_display.setCurrentFont(self.normal_font)
        self.msg_display.setTextColor(QColor(128, 0, 128))
        self.msg_display.insertPlainText(f"\n[我] {get_current_time()}")
        self.msg_display.insertPlainText(f"\n{msg}")
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)

    def display_target_message(self, msg):
        """[对方ID] hh:mm:ss + 换行消息"""
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)
        self.msg_display.setCurrentFont(self.normal_font)
        self.msg_display.setTextColor(QColor(231, 76, 60))
        # 仅用本地时间戳，不解析服务器时间戳
        self.msg_display.insertPlainText(f"\n[{self.target_user}] {get_current_time()}")
        self.msg_display.insertPlainText(f"\n{msg}")
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)

    def _display_system_message(self, msg):
        """显示系统提示（格式：【系统提示】hh:mm:ss + 换行消息）"""
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)
        self.msg_display.setCurrentFont(self.bold_font)
        self.msg_display.setTextColor(QColor(155, 89, 182))
        self.msg_display.insertPlainText(f"\n【系统提示】{get_current_time()}")
        self.msg_display.insertPlainText(f"\n{msg}")
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)

    def closeEvent(self, event):
        """关闭窗口（不变）"""
        if self.parent():
            self.parent().remove_private_chat_window(self.target_user)
        event.accept()