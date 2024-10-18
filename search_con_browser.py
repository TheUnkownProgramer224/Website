import os
import sys
import cv2
import numpy as np
import pyautogui
import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QLineEdit, QApplication,
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QInputDialog, QTabWidget, QFileDialog, QTextEdit, QDialog, QColorDialog
)
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor
from PyQt5.QtCore import QUrl, Qt, QThread
from PyQt5.QtWebEngineWidgets import QWebEngineView

class LogoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap('Logo.png').scaled(50, 50, Qt.KeepAspectRatio)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

class Header(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        title_label = QLabel("Welcome to Horizon Browser")
        title_label.setFont(QFont("Arial", 20))
        title_label.setStyleSheet("color: blue;")
        layout.addWidget(title_label)
        layout.addStretch()
        self.setLayout(layout)

class TabbedBrowser(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.add_new_tab(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), 'search_con.html')), "Home")

    def add_new_tab(self, url, label="New Tab"):
        browser = QWebEngineView()
        browser.setUrl(url)
        self.addTab(browser, label)
        self.setCurrentWidget(browser)

    def close_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)
        elif self.count() == 1:
            self.setCurrentIndex(0)

class ScreenRecorder(QThread):
    def __init__(self):
        super().__init__()
        self.is_recording = False

    def run(self):
        screen_size = (1920, 1080)
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = os.path.join(os.path.expanduser("~"), "Captures", f"screen_recording_{now}.avi")

        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        out = cv2.VideoWriter(output_path, fourcc, 20.0, screen_size)

        while self.is_recording:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)

        out.release()

    def start_recording(self):
        self.is_recording = True
        self.start()

    def stop_recording(self):
        self.is_recording = False
        self.wait()

class AccountManager:
    def __init__(self):
        self.username = None

    def create_account(self, username):
        if username:
            self.username = username
            return True
        return False

    def get_username(self):
        return self.username or "Guest"

class SearchConBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Horizon Browser")
        self.setGeometry(100, 100, 1000, 900)

        self.tabs = TabbedBrowser(self)
        self.recorder = ScreenRecorder()
        self.account_manager = AccountManager()
        self.background_image = None
        self.dark_mode = False
        self.background_color = QColor(255, 255, 255)  # Default background color

        self.setup_ui()
        self.load_session()

    def setup_ui(self):
        self.background_label = QLabel(self)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(self.rect())
        self.set_background()

        header = Header(self)

        # Navigation buttons
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter Search Query...")
        self.url_bar.returnPressed.connect(self.perform_search)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.perform_search)

        self.record_btn = QPushButton("Start Recording")
        self.record_btn.clicked.connect(self.toggle_recording)

        add_tab_btn = QPushButton("+")
        add_tab_btn.setToolTip("New Tab")
        add_tab_btn.clicked.connect(self.add_new_tab)

        fullscreen_btn = QPushButton("Toggle Fullscreen")
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)

        background_btn = QPushButton("Set Background Image")
        background_btn.clicked.connect(self.set_background_image)

        account_btn = QPushButton("Account Settings")
        account_btn.clicked.connect(self.open_account_settings)

        dark_mode_btn = QPushButton("Toggle Dark Mode")
        dark_mode_btn.clicked.connect(self.toggle_dark_mode)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.open_settings)

        ai_chat_btn = QPushButton("Open AI Chat")
        ai_chat_btn.clicked.connect(self.open_ai_chat)

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(search_btn)
        nav_layout.addWidget(add_tab_btn)
        nav_layout.addWidget(self.record_btn)
        nav_layout.addWidget(fullscreen_btn)
        nav_layout.addWidget(background_btn)
        nav_layout.addWidget(account_btn)
        nav_layout.addWidget(dark_mode_btn)
        nav_layout.addWidget(settings_btn)
        nav_layout.addWidget(ai_chat_btn)

        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(header)
        central_layout.addLayout(nav_layout)
        central_layout.addWidget(self.tabs)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        self.background_label.lower()

    def set_background(self):
        self.setStyleSheet(f"background-color: {self.background_color.name()};")  # Set main window background color
        if self.background_image:
            self.background_label.setPixmap(QPixmap(self.background_image))
            self.background_label.setGeometry(0, 0, self.width(), self.height())
            self.background_label.show()
        else:
            self.background_label.hide()

    def set_background_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Background Image", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if file_name:
            self.background_image = file_name
            self.set_background()

    def open_settings(self):
        color = QColorDialog.getColor(self.background_color, self)
        if color.isValid():
            self.background_color = color
            self.set_background()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def open_account_settings(self):
        username, ok = QInputDialog.getText(self, "Account Settings", "Enter your username:")
        if ok and username:
            if self.account_manager.create_account(username):
                QMessageBox.information(self, "Success", f"Account created for {username}")
            else:
                QMessageBox.warning(self, "Error", "Account creation failed.")

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet("background-color: #2E2E2E; color: white;")
            self.tabs.setStyleSheet("background-color: #3E3E3E; color: white;")
        else:
            self.setStyleSheet("")
            self.tabs.setStyleSheet("")

    def open_ai_chat(self):
        chat_dialog = QDialog(self)
        chat_dialog.setWindowTitle("AI Chat")
        chat_dialog.setGeometry(200, 200, 400, 300)

        chat_layout = QVBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask me anything...")
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.process_ai_chat)

        self.chat_output = QTextEdit()
        self.chat_output.setReadOnly(True)

        chat_layout.addWidget(self.chat_output)
        chat_layout.addWidget(self.chat_input)
        chat_layout.addWidget(send_btn)

        chat_dialog.setLayout(chat_layout)
        chat_dialog.exec_()

    def process_ai_chat(self):
        user_input = self.chat_input.text()
        if user_input:
            # Here you can implement your AI logic
            response = f"You asked: {user_input}"  # Dummy response
            self.chat_output.append(f"You: {user_input}")
            self.chat_output.append(f"AI: {response}")
            self.chat_input.clear()

    def perform_search(self):
        search_query = self.url_bar.text().strip()
        if search_query:
            search_url = f"https://www.google.com/search?q={search_query}"
            self.tabs.add_new_tab(QUrl(search_url), search_query)

    def add_new_tab(self):
        self.tabs.add_new_tab(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), 'search_con.html')), "New Tab")

    def toggle_recording(self):
        if not self.recorder.is_recording:
            self.record_btn.setText("Stop Recording")
            self.recorder.start_recording()
        else:
            self.record_btn.setText("Start Recording")
            self.recorder.stop_recording()

    def load_session(self):
        # Load previous session data if available
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = SearchConBrowser()
    browser.show()
    sys.exit(app.exec_())
