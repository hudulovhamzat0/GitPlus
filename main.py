# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import shutil
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QFileDialog,
    QMessageBox, QInputDialog, QGridLayout, QStatusBar, QMenuBar
)
from PySide6.QtCore import QThread, QObject, Signal, Slot
from PySide6.QtGui import QIcon, QAction, QTextCursor, QColor
import qtawesome as qta

# === Worker Class for Running Git Commands in Background ===
# This class runs git commands in a separate thread to prevent the GUI from freezing.
class GitWorker(QObject):
    # Signals to communicate with the main GUI thread
    output = Signal(str)
    error = Signal(str)
    finished = Signal()

    @Slot(list, str)
    def run_command(self, command, repo_path):
        """Runs a subprocess command and emits signals with the result."""
        try:
            # Replace 'git' with the full path if found
            if command[0] == 'git':
                command[0] = self.parent().git_path
            
            self.output.emit(f"🚀 Running: {' '.join(command)}\n")
            
            # Using shell=True on Windows for commands like 'where' or complex paths
            is_shell = sys.platform == "win32"

            result = subprocess.run(
                command,
                cwd=repo_path,
                capture_output=True,
                text=True,
                shell=is_shell,
                encoding='utf-8' # Ensure proper encoding
            )

            if result.returncode == 0:
                if result.stdout:
                    self.output.emit(result.stdout + "\n")
            else:
                if result.stderr:
                    self.error.emit(f"❌ Error: {result.stderr}\n")
                else:
                    self.error.emit(f"❌ Command failed with no specific error message.\n")

        except FileNotFoundError as e:
            self.error.emit(f"❌ File Not Found Error: {str(e)}. Is Git installed and in your PATH?\n")
        except Exception as e:
            self.error.emit(f"❌ An unexpected error occurred: {str(e)}\n")
        finally:
            self.finished.emit()

