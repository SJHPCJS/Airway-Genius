import sys

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from qfluentwidgets import SplashScreen

from airway_genius_gui.globals import GUI_DIR
from airway_genius_gui.main_window import UiMainWindow
import PySide6.QtWidgets as QtWidgets


class CustomizedSplashScreen(SplashScreen):
    def resizeEvent(self, e):
        icon_w = self.iconSize().width()
        icon_h = self.iconSize().height()
        self.iconWidget.move(self.width() // 2 - icon_w // 2, self.height() // 2 - icon_h // 2)
        self.titleBar.resize(0, 0)


class AppWindow(QtWidgets.QMainWindow, UiMainWindow):
    def __init__(self):
        super(AppWindow, self).__init__()
        self.resize(1200, 800)
        self.setWindowTitle('Airway Genius')
        self.setWindowIcon(QIcon(f'{GUI_DIR}/src/fighter_jet.svg'))

        self.splash_screen = CustomizedSplashScreen(self.windowIcon(), self)
        self.splash_screen.setIconSize(QSize(256, 256))

        self.show()

        self.setup_ui(self)

        self.splash_screen.finish()

    def closeEvent(self, event):
        print("close event")
        # check if sub_thread attribute exists
        if hasattr(self, 'sub_thread'):
            try:
                self.terminate_calculation()
            except Exception as e:
                pass
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    app_window = AppWindow()
    app_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
