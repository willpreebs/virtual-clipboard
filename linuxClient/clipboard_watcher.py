import asyncio
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QClipboard

import api

class ClipboardWatcher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clipboard Watcher")
        self.resize(400, 300)

        self.clipboard = QApplication.clipboard()
        self.last_text = ""
        self.history = []

        # Timer to poll clipboard every 500ms when focused
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(500)

        # Basic UI to show history
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.setCentralWidget(self.text_area)

    def check_clipboard(self):
        if self.isActiveWindow():
            current = self.clipboard.text(QClipboard.Clipboard)
            if current and current != self.last_text:
                self.last_text = current
                self.history.append(current)
                print(f"New clipboard entry: {current}")
                asyncio.run(api.post_clipboard_item(current))
                self.update_history()

    def update_history(self):
        self.text_area.setPlainText("\n---\n".join(reversed(self.history)))
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    watcher = ClipboardWatcher()
    watcher.show()
    sys.exit(app.exec_())