# === Main GUI Class ===
class GitPushGUI(QMainWindow):
    # Signal to trigger the worker thread
    command_requested = Signal(list, str)

    def __init__(self):
        super().__init__()
        self.repo_path = ""
        self.git_path = self.find_git_executable()
        self.all_buttons = []
        
        self.init_ui()
        self.init_worker()
        self.apply_stylesheet()
        self.load_settings()

    def init_ui(self):
        """Sets up the main user interface."""
        self.setWindowTitle("Git Push Helper Pro")
        self.setWindowIcon(qta.icon('fa5b.github', color='white'))
        self.resize(1000, 800)

        # --- Menu Bar ---
        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # --- Central Widget and Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- Title ---
        title_label = QLabel("🚀 Git Push Helper Pro")
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)

        # --- Input Fields ---
        # Repository Path
        path_layout = self._create_input_group("Repository Path:", "path_entry", self.browse_repository, "Browse...")
        self.path_entry = path_layout.itemAt(1).widget()
        main_layout.addLayout(path_layout)
        
        # Remote URL
        remote_layout = self._create_input_group("GitHub Repository URL:", "remote_entry")
        self.remote_entry = remote_layout.itemAt(1).widget()
        main_layout.addLayout(remote_layout)
        
        # Branch
        branch_layout = self._create_input_group("Branch:", "branch_entry")
        self.branch_entry = branch_layout.itemAt(1).widget()
        self.branch_entry.setText("main")
        main_layout.addLayout(branch_layout)

        # --- Buttons Grid ---
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(10)
        
        buttons_config = [
            {'text': "Status", 'icon': 'fa5s.chart-bar', 'func': self.check_git_status, 'tip': "Check the current git status."},
            {'text': "Init", 'icon': 'fa5s.magic', 'func': self.init_git_repo, 'tip': "Initialize a new git repository."},
            {'text': "Commit", 'icon': 'fa5s.save', 'func': self.add_and_commit, 'tip': "Add all changes and commit."},
            {'text': "History", 'icon': 'fa5s.history', 'func': self.show_commit_history, 'tip': "Show commit history."},
            {'text': "Push", 'icon': 'fa5s.rocket', 'func': self.push_to_github, 'tip': "Push changes to the remote repository."},
            {'text': "Pull", 'icon': 'fa5s.download', 'func': self.pull_from_remote, 'tip': "Pull changes from the remote repository."},
            {'text': "New Branch", 'icon': 'fa5s.code-branch', 'func': self.create_new_branch, 'tip': "Create and switch to a new branch."},
            {'text': "Switch Branch", 'icon': 'fa5s.exchange-alt', 'func': self.switch_branch, 'tip': "Switch to another branch."},
            {'text': "Delete Branch", 'icon': 'fa5s.trash-alt', 'func': self.delete_branch, 'tip': "Delete a local branch."},
            {'text': "Stash", 'icon': 'fa5s.box', 'func': self.stash_changes, 'tip': "Stash current changes."},
            {'text': "Pop Stash", 'icon': 'fa5s.box-open', 'func': self.apply_stash, 'tip': "Apply the latest stash."},
            {'text': "Clear Output", 'icon': 'fa5s.broom', 'func': self.clear_output, 'tip': "Clear the output terminal."},
        ]

        row, col = 0, 0
        for config in buttons_config:
            button = QPushButton(f" {config['text']}")
            button.setIcon(qta.icon(config['icon'], color='white'))
            button.clicked.connect(config['func'])
            button.setToolTip(config['tip'])
            button.setObjectName("commandButton")
            buttons_layout.addWidget(button, row, col)
            self.all_buttons.append(button)
            col += 1
            if col > 5:
                col = 0
                row += 1
        main_layout.addLayout(buttons_layout)

        # --- Output Text Area ---
        output_label = QLabel("Output:")
        main_layout.addWidget(output_label)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setObjectName("output")
        main_layout.addWidget(self.output_text, 1) # Give it stretch factor
        
        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        git_status = "✅ Git found" if self.git_path != "git" else "⚠️ Git not found in common locations"
        self.log_output(f"Welcome to Git Push Helper Pro! 🚀\n{git_status}: {self.git_path}\nSelect a repository to get started.\n" + "="*70 + "\n")

    def _create_input_group(self, label_text, entry_name, btn_callback=None, btn_text=None):
        """Helper to create a label, line edit, and optional button."""
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(150)
        entry = QLineEdit()
        entry.setObjectName(entry_name)
        
        layout.addWidget(label)
        layout.addWidget(entry)
        
        if btn_callback and btn_text:
            button = QPushButton(btn_text)
            button.clicked.connect(btn_callback)
            layout.addWidget(button)
            
        return layout

    def init_worker(self):
        """Sets up the background worker thread for git commands."""
        self.thread = QThread()
        self.worker = GitWorker()
        self.worker.moveToThread(self.thread)

        self.worker.output.connect(self.log_output)
        self.worker.error.connect(self.log_error)
        self.worker.finished.connect(self.on_command_finished)

        self.command_requested.connect(self.worker.run_command)
        
        self.thread.start()
    
    def on_command_finished(self):
        """Re-enables buttons after a command is done."""
        self.log_output("✅ Command finished.\n" + "="*70 + "\n")
        self.enable_buttons(True)

    def trigger_command(self, command):
        """Central function to run a git command via the worker thread."""
        if not self.repo_path:
            QMessageBox.critical(self, "Error", "Please select a repository first!")
            return
        
        self.enable_buttons(False)
        self.command_requested.emit(command, self.repo_path)
        
    @Slot(str)
    def log_output(self, message):
        self.output_text.moveCursor(QTextCursor.MoveOperation.End)
        self.output_text.setTextColor(QColor("#4CAF50")) # Green for success
        self.output_text.insertPlainText(message)
        self.output_text.ensureCursorVisible()

    @Slot(str)
    def log_error(self, message):
        self.output_text.moveCursor(QTextCursor.MoveOperation.End)
        self.output_text.setTextColor(QColor("#F44336")) # Red for errors
        self.output_text.insertPlainText(message)
        self.output_text.ensureCursorVisible()

    # --- Button Callbacks ---
    def check_git_status(self):
        self.log_output("\n" + "="*30 + " GIT STATUS " + "="*30 + "\n")
        self.trigger_command(['git', 'status'])
    
    def init_git_repo(self):
        self.log_output("\n" + "="*30 + " INITIALIZE GIT " + "="*30 + "\n")
        self.trigger_command(['git', 'init'])

    def add_and_commit(self):
        commit_msg, ok = QInputDialog.getText(self, "Commit Message", 
                                              "Enter commit message:", 
                                              QLineEdit.EchoMode.Normal, "Update files")
        if ok and commit_msg:
            self.log_output("\n" + "="*30 + " ADD & COMMIT " + "="*30 + "\n")
            self.trigger_command(['git', 'add', '.'])
            # We need to chain commands, this requires a more complex worker.
            # For simplicity, we trigger commit right after. A better way is a command queue.
            self.trigger_command(['git', 'commit', '-m', commit_msg])

    def push_to_github(self):
        remote_url = self.remote_entry.text().strip()
        branch = self.branch_entry.text().strip()
        if not remote_url:
            QMessageBox.critical(self, "Error", "Please enter a GitHub repository URL!")
            return
        self.log_output("\n" + "="*30 + " PUSHING TO GITHUB " + "="*30 + "\n")
        self.trigger_command(['git', 'remote', 'set-url', 'origin', remote_url])
        self.trigger_command(['git', 'push', '-u', 'origin', branch])

    def show_commit_history(self):
        self.log_output("\n" + "="*30 + " COMMIT HISTORY " + "="*30 + "\n")
        self.trigger_command(['git', 'log', '--pretty=format:%h | %an | %ad | %s', '--date=short', '-n', '15'])
    
    def pull_from_remote(self):
        self.log_output("\n" + "="*30 + " GIT PULL " + "="*30 + "\n")
        self.trigger_command(['git', 'pull'])

    def create_new_branch(self):
        branch_name, ok = QInputDialog.getText(self, "New Branch", "Enter new branch name:")
        if ok and branch_name:
            self.log_output(f"\n{'='*30} CREATE NEW BRANCH {'='*30}\n")
            self.trigger_command(['git', 'checkout', '-b', branch_name])
            self.branch_entry.setText(branch_name)

    def switch_branch(self):
        branch_name, ok = QInputDialog.getText(self, "Switch Branch", "Enter branch name:")
        if ok and branch_name:
            self.log_output(f"\n{'='*30} SWITCH BRANCH {'='*30}\n")
            self.trigger_command(['git', 'checkout', branch_name])
            self.branch_entry.setText(branch_name)

    def delete_branch(self):
        branch_name, ok = QInputDialog.getText(self, "Delete Branch", "Enter branch to delete:")
        if ok and branch_name:
            self.log_output(f"\n{'='*30} DELETE BRANCH {'='*30}\n")
            self.trigger_command(['git', 'branch', '-d', branch_name])

    def stash_changes(self):
        self.log_output(f"\n{'='*30} STASH CHANGES {'='*30}\n")
        self.trigger_command(['git', 'stash'])

    def apply_stash(self):
        self.log_output(f"\n{'='*30} APPLY STASH {'='*30}\n")
        self.trigger_command(['git', 'stash', 'pop'])
        
    def clear_output(self):
        self.output_text.clear()
        self.status_bar.showMessage("Output cleared.", 3000)

    # --- Helper Functions ---
    def browse_repository(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Git Repository")
        if folder:
            self.repo_path = folder
            self.path_entry.setText(folder)
            self.log_output(f"Selected repository: {folder}\n")
            # Update remote and branch info
            try:
                result = subprocess.run([self.git_path, 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=folder, capture_output=True, text=True, shell=sys.platform == "win32")
                if result.returncode == 0:
                    self.branch_entry.setText(result.stdout.strip())
                
                result = subprocess.run([self.git_path, 'remote', 'get-url', 'origin'], cwd=folder, capture_output=True, text=True, shell=sys.platform == "win32")
                if result.returncode == 0:
                    self.remote_entry.setText(result.stdout.strip())
            except Exception as e:
                self.log_error(f"Error reading repo info: {e}")
            self.save_settings()

    def find_git_executable(self):
        # This function is mostly unchanged
        if shutil.which("git"):
            return shutil.which("git")
        common_paths = [
            r"C:\Program Files\Git\bin\git.exe",
            r"C:\Program Files (x86)\Git\bin\git.exe",
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return "git" # Fallback to PATH

    def enable_buttons(self, enable=True):
        for btn in self.all_buttons:
            btn.setEnabled(enable)

    def save_settings(self):
        settings = {
            "repo_path": self.repo_path,
            "remote": self.remote_entry.text(),
            "branch": self.branch_entry.text()
        }
        with open("git_gui_settings.json", "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        try:
            with open("git_gui_settings.json", "r") as f:
                settings = json.load(f)
                self.repo_path = settings.get("repo_path", "")
                self.path_entry.setText(self.repo_path)
                self.remote_entry.setText(settings.get("remote", ""))
                self.branch_entry.setText(settings.get("branch", "main"))
        except FileNotFoundError:
            pass # No settings file yet
            
    def show_about(self):
        QMessageBox.about(self, "About Git Push Helper Pro",
            """
            <b>Git Push Helper Pro</b>
            <p>A modern GUI for managing your Git repositories.</p>
            <p>This version is built with Python and PySide6/Qt6.</p>
            <p>Original Tkinter app by: Hamzat Hudulov</p>
            <p>PySide6 conversion by: BO7MEDX</p>
            """
        )

    def closeEvent(self, event):
        """Ensure the background thread is terminated properly."""
        self.thread.quit()
        self.thread.wait()
        event.accept()

    def apply_stylesheet(self):
        """Applies a dark, modern stylesheet to the application."""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            #titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #4CAF50;
                padding-bottom: 10px;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                background-color: #404040;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                color: #f0f0f0;
            }
            QTextEdit#output {
                background-color: #1e1e1e;
                border: 1px solid #555;
                border-radius: 5px;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 13px;
            }
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #777;
            }
            QStatusBar {
                color: #ccc;
                font-size: 12px;
            }
            QMenuBar {
                background-color: #3c3c3c;
            }
            QMenuBar::item:selected {
                background-color: #555;
            }
            QMenu {
                background-color: #3c3c3c;
            }
            QMenu::item:selected {
                background-color: #4CAF50;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitPushGUI()
    window.show()
    sys.exit(app.exec())
