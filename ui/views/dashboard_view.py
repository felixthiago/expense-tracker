from datetime import datetime, timedelta
from decimal import Decimal

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from services.expense_service import total_spent, total_by_category, monthly_totals
from services.category_service import list_categories
from ui.styles.theme import COLORS

MESES = ("janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro")

def _format_currency(value: Decimal) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _month_year_pt(dt: datetime) -> str:
    return f"{MESES[dt.month - 1]} {dt.year}"


class DashboardView(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self._content = QWidget()
        self.setWidget(self._content)
        layout = QVBoxLayout(self._content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)


        title = QLabel("Dashboard") 
        title.setProperty("class", "title")
        title.setStyleSheet("font-size: 24px; font-weight: 600;")
        layout.addWidget(title)
        subtitle = QLabel("Resumo financeiro e visão geral das despesas, mensalmente e anualmente")
        subtitle.setProperty("class", "subtitle")
        layout.addWidget(subtitle)
        layout.addSpacing(16)

        self.cards_layout = QGridLayout()
        layout.addLayout(self.cards_layout)

        self._has_charts = False
        charts_widget = QWidget()
        charts_layout = QGridLayout(charts_widget)
        self.chart_pie = None
        self.chart_bars = None
        self._build_charts(charts_layout)
        layout.addWidget(charts_widget, 1)

    def _build_charts(self, parent_layout: QGridLayout):
        try:
            from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
            from PyQt6.QtCore import QMargins
            from PyQt6.QtGui import QColor, QBrush

            self._has_charts = True

        except ImportError:
            self._has_charts = False
            no_charts = QLabel("Instale PyQt6-Charts para ver gráficos: pip install PyQt6-Charts")
            no_charts.setStyleSheet("color: #71717a; padding: 24px;")
            parent_layout.addWidget(no_charts, 0, 0, 1, 2)
            return


        self.pie_container = QWidget()
        pie_layout = QVBoxLayout(self.pie_container)
        self.pie_chart_view = QChartView()
        self.pie_chart_view.setMinimumHeight(280)
        self.pie_chart_view.setStyleSheet("background: transparent;")

        pie_layout.addWidget(self.pie_chart_view)
        parent_layout.addWidget(self.pie_container, 0, 0)

        self.bar_container = QWidget()
        bar_layout = QVBoxLayout(self.bar_container)
        self.bar_chart_view = QChartView()
        self.bar_chart_view.setMinimumHeight(280)
        self.bar_chart_view.setStyleSheet("background: transparent;")
        # self.bar_chart_view.setRenderHint(self.bar_chart_view.RenderHint.Antialiasing)
        bar_layout.addWidget(self.bar_chart_view)
        parent_layout.addWidget(self.bar_container, 0, 1)

    def _clear_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _add_card(self, title: str, value: str, row: int, col: int, subtitle: str = ""):
        card = QFrame()
        card.setProperty("class", "card")
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(4)
        t = QLabel(title)
        t.setStyleSheet("font-size: 12px; color: #71717a;")
        card_layout.addWidget(t)
        v = QLabel(value)
        v.setStyleSheet("font-size: 22px; font-weight: 600;")
        card_layout.addWidget(v)
        if subtitle:
            s = QLabel(subtitle)
            s.setStyleSheet("font-size: 11px; color: #71717a;")
            card_layout.addWidget(s)
        self.cards_layout.addWidget(card, row, col)

    def _update_pie_chart(self, data: list[tuple[str, str, Decimal]]):
        if not self._has_charts or not data:
            return
        from PyQt6.QtCharts import QChart, QPieSeries
        from PyQt6.QtGui import QColor

        series = QPieSeries()

        colors_hex = [
            "#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#ec4899",
            "#8b5cf6", "#3b82f6", "#64748b"
        ]

        for i, (cid, name, total) in enumerate(data):
            if total <= 0:
                continue
            slice_ = series.append(name, float(total))
            slice_.setColor(QColor(colors_hex[i % len(colors_hex)]))
            slice_.setLabelVisible(True)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Por categoria")
        chart.setTitleBrush(chart.legend().labelBrush())
        chart.setBackgroundBrush(QColor(COLORS["bg_card"]))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.pie_chart_view.setChart(chart)

    def _update_bar_chart(self, data: list[tuple[str, Decimal]]):
        if not self._has_charts or not data:
            return
        from PyQt6.QtCharts import QChart, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
        from PyQt6.QtGui import QColor

        bar_set = QBarSet("Despesas (R$)")
        bar_set.setColor(QColor(COLORS["accent"]))
        categories = []
        for ym, total in data:
            bar_set.append(float(total))
            categories.append(ym)

        series = QBarSeries()
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Evolução mensal")
        chart.setBackgroundBrush(QColor(COLORS["bg_card"]))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(False)
        self.bar_chart_view.setChart(chart)

    def refresh(self):
        today = datetime.now().date()
        start_month = datetime(today.year, today.month, 1)
        end_today = datetime.combine(today, datetime.max.time())
        start_year = datetime(today.year, 1, 1)

        total_this_month = total_spent(start_month, end_today)
        total_this_year = total_spent(start_year, end_today)
        by_cat = total_by_category(start_month, end_today)
        monthly = monthly_totals(12)

        self._clear_cards()
        self._add_card("Gastos este mês", _format_currency(total_this_month), 0, 0,
                       _month_year_pt(start_month))
        self._add_card("Gastos este ano", _format_currency(total_this_year), 0, 1,
                       str(today.year))
        self._add_card("Categorias com gastos", str(len(by_cat)), 0, 2)

        if self._has_charts:
            self._update_pie_chart(by_cat)
            self._update_bar_chart(monthly)
