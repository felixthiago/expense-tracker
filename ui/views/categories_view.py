"""Categories view: list, add/edit, limits and alerts."""
from datetime import datetime
from decimal import Decimal

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)
from PyQt6.QtGui import QColor, QBrush

from core.database import session_scope
from core import repository as repo
from services.category_service import list_categories, create_category, update_category, delete_category
from ui.styles.theme import COLORS
from .expenses_view import _format_currency

class CategoryFormDialog(QDialog):
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.category = category
        self.setWindowTitle("Editar categoria" if category else "Nova categoria")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: Alimentação")
        form.addRow("Nome", self.name_edit)

        self.color_edit = QLineEdit()
        self.color_edit.setPlaceholderText("#6366f1")
        self.color_edit.setText("#6366f1")
        form.addRow("Cor (hex)", self.color_edit)

        self.limit_edit = QDoubleSpinBox()
        self.limit_edit.setRange(0, 99999999.99)
        self.limit_edit.setDecimals(2)
        self.limit_edit.setPrefix("R$ ")
        self.limit_edit.setSpecialValueText("Sem limite")
        self.limit_edit.setValue(0)
        form.addRow("Limite mensal (opcional)", self.limit_edit)

        layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Salvar")
        save.setProperty("class", "primary")
        save.clicked.connect(self._save)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

        if category:
            self.name_edit.setText(category.name)
            self.color_edit.setText(category.color or "#6366f1")
            self.limit_edit.setValue(float(category.monthly_limit or 0))

    def _save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Erro", "Informe o nome da categoria.")
            return
        color = self.color_edit.text().strip() or "#6366f1"
        if not color.startswith("#"):
            color = "#" + color
        limit = self.limit_edit.value()
        monthly_limit = Decimal(str(limit)) if limit > 0 else None
        if self.category:
            update_category(self.category.id, name=name, color=color, monthly_limit=monthly_limit)
        else:
            create_category(name, color=color, monthly_limit=monthly_limit)
        self.accept()


class CategoriesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)

        header = QHBoxLayout()
        title = QLabel("Categorias")
        title.setProperty("class", "title")
        title.setStyleSheet("font-size: 24px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch()
        self.add_btn = QPushButton("  Nova categoria")
        self.add_btn.setProperty("class", "primary")
        self.add_btn.clicked.connect(self._open_form)
        header.addWidget(self.add_btn)
        layout.addLayout(header)

        self.alert_frame = QFrame()
        self.alert_frame.setVisible(False)
        self.alert_layout = QVBoxLayout(self.alert_frame)
        layout.addWidget(self.alert_frame)

        self.table = QTableWidget()
        self.table.setColumnWidth(0, 200)
        self.table.setColumnCount(5)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(["Nome", "Cor", "Limite mensal", "Gasto atual*", "Ações"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        self.refresh()

    def _open_form(self, category=None):
        d = CategoryFormDialog(self, category)
        if d.exec():
            self.refresh()
            if self.main_window:
                self.main_window.refresh_current_view()

    def _delete_category(self, category_id: str):
        if QMessageBox.question(
            self, "Confirmar",
            "Excluir esta categoria? Despesas vinculadas precisarão ser reatribuídas ou removidas.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes:
            if delete_category(category_id):
                self.refresh()
                if self.main_window:
                    self.main_window.refresh_current_view()
            else:
                QMessageBox.warning(self, "Erro", "Categoria do sistema não pode ser excluída.")

    def refresh(self):
        categories = list_categories()
        self.table.setRowCount(len(categories))

        today = datetime.now().date()
        start_month = datetime(today.year, today.month, 1)
        end_month = datetime.now()

        with session_scope() as session:
            totals = repo.get_total_by_category_in_period(session, start_month, end_month)
            spent_by_cat = {cid: total for cid, _, total in totals}
            
        alert_widgets = []
        for row, cat in enumerate(categories):
            limit = cat.monthly_limit or Decimal("0")
            spent = spent_by_cat.get(str(cat.id), Decimal("0"))
            
            data = [
                cat.name,
                cat.color or "",
                _format_currency(limit) if float(limit) > 0 else "-",
                _format_currency(spent),
            ]
            
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                if col == 1:
                    item.setForeground(QColor(item.text() or "#000000"))
                self.table.setItem(row, col, item)

            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 0, 4, 0)
            edit_btn = QPushButton("Editar")
            edit_btn.clicked.connect(lambda checked, c=cat: self._open_form(c))
            del_btn = QPushButton("Excluir")
            del_btn.setProperty("class", "danger")
            del_btn.setEnabled(not getattr(cat, "is_system", True))
            del_btn.clicked.connect(lambda checked, cid=cat.id: self._delete_category(cid))
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(del_btn)
            self.table.setCellWidget(row, 4, actions)

        while self.alert_layout.count():
            item = self.alert_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if alert_widgets:
            self.alert_frame.setVisible(True)
            for name, spent, limit in alert_widgets:
                alert = QFrame()
                alert.setProperty("class", "alert_danger")
                alert.setStyleSheet(f"""
                    QFrame {{
                        background-color: {COLORS["danger_soft"]};
                        border: 1px solid {COLORS["danger"]};
                        border-radius: 8px;
                        padding: 12px;
                        margin-bottom: 8px;
                    }}
                """)
                alert_layout = QHBoxLayout(alert)
                alert_layout.addWidget(QLabel(f"Limite atingido/ultrapassado: {name} (gasto: R$ {spent:,.2f}, limite: R$ {limit:,.2f})"))
                self.alert_layout.addWidget(alert)
        else:
            self.alert_frame.setVisible(False)
