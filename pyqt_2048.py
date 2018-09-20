import random
import sys
import random

from PyQt5.QtCore import QBasicTimer, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen, QFont
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QFrame, QHBoxLayout, QPushButton,
                             QLabel, QMainWindow, QVBoxLayout, QWidget, QGridLayout)


class Game(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.centralWidget = QWidget(self)

        self.board = Board(self)
        self.header = QWidget(self)
        self.header.setStyleSheet("QWidget{background: 1px solid #ccc}")

        self.vbox = QVBoxLayout(self.centralWidget)
        self.vbox.setContentsMargins(6, 6, 6, 6)
        self.vbox.addWidget(self.header)
        self.vbox.addWidget(self.board)
        self.vbox.setStretch(0, 1)
        self.vbox.setStretch(1, 4)

        self.setCentralWidget(self.centralWidget)
        self.setFixedSize(400, 468)
        self.center()
        self.show()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width()) / 2,
                  (screen.height()-size.height()) / 2)


class Board(QFrame):
    BoardWidth = 4
    BoardHeight = 4

    def __init__(self, parent):
        super().__init__(parent)
        self.initBoard()
        self.parent = parent

    def initBoard(self):
        self.setStyleSheet("QFrame{background: 1px solid #ecc}")
        self.setFocusPolicy(Qt.StrongFocus)
        self.start()

    def start(self):
        self.shape = Shape()
        self.newNumber()

    def newNumber(self):
        li = [(i, j) for j in range(4)
              for i in range(4) if self.shape.coords[i][j] == 0]
        if li:
            num = random.choice(li)
            self.shape.coords[num[0]][num[1]] = 2
            return True
        else:
            return False

    def keyPressEvent(self, event):

        key = event.key()

        self.shape.merged = False
        self.shape.moveable = False

        if key == Qt.Key_Left:
            self.shape.moveLeft()

        elif key == Qt.Key_Right:
            self.shape.moveRight()

        elif key == Qt.Key_Up:
            self.shape.moveUp()

        elif key == Qt.Key_Down:
            self.shape.moveDown()

        else:
            super(Board, self).keyPressEvent(event)

        def isGameOver():
            for i in range(4):
                if 0 in self.shape.coords[i]:
                    return False
            return True

        # 如果不能合并和移动，格子里没有0, 游戏结束
        if self.shape.merged or self.shape.moveable:
            self.newNumber()
            self.update()

        elif isGameOver():
            print('over')

    def squareWidth(self):
        return self.contentsRect().width() / Board.BoardWidth

    def squareHeight(self):
        return self.contentsRect().height() / Board.BoardHeight

    def paintEvent(self, event):

        painter = QPainter(self)

        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):
                self.drawSquare(painter, j * self.squareWidth(),
                                i * self.squareHeight(), self.shape.coords[i][j])

    def drawSquare(self, painter, x, y, shape):
        colorTable = {
            0: 0xcccccc,
            2: 0xfccff0,
            4: 0xCC6666,
            8: 0x66CC66,
            16: 0x06eC66,
            32: 0xCCCC66,
            64: 0xCC66CC,
            128: 0x66CCCC,
            256: 0xDAAA00,
            512: 0x00CC66,
            1024: 0x0000CC,
            2048: 0x66CCCC,
        }
        color = QColor(colorTable[shape])

        # 画出格子
        painter.fillRect(x + 5, y + 5, self.squareWidth() - 10,
                         self.squareHeight() - 10, color)

        # 画数字，0不用画
        if shape != 0:
            painter.setPen(color.lighter())
            painter.setFont(QFont('Decorative', 20))
            painter.drawText(x + 5, y-5,
                             self.squareHeight(), self.squareWidth(), Qt.AlignCenter, str(shape))


class Shape(object):

    def __init__(self):
        # i行j列，记录每个位置的数字
        self.coords = [[0 for j in range(4)] for i in range(4)]
        self.moveable = False
        self.merged = False
        self.score = 0

    def moveLeft(self):
        for i in range(len(self.coords)):
            self.clearZero(i)
            self.mergeLeft(i)
            self.clearZero(i)

    # 去除空的，后面加上零
    def clearZero(self, x):
        newList = [i for i in self.coords[x] if i != 0]
        newList += [0 for i in range(4 - len(newList))]
        if self.coords[x] != newList:
            self.moveable = True  # 如果新的列表跟旧的不一样，那就是移动了
        self.coords[x] = newList

    def moveRight(self):
        for i in range(len(self.coords)):
            self.coords[i].reverse()
            self.clearZero(i)
            self.mergeLeft(i)
            self.clearZero(i)  # 合并后会出现空元素，删除
            self.coords[i].reverse()

    def moveUp(self):
        self.rotate()
        for i in range(len(self.coords[0])):
            self.clearZero(i)
            self.mergeLeft(i)
            self.clearZero(i)
        self.rotate()

    def moveDown(self):
        self.rotate()
        self.moveRight()
        self.rotate()

    def rotate(self):
        # 反转矩阵
        self.coords = [[self.coords[j][i] for j in range(
            len(self.coords[0]))] for i in range(len(self.coords))]

    def mergeLeft(self, x):
        i = 0
        j = 1
        while i < len(self.coords[x]) and j < len(self.coords[x]):
            if self.coords[x][i] != self.coords[x][j]:
                i += 1
                j += 1
            elif not self.coords[x][i]:
                break  # 等于零了就退出，不用合并了
            else:
                self.merged = True  # 有合并就标记，不生成新元素
                self.coords[x][i] = self.coords[x][j] * 2
                self.score += self.coords[x][i]
                self.coords[x][j] = 0
                i += 2
                j += 2


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setApplicationName('2048')
    game = Game()
    sys.exit(app.exec_())
