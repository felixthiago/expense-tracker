from datetime import datetime, date
from decimal import Decimal

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.expense_service import list_expenses, add_expense, update_expense, remove_expense, get_expense
from services.category_service import list_categories, get_category
from services.export_service import export_csv, export_pdf
from ui.styles.theme import COLORS


def _format_currency(value: Decimal) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class ExpenseFormDialog(QDialog):
    def __init__(self, parent=None, expense=None):
        super().__init__(parent)
        self.expense = expense
        self.setWindowTitle("Editar despesa" if expense else "Nova despesa")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0.01, 99999999.99)
        self.amount.setDecimals(2)
        self.amount.setPrefix("R$ ")
        form.addRow("Valor", self.amount)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(date.today())
        form.addRow("Data", self.date_edit)

        self.category_combo = QComboBox()
        self._load_categories()
        form.addRow("Categoria", self.category_combo)

        self.description = QLineEdit()
        self.description.setPlaceholderText("Descrição do gasto")
        form.addRow("Descrição", self.description)

        self.source = QLineEdit()
        self.source.setPlaceholderText("Sua fonte de pagamento")
        form.addRow("Banco", self.source)

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

        if expense:
            self.amount.setValue(float(expense.amount))
            self.date_edit.setDate(expense.date.date() if hasattr(expense.date, "date") else expense.date)
            idx = self.category_combo.findData(expense.category_id)
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
            self.description.setText(expense.description or "")
            self.source.setText(expense.source or "")

    def _load_categories(self):
        cats = list_categories()
        for c in cats:
            self.category_combo.addItem(c.name, c.id)

    def _save(self):
        amount = Decimal(str(self.amount.value()))
        dt = datetime.combine(self.date_edit.date().toPyDate(), datetime.min.time())
        cat_id = self.category_combo.currentData()
        if not cat_id:
            QMessageBox.warning(self, "Erro", "Selecione uma categoria.")
            return
        desc = self.description.text().strip()
        source = self.source.text().strip()
        if self.expense:
            update_expense(self.expense.id, amount=amount, date=dt, category_id=cat_id,
                           description=desc or None, source=source or None)
        else:
            add_expense(amount, dt, cat_id, desc, source)
        self.accept()


class ExpensesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)

        header = QHBoxLayout()
        title = QLabel("Despesas")
        title.setProperty("class", "title")
        title.setStyleSheet("font-size: 24px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch()
        self.add_btn = QPushButton("  Nova despesa")
        self.add_btn.setProperty("class", "primary")
        self.add_btn.clicked.connect(self._open_form)
        header.addWidget(self.add_btn)
        layout.addLayout(header)

        filters = QGroupBox("Filtros")
        filters_layout = QHBoxLayout(filters)
        self.filter_date_from = QDateEdit()
        self.filter_date_from.setCalendarPopup(True)
        self.filter_date_from.setDate(date.today().replace(day=1))
        self.filter_date_to = QDateEdit()
        self.filter_date_to.setCalendarPopup(True)
        self.filter_date_to.setDate(date.today())
        self.filter_category = QComboBox()
        self.filter_category.addItem("Todas", None)
        self.filter_apply = QPushButton("Aplicar")
        self.filter_apply.setProperty("class", "primary")
        self.filter_apply.clicked.connect(self.refresh)
        filters_layout.addWidget(QLabel("De:"))
        filters_layout.addWidget(self.filter_date_from)
        filters_layout.addWidget(QLabel("Até:"))
        filters_layout.addWidget(self.filter_date_to)
        filters_layout.addWidget(QLabel("Categoria:"))
        filters_layout.addWidget(self.filter_category, 1)
        filters_layout.addWidget(self.filter_apply)
        layout.addWidget(filters)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Data", "Valor", "Categoria", "Descrição", "Banco", "Ações"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        export_row = QHBoxLayout()
        export_row.addStretch()
        self.export_csv_btn = QPushButton("Exportar CSV")
        self.export_csv_btn.clicked.connect(self._export_csv)
        self.export_pdf_btn = QPushButton("Exportar PDF")
        self.export_pdf_btn.clicked.connect(self._export_pdf)
        export_row.addWidget(self.export_csv_btn)
        export_row.addWidget(self.export_pdf_btn)
        layout.addLayout(export_row)

        self._load_category_filter()
        self.refresh()

    def _load_category_filter(self):
        self.filter_category.clear()
        self.filter_category.addItem("Todas", None)
        for c in list_categories():
            self.filter_category.addItem(c.name, c.id)

    def _open_form(self, expense=None):
        d = ExpenseFormDialog(self, expense)
        if d.exec():
            self.refresh()
            if self.main_window:
                self.main_window.refresh_current_view()

    def _export_csv(self):
        try:
            path = export_csv(
                date_from=datetime.combine(self.filter_date_from.date().toPyDate(), datetime.min.time()),
                date_to=datetime.combine(self.filter_date_to.date().toPyDate(), datetime.max.time()),
                category_id=self.filter_category.currentData(),
            )
            QMessageBox.information(self, "Exportado", f"CSV salvo em:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def _export_pdf(self):
        try:
            path = export_pdf(
                date_from=datetime.combine(self.filter_date_from.date().toPyDate(), datetime.min.time()),
                date_to=datetime.combine(self.filter_date_to.date().toPyDate(), datetime.max.time()),
                category_id=self.filter_category.currentData(),
            )
            QMessageBox.information(self, "Exportado", f"PDF salvo em:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def _edit_row(self, row: int):
        expense_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        expense = get_expense(expense_id) if expense_id else None
        if expense:
            self._open_form(expense)

    def _delete_row(self, row: int):
        expense_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        if not expense_id:
            return
        if QMessageBox.question(
            self, "Confirmar",
            "Excluir esta despesa?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes:
            remove_expense(expense_id)
            self.refresh()
            if self.main_window:
                self.main_window.refresh_current_view()

    def refresh(self):
        date_from = datetime.combine(self.filter_date_from.date().toPyDate(), datetime.min.time())
        date_to = datetime.combine(self.filter_date_to.date().toPyDate(), datetime.max.time())
        cat_id = self.filter_category.currentData()
        expenses = list_expenses(date_from=date_from, date_to=date_to, category_id=cat_id)
        # print(expenses)
        self.table.setRowCount(len(expenses))
        for row, e in enumerate(expenses):
            category = get_category(str(e.category_id))

            self.table.setItem(row, 0, QTableWidgetItem(e.date.strftime("%d/%m/%Y") if e.date else ""))
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, e.id)
            self.table.setItem(row, 1, QTableWidgetItem(_format_currency(e.amount)))
            self.table.setItem(row, 2, QTableWidgetItem(str(category.name) if category else "no category relationship"))
            self.table.setItem(row, 3, QTableWidgetItem(str((e.description or ""))[:25]))
            self.table.setItem(row, 4, QTableWidgetItem(str(e.source or "")))

            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 0, 4, 0)

            edit_btn = QPushButton("Edit")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.setFixedSize(20, 20)
            edit_btn.clicked.connect(lambda checked, r=row: self._edit_row(r))

            del_btn = QPushButton("Del")
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setFixedSize(20, 20)
            del_btn.setProperty("class", "danger")
            del_btn.clicked.connect(lambda checked, r=row: self._delete_row(r))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(del_btn)
            self.table.setCellWidget(row, 5, actions)
