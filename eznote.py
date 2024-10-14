from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget,
                             QSplitter, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator,
                             QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QLabel)
from PyQt5.QtCore import Qt, QTimer, QFileSystemWatcher, QPoint, QSize
from PyQt5.QtGui import QIcon, QMouseEvent
import sys
import darkdetect
import markdown
import os

def apply_theme(app, theme):
    if theme == 'dark':
        colors = {
            'main_bg': '#121212',
            'main_text': '#FFFFFF',
            'border': '#292929',
            'navbar_bg': '#1E1E1E',
            'search_bg': '#121212',
            'search_border': '#5E5E5E',
            'button_hover': '#3D3D3D'
        }
    else:
        colors = {
            'main_bg': '#FFFFFF',
            'main_text': '#000000',
            'border': '#D0D0D0',
            'navbar_bg': '#F0F0F0',
            'search_bg': '#F5F5F5',
            'search_border': '#D0D0D0',
            'button_hover': '#D0D0D0'
        }

    stylesheet = f"""
        QMainWindow {{ 
            background-color: transparent; 
        }}
        
        #AppFrame {{
            background-color: {colors['main_bg']}; 
            color: {colors['main_text']}; 
            border: 1px solid {colors['border']};
            border-radius: 10px;
        }}
        
        .Navbar {{ 
            background-color: {colors['navbar_bg']}; 
            color: {colors['main_text']};
            border-bottom: 1px solid {colors['border']};
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }}
        
        .Sidebar {{ 
            background-color: {colors['main_bg']}; 
            color: {colors['main_text']}; 
            border: 1px solid {colors['border']};
            border-bottom-left-radius: 10px;
        }}
        .Sidebar::item:selected {{ 
            background-color: {colors['button_hover']}; 
            color: {colors['main_text']}; 
        }}
        .Sidebar QHeaderView::section {{
            background-color: {colors['main_bg']};
            color: {colors['main_text']};
            font-size: 16px;
            font-weight: bold;
            border: none;
        }}
        
        .TextEditor {{ 
            background-color: {colors['main_bg']}; 
            color: {colors['main_text']}; 
            border: 1px solid {colors['border']};
            border-bottom-right-radius: 10px;
        }}
        
        .SearchBar {{ 
            background-color: {colors['search_bg']}; 
            color: {colors['main_text']}; 
            border: 1px solid {colors['search_border']}; 
            border-radius: 15px;
            padding-left: 10px;
        }}
        
        .WindowButton {{ 
            background-color: transparent;
            border: none; 
            border-radius: 16px;
        }}
        .WindowButton:hover {{ 
            background-color: {colors['button_hover']}; 
        }}
        
        QSplitter::handle {{
            background-color: {colors['border']};
        }}
    """

    app.setStyleSheet(stylesheet)

class Navbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("Navbar")
        self.setProperty("class", "Navbar")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # App title
        self.title_label = QLabel("ezNote")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 24px; color: white;")
        layout.addWidget(self.title_label)

        # Add stretch to push everything else to the center and right
        layout.addStretch(1)

        # Search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search notes...")
        self.search_bar.setFixedWidth(300)
        self.search_bar.setProperty("class", "SearchBar")
        layout.addWidget(self.search_bar)

        # Add stretch to push window controls to the right
        layout.addStretch(1)

        # Settings button
        self.settings_button = QPushButton()
        self.settings_button.setProperty("class", "WindowButton")
        self.settings_button.clicked.connect(self.parent.toggle_theme)  # Assuming this method exists
        layout.addWidget(self.settings_button)

        # Window control buttons
        self.minimize_button = QPushButton()
        self.minimize_button.setProperty("class", "WindowButton")
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        layout.addWidget(self.minimize_button)

        self.maximize_button = QPushButton()
        self.maximize_button.setProperty("class", "WindowButton")
        self.maximize_button.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.maximize_button)

        self.close_button = QPushButton()
        self.close_button.setProperty("class", "WindowButton")
        self.close_button.clicked.connect(self.parent.close)
        layout.addWidget(self.close_button)

        self.setFixedHeight(50)

        self.start = QPoint(0, 0)
        self.pressing = False

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            end = self.mapToGlobal(event.pos())
            movement = end - self.start
            self.parent.setGeometry(self.parent.x() + movement.x(),
                                    self.parent.y() + movement.y(),
                                    self.parent.width(),
                                    self.parent.height())
            self.start = end

    def mouseReleaseEvent(self, event):
        self.pressing = False

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def set_icons(self, theme):
        icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'icons', theme)
        self.settings_button.setIcon(QIcon(os.path.join(icon_dir, 'settings_icon_32.svg')))
        self.minimize_button.setIcon(QIcon(os.path.join(icon_dir, 'minimize_icon_32.svg')))
        self.maximize_button.setIcon(QIcon(os.path.join(icon_dir, 'maximize_icon_32.svg')))
        self.close_button.setIcon(QIcon(os.path.join(icon_dir, 'exit_icon_32.svg')))

        # Set sizes for settings and maximize buttons
        for button in [self.settings_button, self.maximize_button]:
            button.setIconSize(QSize(16, 16))
            button.setFixedSize(32, 32)

        # Set larger sizes for minimize and close buttons
        for button in [self.minimize_button, self.close_button]:
            button.setIconSize(QSize(20, 20))  # Increase icon size
            button.setFixedSize(36, 36)  # Increase button size

