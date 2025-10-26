import sys
import os
from PyQt6.QtCore import QUrl, Qt, QSize, QSettings
from PyQt6.QtGui import QIcon, QAction, QKeySequence, QDesktopServices
from PyQt6.QtWidgets import (QApplication, QMainWindow, QToolBar, QLineEdit, 
                             QTabWidget, QVBoxLayout, QWidget, QPushButton,
                             QHBoxLayout, QProgressBar, QStyle, QMenu, 
                             QMessageBox, QFileDialog, QDialog, QLabel,
                             QListWidget, QDialogButtonBox, QInputDialog)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (QWebEngineProfile, QWebEngineSettings, 
                                   QWebEngineDownloadRequest)


class DownloadManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Menedżer pobierania")
        self.setGeometry(200, 200, 600, 400)
        self.downloads = []
        
        layout = QVBoxLayout()
        
        self.download_list = QListWidget()
        layout.addWidget(QLabel("Aktywne pobierania:"))
        layout.addWidget(self.download_list)
        
        btn_layout = QHBoxLayout()
        self.open_folder_btn = QPushButton("Otwórz folder")
        self.open_folder_btn.clicked.connect(self.open_download_folder)
        self.clear_btn = QPushButton("Wyczyść listę")
        self.clear_btn.clicked.connect(self.clear_list)
        btn_layout.addWidget(self.open_folder_btn)
        btn_layout.addWidget(self.clear_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QListWidget {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QLabel {
                color: #ffffff;
            }
        """)
    
    def add_download(self, filename, path):
        self.download_list.addItem(f"✓ {filename} → {path}")
        self.downloads.append(path)
    
    def open_download_folder(self):
        if self.downloads:
            folder = os.path.dirname(self.downloads[-1])
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
    
    def clear_list(self):
        self.download_list.clear()
        self.downloads.clear()


class HistoryDialog(QDialog):
    def __init__(self, history, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historia przeglądania")
        self.setGeometry(200, 200, 700, 500)
        self.parent_browser = parent
        
        layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.open_url)
        
        for url in reversed(history):
            self.history_list.addItem(url)
        
        layout.addWidget(QLabel(f"Historia ({len(history)} stron):"))
        layout.addWidget(self.history_list)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(self.close)
        
        clear_btn = QPushButton("Wyczyść historię")
        clear_btn.clicked.connect(self.clear_history)
        btn_box.addButton(clear_btn, QDialogButtonBox.ButtonRole.ActionRole)
        
        layout.addWidget(btn_box)
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QListWidget {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QLabel {
                color: #ffffff;
            }
        """)
    
    def open_url(self, item):
        if self.parent_browser:
            self.parent_browser.add_new_tab(item.text())
        self.close()
    
    def clear_history(self):
        self.history_list.clear()
        if self.parent_browser:
            self.parent_browser.history.clear()
        QMessageBox.information(self, "Historia", "Historia została wyczyszczona!")


class BookmarksDialog(QDialog):
    def __init__(self, bookmarks, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zakładki")
        self.setGeometry(200, 200, 700, 500)
        self.parent_browser = parent
        self.bookmarks = bookmarks
        
        layout = QVBoxLayout()
        
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.itemDoubleClicked.connect(self.open_bookmark)
        self.refresh_list()
        
        layout.addWidget(QLabel(f"Zapisane zakładki ({len(bookmarks)}):"))
        layout.addWidget(self.bookmarks_list)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(self.close)
        
        delete_btn = QPushButton("Usuń zaznaczoną")
        delete_btn.clicked.connect(self.delete_bookmark)
        btn_box.addButton(delete_btn, QDialogButtonBox.ButtonRole.ActionRole)
        
        layout.addWidget(btn_box)
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QListWidget {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QLabel {
                color: #ffffff;
            }
        """)
    
    def refresh_list(self):
        self.bookmarks_list.clear()
        for title, url in self.bookmarks:
            self.bookmarks_list.addItem(f"⭐ {title} - {url}")
    
    def open_bookmark(self, item):
        text = item.text()
        url = text.split(" - ", 1)[1] if " - " in text else ""
        if url and self.parent_browser:
            self.parent_browser.add_new_tab(url)
        self.close()
    
    def delete_bookmark(self):
        current = self.bookmarks_list.currentRow()
        if current >= 0:
            del self.bookmarks[current]
            self.refresh_list()


class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://start.duckduckgo.com/"))
        
        # Ustawienia przeglądarki
        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)
        self.setLayout(layout)
    
    def load_url(self, url):
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.browser.setUrl(QUrl(url))


class OneWebBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OneWeb Browser")
        self.setGeometry(100, 100, 1400, 900)
        
        # Historia i zakładki
        self.history = []
        self.bookmarks = []
        
        # Menedżer pobierania
        self.download_manager = DownloadManager(self)
        
        # Profil dla obsługi pobierania
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.downloadRequested.connect(self.download_requested)
        
        # Stylowanie
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QToolBar {
                background-color: #2d2d2d;
                border: none;
                spacing: 8px;
                padding: 8px;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
                background-color: #404040;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 40px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
            QTabWidget::pane {
                border: none;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #b0b0b0;
                border: none;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #404040;
            }
            QProgressBar {
                border: none;
                background-color: #2d2d2d;
                height: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
            }
        """)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        
        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Przyciski nawigacji
        back_btn = QPushButton("←")
        back_btn.setToolTip("Wstecz (Alt+Left)")
        back_btn.clicked.connect(self.navigate_back)
        toolbar.addWidget(back_btn)
        
        forward_btn = QPushButton("→")
        forward_btn.setToolTip("Dalej (Alt+Right)")
        forward_btn.clicked.connect(self.navigate_forward)
        toolbar.addWidget(forward_btn)
        
        reload_btn = QPushButton("⟳")
        reload_btn.setToolTip("Odśwież (Ctrl+R)")
        reload_btn.clicked.connect(self.reload_page)
        toolbar.addWidget(reload_btn)
        
        home_btn = QPushButton("⌂")
        home_btn.setToolTip("Strona główna")
        home_btn.clicked.connect(self.navigate_home)
        toolbar.addWidget(home_btn)
        
        # Przycisk bezpieczny
        self.secure_indicator = QLabel("🔒")
        self.secure_indicator.setToolTip("Połączenie bezpieczne")
        toolbar.addWidget(self.secure_indicator)
        
        # Pasek adresu
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Wyszukaj w DuckDuckGo lub wpisz adres URL...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        # Przycisk zakładki
        bookmark_btn = QPushButton("⭐")
        bookmark_btn.setToolTip("Dodaj zakładkę (Ctrl+D)")
        bookmark_btn.clicked.connect(self.add_bookmark)
        toolbar.addWidget(bookmark_btn)
        
        # Przycisk nowej karty
        new_tab_btn = QPushButton("+")
        new_tab_btn.setToolTip("Nowa karta (Ctrl+T)")
        new_tab_btn.clicked.connect(self.add_new_tab)
        toolbar.addWidget(new_tab_btn)
        
        # Przycisk pobierania
        downloads_btn = QPushButton("⬇")
        downloads_btn.setToolTip("Menedżer pobierania")
        downloads_btn.clicked.connect(self.show_downloads)
        toolbar.addWidget(downloads_btn)
        
        # Przycisk menu
        menu_btn = QPushButton("☰")
        menu_btn.setToolTip("Menu")
        menu_btn.clicked.connect(self.show_menu)
        toolbar.addWidget(menu_btn)
        
        # Pasek postępu
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        
        # Status bar
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #2d2d2d;
                color: #b0b0b0;
            }
        """)
        self.statusBar().showMessage("Gotowy")
        
        # Główny widget
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.tabs)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Skróty klawiszowe
        self.setup_shortcuts()
        
        # Pierwsza karta
        self.add_new_tab()
    
    def setup_shortcuts(self):
        shortcuts = [
            ("Ctrl+T", self.add_new_tab),
            ("Ctrl+W", lambda: self.close_tab(self.tabs.currentIndex())),
            ("Ctrl+R", self.reload_page),
            ("F5", self.reload_page),
            ("Ctrl+L", self.focus_url_bar),
            ("Ctrl+D", self.add_bookmark),
            ("Ctrl+H", self.show_history),
            ("Ctrl+B", self.show_bookmarks),
            ("Ctrl+Shift+Delete", self.clear_browsing_data),
            ("F11", self.toggle_fullscreen),
            ("Alt+Left", self.navigate_back),
            ("Alt+Right", self.navigate_forward),
            ("Ctrl+Tab", self.next_tab),
            ("Ctrl+Shift+Tab", self.prev_tab),
            ("Ctrl++", self.zoom_in),
            ("Ctrl+-", self.zoom_out),
            ("Ctrl+0", self.zoom_reset),
        ]
        
        for key, func in shortcuts:
            action = QAction(self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(func)
            self.addAction(action)
    
    def download_requested(self, download):
        path, _ = QFileDialog.getSaveFileName(
            self, "Zapisz plik", download.downloadFileName()
        )
        
        if path:
            download.setDownloadDirectory(os.path.dirname(path))
            download.setDownloadFileName(os.path.basename(path))
            download.accept()
            
            download.isFinishedChanged.connect(
                lambda: self.download_finished(download, path) if download.isFinished() else None
            )
            
            self.statusBar().showMessage(f"Pobieranie: {os.path.basename(path)}...")
    
    def download_finished(self, download, path):
        if download.state() == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            self.download_manager.add_download(os.path.basename(path), path)
            self.statusBar().showMessage(f"Pobrano: {os.path.basename(path)}", 5000)
            QMessageBox.information(self, "Pobieranie zakończone", 
                f"Plik został zapisany:\n{path}")
        else:
            self.statusBar().showMessage("Pobieranie anulowane", 5000)
    
    def add_new_tab(self, url="https://start.duckduckgo.com/"):
        tab = BrowserTab()
        if url:
            tab.load_url(url)
        
        index = self.tabs.addTab(tab, "Nowa karta")
        self.tabs.setCurrentIndex(index)
        
        # Połączenia sygnałów
        tab.browser.urlChanged.connect(lambda qurl, t=tab: self.update_url_bar(qurl, t))
        tab.browser.titleChanged.connect(lambda title, i=index: self.update_tab_title(title, i))
        tab.browser.loadProgress.connect(self.update_progress)
        tab.browser.loadFinished.connect(self.load_finished)
        tab.browser.loadStarted.connect(self.load_started)
        tab.browser.iconChanged.connect(lambda icon, i=index: self.update_tab_icon(icon, i))
    
    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()
    
    def tab_changed(self, index):
        if index >= 0:
            current_tab = self.tabs.widget(index)
            if current_tab:
                url = current_tab.browser.url().toString()
                self.url_bar.setText(url)
                self.update_secure_indicator(url)
    
    def navigate_back(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.browser.back()
    
    def navigate_forward(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.browser.forward()
    
    def reload_page(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.browser.reload()
    
    def navigate_home(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.load_url("https://start.duckduckgo.com/")
    
    def navigate_to_url(self):
        url = self.url_bar.text()
        current_tab = self.tabs.currentWidget()
        if current_tab:
            if ' ' in url or ('.' not in url and not url.startswith(('http://', 'https://'))):
                url = f"https://duckduckgo.com/?q={url}"
            current_tab.load_url(url)
    
    def update_url_bar(self, qurl, tab):
        if tab == self.tabs.currentWidget():
            url = qurl.toString()
            self.url_bar.setText(url)
            self.update_secure_indicator(url)
            if url not in self.history:
                self.history.append(url)
    
    def update_secure_indicator(self, url):
        if url.startswith("https://"):
            self.secure_indicator.setText("🔒")
            self.secure_indicator.setToolTip("Połączenie bezpieczne (HTTPS)")
        else:
            self.secure_indicator.setText("🔓")
            self.secure_indicator.setToolTip("Połączenie niezabezpieczone")
    
    def update_tab_title(self, title, index):
        if title:
            self.tabs.setTabText(index, title[:25] + "..." if len(title) > 25 else title)
    
    def update_tab_icon(self, icon, index):
        if not icon.isNull():
            self.tabs.setTabIcon(index, icon)
    
    def update_progress(self, progress):
        self.progress_bar.setValue(progress)
        self.statusBar().showMessage(f"Ładowanie... {progress}%")
    
    def load_started(self):
        self.progress_bar.show()
        self.statusBar().showMessage("Ładowanie...")
    
    def load_finished(self):
        self.progress_bar.hide()
        self.statusBar().showMessage("Gotowy", 2000)
    
    def focus_url_bar(self):
        self.url_bar.setFocus()
        self.url_bar.selectAll()
    
    def add_bookmark(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            title = current_tab.browser.title()
            url = current_tab.browser.url().toString()
            
            title, ok = QInputDialog.getText(self, "Dodaj zakładkę", 
                "Nazwa zakładki:", text=title)
            
            if ok and title:
                self.bookmarks.append((title, url))
                self.statusBar().showMessage(f"Dodano zakładkę: {title}", 3000)
                QMessageBox.information(self, "Zakładka", "Zakładka została dodana!")
    
    def show_bookmarks(self):
        dialog = BookmarksDialog(self.bookmarks, self)
        dialog.exec()
    
    def show_history(self):
        dialog = HistoryDialog(self.history, self)
        dialog.exec()
    
    def show_downloads(self):
        self.download_manager.show()
    
    def clear_browsing_data(self):
        reply = QMessageBox.question(self, "Wyczyść dane", 
            "Czy chcesz wyczyścić historię i dane przeglądania?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.history.clear()
            self.profile.clearHttpCache()
            QMessageBox.information(self, "Gotowe", "Dane przeglądania zostały wyczyszczone!")
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def next_tab(self):
        current = self.tabs.currentIndex()
        self.tabs.setCurrentIndex((current + 1) % self.tabs.count())
    
    def prev_tab(self):
        current = self.tabs.currentIndex()
        self.tabs.setCurrentIndex((current - 1) % self.tabs.count())
    
    def zoom_in(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.browser.setZoomFactor(current_tab.browser.zoomFactor() + 0.1)
    
    def zoom_out(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.browser.setZoomFactor(current_tab.browser.zoomFactor() - 0.1)
    
    def zoom_reset(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.browser.setZoomFactor(1.0)
    
    def show_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3c3c3c;
            }
        """)
        
        new_window = menu.addAction("🗔 Nowe okno")
        new_tab = menu.addAction("📄 Nowa karta (Ctrl+T)")
        menu.addSeparator()
        
        history = menu.addAction("📜 Historia (Ctrl+H)")
        bookmarks = menu.addAction("⭐ Zakładki (Ctrl+B)")
        downloads = menu.addAction("⬇ Pobrane pliki")
        menu.addSeparator()
        
        zoom_in = menu.addAction("🔍+ Powiększ (Ctrl++)")
        zoom_out = menu.addAction("🔍- Pomniejsz (Ctrl+-)")
        zoom_reset = menu.addAction("🔍 Resetuj (Ctrl+0)")
        menu.addSeparator()
        
        print_page = menu.addAction("🖨 Drukuj (Ctrl+P)")
        find = menu.addAction("🔎 Znajdź na stronie (Ctrl+F)")
        menu.addSeparator()
        
        clear_data = menu.addAction("🗑 Wyczyść dane (Ctrl+Shift+Del)")
        fullscreen = menu.addAction("⛶ Pełny ekran (F11)")
        menu.addSeparator()
        
        about = menu.addAction("ℹ O przeglądarce")
        
        action = menu.exec(self.mapToGlobal(self.sender().pos()))
        
        if action == new_window:
            new_browser = OneWebBrowser()
            new_browser.show()
        elif action == new_tab:
            self.add_new_tab()
        elif action == history:
            self.show_history()
        elif action == bookmarks:
            self.show_bookmarks()
        elif action == downloads:
            self.show_downloads()
        elif action == zoom_in:
            self.zoom_in()
        elif action == zoom_out:
            self.zoom_out()
        elif action == zoom_reset:
            self.zoom_reset()
        elif action == print_page:
            current_tab = self.tabs.currentWidget()
            if current_tab:
                current_tab.browser.page().printToPdf("page.pdf")
                self.statusBar().showMessage("Zapisano do page.pdf", 3000)
        elif action == find:
            self.focus_url_bar()
        elif action == clear_data:
            self.clear_browsing_data()
        elif action == fullscreen:
            self.toggle_fullscreen()
        elif action == about:
            QMessageBox.information(self, "O przeglądarce", 
                "OneWeb Browser v2.0\n\n"
                "Zaawansowana przeglądarka stworzona w Python + PyQt6\n\n"
                "Funkcje:\n"
                "• Wielozakładkowa nawigacja\n"
                "• Menedżer pobierania plików\n"
                "• Historia i zakładki\n"
                "• Wyszukiwanie DuckDuckGo\n"
                "• Wskaźnik bezpieczeństwa SSL\n"
                "• Pełny ekran i zoom\n"
                "• Eksport do PDF\n"
                "• Liczne skróty klawiszowe\n\n"
                "Szybka, bezpieczna i prywatna!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("OneWeb Browser")
    app.setOrganizationName("OneWeb")
    
    browser = OneWebBrowser()
    browser.show()
    
    sys.exit(app.exec())