#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QApplication


class QImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.printer = QPrinter()

        self.scaleFactor = 0.0
        self.logoFactor = 0.0

        self.endPos = QPoint(0, 0)
        self.lastPos = QPoint(0, 0)

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(False)
        self.scrollArea.viewport().installEventFilter(self)

        self.setCentralWidget(self.scrollArea)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("Image Viewer")
        self.resize(1600, 1200)

        self.imageLabel.setMouseTracking(True)
        self.imageLabel.mouseMoveEvent = self.mouseMove
        self.imageLabel.mousePressEvent = self.mousePress
        self.imageLabel.wheelEvent = self.wheel

    def open(self):
        options = QFileDialog.Options()
        # fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
        fileName, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '',
                                                  'Images (*.png *.jpeg *.jpg *.bmp *.gif)', options=options)
        if fileName:
            image = QImage(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % fileName)
                return

            self.base = QPixmap(image.width(), image.height())
            self.base.fill(Qt.transparent)

            painter = QPainter(self.base)
            painter.drawPixmap(0, 0, QPixmap.fromImage(image))

            self.base_copy = self.base.copy()  # 顯示基底
            self.base_temp = self.base.copy()  # 即時顯示用
            self.imageLabel.setPixmap(self.base_copy)

            self.logo = QPixmap.fromImage(QImage(r'C:\Users\User\Desktop\logo_white.png'))
            self.logo_copy = self.logo.copy()

            self.scaleFactor = 1.0
            self.logoFactor = 1.0

            self.scrollArea.setVisible(True)
            self.printAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

    def print_(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def about(self):
        QMessageBox.about(self, "About Image Viewer",
                          "<p>The <b>Image Viewer</b> example shows how to combine "
                          "QLabel and QScrollArea to display an image. QLabel is "
                          "typically used for displaying text, but it can also display "
                          "an image. QScrollArea provides a scrolling view around "
                          "another widget. If the child widget exceeds the size of the "
                          "frame, QScrollArea automatically provides scroll bars.</p>"
                          "<p>The example demonstrates how QLabel's ability to scale "
                          "its contents (QLabel.scaledContents), and QScrollArea's "
                          "ability to automatically resize its contents "
                          "(QScrollArea.widgetResizable), can be used to implement "
                          "zooming and scaling features.</p>"
                          "<p>In addition the example shows how to use QPainter to "
                          "print an image.</p>")

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.printAct = QAction("&Print...", self, shortcut="Ctrl+P", enabled=False, triggered=self.print_)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+N", enabled=False, triggered=self.normalSize)
        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False, checkable=True, shortcut="Ctrl+F",
                                      triggered=self.fitToWindow)
        self.aboutAct = QAction("&About", self, triggered=self.about)
        self.aboutQtAct = QAction("About &Qt", self, triggered=qApp.aboutQt)

        self.saveAct = QAction("&Save...", self, shortcut="Ctrl+S", triggered=self._save)

        self.logo_white = QAction("&White...", self, shortcut="Ctrl+W", triggered=self._change_logo_white)
        self.logo_black = QAction("&Black...", self, shortcut="Ctrl+B", triggered=self._change_logo_black)

    def _save(self):
        img = self.base_copy.toImage()
        img = img.convertToFormat(QImage.Format_RGB888)
        img.save(r'C:\Users\User\Desktop\123.png', 'png')
        # self.base_copy.save(r'C:\Users\User\Desktop\123.png', 'png')

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addAction(self.saveAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.logoMenu = QMenu("&Logo", self)
        self.logoMenu.addAction(self.logo_white)
        self.logoMenu.addAction(self.logo_black)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.logoMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.base.size())

        #同時也resize圖片
        w = self.base.width()
        h = self.base.height()

        w *= self.scaleFactor
        h *= self.scaleFactor

        self.base_copy = self.base.scaled(w, h)
        self.imageLabel.setPixmap(self.base_copy)



        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))

    def _change_logo_white(self):
        self.logo = QPixmap.fromImage(QImage(r'C:\Users\User\Desktop\logo_white.png'))
        self.logo_copy = self.logo.copy()
        self.logo_white.setEnabled(False)
        self.logo_black.setEnabled(True)

    def _change_logo_black(self):
        self.logo = QPixmap.fromImage(QImage(r'C:\Users\User\Desktop\logo_black.png'))
        self.logo_copy = self.logo.copy()
        self.logo_white.setEnabled(True)
        self.logo_black.setEnabled(False)



    def mouseMove(self, event):

        modifiers = QApplication.keyboardModifiers()
        self.endPos = event.pos()

        if event.buttons() == Qt.NoButton and modifiers == Qt.ControlModifier:

            x = event.x()
            y = event.y()
            print("x: {}, y: {}".format(x, y))

            self.base_temp = self.base_copy.copy()
            painter = QPainter(self.base_temp)
            painter.setOpacity(0.5)
            painter.drawPixmap(
                int(x - self.logo_copy.width() / 2),
                int(y - self.logo_copy.height() / 2),
                self.logo_copy)

            # self.imageLabel.setPixmap(self.base)
            self.imageLabel.setPixmap(self.base_temp)



        elif event.buttons() == Qt.LeftButton:
            print("Left click drag")




        elif event.buttons() == Qt.RightButton:
            print("Right click drag")

    def mousePress(self, event):
        modifiers = QApplication.keyboardModifiers()
        if event.button() == Qt.LeftButton and modifiers == Qt.ControlModifier:

            x = event.x()
            y = event.y()
            print("x: {}, y: {}".format(x, y))

            # self.base_copy = self.base.copy()
            painter = QPainter(self.base_copy)
            painter.drawPixmap(
                int(x - self.logo_copy.width()/2),
                int(y - self.logo_copy.height() / 2),
                self.logo_copy)

            self.imageLabel.setPixmap(self.base_copy)
            # self.imageLabel.setPixmap(self.base_copy)


            # self.lastPos = event.pos()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            x = self.endPos.x()
            y = self.endPos.y()
            self.base_temp = self.base_copy.copy()
            painter = QPainter(self.base_temp)
            painter.setOpacity(0.5)
            painter.drawPixmap(
                int(x - self.logo_copy.width() / 2),
                int(y - self.logo_copy.height() / 2),
                self.logo_copy)

            # self.imageLabel.setPixmap(self.base)
            self.imageLabel.setPixmap(self.base_temp)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.imageLabel.setPixmap(self.base_copy)

    def eventFilter(self, source, event):

        if event.type() == QEvent.Wheel and \
                source is self.scrollArea.viewport():
            return True
        return super().eventFilter(source, event)

    def wheel(self, event):
        print(event.type())

        x = event.x()
        y = event.y()

        deg = event.angleDelta().y() / 120
        print('deg: {}'.format(deg))

        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:

            if deg > 0:
                if self.logoFactor > 3.0:
                    return
                self.logoFactor *= 1.25
            else:
                if self.logoFactor < 0.33:
                    return
                self.logoFactor *= 0.8

            w = self.logo.width()
            h = self.logo.height()

            w *= self.logoFactor
            h *= self.logoFactor
            self.logo_copy = self.logo.scaled(w, h)

            self.base_temp = self.base_copy.copy()
            painter = QPainter(self.base_temp)
            painter.setOpacity(0.5)
            painter.drawPixmap(
                int(x - self.logo_copy.width() / 2),
                int(y - self.logo_copy.height() / 2),
                self.logo_copy)

            # self.imageLabel.setPixmap(self.base)
            self.imageLabel.setPixmap(self.base_temp)

        else:

            if deg > 0:
                if self.scaleFactor > 3.0:
                    return
                self.zoomIn()
            else:
                if self.scaleFactor < 0.33:
                    return
                self.zoomOut()



            # w = self.base.width()
            # h = self.base.height()
            #
            # w *= self.scaleFactor
            # h *= self.scaleFactor
            #
            # self.base_copy = self.base.scaled(w, h)
            # self.imageLabel.setPixmap(self.base_copy)



if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    imageViewer = QImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())
    # TODO QScrollArea support mouse
