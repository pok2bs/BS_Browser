from import_pyside6 import *

class customWebView(QWebEngineView):
    def __init__(self):
        super().__init__()

    def contextMenuEvent(self, event):
        self.menu = self.createStandardContextMenu()

        self.menu.setStyleSheet("""
            QMenu{
                  background-color: rgb(250, 250, 250);
                  border-radius: 20px;
            }
            QMenu::item {
                    background-color: transparent;
                    padding:3px 20px;
                    margin:5px 10px;
            }
            QMenu::item:selected { background-color: gray; border-radius: 20px;}
        """)
        self.menu.actions()[0].setText("뒤로")

        self.menu.popup(event.globalPos())


    def createWindow(self, type_):

        if type_ == QWebEnginePage.WebBrowserWindow:

            return self.window().parent.new_window(profile = self.window().ui.view_widget.page().profile())
        if type_ == QWebEnginePage.WebBrowserTab:

            self.window().background_view_widget = QWebEngineView()
            self.window().background_view_widget.urlChanged.connect(self.window().set_tab_url)
            self.window().match_page = QWebEnginePage(self.window().ui.view_widget.page().profile())
            self.window().background_view_widget.setPage(self.window().match_page)

            return self.window().background_view_widget
        
        return QWebEngineView.createWindow(self, type_)