import random
import sys

from PyQt5.QtCore import QBasicTimer, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QPainter
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QFrame, QHBoxLayout,
                             QLabel, QMainWindow, QVBoxLayout, QWidget)


class Tetris(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.tboard = Board(self)
        self.slide = Slide(self)

        self.centralWidget = QWidget(self)

        self.hbox = QHBoxLayout(self.centralWidget)
        self.hbox.setContentsMargins(6, 6, 6, 6)

        self.hbox.addWidget(self.tboard)
        self.hbox.addWidget(self.slide)

        self.hbox.setStretch(0, 2)
        self.hbox.setStretch(1, 1)

        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle('俄罗斯方块')
        self.setWindowIcon(QIcon('web.png'))

        self.setFixedSize(380, 500)
        self.center()
        self.show()

        self.tboard.start()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2,
                  (screen.height()-size.height())/2)


class Board(QFrame):
    # 这些是Board类的变量。BoardWidth和BoardHeight分别是board的宽度和高度。
    # Speed是游戏的速度，每300ms出现一个新的方块。
    BoardWidth = 10
    BoardHeight = 22
    Speed = 300

    def __init__(self, parent):
        super().__init__(parent)
        self.initBoard()
        self.parent = parent

    def initBoard(self):
        self.timer = QBasicTimer()
        self.setStyleSheet("QFrame{border: 1px solid #ccc}")
        # 获得焦点，才能响应事件
        self.setFocusPolicy(Qt.StrongFocus)
        self.board = [[0 for j in range(Board.BoardWidth)]
                      for i in range(Board.BoardHeight)]
        self.isPaused = False
        self.nextShape = random.randint(1, 7)

    def start(self):
        if self.isPaused:
            return

        self.isStarted = True

        self.numLinesRemoved = 0

        self.parent.slide.sinStatu.emit('游戏中...')

        self.newPiece()
        self.timer.start(Board.Speed, self)

    def pause(self):

        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.parent.slide.sinStatu.emit('暂停')

        else:
            self.timer.start(Board.Speed, self)
            self.parent.slide.sinStatu.emit('游戏中...')

        self.update()

    def newPiece(self):

        self.curPiece = Shape()
        self.curPiece.setShape(self.nextShape)

        # 生成下一个方块
        self.nextShape = random.randint(1, 7)

        # 下一个方块在显示侧边栏
        self.parent.slide.sinShape.emit(self.nextShape)

        # 设置方块的中心点位置
        self.curX = Board.BoardWidth // 2
        self.curY = 0 - self.curPiece.minY()

        # 如果不能生成新方块，游戏结束
        if not self.tryMove(self.curPiece, self.curX, self.curY):

            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.isStarted = False
            self.parent.slide.sinStatu.emit('游戏结束')

    def tryMove(self, newPiece, newX, newY):
        for i in range(4):
            x = newX + newPiece.x(i)
            y = newY + newPiece.y(i)
            # 检测是否超出边界
            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False
            # 如果该位置有方块，不移动
            if self.shapeAt(x, y) != Tetrominoe.NoShape:
                return False

        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()
        return True

    def oneLineDown(self):
        if not self.tryMove(self.curPiece, self.curX, self.curY + 1):
            self.pieceDropped()

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.oneLineDown()
        else:
            super(Board, self).timerEvent(event)

    def pieceDropped(self):
        # 将正在下落的加到已经落下的里
        for i in range(4):
            x = self.curX + self.curPiece.x(i)
            y = self.curY + self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.pieceShape)

        self.removeFullLines()

        self.newPiece()

    def removeFullLines(self):

        numFullLines = 0
        rowsToRemove = []
        for i in range(Board.BoardHeight):
            isFullLine = True
            for j in range(Board.BoardWidth):
                if self.board[i][j] == Tetrominoe.NoShape:
                    isFullLine = False
            if isFullLine:
                rowsToRemove.append(i)

        # 删除满行的并将上面的下移
        for row in rowsToRemove:
            for i in range(row, 0, -1):
                for j in range(Board.BoardWidth):
                    self.setShapeAt(j, i, self.shapeAt(j, i-1))
                # 使用这行代码会出现问题， 列表是引用类型
                # self.board[i] = self.board[i-1]

        numFullLines = numFullLines + len(rowsToRemove)

        if numFullLines > 0:

            # 每消除20行下落速度加快50ms
            if self.numLinesRemoved != 0 and self.numLinesRemoved % 20 == 0:
                Board.Speed -= 50
                self.timer.stop()
                self.timer.start(Board.Speed, self)

            self.numLinesRemoved = self.numLinesRemoved + numFullLines

            # 在侧边栏显示分数
            self.parent.slide.sinScore.emit(self.numLinesRemoved)

            self.curPiece.setShape(Tetrominoe.NoShape)

            self.update()

    def shapeAt(self, j, i):
        return self.board[i][j]

    def setShapeAt(self, j, i, shape):
        self.board[i][j] = shape

    def paintEvent(self, event):

        painter = QPainter(self)

        # 画出已经落下的方块
        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):
                if self.board[i][j] != Tetrominoe.NoShape:
                    self.drawSquare(painter,
                                    j * self.squareWidth(),
                                    i * self.squareHeight(),
                                    self.board[i][j])
        # 画出正在下落的
        if self.curPiece.pieceShape != Tetrominoe.NoShape:
            for i in range(4):
                self.drawSquare(
                    painter,
                    (self.curX +
                     self.curPiece.coords[i][0]) * self.squareWidth(),
                    (self.curY +
                     self.curPiece.coords[i][1]) * self.squareHeight(),
                    self.curPiece.pieceShape)

    def drawSquare(self, painter, x, y, shape):
        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

        color = QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.squareWidth(),
                         self.squareHeight(), color)

        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.squareHeight() - 1, x, y)
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.squareHeight() - 1,
                         x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        painter.drawLine(x + self.squareWidth() - 1,
                         y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)

    def squareWidth(self):
        return self.contentsRect().width() / Board.BoardWidth

    def squareHeight(self):
        return self.contentsRect().height() / Board.BoardHeight

    def keyPressEvent(self, event):

        key = event.key()

        if key == Qt.Key_P:
            self.pause()

        elif key == Qt.Key_Left:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)

        elif key == Qt.Key_Right:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)

        elif key == Qt.Key_Up:
            self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)

        elif key == Qt.Key_Down:
            self.tryMove(self.curPiece, self.curX, self.curY + 1)

        else:
            super(Board, self).keyPressEvent(event)

