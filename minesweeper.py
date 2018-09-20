from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QSplitter,QApplication, QFrame, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
import sys

class Minesweeper(QMainWindow):

    def __init__(self):
        super(Minesweeper, self).__init__()
        self.initUI()
    
    def initUI(self):
        
        self.setWindowTitle('扫雷')
        self.resize(600, 400)
        self.level = Level(self)
        self.setCentralWidget(self.level)
        self.show()
    
    def setUI(self):
        self.centralWidget = QWidget(self)
        self.board = Board(self)
        self.aside = Aside(self)
        self.hbox = QHBoxLayout(self.centralWidget)
        # self.hbox = QSplitter(Qt.Horizontal)
        # self.hbox.addStretch(1)
        self.hbox.addWidget(self.board)
        self.hbox.addWidget(self.aside)
        # self.hbox.addStretch(1)
        self.hbox.setStretch(0, 6)
        self.hbox.setStretch(1, 4)
        self.setCentralWidget(self.centralWidget)

        self.board.start()


class Level(QFrame):

    def __init__(self, parent):
        super(Level, self).__init__(parent)
        self.parent = parent
        self.initLevel()
    
    def buttonClicked(self):
        sender = self.sender()
        if sender == self.lowBtn:
            Board.BoardWidth = 8
            Board.BoardHeight = 8
        elif sender == self.midBtn:
            Board.BoardWidth = 16
            Board.BoardHeight = 16
        elif sender == self.highBtn:
            Board.BoardWidth = 30
            Board.BoardHeight = 16
        self.parent.setUI()
        self.close()

    def initLevel(self):
        hbox = QHBoxLayout()
        hbox.addStretch()
        self.lowBtn = QPushButton('8  *  8')
        self.midBtn = QPushButton('16  *  16')
        self.highBtn = QPushButton('30  *  16')
        self.lowBtn.clicked.connect(self.buttonClicked)
        self.midBtn.clicked.connect(self.buttonClicked)
        self.highBtn.clicked.connect(self.buttonClicked)
        hbox.addWidget(self.lowBtn)
        hbox.addWidget(self.midBtn)
        hbox.addWidget(self.highBtn)
        hbox.addStretch()
        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addLayout(hbox)
        vbox.addStretch()
        self.setLayout(vbox)
        self.setStyleSheet('QFrame{background-color: agb(222,66,77)}')

class Board(QFrame):

    BoardWidth = 8
    BoardHeight = 8

    def __init__(self, parent):
        super(Board, self).__init__(parent)
        self.initBoard()

    def initBoard(self):
        self.setStyleSheet('QFrame{background-color: agb(22,66,77)}')
    
    def start(self):
        self.resize(20 * Board.BoardWidth, 20 * Board.BoardHeight)
        # self.parent.resize(self.)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        painter.setPen(pen)
        for i in range(Board.BoardHeight):
            painter.drawLine(0, i * self.squareHeight(),
                             self.contentsRect().width(), i * self.squareHeight())
        
        for i in range(Board.BoardWidth):
            painter.drawLine(i * self.squareWidth(),0,
                             i * self.squareWidth(),self.contentsRect().height())
    
    def squareWidth(self):
        return self.contentsRect().width() / Board.BoardWidth
    
    def squareHeight(self):
        return self.contentsRect().height() / Board.BoardHeight

class Aside(QWidget):

    def __init__(self, parent):
        super(Aside, self).__init__(parent)
        self.initAside()

    def initAside(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ninesweeper = Minesweeper()
    sys.exit(app.exec_())
