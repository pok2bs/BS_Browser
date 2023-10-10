from import_pyside6 import *
from gui.main_window import MainWindow
from gui.sub_window.add_profile_window import add_profile_widget
from gui.sub_window.password_window import password_widget
from gui.sub_window.password_change_window import password_change_widget

import http.client, requests
import sys, json, shutil, time, os



class BrowserWindow (QMainWindow):
    new_profile_window = Signal(QWebEngineProfile)
    saved = Signal()
    def __init__(self, parent):
        super().__init__()
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"]= "--enable-logging --log-level=3"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--blink-settings=forceDarkModeEnabled=true, darkModeImagePolicy=2 --enable-logging --log-level=3"
        
        self.parent = parent
        self.profile_list = self.parent.profile_list

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

        if len(self.profile_list) > 0:
            for i in range(0,len(self.profile_list)):
                self.ui.select_profile.insertItem(i, self.profile_list[i]["name"])

        #웹뷰 설정
        self.ui.view_widget.page().fullScreenRequested.connect(self.fullscreen)
        self.ui.view_widget.page().profile().downloadRequested.connect(self.on_downloadRequested)
        self.ui.view_widget.urlChanged.connect(self.update_url_edit)
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
        self.shortcut.activated.connect(self.create_bookmark)
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

    def set_tab_url(self):

        #gui/main_window/안 customWebView의 createWindow()에 변수 생성 코드가 있음
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
        
        with open(f"{self.parent.save_path}save.json","w",encoding="utf-8") as save_:
                json.dump(self.profile_list, save_, indent="\t")
        self.saved.emit()

    def set_profile(self):
        self.password = self.password_widget.profile_password_line.text()

        if self.password == self.profile_list[self.profile_num]['password']:
            self.password_widget.close()

            profile = QWebEngineProfile("storage-{0}".format(self.profile_list[self.profile_num]["storagenum"]), self.ui.view_widget)

            page = QWebEnginePage(profile, self.ui.view_widget)

            profile.downloadRequested.connect(self.on_downloadRequested)

            os_info = "Windows NT 10.0; Win64; x64"
            profile.setHttpUserAgent(f"Mozilla/5.0 ({os_info}; rv:90.0) Gecko/20100101 Firefox/90.0")
            profile.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
            self.profile_path = profile.persistentStoragePath()

            page.fullScreenRequested.connect(self.fullscreen)
            page.fullScreenRequested.connect(lambda request: request.accept())

            
            if self.password_widget.is_new_window_show.isChecked():
                self.new_profile_window.emit(page.profile())
                self.profile_num = self.before_num
                return
            else:
                self.ui.view_widget.setPage(page)

            self.bookmarks_update()
            self.ui.view_widget.setUrl("https://google.com")
        else:
            self.password_widget.password_error.setText("<p style=\"color:red;\">비밀번호가 틀렸습니다.</p>")
            print("비밀번호 아님")

    def bookmarks_update(self):
            self.ui.bookmark_widget.clear()
            if len(self.profile_list) > 0:
                for bookmark in self.profile_list[self.profile_num]["bookmarks"]:
                    item = QListWidgetItem(bookmark["name"])
                    try:
                        session = requests.Session()
                        respone = session.get(bookmark['icon'], headers={'User-Agent': 'Mozilla/5.0'})
                        data = respone.content
                        pixmap = QPixmap()
                        pixmap.loadFromData(data)
                        icon = QIcon(pixmap)
                        item.setIcon(icon)
                    except:
                        print(bookmark["icon"])
            

                    self.ui.bookmark_widget.addItem(item)
            self.ui.profile_name_line.setText(self.profile_list[self.profile_num]['name'])

            self.ui.right_menu.setCurrentWidget(self.ui.setting_area)
            self.ui.profile_back_button.setMaximumHeight(self.ui.profile_back_max)      

    def profile_select(self):
        num = self.ui.select_profile.currentRow()
        if num == self.ui.select_profile.count()-1:

            self.add_profile_widget.show()
        else:         
            if "profile_num" in dir(self):
                self.before_num = self.profile_num
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
        self.parent.delete_path_list.append(self.save_path + "storage-{0}".format(self.profile_list[self.profile_num]["storagenum"]))
    
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
        profile_info["isLastProfile"] = False

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

        try:
            #예) https://exemple.com
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
        if len(self.profile_list[self.profile_num]["bookmarks"]) == 0:
            return
        num = self.ui.bookmark_widget.currentRow()
        del self.profile_list[self.profile_num]["bookmarks"][num]
        self.save()
        
    def create_bookmark(self):
        bookmark_list = self.profile_list[self.profile_num]["bookmarks"]
        for i in range(0,len(bookmark_list)):
            if self.text == bookmark_list[i]["name"]:
                return
        bookmark = dict()
        bookmark["name"] = self.ui.view_widget.page().title()
        bookmark["url"] = self.text
        bookmark["icon"] = self.ui.view_widget.iconUrl().toString()
        bookmark_list.append(bookmark)

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
        print(self.profile_num)
    
    def bookmark_name_change(self):
        self.profile_list[self.profile_num]["bookmarks"][self.ui.bookmark_widget.currentRow()]["name"] = self.ui.bookmark_name_line.text()
        self.ui.bookmark_widget.item(self.ui.bookmark_widget.currentRow()).setText(self.ui.bookmark_name_line.text())
        self.save()

    def closeEvent(self, event):
        self.saved.disconnect(self.parent.load)
        self.parent.close_num += 1
        if self.parent.close_num == len(self.parent.view):
            if self.profile_num is not None : self.profile_list[self.profile_num]["isLastProfile"] = True
            self.save()
            self.parent.closeEvent()
        event.accept()

class main(QObject):
    def __init__(self):
        super().__init__()
        self.view = list()
        profile = QWebEngineProfile()
        self.save_path = profile.defaultProfile().persistentStoragePath().rstrip("OffTheRecord")
        self.load()        
        self.view.append(BrowserWindow(self))
        self.view[0].saved.connect(self.load)
        self.view[0].show()
        self.view[0].new_profile_window.connect(self.new_window)
        
        self.close_num = 0
        self.delete_path_list = list()

    def load(self):
        try:
            with open(f"{self.save_path}save.json","r") as save:
                self.profile_list = json.load(save)

        except:
            self.profile_list = list()
            with open(f"{self.save_path}save.json","w",encoding="utf-8") as save:
                json.dump(self.profile_list, save, indent="\t")

        for view in self.view:
            if not view.profile_num is None: 
                view.bookmarks_update()

    @Slot(QWebEngineProfile)
    def new_window(self, profile):
        view = BrowserWindow(self)
        storage_name = profile.persistentStoragePath().split("/")[-1].lstrip("storage-")
        view.ui.view_widget.setPage(QWebEnginePage(profile, self.view[-1].ui.view_widget))
        view.new_profile_window.connect(self.new_window)
        view.saved.connect(self.load)
        
        if storage_name != "OffTheRecord":
            view.profile_num = int(storage_name) - 1
            print(storage_name)
            view.show()
            self.view.append(view)
            self.load()


        view.ui.view_widget.setUrl(QUrl("https:/www.google.com"))

        return view.ui.view_widget
    
    def closeEvent(self):
        print("close")
        for view in self.view:
            view.deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    Appmain = main()
    app.exec()

for path in Appmain.delete_path_list:
    shutil.rmtree(path)
