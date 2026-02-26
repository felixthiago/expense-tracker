import sys


from PyQt6.QtWidgets import QApplication, QStyle
from PyQt6.QtCore import Qt

from app.config import APP_NAME
from core.database import init_db
from ui.main_window import MainWindow

def main():
    init_db()

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)

    # app.setWindowIcon(app.style().standardIcon(getattr(QStyle.StandardPixmap, "SP_ComputerIcon")))
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")

    win = MainWindow()
    win.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n^C\n")
        exit(0)
