"""Gui for Bet app"""

import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Bet Tracker")


        # label = QLabel("Place bets here")
        # label.setAlignment(Qt.AlignCenter)
        # self.setCentralWidget(label)

     
        self.central_widget = QWidget()               
        self.setCentralWidget(self.central_widget)    
        lay = QVBoxLayout(self.central_widget)
        
        label = QLabel(self)
        label.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap('logo.png')
        label.setPixmap(pixmap)
        screen = app.primaryScreen()
        size = screen.size()
        self.resize(size.width(), size.height())
        
        lay.addWidget(label)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()