class Sidebar(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent  # Store reference to main window
        self.setObjectName("Sidebar")
        self.setProperty("class", "Sidebar")
        self.setHeaderLabel("Notebooks")
        self.setColumnCount(1)
        self.itemClicked.connect(self.on_item_clicked)
        
        self.setHeaderHidden(False)
        header = self.header()
        header.setDefaultSectionSize(30)
        header.setStretchLastSection(True)
        self.setSortingEnabled(False)

    def load_notebooks_and_notes(self, notes_dir):
        self.clear()
        self.load_directory(notes_dir, self.invisibleRootItem(), is_root=True)

    def load_directory(self, path, parent, is_root=False):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                notebook_item = QTreeWidgetItem(parent, [item])
                self.load_directory(item_path, notebook_item)
            elif not is_root and item.endswith('.md'):
                QTreeWidgetItem(parent, [item[:-3]])  # Remove .md extension

    def on_item_clicked(self, item, column):
        path = self.get_item_path(item)
        if os.path.isdir(path):  # This is a notebook
            item.setExpanded(not item.isExpanded())  # Toggle expansion
        else:  # This is a note
            self.main_window.load_note(path + '.md')

    def get_item_path(self, item):
        if item is None:
            return None
        path = []
        while item is not None:
            path.append(item.text(0))
            item = item.parent()
        return os.path.join(self.main_window.notes_dir, *reversed(path))

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
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Determine and set the theme
        self.theme = "dark" if darkdetect.isDark() else "light"

        # Define the notes_dir attribute (update this path as needed)
        self.notes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes")
        
        # Create the notes directory if it doesn't exist
        if not os.path.exists(self.notes_dir):
            os.makedirs(self.notes_dir)

        # Create main widget and layout
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add padding
        main_layout.setSpacing(0)

        # Create the app frame
        self.app_frame = QWidget()
        self.app_frame.setObjectName("AppFrame")
        app_frame_layout = QVBoxLayout(self.app_frame)
        app_frame_layout.setContentsMargins(0, 0, 0, 0)
        app_frame_layout.setSpacing(0)

        # Add navbar (now acting as custom title bar)
        self.navbar = Navbar(self)
        app_frame_layout.addWidget(self.navbar)

        # Initialize the watcher before using it
        self.watcher = QFileSystemWatcher(self)
        self.watcher.addPath(self.notes_dir)
        self.watcher.directoryChanged.connect(self.on_directory_changed)

        # Create and set up the sidebar
        self.sidebar = Sidebar(self)
        
        # Define icon directory
        self.icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'icons', self.theme)

        # Load notebooks and notes
        self.load_notebooks_and_notes()

        # Create the main text editing area
        self.text_area = QTextEdit(self)
        self.text_area.setAcceptRichText(True)
        self.text_area.textChanged.connect(self.update_preview)
        self.text_area.setProperty("class", "TextEditor")

        # Create and set up the splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.text_area)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setHandleWidth(1)  # Set handle width to 1px

        # Add splitter to app frame layout
        app_frame_layout.addWidget(self.splitter)

        # Add app frame to main layout
        main_layout.addWidget(self.app_frame)

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
        self.sidebar.load_notebooks_and_notes(self.notes_dir)
        self.update_watched_paths()

    def update_watched_paths(self):
        for path in self.watcher.directories():
            self.watcher.removePath(path)
        
        self.watcher.addPath(self.notes_dir)
        
        for root, dirs, files in os.walk(self.notes_dir):
            for dir in dirs:
                self.watcher.addPath(os.path.join(root, dir))

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
        self.navbar.set_icons(self.theme)

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        apply_theme(self, self.theme)
        self.set_icons()
        # Update other UI elements as needed

    def load_note(self, path):
        self.current_note_path = path
        self.load_note_content()

def create_app():
    app = QApplication(sys.argv)
    editor = MarkdownEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    create_app()