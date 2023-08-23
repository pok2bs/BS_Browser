from import_pyside6 import *

class MainWindow (object):
    def setup_ui(self, parent):


        #위 구성요소
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText('URL을 입력하세요')
        self.back_button = QPushButton("뒤")
        self.forward_button = QPushButton("앞")
        self.reload_button = QPushButton("새로고침")
        self.top_layout = QHBoxLayout()
        self.top_layout.addWidget(self.back_button)
        self.top_layout.addWidget(self.forward_button)
        self.top_layout.addWidget(self.reload_button)
        self.top_layout.addWidget(self.url_edit)
        

        self.top_frame = QFrame()
        self.top_frame.setLayout(self.top_layout)
        self.top_frame.setMaximumHeight(50)

        #웹 표시
        self.view_widget = QWebEngineView()
        url = QUrl("https://WWW.google.com")
        self.view_widget.setUrl(url)


        self.right_menu = QStackedWidget()
        #각종 설정
        self.setting_frame = QFrame()
        
        self.setting_label = QLabel("<b>설정</b>")
        
        self.bookmark_layout = QVBoxLayout()
        self.bookmark_Label = QLabel("즐겨찾기")
        self.bookmark_widget = QListWidget()
        self.bookmark_delete_button = QPushButton("삭제")
        self.bookmarks_clear_button = QPushButton("모두 삭제")

        self.bookmark_name_change = QHBoxLayout()
        self.bookmark_name_line = QLineEdit()
        self.bookmark_name_line.setPlaceholderText("즐겨찾기 이름")
        self.bookmark_name_button = QPushButton("이름변경")
        self.bookmark_name_change.addWidget(self.bookmark_name_line)
        self.bookmark_name_change.addWidget(self.bookmark_name_button)


        self.bookmark_layout.addWidget(self.bookmark_Label)
        self.bookmark_layout.addWidget(self.bookmark_widget)
        self.bookmark_layout.addLayout(self.bookmark_name_change)
        self.bookmark_layout.addWidget(self.bookmark_delete_button)
        self.bookmark_layout.addWidget(self.bookmarks_clear_button)
        
        #프로필 변경
        self.set_profile_layout = QVBoxLayout()
        self.set_profile_label = QLabel("프로필")
        self.password_change = QPushButton("비밀번호 변경")
        self.profile_remove = QPushButton("이 프로필 삭제")
        
        self.profile_name_change = QHBoxLayout()
        self.profile_name_line = QLineEdit()
        self.profile_name_line.setPlaceholderText("프로필 이름")
        self.profile_name_button = QPushButton("이름변경")
        self.profile_name_change.addWidget(self.profile_name_line)
        self.profile_name_change.addWidget(self.profile_name_button)
        
        self.profile_change = QPushButton("프로필 변경")
        self.add_profile = QPushButton("새 프로필 추가")

        self.set_profile_layout.addWidget(self.set_profile_label)
        self.set_profile_layout.addLayout(self.profile_name_change)
        self.set_profile_layout.addWidget(self.profile_change)
        self.set_profile_layout.addWidget(self.password_change)
        self.set_profile_layout.addWidget(self.add_profile)
        self.set_profile_layout.addWidget(self.profile_remove)

        self.setting_layout = QVBoxLayout()
        self.setting_layout.addWidget(self.setting_label)
        self.setting_layout.addLayout(self.bookmark_layout)
        self.setting_layout.addLayout(self.set_profile_layout)
        self.setting_layout.setSpacing(10)
        
        self.setting_frame.setLayout(self.setting_layout)
        
        #프로필 선택
        self.profile_widget = QWidget()
        self.profile_layout = QVBoxLayout()
        self.select_profile_label = QLabel("<b>프로필 선택</b>")
        self.select_profile = QListWidget()
        self.profile_back_button = QPushButton("뒤로")
        self.profile_back_max = self.profile_back_button.maximumHeight()
        self.profile_back_button.setMaximumHeight(0)
        self.not_select_profile = QPushButton("프로필 없이 계속")
        
        self.select_profile.addItem("+ 프로필 추가")
        self.profile_layout.addWidget(self.select_profile_label)
        self.profile_layout.addWidget(self.select_profile)
        self.profile_layout.addWidget(self.profile_back_button)
        self.profile_layout.addWidget(self.not_select_profile)
        
        self.profile_widget.setLayout(self.profile_layout)

        self.right_menu.addWidget(self.setting_frame)
        self.right_menu.addWidget(self.profile_widget)
        self.right_menu.setCurrentWidget(self.profile_widget)
        
        self.right_menu.setMaximumWidth(0)

        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addWidget(self.view_widget)
        self.bottom_layout.addWidget(self.right_menu)
        self.bottom_layout.setContentsMargins(0,0,0,0)
        self.bottom_layout.setSpacing(0)

        self.central_layout = QVBoxLayout()
        self.central_layout.addWidget(self.top_frame)
        self.central_layout.addLayout(self.bottom_layout)
        self.central_layout.setContentsMargins(0,0,0,0)
        self.central_layout.setSpacing(0)



        self.central_widget = QFrame()
        self.central_widget.setLayout(self.central_layout)
        parent.setCentralWidget(self.central_widget)