# 侧边栏


class Slide(QFrame):

    sinScore = pyqtSignal(int)
    sinShape = pyqtSignal(int)
    sinStatu = pyqtSignal(str)

    def __init__(self, parent):
        super(Slide, self).__init__(parent)
        self.initSlide()
        self.parent = parent

    def initSlide(self):
        self.shape = 0
        self.setStyleSheet('QFrame{background-color: rgb(220,220,220)}')
        self.sinScore.connect(self.setScore)
        self.sinShape.connect(self.setShape)
        self.sinStatu.connect(self.setStatu)
        self.vbox = QVBoxLayout(self)
        self.nextPiece = QWidget()
        self.scoreLabel = QLabel('分数: 0')
        self.statuLabel = QLabel('状态: 无')
        self.vbox.addWidget(self.nextPiece)
        self.vbox.addWidget(self.scoreLabel)
        self.vbox.addWidget(self.statuLabel)
        self.vbox.setStretch(0, 1)
        self.vbox.setStretch(1, 1)
        self.vbox.setStretch(2, 1)

    def setShape(self, shape):
        self.shape = Shape()
        self.shape.setShape(shape)
        self.left = self.contentsRect().width() / self.parent.tboard.squareWidth() // 2
        self.top = 2
        self.update()

    def setScore(self, num):
        self.scoreLabel.setText('分数: ' + str(100 * num))

    def setStatu(self, status):
        self.statuLabel.setText('状态: ' + status)

    def paintEvent(self, event):
        painter = QPainter(self)
        # 右边画出下一个落下的方块
        for i in range(4):
            self.parent.tboard.drawSquare(
                painter,
                (self.left + self.shape.coords[i][0]) *
                self.parent.tboard.squareWidth(),
                (self.top + self.shape.coords[i][1]) *
                self.parent.tboard.squareHeight(),
                self.shape.pieceShape)

# 表示形状


class Tetrominoe(object):

    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7


class Shape(object):
    # 对应八种形状，第一个全部0表示无
    coordsTable = (
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)),
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)),
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)),
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)),
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))
    )

    def __init__(self):
        # 每个形状有四个方块,[x,y]记录坐标
        self.coords = [[0, 0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape

        self.setShape(Tetrominoe.NoShape)

    def rotateRight(self):
        # 如果是正方形旋转后还是它自己
        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):

            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result

    def setX(self, index, x):
        self.coords[index][0] = x

    def setY(self, index, y):
        self.coords[index][1] = y

    def x(self, index):
        return self.coords[index][0]

    def y(self, index):
        return self.coords[index][1]

    def shape(self):
        return self.pieceShape

    def setShape(self, shape):
        table = Shape.coordsTable[shape]

        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape

    def minY(self):
        result = self.coords[0][0]
        for i in range(4):
            result = min(result, self.coords[i][1])
        return result


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setApplicationName('Tetris')
    tetris = Tetris()
    sys.exit(app.exec_())
