from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.views.dashboard_view import DashboardView
from ui.views.expenses_view import ExpensesView
from ui.views.categories_view import CategoriesView
from ui.styles.theme import get_stylesheet, COLORS
from ui.styles.fonts import load_fonts

class NavButton(QPushButton):
    def __init__(self, text: str, icon_char: str = "", parent=None):
        super().__init__(parent)
        self.setText(f"  {icon_char}  {text}" if icon_char else f"  {text}")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(44)
        self.setProperty("nav", True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense Tracker")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        font_family = load_fonts()
        self.setStyleSheet(get_stylesheet(font_family))

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(f"""
            QFrame#sidebar {{
                background-color: {COLORS["bg_secondary"]};
                border-right: 1px solid {COLORS["border"]};
            }}
            QPushButton[nav="true"] {{
                text-align: left;
                font-size: 20px;
                border: none;
                border-radius: 8px;
                margin: 8px 0px;
            }}
            QPushButton[nav="true"]:checked {{
                background-color: {COLORS["accent_soft"]};
                color: {COLORS["accent"]};
            }}
            QPushButton[nav="true"]:hover:!checked {{
                background-color: {COLORS["bg_hover"]};
            }}
        """)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 24, 12, 24)
        sidebar_layout.setSpacing(4)

        title = QLabel("Expense Tracker")
        title.setProperty("class", "title")
        title.setStyleSheet("font-size: 24px; font-weight: 900; margin: 8px 6px; color: #FFF; background-color: transparent; font-style: bold;")
        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(8)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")

        self.dashboard_view = DashboardView(self)
        self.expenses_view = ExpensesView(self)
        self.categories_view = CategoriesView(self)

        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.expenses_view)
        self.stack.addWidget(self.categories_view)

        nav_items = [
            ("Dashboard", "📊", 0),
            ("Expenses", "📝", 1),
            ("Categories", "📁", 2),
        ]

        self.nav_buttons = []
        for text, icon, index in nav_items:
            btn = self.create_nav_button(text, icon, index)
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        self.nav_buttons[0].setChecked(True)
        sidebar_layout.addStretch()
        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)
        self.dashboard_view.refresh()
        
    def _go_to(self, index: int):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.dashboard_view.refresh()
        elif index == 1:
            self.expenses_view.refresh()
        elif index == 2:
            self.categories_view.refresh()

    def refresh_current_view(self):
        idx = self.stack.currentIndex()
        if idx == 0:
            self.dashboard_view.refresh()
        elif idx == 1:
            self.expenses_view.refresh()
        elif idx == 2:
            self.categories_view.refresh()

    def create_nav_button(self, text: str, icon: str = "", index: int = 0) -> NavButton:
        btn = NavButton(text, icon)
        btn.clicked.connect(lambda checked, i = index: self._go_to(i))
        return btn
    