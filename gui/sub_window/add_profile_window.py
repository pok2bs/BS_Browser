from import_pyside6 import *

class add_profile_widget(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.add_profile_layout = QVBoxLayout()
        self.profile_name_line = QLineEdit()
        self.profile_name_line.setPlaceholderText("프로필 이름")
        self.profile_password_line = QLineEdit()
        self.profile_password_line.setPlaceholderText("비밀번호")
        self.profile_password_line.setEchoMode(QLineEdit.Password)
        self.accept_button = QPushButton("확인")
        self.add_profile_layout.addWidget(self.profile_name_line)
        self.add_profile_layout.addWidget(self.profile_password_line)
        self.add_profile_layout.addWidget(self.accept_button)
        self.setLayout(self.add_profile_layout)
        self.setWindowTitle("프로필 추가")