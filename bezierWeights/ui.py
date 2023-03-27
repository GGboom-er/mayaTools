# coding:utf-8
import os
import json
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *

import weight

window = None


def get_host_app():
    try:
        main_window = QApplication.activeWindow()
        while True:
            last_win = main_window.parent()
            if last_win:
                main_window = last_win
            else:
                break
        return main_window
    except:
        pass


class Bezier(QWidget):
    valueChanged = Signal()

    def __init__(self):
        QWidget.__init__(self)
        self.points = [[0.0, 1.0], [1.0 / 3, 1.0], [2.0 / 3, 0.0], [1.0, 0.0]]
        self.__movePoint = 0
        self.__mirror = False
        self.__adsorb = False
        print 512-2**6
        self.setFixedSize(512, 448)

    def paintEvent(self, event):
        QWidget.paintEvent(self, event)
        painter = QPainter(self)
        # background
        painter.setBrush(QBrush(QColor(120, 120, 120), Qt.SolidPattern))
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        painter.drawRect(0, 0, self.width()-1, self.height()-1)
        # curve
        painter.setBrush(QBrush(QColor(100, 100, 100), Qt.SolidPattern))
        points = [QPointF((self.width()-1) * p[0], (self.height()-1) * p[1]) for p in self.points]
        path = QPainterPath()
        path.moveTo(0, self.height()-1)
        path.lineTo(points[0])
        path.cubicTo(*points[1:])
        path.lineTo(self.width()-1, self.height()-1)
        painter.drawPath(path)
        # grid
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.DotLine))
        w_step = (self.width()-1)/6.0
        h_step = (self.height()-1)/6.0
        for i in range(1, 6):
            w = w_step * i
            h = h_step * i
            painter.drawLine(w, 0, w, self.height())
            painter.drawLine(0, h, self.width(), h)
        # control point
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(200, 200, 200), Qt.SolidPattern))
        painter.drawEllipse(points[1], 6, 6)
        painter.drawEllipse(points[2], 6, 6)
        # edge
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        edge_points = []
        for w, h in zip([0, 0, 1, 1, 0], [0, 1, 1, 0, 0]):
            p = QPointF(w*(self.width()-1), h*(self.height()-1))
            edge_points.extend([p, p])
        painter.drawLines(edge_points[1:-1])
        # control line
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.DashLine))
        painter.drawLine(points[0], points[1])
        painter.drawLine(points[3], points[2])
        painter.end()

    def mousePressEvent(self, event):
        self.setFocus()
        QWidget.mousePressEvent(self, event)
        points = [QPointF((self.width() - 1) * p[0], (self.height() - 1) * p[1]) for p in self.points]
        p = QPointF(event.pos())-points[1]
        length = (p.x()**2 + p.y()**2)**0.5
        if length < 10:
            self.__movePoint = 1
            return
        p = QPointF(event.pos()) - points[2]
        length = (p.x() ** 2 + p.y() ** 2) ** 0.5
        if length < 10:
            self.__movePoint = 2
            return
        self.__movePoint = 0

    def mouseMoveEvent(self, event):
        QWidget.mouseMoveEvent(self, event)
        if self.__movePoint == 1:
            p = QPointF(event.pos())
            x = max(min(float(p.x())/(self.width()-1), 1.0), 0.0)
            y = max(min(float(p.y())/(self.height()-1), 1.0), 0.0)
            if self.__adsorb:
                x = round(x*12)/12.0
                y = round(y*12)/12.0
            if self.__mirror:
                mx = (1-x)
                my = (1-y)
                self.points[2] = [mx, my]
            self.points[1] = [x, y]
            self.update()
            self.valueChanged.emit()
        if self.__movePoint == 2:
            p = QPointF(event.pos())
            x = max(min(float(p.x())/(self.width()-1), 1.0), 0.0)
            y = max(min(float(p.y())/(self.height()-1), 1.0), 0.0)
            if self.__adsorb:
                x = round(x*6)/6.0
                y = round(y*6)/6.0
            if self.__mirror:
                mx = (1-x)
                my = (1-y)
                self.points[1] = [mx, my]
            self.points[2] = [x, y]
            self.update()
            self.valueChanged.emit()

    def keyPressEvent(self, event):
        QWidget.keyPressEvent(self, event)
        if event.key() == Qt.Key_X:
            self.__adsorb = True
        if event.modifiers() == Qt.ControlModifier:
            self.__mirror = True

    def keyReleaseEvent(self, event):
        QWidget.keyReleaseEvent(self, event)
        self.__mirror = False
        self.__adsorb = False


