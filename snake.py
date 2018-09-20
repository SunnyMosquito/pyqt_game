from PyQt5.QtWidgets import (QMainWindow,QFrame, 
                             QDesktopWidget, QApplication)
from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtGui import QPainter, QColor
from enum import Enum
import sys, random

class Direct(Enum):
    Right = 1
    Down = 2
    Left = 3
    Up = 4

class Snake(QMainWindow):

    def __init__(self):
        super(Snake, self).__init__()

        self.initUI()


    def initUI(self):
        self.setFixedSize(400, 400)

        self.tboard = Board(self)

        self.setCentralWidget(self.tboard)

        self.center()
        self.setWindowTitle('Snake')        
        self.show()
        self.tboard.start()


    def center(self):

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, 
            (screen.height()-size.height())/2)

class Board(QFrame):
    BoardWidth = 20
    BoardHeight = 20
    Speed = 350

    def __init__(self, parent):
        super().__init__(parent)

        self.initBoard()

    def initBoard(self):
        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

    def start(self):
        self.board = [(Board.BoardWidth // 2, Board.BoardHeight // 2)]
        self.direct = Direct.Left
        self.isPaused = False
        self.timer.start(Board.Speed, self)
        self.newFood()
    
    def pause(self):
        self.isPaused = not self.isPaused
        if self.isPaused:
            self.timer.stop()
        else:
            self.timer.start(Board.Speed, self)
        self.update()

    def tryMove(self):
        if self.direct == Direct.Right:
            x=self.board[0][0]+1
            y=self.board[0][1]
        
        elif self.direct == Direct.Left:
            x=self.board[0][0]-1
            y=self.board[0][1]

        elif self.direct == Direct.Down:
            x=self.board[0][0]
            y=self.board[0][1]+1

        elif self.direct == Direct.Up:
            x=self.board[0][0]
            y=self.board[0][1]-1

        if x < 0 or x >= self.BoardWidth or y < 0 or y >= self.BoardHeight:
            self.timer.stop()
            self.start()
            return False

        if (x, y) in self.board:
            self.timer.stop()
            self.start()
            return False

        self.board.insert(0, (x,y))
        
        if not self.eatFood(x, y):
            self.board.pop()
        
        self.update()

        return True

    def eatFood(self, x, y):
        if self.food == (x, y):
            self.newFood()
            return True
        else:
            return False

    def newFood(self):
        self.food = (random.randint(0, Board.BoardWidth-1),
                     random.randint(0, Board.BoardHeight-1))
        
        if self.food in self.board:
            self.newFood()

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_P:
            self.pause()

        elif key == Qt.Key_Left:
            if self.direct != Direct.Left and self.direct != Direct.Right:
                self.direct = Direct.Left
                self.tryMove()

        elif key == Qt.Key_Right:
            if self.direct != Direct.Right and self.direct != Direct.Left:
                self.direct = Direct.Right
                self.tryMove()

        elif key == Qt.Key_Down:
            if self.direct != Direct.Down and self.direct != Direct.Up:
                self.direct = Direct.Down
                self.tryMove()

        elif key == Qt.Key_Up:
            if self.direct != Direct.Up and self.direct != Direct.Down:
                self.direct = Direct.Up
                self.tryMove()

        else:
            super(Board, self).keyPressEvent(event)

    def paintEvent(self, event):

        painter = QPainter(self)

        for i in range(len(self.board)):
            x = self.board[i][0]
            y = self.board[i][1]
            if i == 0:
                self.drawEllipse(painter,
                            x * self.squareWidth(),
                            y * self.squareHeight(),
                            0x33ff55)
                continue
            self.drawSquare(painter,
                            x * self.squareWidth(),
                            y * self.squareHeight(),
                            0x336699)

        self.drawSquare(painter, 
                        self.food[0] * self.squareWidth(),
                        self.food[1] * self.squareHeight(),
                        0x001177)

    def timerEvent(self, event):
        '''handles timer event'''

        if event.timerId() == self.timer.timerId():
            self.tryMove()
        else:
            super(Board, self).timerEvent(event)

    def squareWidth(self):
        return self.contentsRect().width() / Board.BoardWidth


    def squareHeight(self):
        return self.contentsRect().height() / Board.BoardHeight

    def drawEllipse(self, painter, x, y, color):
        color = QColor(color)
        painter.setBrush(color)
        painter.setPen(color)
        painter.drawEllipse(x, y, self.squareWidth(), self.squareHeight())

    def drawSquare(self, painter, x, y, color):
        color = QColor(color)
        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2, 
            self.squareHeight() - 2, color)

if __name__ == '__main__':

    app = QApplication([])
    tetris = Snake()    
    sys.exit(app.exec_())
