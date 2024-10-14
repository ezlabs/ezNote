from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget,
                             QSplitter, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator,
                             QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout)
from PyQt5.QtCore import Qt, QTimer, QFileSystemWatcher
from PyQt5.QtGui import QIcon
import sys
import darkdetect
import markdown
import os

def apply_theme(app, theme):
    if theme == 'dark':
        app.setStyleSheet("""
            QMainWindow, QWidget { background-color: #2E2E2E; color: #FFFFFF; }
            QTextEdit { background-color: #3E3E3E; color: #FFFFFF; border: none; }
            QTreeWidget { background-color: #3E3E3E; color: #FFFFFF; border: none; }
            QTreeWidget::item:selected { background-color: #4E4E4E; }
            QLineEdit { background-color: #3E3E3E; color: #FFFFFF; border: 1px solid #5E5E5E; }
            QPushButton { background-color: #4E4E4E; color: #FFFFFF; border: none; padding: 5px; }
            QPushButton:hover { background-color: #5E5E5E; }
        """)
    else:
        app.setStyleSheet("""
            QMainWindow, QWidget { background-color: #FFFFFF; color: #000000; }
            QTextEdit { background-color: #F5F5F5; color: #000000; border: none; }
            QTreeWidget { background-color: #F5F5F5; color: #000000; border: none; }
            QTreeWidget::item:selected { background-color: #E0E0E0; }
            QLineEdit { background-color: #F5F5F5; color: #000000; border: 1px solid #D0D0D0; }
            QPushButton { background-color: #E0E0E0; color: #000000; border: none; padding: 5px; }
            QPushButton:hover { background-color: #D0D0D0; }
        """)

class Navbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)

        # Add spacer on the left
        self.layout.addStretch(1)

        # Add search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search notes...")
        self.search_bar.setFixedWidth(300)
        self.layout.addWidget(self.search_bar)

        # Add spacer on the right
        self.layout.addStretch(1)

        # Add settings button
        self.settings_button = QPushButton(self)
        self.settings_button.setFixedSize(32, 32)
        self.layout.addWidget(self.settings_button)

        self.setFixedHeight(40)

    def set_icon(self, theme):
        icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'icons', theme)
        settings_icon_path = os.path.join(icon_dir, 'settings_icon_32.svg')
        self.settings_button.setIcon(QIcon(settings_icon_path))