class FloatSliderGroup(QHBoxLayout):
    valueChange = Signal(float)

    def __init__(self):
        QHBoxLayout.__init__(self)
        self.slider = QSlider(Qt.Horizontal)
        self.spin = QDoubleSpinBox()
        self.addWidget(self.spin)
        self.addWidget(self.slider)
        self.set_range(0, 1)
        self.spin.valueChanged.connect(self.convert_slider)
        self.slider.valueChanged.connect(self.convert_spin)
        self.spin.setSingleStep(0.01)
        self.spin.setDecimals(3)

    def convert_spin(self, value):
        self.spin.setValue(value/1000.0)
        self.valueChange.emit(self.spin.value())

    def convert_slider(self, value):
        self.slider.setValue(int(round(1000*value)))

    def set_range(self, min_value, max_value):
        self.spin.setRange(min_value, max_value)
        self.slider.setRange(min_value*1000, max_value*1000)

    def value(self):
        return self.spin.value()

    def set_value(self, value):
        self.spin.setValue(value)


class FaceWeight(QWidget):

    def __init__(self):
        QWidget.__init__(self, get_host_app(), 1)
        self.kwargs = None
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(1, 1, 1, 1)
        self.bezier = Bezier()
        layout.addWidget(self.bezier)
        layout.addStretch()
        h_layout = QHBoxLayout()
        layout.addLayout(h_layout)
        h_layout.addStretch()
        argument_form = QFormLayout()
        h_layout.addLayout(argument_form)
        h_layout.addStretch()

        self.type = QButtonGroup()
        radio_layout = QGridLayout()
        for i, text in enumerate([u"次级", u"关节", u"横向拆分",
                                  u"多次级", u"多关节",  u"循环边"]):
            radio = QRadioButton(text)
            self.type.addButton(radio, i)
            radio_layout.addWidget(radio, i / 3, i % 3, 1, 1)
        self.type.button(0).setChecked(True)
        argument_form.addRow(u"类型：", radio_layout)

        self.mode = QCheckBox()
        argument_form.addRow(u"实时：", self.mode)

        self.direction = QButtonGroup()
        radio_layout = QGridLayout()
        for i, text in enumerate([u"x", u"y", u"z", u"none"]):
            radio = QRadioButton(text)
            self.direction.addButton(radio, i)
            radio_layout.addWidget(radio, 0, i, 1, 1)
        self.direction.button(0).setChecked(True)
        argument_form.addRow(u"轴向：", radio_layout)

        self.radius = FloatSliderGroup()
        self.radius.set_range(0, 3)
        self.radius.set_value(1)
        argument_form.addRow(u"半径：", self.radius)

        layout.addStretch()
        button = QPushButton(u"解算")
        layout.addWidget(button)

        self.type.buttonClicked.connect(self.type_changed)
        self.mode.stateChanged.connect(self.real_time)
        self.radius.valueChange.connect(self.args_changed)
        self.bezier.valueChanged.connect(self.args_changed)
        button.clicked.connect(self.apply)

    def type_changed(self):
        self.mode.setChecked(Qt.Unchecked)

    def args_changed(self):
        if not self.mode.isChecked():
            return
        self.solve()

    def real_time(self, checked):
        if checked:
            self.kwargs = weight.solve_kwargs(self.type.checkedId(), self.direction.checkedId())
            self.solve()
        else:
            self.kwargs = None

    def apply(self):
        if not self.mode.isChecked():
            self.kwargs = weight.solve_kwargs(self.type.checkedId(), self.direction.checkedId())
        self.solve()

    def solve(self):
        if self.kwargs is None:
            return
        i = self.type.checkedId()
        r = self.radius.value()
        d = self.direction.checkedId()
        xs, ys = zip(*self.bezier.points)
        ys = [1-y for y in ys]
        self.kwargs.update(**locals())
        weight.solve(**self.kwargs)


qss = u"""
QWidget{
    font-size: 14px;
    font-family: 楷体;
} 
"""


def show():
    global window
    if window is None:
        window = FaceWeight()
        window.setWindowTitle("bezierWeight")
        window.setStyleSheet(qss)
        window.bezier.setFixedSize(512, 512)
        window.setFixedHeight(700)
    window.show()

