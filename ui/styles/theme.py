
COLORS = {
    "bg_primary": "#0f0f0f",
    "bg_secondary": "#18181b",
    "bg_tertiary": "#27272a",
    "bg_card": "#1c1c1e",
    "bg_hover": "#2d2d30",
    "border": "#3f3f46",
    "border_light": "#52525b",
    "text_primary": "#fafafa",
    "text_secondary": "#a1a1aa",
    "text_muted": "#71717a",
    "accent": "#6366f1",
    "accent_hover": "#818cf8",
    "accent_soft": "rgba(99, 102, 241, 0.15)",
    "success": "#22c55e",
    "success_soft": "rgba(34, 197, 94, 0.15)",
    "warning": "#f59e0b",
    "warning_soft": "rgba(245, 158, 11, 0.15)",
    "danger": "#ef4444",
    "danger_soft": "rgba(239, 68, 68, 0.15)",
}


def get_stylesheet(font_family: str = "Poppins, Segoe UI, sans-serif") -> str:
    return f"""
    QWidget {{
        background-color: {COLORS["bg_primary"]};
        color: {COLORS["text_primary"]};
        font-family: {font_family};
    }}

    QMainWindow {{
        background-color: {COLORS["bg_primary"]};
        font-weight: 400;
    }}

    /* Labels */
    QLabel {{
        color: {COLORS["text_primary"]};
        font-size: 13px;
    }}

    QLabel[class="title"] {{
        font-size: 24px;
        font-weight: 600;
        color: {COLORS["text_primary"]};
    }}

    QLabel[class="subtitle"] {{
        font-size: 14px;
        color: {COLORS["text_secondary"]};
    }}

    QLabel[class="muted"] {{
        color: {COLORS["text_muted"]};
        font-size: 12px;
    }}

    
    /* Line edits */
    QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox {{
        background-color: {COLORS["bg_tertiary"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 13px;
        min-height: 20px;
        selection-background-color: {COLORS["accent"]};
    }}

    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
    QDateEdit:focus, QComboBox:focus {{
        border: 1px solid {COLORS["accent"]};
    }}

    QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover,
    QDateEdit:hover, QComboBox:hover {{
        border: 1px solid {COLORS["border_light"]};
    }}

    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {COLORS["bg_tertiary"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 4px;
        selection-background-color: {COLORS["accent_soft"]};
    }}

    QDateEdit::drop-down {{
        border: none;
    }}

    
    /* Text edit */
    QTextEdit, QPlainTextEdit {{
        background-color: {COLORS["bg_tertiary"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 10px;
        font-size: 13px;
        selection-background-color: {COLORS["accent"]};
    }}

    QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {COLORS["accent"]};
    }}

    
    /* Buttons */
    QPushButton {{
        background-color: {COLORS["bg_tertiary"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 10px 18px;
        font-size: 13px;
        font-weight: 500;
    }}

    QPushButton:hover {{
        background-color: {COLORS["bg_hover"]};
        border: 1px solid {COLORS["border_light"]};
    }}

    QPushButton:pressed {{
        background-color: {COLORS["border"]};
    }}

    QPushButton[class="primary"] {{
        background-color: {COLORS["accent"]};
        color: white;
        border: none;
    }}

    QPushButton[class="primary"]:hover {{
        background-color: {COLORS["accent_hover"]};
    }}

    QPushButton[class="primary"]:pressed {{
        background-color: #4f46e5;
    }}

    QPushButton[class="danger"] {{
        background-color: #cc0011;
        color: #f11111;
        border: none;
    }}

    QPushButton[class="danger"]:hover {{
        background-color: #cf1111;
    }}

    QPushButton:disabled {{
        background-color: {COLORS["bg_tertiary"]};
        color: {COLORS["text_muted"]};
        border: 1px solid {COLORS["border"]};
    }}

    /* Table */
    QTableWidget {{
        background-color: {COLORS["bg_secondary"]};
        alternate-background-color: {COLORS["bg_card"]};
        color: {COLORS["text_primary"]};
        gridline-color: {COLORS["border"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 12px;
        padding: 4px;
    }}

    QTableWidget::item {{
        padding: 10px 12px;
        font-size: 13px;
    }}

    QTableWidget::item:selected {{
        background-color: {COLORS["accent_soft"]};
        color: {COLORS["text_primary"]};
    }}

    QHeaderView::section {{
        background-color: {COLORS["bg_tertiary"]};
        color: {COLORS["text_secondary"]};
        padding: 12px 14px;
        font-size: 12px;
        font-weight: 600;
        border: none;
        border-bottom: 2px solid {COLORS["border"]};
    }}

    /* Scroll bars */
    QScrollBar:vertical {{
        background-color: {COLORS["bg_secondary"]};
        width: 10px;
        border-radius: 5px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background-color: {COLORS["border_light"]};
        border-radius: 5px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS["text_muted"]};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    QScrollBar:horizontal {{
        background-color: {COLORS["bg_secondary"]};
        height: 10px;
        border-radius: 5px;
        margin: 0;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {COLORS["border_light"]};
        border-radius: 5px;
        min-width: 30px;
    }}

    /* Group box */
    QGroupBox {{
        font-size: 13px;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 12px;
        margin-top: 12px;
        padding: 16px;
        padding-top: 24px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 14px;
        padding: 0 8px;
        background-color: {COLORS["bg_secondary"]};
        color: {COLORS["text_secondary"]};
    }}

    /* Tab widget */
    QTabWidget::pane {{
        background-color: {COLORS["bg_secondary"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 12px;
        top: -1px;
        padding: 12px;
    }}

    QTabBar::tab {{
        background-color: transparent;
        color: {COLORS["text_secondary"]};
        padding: 12px 20px;
        margin-right: 4px;
        font-size: 13px;
        font-weight: 500;
    }}

    QTabBar::tab:selected {{
        color: {COLORS["accent"]};
        background-color: {COLORS["bg_secondary"]};
        border: 1px solid {COLORS["border"]};
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }}

    QTabBar::tab:hover:!selected {{
        color: {COLORS["text_primary"]};
    }}

    /* Slider (for future use) */
    QSlider::groove:horizontal {{
        height: 6px;
        background: {COLORS["border"]};
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        background: {COLORS["accent"]};
        width: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }}

    /* Tool tip */
    QToolTip {{
        background-color: {COLORS["bg_tertiary"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}

    /* Frame / Card */
    QFrame[class="card"] {{
        background-color: {COLORS["bg_card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 12px;
        padding: 16px;
    }}

    QFrame[class="alert_warning"] {{
        background-color: {COLORS["warning_soft"]};
        border: 1px solid {COLORS["warning"]};
        border-radius: 8px;
        padding: 12px;
    }}

    QFrame[class="alert_danger"] {{
        background-color: {COLORS["danger_soft"]};
        border: 1px solid {COLORS["danger"]};
        border-radius: 8px;
        padding: 12px;
    }}
    """