class Sidebar(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Notebooks")
        self.setColumnCount(1)
        self.itemClicked.connect(self.on_item_clicked)

    def load_notebooks_and_notes(self, notes_dir):
        self.clear()
        self.load_directory(notes_dir, self, is_root=True)

    def load_directory(self, path, parent, is_root=False):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                notebook_item = QTreeWidgetItem(parent, [item])
                self.load_directory(item_path, notebook_item)
            elif not is_root and item.endswith('.md'):
                QTreeWidgetItem(parent, [item[:-3]])  # Remove .md extension

    def on_item_clicked(self, item, column):
        # This method will be connected to the MarkdownEditor's logic
        pass

    def get_item_path(self, item):
        if item is None:
            return None
        path = []
        while item is not None:
            path.append(item.text(0))
            item = item.parent()
        return os.path.join(self.parent().notes_dir, *reversed(path))

    def get_expanded_items(self):
        expanded = []
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            if item.isExpanded():
                expanded.append(self.get_item_path(item))
            iterator += 1
        return expanded

    def restore_expanded_items(self, expanded_paths):
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            if self.get_item_path(item) in expanded_paths:
                item.setExpanded(True)
            iterator += 1

    def restore_current_item(self, path):
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            if self.get_item_path(item) == path:
                self.setCurrentItem(item)
                break
            iterator += 1

    def search_notes(self, search_term):
        search_term = search_term.lower()
        self.collapseAll()
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            if search_term in item.text(0).lower():
                item.setHidden(False)
                parent = item.parent()
                while parent:
                    parent.setExpanded(True)
                    parent.setHidden(False)
                    parent = parent.parent()
            else:
                item.setHidden(True)
            iterator += 1

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ezNote")
        self.setGeometry(100, 100, 1000, 600)

        # Create the notes directory if it doesn't exist
        self.notes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes")
        os.makedirs(self.notes_dir, exist_ok=True)

        # Determine and set the theme
        self.theme = "dark" if darkdetect.isDark() else "light"
        
        # Create main widget and layout
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add navbar
        self.navbar = Navbar(self)
        main_layout.addWidget(self.navbar)

        # Create and set up the sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.itemClicked.connect(self.on_item_clicked)

        # Load notebooks and notes
        self.sidebar.load_notebooks_and_notes(self.notes_dir)

        # Set up file system watcher
        self.watcher = QFileSystemWatcher(self)
        self.watcher.addPath(self.notes_dir)
        self.watcher.directoryChanged.connect(self.on_directory_changed)

        # Create the main text editing area
        self.text_area = QTextEdit(self)
        self.text_area.setAcceptRichText(True)
        self.text_area.textChanged.connect(self.update_preview)

        # Create and set up the splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.text_area)
        self.splitter.setStretchFactor(1, 1)  # Make the text area expand more than the sidebar

        # Add splitter to main layout
        main_layout.addWidget(self.splitter)

        # Set the main widget as the central widget
        self.setCentralWidget(main_widget)

        # Apply the theme
        apply_theme(self, self.theme)
        self.set_icons()

        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_sidebar)

        self.current_note_path = None

    def load_notebooks_and_notes(self):
        self.sidebar.clear()
        self.load_directory(self.notes_dir, self.sidebar, is_root=True)
        self.update_watched_paths()

    def load_directory(self, path, parent, is_root=False):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                notebook_item = QTreeWidgetItem(parent, [item])
                self.load_directory(item_path, notebook_item)
            elif not is_root and item.endswith('.md'):
                QTreeWidgetItem(parent, [item[:-3]])  # Remove .md extension

    def update_watched_paths(self):
        for path in self.watcher.directories():
            self.watcher.removePath(path)
        
        self.watcher.addPath(self.notes_dir)
        
        for root, dirs, files in os.walk(self.notes_dir):
            for dir in dirs:
                self.watcher.addPath(os.path.join(root, dir))

    def on_item_clicked(self, item, column):
        path = self.sidebar.get_item_path(item)
        if os.path.isdir(path):  # This is a notebook
            self.text_area.setPlainText(f"Notebook: {item.text(0)}")
            self.current_note_path = None
        else:  # This is a note
            self.current_note_path = f"{path}.md"
            self.load_note_content()

    def get_item_path(self, item):
        if item is None:
            return None
        path = []
        while item is not None:
            path.append(item.text(0))
            item = item.parent()
        return os.path.join(self.notes_dir, *reversed(path))

    def load_note_content(self):
        if self.current_note_path and os.path.exists(self.current_note_path):
            with open(self.current_note_path, 'r', encoding='utf-8') as file:
                content = file.read()
            self.text_area.setPlainText(content)
        else:
            self.text_area.setPlainText("")

    def update_preview(self):
        self.update_timer.start(300)
        if self.current_note_path:
            self.save_note_content()

    def save_note_content(self):
        if self.current_note_path:
            content = self.text_area.toPlainText()
            with open(self.current_note_path, 'w', encoding='utf-8') as file:
                file.write(content)

    def render_markdown(self):
        raw_text = self.text_area.toPlainText()
        rendered_html = markdown.markdown(raw_text)
        self.text_area.blockSignals(True)
        self.text_area.setHtml(rendered_html)
        self.text_area.blockSignals(False)

    def on_directory_changed(self, path):
        print(f"Directory changed: {path}")
        self.update_timer.start(300)  # Wait 300 ms before updating

    def update_sidebar(self):
        current_item = self.sidebar.currentItem()
        current_path = self.sidebar.get_item_path(current_item) if current_item else None
        expanded_items = self.sidebar.get_expanded_items()

        self.sidebar.load_notebooks_and_notes(self.notes_dir)

        if current_path:
            self.sidebar.restore_current_item(current_path)
        self.sidebar.restore_expanded_items(expanded_items)

    def get_expanded_items(self):
        expanded = []
        iterator = QTreeWidgetItemIterator(self.sidebar)
        while iterator.value():
            item = iterator.value()
            if item.isExpanded():
                expanded.append(self.get_item_path(item))
            iterator += 1
        return expanded

    def restore_expanded_items(self, expanded_paths):
        iterator = QTreeWidgetItemIterator(self.sidebar)
        while iterator.value():
            item = iterator.value()
            if self.get_item_path(item) in expanded_paths:
                item.setExpanded(True)
            iterator += 1

    def restore_current_item(self, path):
        iterator = QTreeWidgetItemIterator(self.sidebar)
        while iterator.value():
            item = iterator.value()
            if self.get_item_path(item) == path:
                self.sidebar.setCurrentItem(item)
                break
            iterator += 1

    def search_notes(self):
        search_term = self.navbar.search_bar.text()
        self.sidebar.search_notes(search_term)

    def set_icons(self):
        self.navbar.set_icon(self.theme)
        # Add more icon settings here as needed
        # Add more icons here as needed

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        apply_theme(self, self.theme)
        self.setup_icons()
        # Update other UI elements as needed

def create_app():
    app = QApplication(sys.argv)
    editor = MarkdownEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    create_app()
