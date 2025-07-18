import os
import sys
import requests
import zipfile
import rarfile
import py7zr
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QComboBox, 
                             QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                             QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSize
from PyQt6.QtGui import QFont, QIcon

REPO_URL = ''
API_URL = f''
GITHUB_TOKEN = ''

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DownloadWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, folder_name, save_dir):
        super().__init__()
        self.folder_name = folder_name
        self.save_dir = save_dir
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        if GITHUB_TOKEN:
            self.headers['Authorization'] = f'token {GITHUB_TOKEN}'

    def run(self):
        try:
            folder_api_url = f'{API_URL}{self.folder_name}'
            self.download_folder_recursively(folder_api_url, self.save_dir)
            self.progress.emit('<font color="#00ff00">✅ Download complete. Extracting archives...</font>')
            self.extract_all_archives(self.save_dir)
            self.progress.emit('<font color="#00ff00">🎉 Patching complete! You can close this window.</font>')
        except Exception as e:
            self.error.emit(f'An error occurred: {e}')
        finally:
            self.finished.emit()

    def download_folder_recursively(self, folder_url, save_dir):
        response = requests.get(folder_url, headers=self.headers)
        response.raise_for_status()
        items = response.json()
        for item in items:
            item_name = item['name']
            item_path = os.path.join(save_dir, item_name)
            if item['type'] == 'file':
                self.download_file(item['download_url'], item_path)
            elif item['type'] == 'dir':
                os.makedirs(item_path, exist_ok=True)
                self.download_folder_recursively(item['url'], item_path)

    def download_file(self, url, save_path):
        try:
            filename = os.path.basename(save_path)
            self.progress.emit(f'<font color="#ffffff">⏳ Downloading: {filename}</font>')
            response = requests.get(url, headers=self.headers, stream=True)
            response.raise_for_status()
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download {os.path.basename(save_path)}: {e}")

    def extract_all_archives(self, directory):
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                extracted = False
                try:
                    if file.lower().endswith('.rar'):
                        self.progress.emit(f'<font color="#ffffff">Unpacking {file}...</font>')
                        with rarfile.RarFile(file_path, 'r') as rar_ref:
                            rar_ref.extractall(root)
                        extracted = True
                    elif file.lower().endswith('.zip'):
                        self.progress.emit(f'<font color="#ffffff">Unpacking {file}...</font>')
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(root)
                        extracted = True
                    elif file.lower().endswith('.7z'):
                        self.progress.emit(f'<font color="#ffffff">Unpacking {file}...</font>')
                        with py7zr.SevenZipFile(file_path, mode='r') as z_ref:
                            z_ref.extractall(path=root)
                        extracted = True
                    if extracted:
                        os.remove(file_path)
                        self.handle_subfolder_after_extraction(root, file)
                except Exception as e:
                    self.progress.emit(f'<font color="red">Could not extract {file}: {e}</font>')

    def handle_subfolder_after_extraction(self, parent_dir, archive_filename):
        potential_folder_name = os.path.splitext(archive_filename)[0]
        subfolder_path = os.path.join(parent_dir, potential_folder_name)
        if os.path.isdir(subfolder_path):
            self.progress.emit(f'<font color="#ffffff">Organizing files from {potential_folder_name}...</font>')
            for item in os.listdir(subfolder_path):
                src_path = os.path.join(subfolder_path, item)
                dst_path = os.path.join(parent_dir, item)
                if os.path.exists(dst_path):
                    if os.path.isdir(dst_path): shutil.rmtree(dst_path)
                    else: os.remove(dst_path)
                shutil.move(src_path, dst_path)
            try:
                os.rmdir(subfolder_path)
            except OSError:
                pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('OnlineFix | Bypass')
        self.setFixedSize(420, 420)
        self.all_game_names = []
        self.download_worker = None
        self.init_ui()
        self.load_game_list()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 10)
        self.main_layout.setSpacing(10)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search game patch here...")
        self.search_bar.textChanged.connect(self.filter_games)
        self.main_layout.addWidget(self.search_bar)

        self.game_choice = QComboBox()
        self.main_layout.addWidget(self.game_choice)

        dir_layout = QHBoxLayout()
        self.directory_entry = QLineEdit()
        self.directory_entry.setPlaceholderText("Click BROWSE to select game folder")
        self.directory_entry.setReadOnly(True)
        dir_layout.addWidget(self.directory_entry)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setObjectName("BrowseButton")
        self.browse_button.clicked.connect(self.browse_folder)
        dir_layout.addWidget(self.browse_button)
        self.main_layout.addLayout(dir_layout)
        
        self.start_button = QPushButton("PATCH GAME")
        self.start_button.setObjectName("PatchButton")
        self.start_button.clicked.connect(self.start_download)
        self.main_layout.addWidget(self.start_button)
        
        self.status_label = QLabel()
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.status_label.setWordWrap(True)
        self.status_label.setTextFormat(Qt.TextFormat.RichText)
        self.main_layout.addWidget(self.status_label, 1)

        footer_label = QLabel("Made by Helstorm [Mike]")
        footer_label.setObjectName("FooterLabel")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(footer_label)
        
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D30;
            }
            QWidget {
                color: #F1F1F1;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
            }
            QLineEdit, QComboBox {
                background-color: #3F3F46;
                border: 1px solid #1E1E1E;
                border-radius: 4px;
                padding: 8px;
                min-height: 22px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #007ACC;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
            }
            #PatchButton, #BrowseButton {
                background-color: #555555;
                border: 1px solid #1E1E1E;
                border-radius: 4px;
                font-weight: bold;
            }
            #PatchButton {
                padding: 12px;
            }
            #BrowseButton {
                padding: 8px 12px;
                font-weight: normal;
            }
            #PatchButton:hover, #BrowseButton:hover {
                background-color: #6A6A6A;
            }
            #PatchButton:pressed, #BrowseButton:pressed {
                background-color: #4A4A4A;
            }
            #StatusLabel {
                background-color: #1E1E1E;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                padding: 10px;
                font-size: 9pt;
            }
            #FooterLabel {
                color: #8A8A8A;
                font-size: 8pt;
                margin-top: 5px;
            }
        """)

    def load_game_list(self):
        self.status_label.setText("<font color='#55aaff'>Fetching game list...</font>")
        QApplication.processEvents()
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            if GITHUB_TOKEN:
                headers['Authorization'] = f'token {GITHUB_TOKEN}'
            response = requests.get(API_URL, headers=headers)
            response.raise_for_status()
            files = response.json()
            self.all_game_names = sorted([file['name'] for file in files if file['type'] == 'dir'])
            self.game_choice.addItems(self.all_game_names)
            status_text = (
                f"<font color='#55aaff'>Fetching game list...</font><br>"
                f"<font color='#00ff00'>Found {len(self.all_game_names)} online fixes.</font><br>"
                f"<font color='#ffff00'>Ready! Select game and folder.</font>"
            )
            self.status_label.setText(status_text)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, 'Network Error', f'Failed to fetch game list from GitHub:\n{e}')
            self.status_label.setText('<font color="red">Error: Could not load game list.</font>')

    def filter_games(self):
        search_text = self.search_bar.text().lower()
        if not self.all_game_names: return
        filtered_games = [game for game in self.all_game_names if search_text in game.lower()]
        self.game_choice.clear()
        self.game_choice.addItems(filtered_games)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Your Game\'s Main Directory')
        if folder:
            self.directory_entry.setText(folder)

    def start_download(self):
        selected_folder = self.game_choice.currentText()
        save_dir = self.directory_entry.text()
        if not selected_folder:
            QMessageBox.warning(self, 'Input Error', 'Please select a game from the list.')
            return
        if not save_dir or not os.path.isdir(save_dir):
            QMessageBox.warning(self, 'Input Error', 'Please select a valid game directory.')
            return
        
        self.set_ui_enabled(False)
        self.status_label.setText(f'<font color="#55aaff">Starting patch for {selected_folder}...</font>')
        
        self.download_worker = DownloadWorker(selected_folder, save_dir)
        self.download_worker.progress.connect(self.update_status)
        self.download_worker.finished.connect(self.on_download_finished)
        self.download_worker.error.connect(self.on_download_error)
        self.download_worker.start()

    def set_ui_enabled(self, enabled):
        self.search_bar.setEnabled(enabled)
        self.game_choice.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
        self.start_button.setEnabled(enabled)

    def update_status(self, message):
        self.status_label.setText(message)

    def on_download_finished(self):
        self.set_ui_enabled(True)

    def on_download_error(self, error_message):
        self.status_label.setText(f'<font color="red">Error: Patch failed.</font>')
        QMessageBox.critical(self, 'Error', error_message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
