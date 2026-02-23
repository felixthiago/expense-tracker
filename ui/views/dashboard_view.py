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
from PyQt6.QtGui import QColor, QPen

from services.expense_service import total_spent, total_by_category, monthly_totals
from services.category_service import get_category_color_by_id
from ui.styles.theme import COLORS
from .expenses_view import _format_currency


MESES = ("janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro")

def _month_year_pt(dt: datetime) -> str:
    return f"{MESES[dt.month - 1]}, {dt.year}"

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


        except ImportError as e:
            self._has_charts = False
            print(self._has_charts, e)

            no_charts = QLabel("Instale PyQt6-Charts para ver gráficos: pip install PyQt6-Charts")
            no_charts.setStyleSheet("color: #71717a; padding: 24px;")
            parent_layout.addWidget(no_charts, 0, 0, 1, 2)
            return

        self.pie_container = QWidget()
        pie_layout = QVBoxLayout(self.pie_container)
        self.pie_chart_view = QChartView()
        self.pie_chart_view.setMinimumHeight(280)
        self.pie_chart_view.setStyleSheet(f"background: transparent; border-radius: 8px; border: 1px solid {COLORS['border']}; padding: 0px;")

        pie_layout.addWidget(self.pie_chart_view)
        parent_layout.addWidget(self.pie_container, 0, 0)

        self.bar_container = QWidget()
        bar_layout = QVBoxLayout(self.bar_container)
        self.bar_chart_view = QChartView()
        self.bar_chart_view.setMinimumHeight(280)
        self.bar_chart_view.setStyleSheet(f"background: transparent; border-radius: 8px; border: 1px solid {COLORS['border']};")
        self.bar_chart_view.setRenderHint(self.bar_chart_view.renderHints().Antialiasing)
        bar_layout.addWidget(self.bar_chart_view)
        parent_layout.addWidget(self.bar_container, 0, 1)

    def _clear_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


    def _add_card(self, title: str, value: str, row: int, col: int, subtitle: str = "", color: str = COLORS["success"], is_money: bool = False):
            card = QFrame()
            card.setProperty("class", "card")
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS["bg_card_dashboard"]};
                    border: 1px solid {COLORS["border"]};
                    border-radius: 12px;
                    padding: 20px;
                    margin-top: 3px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(4)

            t = QLabel(title)
            t.setStyleSheet(f"font-size: 14px; color: #fff; font-weight: 400;")
            t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(t)

            v = QLabel(value)
            v.setStyleSheet(f"font-size: 24px; font-weight: 500; color: {color};")
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(v)

            if subtitle:
                s = QLabel(subtitle)
                if is_money:
                    color = COLORS["success"]
                else:
                    color = COLORS["text_secondary"]

                s.setStyleSheet(f"font-size: 12px; color: {color};")
                s.setAlignment(Qt.AlignmentFlag.AlignCenter)
                card_layout.addWidget(s)

            self.cards_layout.addWidget(card, row, col)

    def _update_pie_chart(self, data: list[tuple[str, str, Decimal]]):
        if not self._has_charts:
            return

        from PyQt6.QtCharts import QChart, QPieSeries
        series = QPieSeries()

        if not data:
            self.pie_chart_view.setChart(QChart())
            slice_ = series.append("Nenhum Gasto", 1)
            slice_.setColor(QColor(COLORS["bg_tertiary"]))
            slice_.setLabelVisible(False)
            slice_.setExploded(False)

        for i, (cid, name, total) in enumerate(data):
            ccolor = get_category_color_by_id(cid)
            if total <= 0:
                continue    

            slice_ = series.append(name, float(total))
            slice_.setColor(QColor(ccolor))
            slice_.setLabelVisible(True)

            slice_pen = QPen(QColor("#fff"), 1)
            slice_.setPen(slice_pen)
    

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Por categoria")
        chart.setTitleBrush(QColor(COLORS["text_primary"]))
        chart.setTitleBrush(chart.legend().labelBrush())
        chart.setBackgroundBrush(QColor(COLORS["bg_card_dashboard"]))

        chart_pen = QPen(QColor(COLORS["border"]), 1)
        chart.setPlotAreaBackgroundPen(chart_pen)
        chart.setPlotAreaBackgroundVisible(True)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        legend = chart.legend()
        
        if legend:
            legend.setVisible(True)
            legend.setAlignment(Qt.AlignmentFlag.AlignBottom)
            legend.setLabelBrush(QColor(COLORS["text_primary"]))

        self.pie_chart_view.setChart(chart)

    def _update_bar_chart(self, data: list[tuple[str, Decimal]]):
        if not self._has_charts:
            return
        
        from PyQt6.QtCharts import QChart, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
        from PyQt6.QtGui import QColor

        if not data:
            self.bar_chart_view.setChart(QChart())

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

        self._clear_cards()

        total_this_month = total_spent(start_month, end_today)
        self._add_card("Gastos este mês", _format_currency(total_this_month), 0, 0, _month_year_pt(start_month)) if float(total_this_month) > 0 else self._add_card("Gastos este mês", _format_currency(Decimal("0")), 0, 0, _month_year_pt(start_month))
        
        total_this_year = total_spent(start_year, end_today)
        self._add_card("Gastos este ano", _format_currency(total_this_year), 0, 1,
                       str(today.year)) if float(total_this_year) > 0 else self._add_card("Gastos esse ano", _format_currency(Decimal("0")), 0, 1, str(today.year))
        
        totals = total_by_category(start_month, end_today)
        top_cid, top_name, top_total = max(totals, key=lambda x: x[2]) if totals else (0, "Nenhum gasto", Decimal("0"))
        main_color = get_category_color_by_id(top_cid)

        self._add_card("Categoria com maior gasto ", top_name, 0, 2, _format_currency(top_total), color = main_color, is_money = True)

        if self._has_charts:
            by_cat = total_by_category(start_month, end_today)
            monthly = monthly_totals(12)

            self._update_pie_chart(by_cat)
            self._update_bar_chart(monthly)
