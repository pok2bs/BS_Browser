from import_pyside6 import *
from gui.main_window import MainWindow
from gui.add_profile_window import add_profile_widget
from gui.password_window import password_widget
from gui.password_change_window import password_change_widget

import http.client, requests
from urllib.request import Request, urlopen
import sys, json, shutil, time


class AppMain (QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.ui = MainWindow()
        self.add_profile_widget = add_profile_widget()
        self.password_widget = password_widget() 
        self.password_change_widget = password_change_widget()
        self.add_profile_widget.accept_button.clicked.connect(self.add_profile)
        self.password_widget.accept_button.clicked.connect(self.set_profile)
        self.password_change_widget.accept_button.clicked.connect(self.password_change)
        self.setMinimumSize(400, 200)
        self.profile_num = None

        self.ui.setup_ui(self)
        self.edit_widget = QWidget()
        self.edit_layout = QVBoxLayout()
        self.text_widget = QTextEdit()
        self.text_accept_button = QPushButton("실행")
        self.edit_layout.addWidget(self.text_widget)
        self.edit_layout.addWidget(self.text_accept_button)
        self.edit_widget.setLayout(self.edit_layout)
        self.edit_widget.setWindowTitle("run javascript")
        
        self.profile_path = self.ui.view_widget.page().profile().persistentStoragePath()
        delete_path = self.profile_path.split("/")[-1]
        self.profile_path = self.profile_path.strip(delete_path)
        print(self.profile_path)

        try:
            with open(f"{self.profile_path}save.json","r") as save:
                self.profile_list = json.load(save)
            if len(self.profile_list) > 0:
                for i in range(0,len(self.profile_list)):
                    self.ui.select_profile.insertItem(i, self.profile_list[i]["name"])
        except:
            self.profile_list = list()
            with open(f"{self.profile_path}save.json","w",encoding="utf-8") as save:
                json.dump(self.profile_list, save, indent="\t")

        #웹뷰 설정
        self.ui.view_widget.page().fullScreenRequested.connect(self.fullscreen)
        self.ui.view_widget.page().profile().downloadRequested.connect(self.on_downloadRequested)
        self.ui.view_widget.urlChanged.connect(self.update_url_edit)
        self.ui.view_widget.show_window.connect(self.show_web_window)
        self.ui.view_widget.iconChanged.connect(self.update_icon)
        self.ui.view_widget.titleChanged.connect(self.update_title)
        self.ui.view_widget.loadProgress.connect(self.loading)
        self.ui.view_widget.loadFinished.connect(self.ui.load_progress_bar.reset)
        
        #상단 바 ui와 기능들 연결
        self.ui.back_button.clicked.connect(self.ui.view_widget.back)
        self.ui.forward_button.clicked.connect(self.ui.view_widget.forward)
        self.ui.reload_button.clicked.connect(self.ui.view_widget.reload)
        self.ui.url_edit.returnPressed.connect(self.move_to_url)

        #즐겨찾기 편집 기능 버튼들과 기능들 연결
        self.ui.bookmarks_clear_button.clicked.connect(self.bookmarks_clear)
        self.ui.bookmark_delete_button.clicked.connect(self.bookmark_delete)
        self.ui.bookmark_name_button.clicked.connect(self.bookmark_name_change)

        #프로필 편집 기능 버튼들과 기능 연결
        self.ui.profile_name_button.clicked.connect(self.profile_name_change)
        self.ui.password_change.clicked.connect(self.password_change_show)
        self.ui.profile_back_button.clicked.connect(self.change_widget)
        self.ui.add_profile.clicked.connect(self.add_profile_widget.show)
        self.ui.profile_remove.clicked.connect(self.profile_remove)

        #오버레이 해주는 버튼 연결
        self.ui.stay_on_top.clicked.connect(self.window_stay_on_top)
        
        self.text_accept_button.clicked.connect(self.run_js)

        #단축기 설정
        self.shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut.activated.connect(self.save_url)
        self.Load_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        self.Load_shortcut.activated.connect(self.save_load)
        self.dev_tool_shortcut = QShortcut(QKeySequence("F12"), self)
        self.dev_tool_shortcut.activated.connect(self.edit_widget.show)

        self.ui.bookmark_widget.itemDoubleClicked.connect(self.link_connect)
        self.ui.bookmark_widget.itemClicked.connect(self.bookmark_edit)
        self.isActive = False

        self.ui.not_select_profile.clicked.connect(self.no_profile)
        self.ui.profile_change.clicked.connect(self.profile_change)
        self.ui.select_profile.itemClicked.connect(self.profile_select)
        self.ui.opacity.valueChanged.connect(self.set_opacity)
    
    @Slot(int)
    def loading(self, prog):
        print(":load progress", prog)
        self.ui.load_progress_bar.setValue(prog)

    
    def show_web_window(self):
        pass

    def set_tab_url(self):
        self.url = self.background_view_widget.url()

        self.background_view_widget.close()
        self.background_view_widget.deleteLater()
        self.match_page.deleteLater()
        del self.background_view_widget
        
        self.ui.view_widget.setUrl(self.url)
        

    def update_icon(self):
        self.setWindowIcon(self.ui.view_widget.page().icon())

    def update_title(self):
        self.setWindowTitle(self.ui.view_widget.page().title())

    def run_js(self):
        text = self.text_widget.toPlainText()
        self.ui.view_widget.page().runJavaScript(text)


    def window_stay_on_top(self):
        if self.ui.stay_on_top.isChecked():
            self.setWindowFlag(Qt.WindowStaysOnTopHint)
            self.show()
        else:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            self.show()

    def set_opacity(self):
        self.setWindowOpacity(self.ui.opacity.value()/100)

    def change_widget(self):
        self.ui.right_menu.setCurrentWidget(self.ui.setting_area)

    def save(self):
        with open(f"{self.profile_path}save.json","w",encoding="utf-8") as save:
                json.dump(self.profile_list, save, indent="\t")

    def set_profile(self):
        self.password = self.password_widget.profile_password_line.text()

        if self.password == self.profile_list[self.profile_num]['password']:
            self.password_widget.close()
            
            if "page" in dir(self):
                self.page.deleteLater()
                self.profile.deleteLater()

            self.profile = QWebEngineProfile("storage-{0}".format(self.profile_list[self.profile_num]["storagenum"]), self.ui.view_widget)

            self.page = QWebEnginePage(self.profile, self.ui.view_widget)

            self.page.fullScreenRequested.connect(self.fullscreen)
            self.page.profile().downloadRequested.connect(self.on_downloadRequested)
            self.page.fullScreenRequested.connect(lambda request: request.accept())
            os_info = "Windows NT 10.0; Win64; x64"
            self.page.profile().setHttpUserAgent(f"Mozilla/5.0 ({os_info}; rv:90.0) Gecko/20100101 Firefox/90.0")
            
            self.ui.view_widget.setPage(self.page)
            self.ui.view_widget.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
            self.ui.view_widget.setUrl(QUrl("https:/www.google.com"))
            
            self.ui.bookmark_widget.clear()
            
            if len(self.profile_list) > 0:
                for i in range(0,len(self.profile_list[self.profile_num]["bookmarks"])):
                    item = QListWidgetItem(self.profile_list[self.profile_num]["bookmarks"][i]["name"])
                    try:
                        session = requests.Session()
                        respone = session.get(self.profile_list[self.profile_num]["bookmarks"][i]['icon'], headers={'User-Agent': 'Mozilla/5.0'})
                        data = respone.content
                        pixmap = QPixmap()
                        pixmap.loadFromData(data)
                        icon = QIcon(pixmap)
                        item.setIcon(icon)
                    except:
                        print(self.profile_list[self.profile_num]["bookmarks"][i]["icon"])
            

                    self.ui.bookmark_widget.addItem(item)
            self.ui.profile_name_line.setText(self.profile_list[self.profile_num]['name'])

            self.ui.right_menu.setCurrentWidget(self.ui.setting_area)
            self.ui.profile_back_button.setMaximumHeight(self.ui.profile_back_max)      
        else:
            self.password_widget.password_error.setText("<p style=\"color:red;\">비밀번호가 틀렸습니다.</p>")
            print("비밀번호 아님")

    def profile_select(self):
        num = self.ui.select_profile.currentRow()
        if num == self.ui.select_profile.count()-1:

            self.add_profile_widget.show()
        else:         

            self.profile_num = num
            name = self.profile_list[self.profile_num]['name']
            self.password_widget.profile_name.setText(name) 
            self.password_widget.profile_password_line.setText('')
            self.password_widget.password_error.setText("")
            self.password_change_widget.profile_name.setText(name)

            self.password_widget.show()

    def profile_name_change(self):
        profile_name = self.ui.profile_name_line.text()
        self.profile_list[self.profile_num]["name"] =  profile_name
        self.ui.select_profile.item(self.profile_num).setText(profile_name)
        self.save()

    def profile_remove(self):
        self.delete_path_list = []
        page = QWebEnginePage()
        self.ui.view_widget.setPage(page)
        self.delete_path_list.append(self.page.profile().persistentStoragePath())
    
        del self.profile_list[self.profile_num]

        self.save()
        self.ui.select_profile.takeItem(self.profile_num)
        self.ui.right_menu.setCurrentWidget(self.ui.profile_widget)

    def add_profile(self):
        profile_info = dict()
        name = self.add_profile_widget.profile_name_line.text()
        password = self.add_profile_widget.profile_password_line.text()
        if name == '':
            self.add_profile_widget.close()
            return
        bookmarks = list() 
        profile_info["name"] = name
        profile_info["password"] = password
        profile_info["bookmarks"] = bookmarks
        profile_info["storagenum"] = self.ui.select_profile.count()

        self.profile_list.append(profile_info)
        self.ui.select_profile.insertItem(self.ui.select_profile.count()-1, name)
        self.save()
        self.add_profile_widget.close()

    def profile_change(self):
        self.ui.right_menu.setCurrentWidget(self.ui.profile_widget)
    
    def no_profile(self):
        page = QWebEnginePage()
        self.ui.view_widget.setPage(page)
        self.ui.view_widget.page().setUrl(QUrl("https://www.google.com"))
        self.ui.right_menu.setCurrentWidget(self.ui.setting_area)

    def password_change_show(self):
        self.password_change_widget.show()
 

    def password_change(self):
        
        password = self.password_change_widget.profile_password_line.text()
        new_password = self.password_change_widget.new_password_line.text()
        new_password_check = self.password_change_widget.new_password_check_line.text()

        if password == self.profile_list[self.profile_num]["password"] and new_password == new_password_check:
            self.profile_list[self.profile_num]["password"] = self.password_change_widget.new_password_line.text()
            self.password_change_widget.close()

        elif password != self.profile_list[self.profile_num]["password"]:
            self.password_change_widget.password_error.setText("<p style= \"color:red;\">비밀번호가 틀렸습니다.</p>")
        elif new_password != new_password_check:
            self.password_change_widget.new_password_check_error.setText("<p style= \"color:red;\">새 비밀번호랑 다릅니다.</p>")
        self.save()

    def link_connect(self):
        num = self.ui.bookmark_widget.currentRow()
        self.ui.view_widget.setUrl(QUrl(self.profile_list[self.profile_num]["bookmarks"][num]["url"]))

    def move_to_url(self):
        self.input_url = self.ui.url_edit.text()
        url_ok = False
        url = QUrl(self.input_url)
        print(len(self.input_url.split(".")))
        try:
            if self.input_url.split(":")[0] == "https" or self.input_url.split(":")[0] == "http":
                url_ok = True
            elif len(self.input_url.split("/")) != 1 or len(self.input_url.split(".")) != 1:
                conn = http.client.HTTPConnection(self.input_url)
                conn.request("HEAD", "/")
                r1 = conn.getresponse()
                print(r1.status, r1.reason)
                if r1.status == 200 or r1.status == 301 or r1.status == 302:
                    url.setScheme("http")
                    url_ok = True
        except:
            pass
            print("fail")

        if url_ok == True:
            self.ui.view_widget.setUrl(url)
        else:
            self.ui.view_widget.setUrl(f"https://www.google.com/search?q={self.input_url}")
        

    def fullscreen(self):
        if self.isActive:
            self.ui.top_frame.setMaximumHeight(50)
            self.showMaximized()
            self.setWindowOpacity(self.ui.opacity.value()/100)

            self.isActive = False

        else:
            self.ui.top_frame.setMaximumHeight(0)
            self.showFullScreen()
            self.setWindowOpacity(1)
            self.isActive = True

    def update_url_edit(self):
        print(self.ui.view_widget.url().toString())
        self.text = self.ui.view_widget.url().toString()
        self.ui.url_edit.setText(self.text)
        self.ui.url_edit.setCursorPosition(0)

    @Slot("QWebEngineDownloadItem*")
    def on_downloadRequested(self, download):
        old_path = download.url().path()  # download.path()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save File", old_path, download.mimeType()
        )
        type = download.downloadFileName().split('.')[-1] 
        dir = path.split('/')
        filename = dir[-1] + '.' + type
    

        if path:
            download.setDownloadFileName(filename)
            download.setDownloadDirectory(path.strip(filename))
            print(path)
            download.accept()

    def keyPressEvent(self, e):

        if e.key() == Qt.Key_F11:
            self.fullscreen()
        elif e.key() == Qt.Key_F11 and self.isFullScreen():
            self.ui.top_frame.setMaximumHeight(50)
            self.showMaximized()

        if e.key() == Qt.Key_Escape:
            print('esc')
            self.showNormal()
        if e.key() == Qt.Key_F5:
            self.ui.view_widget.reload()
        if e.key() == Qt.Key_Enter:
            self.link_connect()

    def bookmarks_clear(self):
        self.profile_list[self.profile_num]["bookmarks"] = list()
        self.ui.bookmark_widget.clear()
        self.save()

    def bookmark_delete(self):
        num = self.ui.bookmark_widget.currentRow()
        self.ui.bookmark_widget.takeItem(num)
        del self.profile_list[self.profile_num]["bookmarks"][num]
        self.save()
        
    def save_url(self):
        bookmark_list = self.profile_list[self.profile_num]["bookmarks"]
        for i in range(0,len(bookmark_list)):
            if self.text == bookmark_list[i]["name"]:
                return
        bookmark = dict()
        bookmark["name"] = self.ui.view_widget.page().title()
        bookmark["url"] = self.text
        bookmark["icon"] = self.ui.view_widget.iconUrl().toString()
        bookmark_list.append(bookmark)

        item = QListWidgetItem(bookmark["name"])
        item.setIcon(self.ui.view_widget.icon())

        self.ui.bookmark_widget.addItem(item)
        self.save()

    def save_load(self):        
        if self.ui.right_menu.maximumWidth() == 0:
            self.ui.right_menu.setMaximumWidth(250)
            self.ui.right_menu.setMinimumWidth(200)
        else:
            self.ui.right_menu.setMaximumWidth(0)
            self.ui.right_menu.setMinimumWidth(0)
            
    def bookmark_edit(self):
        self.ui.bookmark_name_line.setText(self.profile_list[self.profile_num]["bookmarks"][self.ui.bookmark_widget.currentRow()]["name"])

    def bookmark_name_change(self):
        self.profile_list[self.profile_num]["bookmarks"][self.ui.bookmark_widget.currentRow()]["name"] = self.ui.bookmark_name_line.text()
        self.ui.bookmark_widget.item(self.ui.bookmark_widget.currentRow()).setText(self.ui.bookmark_name_line.text())
        self.save()

    def add_tab(self):
        view = QWebEngineView()
        self.ui.stacked_view.addWidget(view)

    def closeEvent(self, event):
        self.ui.view_widget.close()
        self.ui.view_widget.deleteLater()
        if "profile" in dir(self):
            self.profile.deleteLater()
            self.page.deleteLater()

        event.accept()

class main(QObject):
    def __init__(self):
        super().__init__()
        self.view = list()
        self.view.append(AppMain(self))
        self.view[0].show()

    def new_window(self):
        self.view.append(AppMain(self))
        self.view[-1].show()
        self.view[-1].ui.view_widget.setPage(self.page)
        self.view[-1].profile_num = self.profile_num
        if self.profile_num != None:
            self.view[-1].password_widget.profile_password_line.setText(self.view[-1].profile_list[self.profile_num]['password']) 
            self.view[-1].set_profile()
        return self.view[-1].ui.view_widget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    Appmain = main()

    app.exec()
    
if 'delete_path_list' in dir(main):
    print('running delete process...')
    time.sleep(1)
    for i in range(0, len(main.delete_path_list)):
        shutil.rmtree(main.delete_path_list[i])
