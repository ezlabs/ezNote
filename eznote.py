from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget
import sys
import darkdetect
import markdown
from PyQt5.QtCore import QTimer

def apply_theme(editor,theme):
        if theme == 'dark':
            editor.setStyleSheet("background-color: #2E2E2E; color: #FFFFFF;")
        else:
             editor.setStyleSheet("background-color: #FFFFFF; color: #000000;")

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set up the main window
        self.setWindowTitle("ezNote")
        self.setGeometry(100, 100, 800, 600)

        # Create the main text editing area
        self.text_area = QTextEdit(self)
        self.text_area.setAcceptRichText(True)
        self.text_area.textChanged.connect(self.update_preview)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.text_area)

        # Create a container for the layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Determine and apply the theme
        theme = "dark" if darkdetect.isDark() else "light"
        apply_theme(self.text_area, theme)

        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.render_markdown)

    def update_preview(self):
        self.update_timer.start(300)

    def render_markdown(self):
        raw_text = self.text_area.toPlainText()
        rendered_html = markdown.markdown(raw_text)
        self.text_area.blockSignals(True)
        self.text_area.setHtml(rendered_html)
        self.text_area.blockSignals(False)


def create_app():
    app = QApplication(sys.argv)
    editor = MarkdownEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    create_app()
