# _*_ coding:cp936 _*_
"""
Scripts :    python.tools.rigging.toolkitBasedCurve
Author  :    JesseChou
Date    :    2018/5/6
QQ      :    375714316
E-Mail  :    JesseChou0612@gmail.com or 375714316@qq.com
"""
import math
from PySide2 import QtWidgets, QtCore, QtGui
from maya import cmds
from python.core import myMath, setting
from python.meta import parent, attributes
from python.tools.rigging import controllerCreator, controllerManager

CONTROLLER_ATTRS_LIST = ['deformVis', 'switch', 'size', 'stretch', 'volume', 'coneU', 'coneV', 'volumeMultiplier',
                         'roll', 'twist', 'slide', 'decay', 'dropoff']


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parentUI=None):
        super(MainWindow, self).__init__(parentUI)
        self.setWindowTitle(u'曲线创建工具主窗口 Ver 2.0.0')
        self.createWidgets()
        self.createLayouts()
        self.createConnections()
        self._baseMainController = ''
        self._targetControllers = []
        self.__polyRadio = 1

    @property
    def colors(self):
        return [[0.627, 0.627, 0.627],
                [0.467, 0.467, 0.467],
                [0.0, 0.0, 0.0],
                [0.247, 0.247, 0.247],
                [0.498, 0.498, 0.498],
                [0.608, 0.0, 0.157],
                [0.0, 0.016, 0.373],
                [0.0, 0.0, 1.0],
                [0.0, 0.275, 0.094],
                [0.145, 0.0, 0.263],
                [0.78, 0.0, 0.78],
                [0.537, 0.278, 0.2],
                [0.243, 0.133, 0.122],
                [0.6, 0.145, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.255, 0.6],
                [1.0, 1.0, 1.0],
                [1.0, 1.0, 0.0],
                [0.388, 0.863, 1.0],
                [0.263, 1.0, 0.635],
                [1.0, 0.686, 0.686],
                [0.89, 0.675, 0.475],
                [1.0, 1.0, 0.384],
                [0.0, 0.6, 0.325],
                [0.627, 0.412, 0.188],
                [0.62, 0.627, 0.188],
                [0.408, 0.627, 0.188],
                [0.188, 0.627, 0.365],
                [0.188, 0.627, 0.627],
                [0.188, 0.404, 0.627],
                [0.435, 0.188, 0.627]]

    def createWidgets(self):
        self._mainTabTW_ = QtWidgets.QTabWidget()
        self._mainTabTW_.setTabPosition(QtWidgets.QTabWidget.North)

        def pedrailWidgets():
            self._pedrailCurveLE_ = QtWidgets.QLineEdit()
            self._pedrailCurveLE_.setEnabled(False)
            self._pedrailCurvePB_ = QtWidgets.QPushButton(u'载入曲线')

            self._pedrailModelLE_ = QtWidgets.QLineEdit()
            self._pedrailModelLE_.setEnabled(False)
            self._pedrailModelPB_ = QtWidgets.QPushButton(u'载入模型')

            self._frontAxisxRB_ = QtWidgets.QRadioButton('X')
            self._frontAxisxRB_.setChecked(True)
            self._frontAxisyRB_ = QtWidgets.QRadioButton('Y')
            self._frontAxiszRB_ = QtWidgets.QRadioButton('Z')

            self._customNumberCB_ = QtWidgets.QCheckBox(u'自定义数目')
            self._customAttributeCB_ = QtWidgets.QCheckBox(u'自定义属性')

            self._pedrailNumberSB_ = QtWidgets.QSpinBox()
            self._pedrailNumberSB_.setValue(9)
            self._pedrailNumberSB_.setEnabled(False)
            self._pedrailNumberSL_ = QtWidgets.QSlider()
            self._pedrailNumberSL_.setValue(9)
            self._pedrailNumberSL_.setEnabled(False)
            self._pedrailNumberSL_.setOrientation(QtCore.Qt.Horizontal)

            self._crossRatioSB_ = QtWidgets.QSpinBox()
            self._crossRatioSB_.setEnabled(False)
            self._crossRatioSL_ = QtWidgets.QSlider()
            self._crossRatioSL_.setEnabled(False)
            self._crossRatioSL_.setOrientation(QtCore.Qt.Horizontal)

            self._rotationSB_ = QtWidgets.QSpinBox()
            self._rotationSB_.setEnabled(False)
            self._rotationSL_ = QtWidgets.QSlider()
            self._rotationSL_.setEnabled(False)
            self._rotationSL_.setOrientation(QtCore.Qt.Horizontal)

            self._createPedrailPB_ = QtWidgets.QPushButton(u'创建履带')
            self._createPedrailPB_.setMinimumHeight(40)
            self._deletePedrailPB_ = QtWidgets.QPushButton(u'删除履带')

        def jointWidgets():
            self._jointCurveLE_ = QtWidgets.QLineEdit()
            self._jointCurveLE_.setEnabled(False)
            self._jointCurvePB_ = QtWidgets.QPushButton(u'载入曲线')
            self._jointNameLE_ = QtWidgets.QLineEdit()
            self._jointNameLE_.setText('splineJoint')
            self._jointNumberSB_ = QtWidgets.QSpinBox()
            self._jointNumberSB_.setValue(9)
            self._jointNumberSL_ = QtWidgets.QSlider()
            self._jointNumberSL_.setValue(9)
            self._jointNumberSL_.setOrientation(QtCore.Qt.Horizontal)
            self._jointReductionDSB_ = QtWidgets.QDoubleSpinBox()
            self._jointReductionDSB_.setValue(1)
            self._jointReductionDSB_.setRange(0.3, 3)
            self._jointReductionDSB_.setSingleStep(0.05)
            self._jointReductionSL_ = QtWidgets.QSlider()
            self._jointReductionSL_.setRange(30, 300)
            self._jointReductionSL_.setValue(100)
            self._jointReductionSL_.setOrientation(QtCore.Qt.Horizontal)

            self._jointCustomSideCB_ = QtWidgets.QCheckBox('')
            self._jointStartPositionDSB_ = QtWidgets.QDoubleSpinBox()
            self._jointStartPositionDSB_.setRange(0, 0.99)
            self._jointStartPositionDSB_.setEnabled(False)
            self._jointStartPositionDSB_.setSingleStep(0.05)
            self._jointStartPositionSL_ = QtWidgets.QSlider()
            self._jointStartPositionSL_.setRange(0, 99)
            self._jointStartPositionSL_.setEnabled(False)
            self._jointStartPositionSL_.setOrientation(QtCore.Qt.Horizontal)
            self._jointEndPositionDSB_ = QtWidgets.QDoubleSpinBox()
            self._jointEndPositionDSB_.setRange(0.01, 1)
            self._jointEndPositionDSB_.setValue(1)
            self._jointEndPositionDSB_.setEnabled(False)
            self._jointEndPositionDSB_.setSingleStep(0.05)
            self._jointEndPositionSL_ = QtWidgets.QSlider()
            self._jointEndPositionSL_.setRange(1, 100)
            self._jointEndPositionSL_.setValue(100)
            self._jointEndPositionSL_.setEnabled(False)
            self._jointEndPositionSL_.setOrientation(QtCore.Qt.Horizontal)

            self._createJointPB_ = QtWidgets.QPushButton(u'创建骨骼链')
            self._createJointPB_.setMinimumHeight(40)
            self._correctJointAxisPB_ = QtWidgets.QPushButton(u'修正骨骼轴向')
            self._storeJointAxisPB_ = QtWidgets.QPushButton(u'还原骨骼链')
            self._createPolyPB_ = QtWidgets.QPushButton(u'创建蒙皮模型')

        def splineWidgets():
            self._baseSplineGB_ = QtWidgets.QGroupBox()
            self._baseSplineGB_.setTitle(u'基础功能')

            self._controllerNumSB_ = QtWidgets.QSpinBox()
            self._controllerNumSB_.setRange(3, 20)
            self._controllerNumSB_.setValue(4)
            self._controllerNumSL_ = QtWidgets.QSlider()
            self._controllerNumSL_.setRange(3, 20)
            self._controllerNumSL_.setValue(4)
            self._controllerNumSL_.setOrientation(QtCore.Qt.Orientation.Horizontal)
            self._upVectorxDSB_ = QtWidgets.QDoubleSpinBox()
            self._upVectoryDSB_ = QtWidgets.QDoubleSpinBox()
            self._upVectoryDSB_.setValue(1)
            self._upVectorzDSB_ = QtWidgets.QDoubleSpinBox()

            self._frontVectorxDSB_ = QtWidgets.QDoubleSpinBox()
            self._frontVectorxDSB_.setValue(1)
            self._frontVectoryDSB_ = QtWidgets.QDoubleSpinBox()
            self._frontVectorzDSB_ = QtWidgets.QDoubleSpinBox()

            self._upObjectLE_ = QtWidgets.QLineEdit()
            self._upObjectLE_.setEnabled(False)
            self._upObjectPB_ = QtWidgets.QPushButton(u'选择')
            self._aimRB_ = QtWidgets.QRadioButton(u'目标')
            self._tangentRB_ = QtWidgets.QRadioButton(u'切线')
            self._tangentRB_.setChecked(True)
            self._offsetCB_ = QtWidgets.QCheckBox()
            self._offsetCB_.setChecked(True)

            self._addToSetsCB_ = QtWidgets.QCheckBox('')
            self._addToSetsCB_.setChecked(True)
            self._addToSetsLE_ = QtWidgets.QLineEdit()
            self._addToSetsLE_.setEnabled(False)
            self._addToSetsLE_.setText('ExtraControlSet')
            self._selectSetPB_ = QtWidgets.QPushButton(u'载入Set')

            self._mainControllerColorLB_ = QtWidgets.QLabel('')
            self._mainControllerColorSL_ = QtWidgets.QSlider()
            self._mainControllerColorSL_.setValue(6)
            self._mainControllerColorPM_ = QtGui.QPixmap(40, 15)
            self.setPixmapColor(self._mainControllerColorLB_, self._mainControllerColorPM_, 6)

            self._rollControllerColorLB_ = QtWidgets.QLabel('')
            self._rollControllerColorSL_ = QtWidgets.QSlider()
            self._rollControllerColorSL_.setValue(18)
            self._rollControllerColorPM_ = QtGui.QPixmap(40, 15)
            self.setPixmapColor(self._rollControllerColorLB_, self._rollControllerColorPM_, 18)

            self._fkControllerColorLB_ = QtWidgets.QLabel('')
            self._fkControllerColorSL_ = QtWidgets.QSlider()
            self._fkControllerColorSL_.setValue(14)
            self._fkControllerColorPM_ = QtGui.QPixmap(40, 15)
            self.setPixmapColor(self._fkControllerColorLB_, self._fkControllerColorPM_, 14)

            self._ikControllerColorLB_ = QtWidgets.QLabel('')
            self._ikControllerColorSL_ = QtWidgets.QSlider()
            self._ikControllerColorSL_.setValue(20)
            self._ikControllerColorPM_ = QtGui.QPixmap(40, 15)
            self.setPixmapColor(self._ikControllerColorLB_, self._ikControllerColorPM_, 20)

            self._createSplinePB_ = QtWidgets.QPushButton(u'创建骨骼链绑定（旧版本）')
            self._createSplinePB_.setMinimumHeight(20)
            self._createSplineSystemPB_ = QtWidgets.QPushButton(u'创建骨骼链系统')
            self._createSplineSystemPB_.setMinimumHeight(40)

            self._additionalGB_ = QtWidgets.QGroupBox()
            self._additionalGB_.setTitle(u'附加功能')

            self._baseControllerLE_ = QtWidgets.QLineEdit()
            self._baseControllerLE_.setEnabled(False)
            self._baseControllerPB_ = QtWidgets.QPushButton(u'载入')
            self._targetControllersLE_ = QtWidgets.QLineEdit()
            self._targetControllersLE_.setEnabled(False)
            self._targetControllersPB_ = QtWidgets.QPushButton(u'载入')
            self._hideTargetControllersCB_ = QtWidgets.QCheckBox()
            self._hideTargetControllersCB_.setChecked(True)
            self._connectAttrsPB_ = QtWidgets.QPushButton(u'属性关联')

            self._switchPB_ = QtWidgets.QPushButton(u'IK/FK 切换')

            for slider in [self._mainControllerColorSL_, self._rollControllerColorSL_, self._fkControllerColorSL_,
                           self._ikControllerColorSL_]:
                slider.setRange(0, 30)
                slider.setOrientation(QtCore.Qt.Orientation.Horizontal)

        pedrailWidgets()
        jointWidgets()
        splineWidgets()

    def createLayouts(self):
        self._mainLayout_ = QtWidgets.QVBoxLayout(self)

        def pedrailLayout():
            pedrailWT = QtWidgets.QWidget()

            pedrailLay = QtWidgets.QVBoxLayout(pedrailWT)

            pedrailSettingLay = QtWidgets.QFormLayout()

            curveLay = QtWidgets.QHBoxLayout()
            curveLay.addWidget(self._pedrailCurveLE_)
            curveLay.addWidget(self._pedrailCurvePB_)
            pedrailSettingLay.addRow(u'附着曲线:', curveLay)

            modelLay = QtWidgets.QHBoxLayout()
            modelLay.addWidget(self._pedrailModelLE_)
            modelLay.addWidget(self._pedrailModelPB_)
            pedrailSettingLay.addRow(u'履带模型:', modelLay)

            axisLay = QtWidgets.QHBoxLayout()
            axisLay.addWidget(self._frontAxisxRB_)
            axisLay.addWidget(self._frontAxisyRB_)
            axisLay.addWidget(self._frontAxiszRB_)
            pedrailSettingLay.addRow(u'向前轴向:', axisLay)

            customLay = QtWidgets.QHBoxLayout()
            customLay.addWidget(self._customNumberCB_)
            customLay.addWidget(self._customAttributeCB_)
            pedrailSettingLay.addRow(u'个性设置:', customLay)

            numberLay = QtWidgets.QHBoxLayout()
            numberLay.addWidget(self._pedrailNumberSB_)
            numberLay.addWidget(self._pedrailNumberSL_)
            pedrailSettingLay.addRow(u'履带数目:', numberLay)

            crossLay = QtWidgets.QHBoxLayout()
            crossLay.addWidget(self._crossRatioSB_)
            crossLay.addWidget(self._crossRatioSL_)
            pedrailSettingLay.addRow(u'交叉比例:', crossLay)

            rotateLay = QtWidgets.QHBoxLayout()
            rotateLay.addWidget(self._rotationSB_)
            rotateLay.addWidget(self._rotationSL_)
            pedrailSettingLay.addRow(u'旋转角度:', rotateLay)

            pedrailLay.addLayout(pedrailSettingLay)
            pedrailLay.addWidget(self._createPedrailPB_)
            pedrailLay.addWidget(self._deletePedrailPB_)
            return pedrailWT

        def jointLayout():
            jointWT = QtWidgets.QWidget()
            jointLay = QtWidgets.QVBoxLayout(jointWT)
            jointSettingLay = QtWidgets.QFormLayout()
            curveLay = QtWidgets.QHBoxLayout()
            curveLay.addWidget(self._jointCurveLE_)
            curveLay.addWidget(self._jointCurvePB_)

            jointSettingLay.addRow(u'附着曲线:', curveLay)

            jointSettingLay.addRow(u'骨骼名称:', self._jointNameLE_)

            numberLay = QtWidgets.QHBoxLayout()
            numberLay.addWidget(self._jointNumberSB_)
            numberLay.addWidget(self._jointNumberSL_)

            jointSettingLay.addRow(u'骨骼段数:', numberLay)

            reductionLay = QtWidgets.QHBoxLayout()
            reductionLay.addWidget(self._jointReductionDSB_)
            reductionLay.addWidget(self._jointReductionSL_)

            jointSettingLay.addRow(u'衰减比例:', reductionLay)

            jointSettingLay.addRow(u'自定义首尾:', self._jointCustomSideCB_)

            startLay = QtWidgets.QHBoxLayout()
            startLay.addWidget(self._jointStartPositionDSB_)
            startLay.addWidget(self._jointStartPositionSL_)

            jointSettingLay.addRow(u'起点位置:', startLay)

            endLay = QtWidgets.QHBoxLayout()
            endLay.addWidget(self._jointEndPositionDSB_)
            endLay.addWidget(self._jointEndPositionSL_)

            jointSettingLay.addRow(u'终点位置:', endLay)

            jointLay.addLayout(jointSettingLay)
            jointLay.addWidget(self._createJointPB_)

            plusLay = QtWidgets.QHBoxLayout()
            plusLay.addWidget(self._correctJointAxisPB_)
            plusLay.addWidget(self._storeJointAxisPB_)
            plusLay.addWidget(self._createPolyPB_)
            jointLay.addLayout(plusLay)

            return jointWT

        def splineLayout():
            splineWT = QtWidgets.QWidget()
            splineLay = QtWidgets.QVBoxLayout(splineWT)
            splineLay.addWidget(self._baseSplineGB_)
            splineLay.addWidget(self._additionalGB_)

            baseLay = QtWidgets.QVBoxLayout(self._baseSplineGB_)
            formLayout = QtWidgets.QFormLayout()
            numLay = QtWidgets.QHBoxLayout()
            numLay.addWidget(self._controllerNumSB_)
            numLay.addWidget(self._controllerNumSL_)
            formLayout.addRow(u'控制器数量:', numLay)

            upLay = QtWidgets.QHBoxLayout()
            upLay.addWidget(self._upVectorxDSB_)
            upLay.addWidget(self._upVectoryDSB_)
            upLay.addWidget(self._upVectorzDSB_)
            formLayout.addRow(u'向上向量:', upLay)

            frontLay = QtWidgets.QHBoxLayout()
            frontLay.addWidget(self._frontVectorxDSB_)
            frontLay.addWidget(self._frontVectoryDSB_)
            frontLay.addWidget(self._frontVectorzDSB_)
            formLayout.addRow(u'向前向量:', frontLay)

            objLay = QtWidgets.QHBoxLayout()
            objLay.addWidget(self._upObjectLE_)
            objLay.addWidget(self._upObjectPB_)
            formLayout.addRow(u'向上物体:', objLay)

            axisLay = QtWidgets.QHBoxLayout()
            axisLay.addWidget(self._aimRB_)
            axisLay.addWidget(self._tangentRB_)
            formLayout.addRow(u'轴向类型:', axisLay)

            formLayout.addRow(u'保持偏移:', self._offsetCB_)

            setLay = QtWidgets.QHBoxLayout()
            setLay.addWidget(self._addToSetsCB_)
            setLay.addWidget(self._addToSetsLE_)
            setLay.addWidget(self._selectSetPB_)
            formLayout.addRow(u'添加Set:', setLay)

            mainColorLay = QtWidgets.QHBoxLayout()
            mainColorLay.addWidget(self._mainControllerColorLB_)
            mainColorLay.addWidget(self._mainControllerColorSL_)
            formLayout.addRow(u'main颜色', mainColorLay)

            rollColorLay = QtWidgets.QHBoxLayout()
            rollColorLay.addWidget(self._rollControllerColorLB_)
            rollColorLay.addWidget(self._rollControllerColorSL_)
            formLayout.addRow(u'roll颜色', rollColorLay)

            fkColorLay = QtWidgets.QHBoxLayout()
            fkColorLay.addWidget(self._fkControllerColorLB_)
            fkColorLay.addWidget(self._fkControllerColorSL_)
            formLayout.addRow(u'FK颜色', fkColorLay)

            ikColorLay = QtWidgets.QHBoxLayout()
            ikColorLay.addWidget(self._ikControllerColorLB_)
            ikColorLay.addWidget(self._ikControllerColorSL_)
            formLayout.addRow(u'IK颜色', ikColorLay)

            baseLay.addLayout(formLayout)
            baseLay.addStretch(True)
            baseLay.addWidget(self._createSplinePB_)
            baseLay.addWidget(self._createSplineSystemPB_)

            additionalLay = QtWidgets.QVBoxLayout(self._additionalGB_)

            ctrlLay = QtWidgets.QFormLayout()

            mainCtrLay = QtWidgets.QHBoxLayout()
            mainCtrLay.addWidget(self._baseControllerLE_)
            mainCtrLay.addWidget(self._baseControllerPB_)
            ctrlLay.addRow(u'基础控制器:', mainCtrLay)

            targetCtrLay = QtWidgets.QHBoxLayout()
            targetCtrLay.addWidget(self._targetControllersLE_)
            targetCtrLay.addWidget(self._targetControllersPB_)
            ctrlLay.addRow(u'目标控制器:', targetCtrLay)

            ctrlLay.addRow(u'隐藏目标体:', self._hideTargetControllersCB_)
            additionalLay.addLayout(ctrlLay)

            additionalLay.addWidget(self._connectAttrsPB_)
            additionalLay.addWidget(self._switchPB_)

            return splineWT

        self._mainTabTW_.addTab(pedrailLayout(), u'创建履带')
        self._mainTabTW_.addTab(jointLayout(), u'创建骨骼')
        self._mainTabTW_.addTab(splineLayout(), u'骨骼链控制')
        self._mainLayout_.addWidget(self._mainTabTW_)

    def createConnections(self):
        def pedrailConnections():
            self._pedrailNumberSB_.valueChanged.connect(self._pedrailNumberSL_.setValue)
            self._pedrailNumberSL_.valueChanged.connect(self._pedrailNumberSB_.setValue)
            self._crossRatioSB_.valueChanged.connect(self._crossRatioSL_.setValue)
            self._crossRatioSL_.valueChanged.connect(self._crossRatioSB_.setValue)
            self._rotationSB_.valueChanged.connect(self._rotationSL_.setValue)
            self._rotationSL_.valueChanged.connect(self._rotationSB_.setValue)
            self._customNumberCB_.stateChanged.connect(self._pedrailNumberSB_.setEnabled)
            self._customNumberCB_.stateChanged.connect(self._pedrailNumberSL_.setEnabled)
            self._customAttributeCB_.stateChanged.connect(self._crossRatioSB_.setEnabled)
            self._customAttributeCB_.stateChanged.connect(self._crossRatioSL_.setEnabled)
            self._customAttributeCB_.stateChanged.connect(self._rotationSB_.setEnabled)
            self._customAttributeCB_.stateChanged.connect(self._rotationSL_.setEnabled)
            self._createPedrailPB_.clicked.connect(self.createPedrail)
            self._deletePedrailPB_.clicked.connect(self.removePedrail)
            self._pedrailCurvePB_.clicked.connect(self.loadPedrailCurve)
            self._pedrailModelPB_.clicked.connect(self.loadPedrailModel)

        def jointConnections():
            self._jointNumberSB_.valueChanged.connect(self._jointNumberSL_.setValue)
            self._jointNumberSL_.valueChanged.connect(self._jointNumberSB_.setValue)
            self._jointCustomSideCB_.stateChanged.connect(self._jointStartPositionDSB_.setEnabled)
            self._jointCustomSideCB_.stateChanged.connect(self._jointStartPositionSL_.setEnabled)
            self._jointCustomSideCB_.stateChanged.connect(self._jointEndPositionDSB_.setEnabled)
            self._jointCustomSideCB_.stateChanged.connect(self._jointEndPositionSL_.setEnabled)

            self._jointReductionDSB_.valueChanged.connect(self.changeJointReductionDSB)
            self._jointReductionSL_.valueChanged.connect(self.changeJointReductionSL)
            self._jointStartPositionDSB_.valueChanged.connect(self.changeJointStartDSB)
            self._jointStartPositionSL_.valueChanged.connect(self.changeJointStartSL)
            self._jointEndPositionDSB_.valueChanged.connect(self.changeJointEndDSB)
            self._jointEndPositionSL_.valueChanged.connect(self.changeJointEndSL)

            self._jointCurvePB_.clicked.connect(self.loadJointCurve)
            self._createJointPB_.clicked.connect(self.createJoint)
            self._jointCustomSideCB_.stateChanged.connect(self.changeJointSide)
            self._correctJointAxisPB_.clicked.connect(self.correctJointAxis)
            self._storeJointAxisPB_.clicked.connect(restoreJoints)
            self._createPolyPB_.clicked.connect(self.createPolys)

        def splineConnections():
            self._controllerNumSB_.valueChanged.connect(self._controllerNumSL_.setValue)
            self._controllerNumSL_.valueChanged.connect(self._controllerNumSB_.setValue)
            self._createSplinePB_.clicked.connect(self.createSplineJoint)
            self._createSplineSystemPB_.clicked.connect(self.createSplineSystem)
            self._upObjectPB_.clicked.connect(self.loadUpObject)
            self._baseControllerPB_.clicked.connect(self.loadBaseController)
            self._targetControllersPB_.clicked.connect(self.loadTargetControllers)
            self._connectAttrsPB_.clicked.connect(self.connectAttrs)
            self._mainControllerColorSL_.valueChanged.connect(self.changeMainColor)
            self._rollControllerColorSL_.valueChanged.connect(self.changeRollColor)
            self._fkControllerColorSL_.valueChanged.connect(self.changeFkColor)
            self._ikControllerColorSL_.valueChanged.connect(self.changeIkColor)
            self._addToSetsCB_.stateChanged.connect(self._selectSetPB_.setEnabled)
            self._selectSetPB_.clicked.connect(self.loadControlSets)

        pedrailConnections()
        jointConnections()
        splineConnections()

    def changeJointReductionDSB(self, *args):
        value = self._jointReductionDSB_.value()
        self._jointReductionSL_.setValue(int(value * 100))

    def changeJointReductionSL(self, *args):
        value = self._jointReductionSL_.value()
        self._jointReductionDSB_.setValue(value * 0.01)

    def changeJointStartDSB(self, *args):
        start = self._jointStartPositionDSB_.value()
        self._jointStartPositionSL_.setValue(int(start * 100))
        end = self._jointEndPositionDSB_.value()
        if start >= end:
            self._jointEndPositionDSB_.setValue(start + 0.01)
        self.slideJoints()

    def changeJointStartSL(self, *args):
        start = self._jointStartPositionSL_.value()
        self._jointStartPositionDSB_.setValue(start * 0.01)
        end = self._jointEndPositionSL_.value()
        if start >= end:
            self._jointEndPositionDSB_.setValue((start + 1) * 0.01)

    def changeJointEndDSB(self, *args):
        end = self._jointEndPositionDSB_.value()
        self._jointEndPositionSL_.setValue(int(end * 100))
        start = self._jointStartPositionDSB_.value()
        if end <= start:
            self._jointStartPositionDSB_.setValue(end - 0.01)
        self.slideJoints()

    def changeJointEndSL(self, *args):
        end = self._jointEndPositionSL_.value()
        self._jointEndPositionDSB_.setValue(end * 0.01)
        start = self._jointStartPositionSL_.value()
        if end <= start:
            self._jointStartPositionSL_.setValue(end - 1)

    def createPedrail(self, *args):
        curve = self._pedrailCurveLE_.text()
        model = self._pedrailModelLE_.text()
        if cmds.objExists(curve) and cmds.objExists(model):
            axis, number, cross, rotate = 0, 0, 0, 0
            if self._frontAxisyRB_.isChecked():
                axis = 1
            if self._frontAxiszRB_.isChecked():
                axis = 2
            if self._customNumberCB_.isChecked():
                number = self._pedrailNumberSB_.value()
            if self._customAttributeCB_.isChecked():
                cross = self._crossRatioSB_.value()
                rotate = self._rotationSB_.value()

            createPedrail(curve, model, axis=axis, num=number, cross=cross, rotate=rotate)

    def removePedrail(self, *args):
        curve = self._pedrailCurveLE_.text()
        if cmds.objExists('%sTreadsGrp' % curve):
            cmds.delete('%sTreadsGrp' % curve)

    def loadPedrailCurve(self, *args):
        curve = getSelectedByShape() or ''
        self._pedrailCurveLE_.setText(curve)

    def loadPedrailModel(self, *args):
        model = getSelectedByShape('mesh') or ''
        self._pedrailModelLE_.setText(model)

    def loadJointCurve(self, *args):
        curve = getSelectedByShape() or ''
        self._jointCurveLE_.setText(curve)

    def createJoint(self, *args):
        curve = self._jointCurveLE_.text()
        name = self._jointNameLE_.text()
        number = self._jointNumberSB_.value()
        attenuate = self._jointReductionDSB_.value()
        sign, start, end = 0, 0, 1
        if self._jointCustomSideCB_.isChecked():
            start = self._jointStartPositionDSB_.value()
            end = self._jointEndPositionDSB_.value()
            removeSideJoints(curve, name)
        createJoints(curve, name, number, sign=sign, start=start, end=end, attenuate=attenuate)

    def changeJointSide(self, *args):
        curve = self._jointCurveLE_.text()
        name = self._jointNameLE_.text()
        number = self._jointNumberSB_.value()
        if self._jointCustomSideCB_.isChecked():
            sideJoints(curve, name, number)
        else:
            removeSideJoints(curve, name)

    def slideJoints(self):
        name = self._jointNameLE_.text()
        number = self._jointNumberSB_.value()
        start = self._jointStartPositionDSB_.value()
        end = self._jointEndPositionDSB_.value()
        sign = 0
        startJnt = '%s%s1' % (name, ['', '_'][sign])
        cmds.setAttr('%s.localPosition' % startJnt, start)
        endJnt = '%s%s%d' % (name, ['', '_'][sign], number + 1)
        cmds.setAttr('%s.localPosition' % endJnt, end)

    def correctJointAxis(self, *args):
        sels = cmds.ls(sl=1, type='joint')
        if sels:
            correctAxis(sels[0])

    def createPolys(self, *args):
        sels = cmds.ls(sl=1, typ='joint')
        if sels:
            createPolyAlongJoints(sels[0], self.__polyRadio)

    def loadUpObject(self, *args):
        sels = cmds.ls(sl=1)
        if sels:
            self._upObjectLE_.setText(sels[0])
        else:
            self._upObjectLE_.setText('')

    def setPixmapColor(self, label, pixmap, index):
        color = QtGui.QColor()
        color.setRgbF(*self.colors[index + 1])
        pixmap.fill(color)
        label.setPixmap(pixmap)

    def changeMainColor(self, *args):
        value = self._mainControllerColorSL_.value()
        self.setPixmapColor(self._mainControllerColorLB_, self._mainControllerColorPM_, value)

    def changeRollColor(self, *args):
        value = self._rollControllerColorSL_.value()
        self.setPixmapColor(self._rollControllerColorLB_, self._rollControllerColorPM_, value)

    def changeFkColor(self, *args):
        value = self._fkControllerColorSL_.value()
        self.setPixmapColor(self._fkControllerColorLB_, self._fkControllerColorPM_, value)

    def changeIkColor(self, *args):
        value = self._ikControllerColorSL_.value()
        self.setPixmapColor(self._ikControllerColorLB_, self._ikControllerColorPM_, value)

    def createSplineJoint(self, *args):
        number = self._controllerNumSB_.value()
        upObject = self._upObjectLE_.text()

        up = [self._upVectorxDSB_.value(),
              self._upVectoryDSB_.value(),
              self._upVectorzDSB_.value()]

        front = [self._frontVectorxDSB_.value(),
                 self._frontVectoryDSB_.value(),
                 self._frontVectorzDSB_.value()]
        style = 'aim'
        if self._tangentRB_.isChecked():
            style = 'tangent'
        offset = self._offsetCB_.isChecked()
        sels = cmds.ls(sl=1, type='joint')
        for sel in sels:
            createSplineSystem(sel, number, uo=upObject, uv=up, av=front, axis=style, offset=offset)

    def createSplineSystem(self, *args):
        addToSet = self._addToSetsCB_.isChecked()
        setName = self._addToSetsLE_.text()
        number = self._controllerNumSB_.value()
        upObject = self._upObjectLE_.text()
        up = [self._upVectorxDSB_.value(),
              self._upVectoryDSB_.value(),
              self._upVectorzDSB_.value()]

        aim = [self._frontVectorxDSB_.value(),
               self._frontVectoryDSB_.value(),
               self._frontVectorzDSB_.value()]
        style = 0
        mainColor = self._mainControllerColorSL_.value()
        rollColor = self._rollControllerColorSL_.value()
        fkColor = self._fkControllerColorSL_.value()
        ikColor = self._ikControllerColorSL_.value()
        if self._tangentRB_.isChecked():
            style = 1
        keepOffset = self._offsetCB_.isChecked()
        sels = cmds.ls(sl=1, type='joint')
        for sel in sels:
            system = SplineSystem(sel, controllerNumber=number, upVector=up, aimVector=aim, upObject=upObject,
                                  axis=style, keepOffset=keepOffset, mainColor=mainColor, rollColor=rollColor,
                                  fkColor=fkColor, ikColor=ikColor, ats=addToSet, sn=setName)
            system.createSplineSystem()

    def loadBaseController(self, *args):
        ctrs = getMainControllers()
        if ctrs:
            self._baseMainController = ctrs[0]
        else:
            self._baseMainController = ''
        self._baseControllerLE_.setText(self._baseMainController)

    def loadTargetControllers(self, *args):
        ctrs = getMainControllers()
        if self._baseMainController in ctrs:
            ctrs.remove(self._baseMainController)
        self._targetControllers = ctrs
        self._targetControllersLE_.setText(','.join(self._targetControllers))

    def connectAttrs(self, *args):
        hide = self._hideTargetControllersCB_.isChecked()
        if self._baseMainController and self._targetControllers:
            if cmds.objExists(self._baseMainController):
                failedList = []
                for ctr in self._targetControllers:
                    judge = connectControllerAttrs(self._baseMainController, ctr, hide)
                    if not judge:
                        failedList.append(ctr)
                if failedList:
                    QtWidgets.QMessageBox.warning(self, u'未完全连接成功',
                                                  u'以下控制器，未完全连接成功\r\n%s' % ('\r\n'.join(failedList)))
            else:
                QtWidgets.QMessageBox.warning(self, u'信息不全', u'指定的主控制器不存在')
        else:
            QtWidgets.QMessageBox.warning(self, u'信息不全', u'请指定主控制器和目标控制器')

    def loadControlSets(self):
        selectSets = getSelectionSets()
        if selectSets:
            self._addToSetsLE_.setText(selectSets)


def checkIsMainController(controller):
    """
    # 检查指定控制器是否为骨骼链系统的主控制器
    :param controller: 指定控制器名称
    :return: True/False
    """
    judge = False
    num = 0
    for attr in CONTROLLER_ATTRS_LIST:
        if cmds.objExists('%s.%s' % (controller, attr)):
            num += 1
            if num > 5:
                judge = True
                break
    return judge


def connectControllerAttrs(baseController, targetController, hide=True):
    """
    连接两个控制器的控制属性
    :param baseController: 基础控制器
    :param targetController: 目标控制器
    :param hide: 隐藏目标体
    :return:
    """
    judge = True
    for attr in CONTROLLER_ATTRS_LIST:
        if cmds.objExists('%s.%s' % (baseController, attr)) and cmds.objExists('%s.%s' % (targetController, attr)):
            cmds.connectAttr('%s.%s' % (baseController, attr), '%s.%s' % (targetController, attr), f=True)
        else:
            if attr not in ['dropoff']:
                judge = False
    if judge and hide:
        try:
            cmds.setAttr('%s.v' % targetController, 0)
        except Exception as e:
            print (e)
    return judge


def getMainControllers():
    # 获取所选物体中的主控制器
    sels = cmds.ls(sl=True)
    controllers = []
    for sel in sels:
        judge = checkIsMainController(sel)
        if judge:
            controllers.append(sel)
    return controllers


def getSelectedByShape(shape='nurbsCurve', mode=0):
    """
    # 根据形节点类型获取物体
    :param shape: 形节点类型
    :param mode: 选择模式,0 => 单物体模式，1 => 多物体模式
    :return: 获取的物体信息
    """
    sels = cmds.ls(sl=1)
    objs = []
    for sel in sels:
        shapes = cmds.listRelatives(sel, s=1)
        for tmp in shapes:
            if cmds.nodeType(tmp) == shape:
                if mode == 0:
                    objs = sel
                    break
                if mode == 1:
                    objs.append(sel)
    return objs


def createPedrail(curve, model, **kwargs):
    """
    # 创建链条
    curve: the path curve
    model: the base model to duplicate
    axis: front and up axis,0 => ['X','Y'],1 => ['Y','Z'],2 => ['Z','X']
    num : the number you want to duplicate,if num is 0,we will compute the best num
    cross: the cross of tow models
    rotate: the rotate of tow models
    """
    axis = kwargs.get('axis', 0)
    num = kwargs.get('num', 0)
    cross = kwargs.get('cross', 0)
    rotate = kwargs.get('rotate', 0)
    length = cmds.arclen(curve)
    modelBb = cmds.xform(model, q=1, bb=1)
    widthX = abs(modelBb[3] - modelBb[0])
    widthY = abs(modelBb[4] - modelBb[1])
    widthZ = abs(modelBb[5] - modelBb[2])
    front, up = [['X', 'Y'], ['Y', 'Z'], ['Z', 'X']][axis]
    if num == 0:
        num = int(length / [widthX, widthY, widthZ][axis] / (1 - cross * .001))
    else:
        scale = length / num / ([widthX, widthY, widthZ][axis] * (1 - cross * .01))
        cmds.setAttr('%s.s' % model, scale, scale, scale, type='double3')
    offset = 1.0 / num
    instanceModels = []
    for i in range(num):
        instanceModel = cmds.instance(model, n='%sTread%d' % (curve, i + 1))
        instanceModels.append(instanceModel[0])
        motionPath = cmds.pathAnimation(instanceModel, c=curve, n='%sMotPath%d' % (curve, i + 1), fm=1, f=1, fa=front,
                                        ua=up, iu=0, inverseFront=0, b=0, stu=1, wut='normal')
        cmds.setAttr('%s.frontTwist' % motionPath, rotate * i)
        tmps = cmds.connectionInfo('%s.uValue' % motionPath, sfd=1).split('.')
        cmds.delete(tmps[0])
        cmds.setAttr('%s.uValue' % motionPath, offset * i)
    cmds.group(instanceModels, w=1, n='%sTreadsGrp' % curve)
    cmds.scale(1, 1, 1, model, a=1)


def sideJoints(curve, name, num, sign=0):
    """
    # 创建边界骨骼点
    curve: the path curve
    name: the joint name
    num: the joint number
    sign: if needs a sign between the name and index
    """
    infos = []
    if cmds.objExists(curve):
        indexs = [1, num + 1]
        copyCurve = cmds.duplicate(curve, rr=1, n='%sCopyFor%s' % (curve, name))[0]
        infos.append(copyCurve)
        cmds.rebuildCurve(copyCurve, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=100, d=3, tol=.01)
        cmds.setAttr('%s.v' % copyCurve, 0)
        shape = cmds.listRelatives(copyCurve, s=1)[0]
        for i in [0, 1]:
            jointName = '%s_%d' % (name, indexs[i]) if sign else '%s%d' % (name, indexs[i])
            infos.append(jointName)
            poci = cmds.createNode('pointOnCurveInfo', n='%s_%s_poci' % (copyCurve, jointName))
            cmds.connectAttr('%s.worldSpace[0]' % shape, '%s.inputCurve' % poci, f=1)
            jointName = cmds.joint(n=jointName)
            cmds.connectAttr('%s.position' % poci, '%s.t' % jointName, f=1)
            cmds.setAttr('%s.turnOnPercentage' % poci, 1)
            cmds.setAttr('%s.parameter' % poci, i)
            cmds.addAttr(jointName, ln='localPosition', at='double', min=0, max=1, dv=i)
            cmds.setAttr('%s.localPosition' % jointName, e=1, k=1)
            cmds.connectAttr('%s.localPosition' % jointName, '%s.parameter' % poci, f=1)
    return infos


def removeSideJoints(curve, name):
    # 删除边界骨骼点
    copyCurve = '%sCopyFor%s' % (curve, name)
    if cmds.objExists(copyCurve):
        shape = cmds.listRelatives(copyCurve, s=1)[0]
        connections = cmds.listConnections('%s.worldSpace[0]' % shape)
        if connections:
            for con in connections:
                tmps = cmds.listConnections('%s.position' % con)
                cmds.delete(con)
                if tmps:
                    cmds.delete(tmps)
        cmds.delete(copyCurve)
    return None


def createJoints(curve, name, num, **kwargs):
    """
    # 在曲线创建骨骼链
    curve: the path curve
    name: the joint name
    num: the joint number
    sign: if needs a sign between the name and index
    start: the position of the first joint to build
    end: the position of the end joint to build
    attenuate: the attenuate of the joints
    """
    joints = []
    sign = kwargs.get('sign', 0)
    start = kwargs.get('start', 0)
    end = kwargs.get('end', 1)
    attenuate = kwargs.get('attenuate', 1)

    copyCurve = cmds.duplicate(curve, rr=1, n='%sCopyFor%s' % (curve, name))[0]
    cmds.rebuildCurve(copyCurve, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=100, d=3, tol=.01)

    curveLength = cmds.arclen(copyCurve)
    length = (end - start) * curveLength
    eachLengths = [pow(attenuate, n) for n in range(num)]
    preLength = length / sum(eachLengths)

    startPosition = start * curveLength
    positions = [startPosition]
    for i in eachLengths:
        startPosition += preLength * i
        positions.append(startPosition)

    pos = [cmds.pointOnCurve(copyCurve, top=1, pr=p / curveLength, p=1) for p in positions]
    cmds.delete(copyCurve)
    parentJnt = ''
    for i in range(num + 1):
        nam = '%s_%d' % (name, i + 1) if sign else '%s%d' % (name, i + 1)
        jnt = cmds.joint(p=pos[i], n=nam)
        joints.append(jnt)
        if parentJnt:
            cmds.joint(parentJnt, e=1, zso=1, oj='xyz', sao='yup')
        parentJnt = jnt
    cmds.delete(cmds.orientConstraint(joints[-2], joints[-1], w=1))
    cmds.makeIdentity(joints, a=1, t=1, r=1, s=1)
    return joints


def correctAxis(joint):
    # 修正骨骼链轴向
    parent = cmds.listRelatives(joint, p=1)
    group = '%s__CorrectAxis' % joint
    group = cmds.createNode('transform', n=group)
    if parent:
        cmds.parent(group, parent)
    cmds.addAttr(group, ln='jointInfos', dt='string')
    cmds.addAttr(group, ln='constraint', dt='string')

    infos = analyseJointInfos(joint)
    cmds.setAttr('%s.jointInfos' % group, str(infos), typ='string', l=1)

    joints = infos.keys()
    cmds.parent(joints, group)
    for jnt in joints:
        cmds.setAttr('%s.displayLocalAxis' % jnt, 1)

    tipJnts = []
    for key in joints:
        if not infos.get(key):
            tipJnts.append(key)
    cons = []
    for key in joints:
        if key not in tipJnts:
            children = infos.get(key, [])
            for child in children:
                if child in tipJnts:
                    con = cmds.orientConstraint(key, child, w=1, o=[0, 0, 0])
                else:
                    con = cmds.orientConstraint(key, child, w=1, o=[0, 0, 0], skip=['y', 'z'])
                cons += con
    cmds.setAttr('%s.constraint' % group, str(cons), typ='string', l=1)
    return None


def restoreJoints(*args):
    # 还原骨骼链
    sels = cmds.ls(sl=1)
    for sel in sels:
        pars = cmds.listRelatives(sel, p=1)
        if pars:
            group = pars[0]
            if group.endswith('__CorrectAxis'):
                infos = eval(cmds.getAttr('%s.jointInfos' % group))
                cons = eval(cmds.getAttr('%s.constraint' % group))
                for con in cons:
                    if cmds.objExists(con):
                        cmds.delete(con)

                for key, value in infos.iteritems():
                    cmds.setAttr('%s.displayLocalAxis' % key, 0)
                    if value:
                        cmds.parent(value, key)

                parent = cmds.listRelatives(group, p=1)
                topJnt = cmds.listRelatives(group, c=1)
                if parent:
                    cmds.parent(topJnt, parent)
                else:
                    cmds.parent(topJnt, w=1)
                cmds.delete(group)
    return None


def analyseJointInfos(joint):
    # 分析骨骼信息
    children = cmds.listRelatives(joint, c=1, type='joint') or []
    infos = {joint: children}
    for child in children:
        for k, v in analyseJointInfos(child).items():
            infos[k] = v
    return infos


def createPolyAlongJoints(startJoint, radio=1):
    # 沿骨骼链创建poly模型
    joints = getSplineJoints(startJoint)
    plane = cmds.polyPlane(w=radio, h=radio, sx=1, sy=1, ax=[1, 0, 0], ch=0)[0]
    p1, p2, p3, p4 = [], [], [], []
    for i in range(len(joints)):
        cons = cmds.parentConstraint(joints[i], plane, w=1, mo=0)
        p1.append(cmds.xform('%s.pnts[0]' % plane, q=1, ws=1, t=1))
        p2.append(cmds.xform('%s.pnts[1]' % plane, q=1, ws=1, t=1))
        p3.append(cmds.xform('%s.pnts[3]' % plane, q=1, ws=1, t=1))
        p4.append(cmds.xform('%s.pnts[2]' % plane, q=1, ws=1, t=1))
        cmds.delete(cons)
    cmds.delete(plane)

    polys = []
    for i in range(len(p1) - 1):
        pol1 = cmds.polyCreateFacet(p=[p2[i], p2[i + 1], p1[i + 1], p1[i]], ch=0)[0]
        pol2 = cmds.polyCreateFacet(p=[p3[i], p3[i + 1], p2[i + 1], p2[i]], ch=0)[0]
        pol3 = cmds.polyCreateFacet(p=[p4[i], p4[i + 1], p3[i + 1], p3[i]], ch=0)[0]
        pol4 = cmds.polyCreateFacet(p=[p1[i], p1[i + 1], p4[i + 1], p4[i]], ch=0)[0]
        polys += [pol1, pol2, pol3, pol4]

    poly = cmds.polyUnite(polys, ch=0, n='%sPoly' % startJoint)[0]
    cmds.polyMergeVertex('%s.vtx[*]' % poly, d=0.001, ch=0, am=1)
    cmds.select(cl=1)
    return poly


def getSplineJoints(start, style=0):
    """
    # 获取骨骼链
    start: the start joint name
    style: get style, 0 => max, 1 => min
    """
    infos = [start]
    children = cmds.listRelatives(start, c=1, f=1) or []
    length = 0
    child_infs = []
    for child in children:
        infs = getSplineJoints(child, style)
        if style == 0:
            if len(infs) > length:
                length = len(infs)
                child_infs = infs
        if style == 1:
            if length == 0:
                length = len(infs)
                child_infs = infs
            else:
                if len(infs) < length:
                    length = len(infs)
                    child_infs = infs
    infos += child_infs
    return infos


# 骨骼链创建工具

def createSplineSystem(startJoint, number, **kwargs):
    """
    #创建骨骼链绑定
    :param startJoint: 起始骨骼
    :param number: 控制器数目
    :param kwargs:  axis => 轴向类型
                    upObject => 朝向物体
                    offset => 保持偏移
                    upVector => 向上向量
                    aimVector => 目标向量
    :return:
    """
    axis = kwargs.get('axis', 'tangent')
    upObject = kwargs.get('upObject', kwargs.get('uo', None))
    offset = kwargs.get('offset', kwargs.get('o', True))
    upVector = kwargs.get('upVector', kwargs.get('uv', [0, 1, 0]))
    aimVector = kwargs.get('aimVector', kwargs.get('av', [1, 0, 0]))
    name = startJoint
    while True:
        if name[-1].isdigit():
            name = name[:-1]
        else:
            break

    mainGrp = '%sSplineGrp' % name
    if not cmds.objExists(mainGrp):
        mainGrp = cmds.createNode('transform', n=mainGrp)
        cmds.addAttr(mainGrp, ln='Author', dt='string')
        cmds.setAttr('%s.Author' % mainGrp, 'Jesse Chou', type='string', l=1)

        cmds.addAttr(mainGrp, ln='Mail', dt='string')
        cmds.setAttr('%s.Mail' % mainGrp, 'JesseChou0612@gmail.com or 375714316@qq.com', type='string', l=1)

    rigSystem = '%sRigSystem' % name
    if not cmds.objExists(rigSystem):
        rigSystem = cmds.createNode('transform', n=rigSystem)
        cmds.setAttr('%s.v' % rigSystem, 0, l=1)
        cmds.setAttr('%s.inheritsTransform' % rigSystem, 0)
        cmds.parent(rigSystem, mainGrp)
        lockChannels(rigSystem)

    globalScaleLoc = '%sGlobalScaleLoc' % name
    if not cmds.objExists(globalScaleLoc):
        globalScaleLoc = cmds.container(type='dagContainer', ind=['inputs', 'outputs'], includeShaders=True,
                                        includeHierarchyBelow=True, includeTransform=True, n=globalScaleLoc)
        cmds.setAttr('%s.iconName' % globalScaleLoc, 'out_transform.png', type='string', l=1)
        cmds.setAttr('%s.blackBox' % globalScaleLoc, 1, l=1)
        cmds.setAttr('%s.inheritsTransform' % globalScaleLoc)
        cmds.parent(globalScaleLoc, rigSystem)
        scaleCons = cmds.scaleConstraint(mainGrp, globalScaleLoc)
        lockChannels(globalScaleLoc)
        cmds.addAttr(globalScaleLoc, ln='Author', dt='string')
        cmds.setAttr('%s.Author' % globalScaleLoc, 'Jesse Chou', type='string', l=1)

        cmds.addAttr(globalScaleLoc, ln='Mail', dt='string')
        cmds.setAttr('%s.Mail' % globalScaleLoc, 'JesseChou0612@gmail.com or 375714316@qq.com', type='string', l=1)

    deformSystem = '%sDeformSystem' % name
    if not cmds.objExists(deformSystem):
        deformSystem = cmds.createNode('transform', n=deformSystem)
        cmds.parent(deformSystem, mainGrp)

    joints = getSplineJoints(startJoint)

    baseCurve = createSplineCurveOld(joints, number, name)

    pointsInfos = createLocationPoints(baseCurve, name)
    targetCurve = pointsInfos.get('targetCrv')
    location = pointsInfos.get('location')

    setAxis(baseCurve, location, style=axis, upObj=upObject, upVector=upVector, aimVector=aimVector)

    ctrls = correctSidePositions(location)

    handleGrp = createControlHandle(ctrls)

    ctrInfos = createController(name, ctrls)

    constraintGrp = ctrInfos.get('constraintGrp')
    cmds.parent(scaleCons, constraintGrp)
    controllerGrp = ctrInfos.get('controllerGrp')

    controller = ctrInfos.get('mainCtr')

    motionInfos = createMotionPathSystem(joints, baseCurve, targetCurve, controller, globalScaleLoc, offset)
    positionGrp = motionInfos.get('positionGrp')
    constraints = motionInfos.get('constraints')
    nodes = motionInfos.get('nodes')
    cmds.parent(constraints, constraintGrp)

    cmds.parent(baseCurve, targetCurve, handleGrp, constraintGrp, positionGrp, rigSystem)
    cmds.parent(controllerGrp, mainGrp)
    cmds.parent(startJoint, deformSystem)
    cmds.connectAttr('%s.deformVis' % controller, '%s.v' % deformSystem, f=1)
    # createJointGroup(joints, deformSystem)
    cmds.container(globalScaleLoc, e=1, f=1, addNode=nodes)


def lockChannels(obj):
    # 锁定并隐藏物体通道属性
    for attr in setting.CHANNEL_BASE_ATTRS:
        cmds.setAttr('%s.%s' % (obj, attr), e=1, l=1, k=0)
    return None


def createSplineCurveOld(joints, number, name):
    """
    #创建曲线
    :param joints: 需要创建曲线的骨骼
    :param number: 创建曲线的点数
    :param name: 曲线名称
    :return:
    """
    pos = [cmds.xform(jnt, q=1, ws=1, t=1) for jnt in joints]
    crv = cmds.curve(d=1, n='%sBaseCrv' % name, p=pos)
    shape = cmds.listRelatives(crv, s=1)[0]
    cmds.rename(shape, '%sShape' % crv)
    cmds.rebuildCurve(crv, s=number - 1, d=3, kr=0)
    cmds.setAttr('%s.v' % crv, 0)
    lockChannels(crv)
    return crv


def createLocationPoints(curve, name):
    """
    # 创建控制loc
    :param curve: 基础曲线
    :param name: 控制点名称
    :return:
    """

    infos = {'location': [], 'aim': [], 'targetCrv': None}
    curve_shape = None
    if cmds.nodeType(curve) != 'nurbsCurve':
        shapes = cmds.listRelatives(curve, s=1)
        for sha in shapes:
            if cmds.nodeType(sha) == 'nurbsCurve':
                curve_shape = sha
                break
    else:
        curve_shape = curve
    if curve_shape:
        tarCrv = cmds.duplicate(curve, n='%sTargetCrv' % name)[0]
        infos['targetCrv'] = tarCrv
        tarShape = cmds.listRelatives(tarCrv, s=1, typ='nurbsCurve')[0]
        tcps = cmds.ls('%s.controlPoints[*]' % tarShape, fl=1)
        length = cmds.arclen(curve_shape, ch=0)
        cps = cmds.ls('%s.controlPoints[*]' % curve_shape, fl=1)
        num = len(cps)
        offset = length * 1.0 / num
        n = 1
        for i in range(num):
            position = cmds.xform(cps[i], q=1, ws=1, t=1)
            if i == 1:
                nam_cp = '%sPositionExt%d_cp' % (name, n - 1)
                nam_aim = '%sPositionExt%d_aim' % (name, n - 1)
            elif i == num - 2:
                nam_cp = '%sPositionExt%d_cp' % (name, n)
                nam_aim = '%sPositionExt%d_aim' % (name, n)
            else:
                nam_cp = '%sPosition%d_cp' % (name, n)
                nam_aim = '%sPosition%d_aim' % (name, n)
                n += 1

            pos_cp = cmds.spaceLocator(n=nam_cp, p=[0, 0, 0])[0]
            cmds.setAttr('%s.v' % pos_cp, 0)
            pos_aim = cmds.spaceLocator(n=nam_aim, p=[0, 0, 0])[0]
            cmds.setAttr('%s.v' % pos_aim, 0)
            cmds.setAttr('%s.ty' % pos_aim, offset)
            cmds.parent(pos_aim, pos_cp)
            cmds.xform(pos_cp, ws=1, t=position)
            shape = cmds.listRelatives(nam_cp, s=1)[0]
            cmds.connectAttr('%s.worldPosition[0]' % shape, cps[i])
            aimShape = cmds.listRelatives(nam_aim, s=1)[0]
            cmds.connectAttr('%s.worldPosition[0]' % aimShape, tcps[i])
            infos['location'].append(pos_cp)
            infos['aim'].append(pos_aim)

    return infos


def setAxis(curve, controlPoints, style='aim', upObj=None, upVector=[0, 1, 0], aimVector=[1, 0, 0]):
    """
    #设置控制点方向
    :param curve:基础曲线
    :param controlPoints:控制点
    :param style:轴向模式
    :param upObj:朝向物体
    :param upVector:向上向量
    :param aimVector:朝向向量
    :return:
    """
    delObjs = []
    if not upObj:
        nums = len(controlPoints)
        aimObj = controlPoints[nums // 2]
        if nums % 2 == 0:
            aimObj = cmds.group(em=1)
            cmds.delete(cmds.pointConstraint(controlPoints[nums / 2 - 1], controlPoints[nums / 2], aimObj, w=1))
            delObjs.append(aimObj)

        upObj = cmds.group(em=1)
        upOft = cmds.group(upObj)
        cmds.setAttr('%s.tx' % upObj, -10000)
        cmds.delete(cmds.pointConstraint(controlPoints[0], controlPoints[-1], upOft, w=1))
        cmds.delete(cmds.aimConstraint(aimObj, upOft, w=1, o=[0, 0, 0], aimVector=[1, 0, 0], upVector=[0, 1, 0],
                                       worldUpVector=[0, 1, 0], worldUpType="vector"))
        delObjs += [upOft]

    if style == 'aim':
        nums = len(controlPoints)
        for i in range(nums - 1):
            cmds.delete(
                cmds.aimConstraint(controlPoints[i + 1], controlPoints[i], aim=aimVector, u=upVector, wut='object',
                                   wuo=upObj))
        cmds.delete(cmds.orientConstraint(controlPoints[-2], controlPoints[-1], w=1, mo=0))

    if style == 'tangent':
        for obj in controlPoints:
            cmds.delete(cmds.tangentConstraint(curve, obj, aim=aimVector, u=upVector, wut='object', wuo=upObj))
    if delObjs:
        cmds.delete(delObjs)
    return None


def correctSidePositions(controlPoints):
    # 修正首位附加点
    name = controlPoints[0][:-4]
    # 首节点
    start_dist = cmds.createNode('distanceBetween', n='%s_start_dist' % name)
    start1_shape = cmds.listRelatives(controlPoints[0], s=1)[0]
    start2_shape = cmds.listRelatives(controlPoints[2], s=1)[0]
    cmds.connectAttr('%s.worldPosition[0]' % start1_shape, '%s.point1' % start_dist, f=1)
    cmds.connectAttr('%s.worldPosition[0]' % start2_shape, '%s.point2' % start_dist, f=1)
    start_str = cmds.createNode('setRange', n='%s_start_str' % name)
    cmds.connectAttr('%s.distance' % start_dist, '%s.valueX' % start_str, f=1)
    cmds.setAttr('%s.oldMaxX' % start_str, cmds.getAttr('%s.distance' % start_dist) * 1.01)
    length = myMath.vectorCrossProduct(cmds.xform(controlPoints[0], q=1, t=1, ws=1),
                                       cmds.xform(controlPoints[1], q=1, t=1, ws=1))
    cmds.setAttr('%s.maxX' % start_str, length)
    cmds.parent(controlPoints[1], controlPoints[0])
    cmds.connectAttr('%s.outValueX' % start_str, '%s.translateX' % controlPoints[1], f=1)

    # 尾节点
    end_dist = cmds.createNode('distanceBetween', n='%s_end_dist' % name)
    end1_shape = cmds.listRelatives(controlPoints[-1], s=1)[0]
    end2_shape = cmds.listRelatives(controlPoints[-3], s=1)[0]
    cmds.connectAttr('%s.worldPosition[0]' % end1_shape, '%s.point1' % end_dist, f=1)
    cmds.connectAttr('%s.worldPosition[0]' % end2_shape, '%s.point2' % end_dist, f=1)
    end_str = cmds.createNode('setRange', n='%s_end_str' % name)

    cmds.connectAttr('%s.distance' % end_dist, '%s.valueX' % end_str, f=1)
    cmds.setAttr('%s.oldMaxX' % end_str, cmds.getAttr('%s.distance' % end_dist) * 1.01)
    length = myMath.vectorCrossProduct(cmds.xform(controlPoints[0], q=1, t=1, ws=1),
                                       cmds.xform(controlPoints[1], q=1, t=1, ws=1))
    cmds.setAttr('%s.maxX' % end_str, length * -1)
    cmds.parent(controlPoints[-2], controlPoints[-1])

    cmds.connectAttr('%s.outValueX' % end_str, '%s.translateX' % controlPoints[-2], f=1)
    controlPoints.pop(1)
    controlPoints.pop(-2)
    return controlPoints


def createControlHandle(controlPoints):
    # 创建控制点
    handleGrp = '%sPositionsHandleGrp' % controlPoints[0].split('Position')[0]

    if not cmds.objExists(handleGrp):
        handleGrp = cmds.createNode('transform', n=handleGrp)

    for controller in controlPoints:
        name = controller[:-3]
        ext = cmds.createNode('transform', n='%sExt' % name)
        tra = cmds.createNode('transform', n='%sTra' % name)
        cmds.parent(ext, tra)
        oft = cmds.createNode('transform', n='%sOft' % name)
        cmds.parent(tra, oft)
        cmds.parent(oft, handleGrp)

        cmds.delete(cmds.parentConstraint(controller, oft, w=1, mo=0))
        cmds.parent(controller, ext)

    return handleGrp


def createController(name, controlPoints):
    # 创建控制器
    # 约束组
    constraintGrp = '%sConstraintsGrp' % name
    if not cmds.objExists(constraintGrp):
        constraintGrp = cmds.createNode('transform', n=constraintGrp)
        lockChannels(constraintGrp)

    CtrGrp = '%sControllersGrp' % name
    if not cmds.objExists(CtrGrp):
        CtrGrp = cmds.createNode('transform', n=CtrGrp)

    FKGrp = '%sFKControllersGrp' % name
    if not cmds.objExists(FKGrp):
        FKGrp = cmds.createNode('transform', n=FKGrp)
        cmds.parent(FKGrp, CtrGrp)

    IKGrp = '%sIKControllersGrp' % name
    if not cmds.objExists(IKGrp):
        IKGrp = cmds.createNode('transform', n=IKGrp)
        cmds.parent(IKGrp, CtrGrp)
        cmds.setAttr('%s.inheritsTransform' % IKGrp, 0)
        scaleCon = cmds.scaleConstraint(CtrGrp, IKGrp, w=1)
        cmds.parent(scaleCon, constraintGrp)

    lengths = [myMath.vectorCrossProduct(cmds.xform(controlPoints[i], q=1, ws=1, t=1),
                                         cmds.xform(controlPoints[i + 1], q=1, ws=1, t=1)) for i in
               range(len(controlPoints) - 1)]

    length = max(lengths)

    # 主控制器
    mainCtr = '%sMainCtr' % name

    main_infs = controllerCreator.createCtrl('', n=mainCtr, g=['Ext', 'Tra', 'Oft'], post='', st=37, color=7)
    main_ctr = main_infs.get('curve')
    main_grp = main_infs.get('group')

    addControlAttrs(main_ctr)

    cmds.setAttr('%s.rz' % main_ctr, 90)
    cmds.setAttr('%s.s' % main_ctr, length * .7, length * .7, length * .7, type='double3')
    cmds.makeIdentity(main_ctr, r=1, a=1, t=1, s=1)
    cmds.delete(cmds.parentConstraint(controlPoints[0], main_grp, w=1))
    cmds.parent(main_grp, CtrGrp)

    # IK尖端控制器
    IKTipName = '%sIKTip' % name
    IKTip_infs = controllerCreator.createCtrl('', n=IKTipName, g=['Ext', 'Tra', 'Oft'], post='', st=55, color=18)

    IKTip_ctr = IKTip_infs.get('curve')
    IKTip_grp = IKTip_infs.get('group')

    cmds.delete(cmds.parentConstraint(controlPoints[-1], IKTip_grp, w=1))
    cmds.setAttr('%s.s' % IKTip_ctr, length * .15, length * .15, length * .15, type='double3')
    cmds.makeIdentity(IKTip_ctr, r=1, a=1, t=1, s=1)
    cmds.parent(IKTip_grp, IKGrp)

    FIKCdn = cmds.createNode('condition', n='%sFIKSwitchCDN' % name)
    cmds.setAttr('%s.operation' % FIKCdn, 0)
    cmds.setAttr('%s.secondTerm' % FIKCdn, 0)
    cmds.setAttr('%s.colorIfTrue' % FIKCdn, 1, 1, 0, type='double3')
    cmds.setAttr('%s.colorIfFalse' % FIKCdn, 0, 0, 0, type='double3')
    cmds.connectAttr('%s.switch' % mainCtr, '%s.firstTerm' % FIKCdn, f=1)

    FKCdn = cmds.createNode('condition', n='%sFKSwitchCDN' % name)
    cmds.setAttr('%s.operation' % FKCdn, 0)
    cmds.setAttr('%s.secondTerm' % FKCdn, 1)
    cmds.setAttr('%s.colorIfTrue' % FKCdn, 1, 0, 0, type='double3')
    cmds.connectAttr('%s.switch' % mainCtr, '%s.firstTerm' % FKCdn, f=1)
    cmds.connectAttr('%s.outColor' % FIKCdn, '%s.colorIfFalse' % FKCdn, f=1)

    IKCdn = cmds.createNode('condition', n='%sIKSwitchCDN' % name)
    cmds.setAttr('%s.operation' % IKCdn, 0)
    cmds.setAttr('%s.secondTerm' % IKCdn, 2)
    cmds.setAttr('%s.colorIfTrue' % IKCdn, 0, 1, 1, type='double3')
    cmds.connectAttr('%s.switch' % mainCtr, '%s.firstTerm' % IKCdn, f=1)
    cmds.connectAttr('%s.outColor' % FKCdn, '%s.colorIfFalse' % IKCdn, f=1)

    cmds.connectAttr('%s.outColorR' % IKCdn, '%s.v' % FKGrp, f=1)
    cmds.connectAttr('%s.outColorG' % IKCdn, '%s.v' % IKGrp, f=1)
    cmds.connectAttr('%s.outColorB' % IKCdn, '%s.v' % IKTip_grp, f=1)

    weightRV = cmds.createNode('reverse', n='%sWeightRV' % name)
    cmds.connectAttr('%s.outColorR' % IKCdn, '%s.inputX' % weightRV, f=1)

    FKCtrls = []
    IKCtrls = []

    FKRot_infs = controllerCreator.createCtrl('', n='%sFKRot' % name, g=['Oft'], post='', st=20, color=19)
    FKRot_ctr = FKRot_infs.get('curve')
    cmds.setAttr('%s.s' % FKRot_ctr, length * .32, length * .32, length * .32, type='double3')
    cmds.makeIdentity(FKRot_ctr, r=1, a=1, t=1, s=1)
    attributes.edit(FKRot_ctr, ['%s%s' % (x, y) for x in 'ts' for y in 'xyz'] + ['v'], [], 1)
    FKRot_grp = FKRot_infs.get('group')
    cmds.parentConstraint(main_ctr, FKRot_grp, w=1)
    cmds.parent(FKRot_grp, FKGrp)

    par = FKGrp
    for i in range(len(controlPoints)):
        # FK控制器
        FKName = '%s%dFK' % (name, i + 1)
        FK_infs = controllerCreator.createCtrl('', n=FKName, g=['Ext', 'Tra', 'Oft'], post='', st=28, color=15)
        FK_ctr = FK_infs.get('curve')
        FK_grp = FK_infs.get('group')
        cmds.delete(cmds.parentConstraint(controlPoints[i], FK_grp, w=1))
        cmds.setAttr('%s.rz' % FK_ctr, 90)
        cmds.setAttr('%s.s' % FK_ctr, length * .5, length * .5, length * .5, type='double3')
        cmds.makeIdentity(FK_ctr, r=1, a=1, t=1, s=1)
        attributes.edit(FK_ctr, ['sx', 'sy', 'sz', 'v'], [], 1)
        FKCtrls.append(FK_ctr)
        FK_tra = cmds.listRelatives(FK_grp, c=1)[0]
        cmds.connectAttr('%s.r' % FKRot_ctr, '%s.r' % FK_tra, f=1)
        if par:
            cmds.parent(FK_grp, par)
        par = FK_ctr
        # IK控制器
        IKName = '%s%dIK' % (name, i + 1)
        IK_infs = controllerCreator.createCtrl('', n=IKName, g=['Ext', 'Tra', 'Con', 'Oft'], post='', st=11, color=21)
        IK_ctr = IK_infs.get('curve')
        IK_grp = IK_infs.get('group')
        IKCtrls.append(IK_ctr)
        cmds.delete(cmds.parentConstraint(controlPoints[i], IK_grp, w=1))
        cmds.setAttr('%s.s' % IK_ctr, length * .3, length * .3, length * .3, type='double3')
        cmds.makeIdentity(IK_ctr, r=1, a=1, t=1, s=1)
        attributes.edit(IK_ctr, ['sx', 'sy', 'sz', 'v'], [], 1)
        cmds.parent(IK_grp, IKGrp)
        con = cmds.parentConstraint(IK_ctr, '%sTra' % controlPoints[i][:-3], w=1, mo=1)
        cmds.parent(con, constraintGrp)
        par_con = cmds.parentConstraint('%sCon' % IKName, FK_ctr, '%sTra' % IKName, w=1, mo=0)[0]
        # lockChannels(IKName)
        cmds.parent(par_con, constraintGrp)
        cmds.connectAttr('%s.outputX' % weightRV, '%s.target[0].targetWeight' % par_con, f=1)
        cmds.connectAttr('%s.outColorR' % IKCdn, '%s.target[1].targetWeight' % par_con, f=1)
        if i == 0:
            FK_con = cmds.parentConstraint(main_ctr, FK_grp, w=1, mo=1)
            cmds.parent(FK_con, constraintGrp)
            IK_con = cmds.parentConstraint(main_ctr, IK_grp, w=1, mo=1)
            cmds.parent(IK_con, constraintGrp)

    infos = {'constraintGrp': constraintGrp, 'controllerGrp': CtrGrp, 'FKGrp': FKGrp, 'IKGrp': IKGrp,
             'mainCtr': mainCtr, 'IKTip': IKTip_ctr, 'FKCtrs': FKCtrls, 'IKCtrs': IKCtrls}
    return infos


def addControlAttrs(controller):
    # 为控制器添加控制属性
    # 添加骨骼显隐切换属性
    if not cmds.objExists('%s.deformVis' % controller):
        cmds.addAttr(controller, ln='deformVis', at='bool')
        cmds.setAttr('%s.deformVis' % controller, 1, e=1, cb=1, k=0)

    # 添加FIK切换属性
    if not cmds.objExists('%s.switch' % controller):
        cmds.addAttr(controller, ln='switch', at='enum', en='FIK:FK:IK')
        cmds.setAttr('%s.switch' % controller, e=1, k=1)

    # 添加缩放控制属性
    if not cmds.objExists('%s.size' % controller):
        cmds.addAttr(controller, ln='size', at='double', min=0.001, dv=1)
        cmds.setAttr('%s.size' % controller, e=1, k=1)

    # 添加拉伸控制属性
    if not cmds.objExists('%s.stretch' % controller):
        cmds.addAttr(controller, ln='stretch', at='double', min=0, max=1, dv=0)
        cmds.setAttr('%s.stretch' % controller, e=1, k=1)

    # 添加体积控制属性
    if not cmds.objExists('%s.volume' % controller):
        cmds.addAttr(controller, ln='volume', at='enum', en='None:Full:Head:Tail:Center:Sides:')
        cmds.setAttr('%s.volume' % controller, e=1, k=1)

    # 添加圆锥变形控制属性
    if not cmds.objExists('%s.coneU' % controller):
        cmds.addAttr(controller, ln='coneU', at='double', dv=0)
        cmds.setAttr('%s.coneU' % controller, e=1, k=1)
    if not cmds.objExists('%s.coneV' % controller):
        cmds.addAttr(controller, ln='coneV', at='double', dv=0)
        cmds.setAttr('%s.coneV' % controller, e=1, k=1)

    # 添加体积乘数控制属性
    if not cmds.objExists('%s.volumeMultiplier' % controller):
        cmds.addAttr(controller, ln='volumeMultiplier', at='double', dv=1, min=0)
        cmds.setAttr('%s.volumeMultiplier' % controller, e=1, k=1)

    # 添加扭曲控制属性
    if not cmds.objExists('%s.roll' % controller):
        cmds.addAttr(controller, ln='roll', at='double', dv=0)
        cmds.setAttr('%s.roll' % controller, e=1, k=1)

    # 添加扭曲控制属性
    if not cmds.objExists('%s.twist' % controller):
        cmds.addAttr(controller, ln='twist', at='double', dv=0)
        cmds.setAttr('%s.twist' % controller, e=1, k=1)

    # 添加滑动控制属性
    if not cmds.objExists('%s.slide' % controller):
        cmds.addAttr(controller, ln='slide', at='double', dv=0, min=0, max=1)
        cmds.setAttr('%s.slide' % controller, e=1, k=1)

    # 添加衰减控制属性
    if not cmds.objExists('%s.dropoff' % controller):
        cmds.addAttr(controller, ln='dropoff', at='double', dv=0)
        cmds.setAttr('%s.dropoff' % controller, e=1, k=1)

    return None


def createMotionPathSystem(joints, baseCurve, targetCurve, controller, globalScaleLoc, offset=True):
    """
    # 创建路径动画系统
    :param joints:
    :param baseCurve:
    :param targetCurve:
    :param controller:
    :param globalScaleLoc:
    :param offset:
    :return:
    """
    conversion = getUnitConversionValue()
    constraints = []
    percentInfos = getPositionPercent(joints)

    baseShape = cmds.listRelatives(baseCurve, s=1)[0]
    targetShape = cmds.listRelatives(targetCurve, s=1)[0]
    totalLengthCI = cmds.createNode('curveInfo', n='%sTotalLengthCI' % baseCurve)
    cmds.connectAttr('%s.worldSpace[0]' % baseShape, '%s.inputCurve' % totalLengthCI, f=1)
    length = cmds.getAttr('%s.arcLength' % totalLengthCI)

    globalSwitchCD = cmds.createNode('condition', n='%sGlobalScaleSwitchCD' % baseCurve)
    cmds.connectAttr('%s.blackBox' % globalScaleLoc, '%s.firstTerm' % globalSwitchCD, f=1)
    cmds.connectAttr('%s.size' % controller, '%s.colorIfFalseR' % globalSwitchCD, f=1)

    globalScaleMDL = cmds.createNode('multDoubleLinear', n='%sGlobalScaleMDL' % baseCurve)
    cmds.connectAttr('%s.outColorR' % globalSwitchCD, '%s.input1' % globalScaleMDL, f=1)
    cmds.connectAttr('%s.sx' % globalScaleLoc, '%s.input2' % globalScaleMDL, f=1)
    totalLengthMDL = cmds.createNode('multDoubleLinear', n='%sTotalLengthMDL' % baseCurve)
    cmds.setAttr('%s.input1' % totalLengthMDL, length, l=1)
    cmds.connectAttr('%s.output' % globalScaleMDL, '%s.input2' % totalLengthMDL, f=1)

    # 添加拉伸切换
    stretchyBC = cmds.createNode('blendColors', n='%sBlendBC' % baseCurve)
    cmds.connectAttr('%s.arcLength' % totalLengthCI, '%s.color1R' % stretchyBC, f=1)
    cmds.connectAttr('%s.output' % totalLengthMDL, '%s.color2R' % stretchyBC, f=1)
    cmds.connectAttr('%s.stretch' % controller, '%s.blender' % stretchyBC, f=1)

    # 添加滑动属性
    distancePMA = cmds.createNode('plusMinusAverage', n='%sDistancePMA' % baseCurve)
    cmds.setAttr('%s.operation' % distancePMA, 2)

    cmds.connectAttr('%s.arcLength' % totalLengthCI, '%s.input1D[0]' % distancePMA, f=1)
    cmds.connectAttr('%s.outputR' % stretchyBC, '%s.input1D[1]' % distancePMA, f=1)

    distanceCL = cmds.createNode('clamp', n='%sDistanceCL' % baseCurve)
    cmds.setAttr('%s.maxR' % distanceCL, 999999999)
    cmds.connectAttr('%s.output1D' % distancePMA, '%s.inputR' % distanceCL, f=1)

    distancePercentMD = cmds.createNode('multiplyDivide', n='%sDistancePercentMD' % baseCurve)
    cmds.setAttr('%s.operation' % distancePercentMD, 2)
    cmds.connectAttr('%s.outputR' % distanceCL, '%s.input1X' % distancePercentMD, f=1)
    cmds.connectAttr('%s.arcLength' % totalLengthCI, '%s.input2X' % distancePercentMD, f=1)

    slideMDL = cmds.createNode('multDoubleLinear', n='%sSlideMDL' % baseCurve)
    cmds.connectAttr('%s.outputX' % distancePercentMD, '%s.input1' % slideMDL, f=1)
    cmds.connectAttr('%s.slide' % controller, '%s.input2' % slideMDL, f=1)

    # 添加衰减属性控制
    dropMDL = cmds.createNode('multDoubleLinear', n='%sDropoffMDL' % baseCurve)
    cmds.setAttr('%s.input1' % dropMDL, 0.01)
    cmds.connectAttr('%s.dropoff' % controller, '%s.input2' % dropMDL, f=1)

    dropPMA = cmds.createNode('plusMinusAverage', n='%sDropoffPMA' % baseCurve)
    cmds.setAttr('%s.input1D[0]' % dropPMA, 1)
    cmds.connectAttr('%s.output' % dropMDL, '%s.input1D[1]' % dropPMA, f=1)

    dropTotalPMA = cmds.createNode('plusMinusAverage', n='%sDropoffTotalPMA' % baseCurve)
    dropPreMD = cmds.createNode('multiplyDivide', n='%sDropoffPercentMD' % baseCurve)
    cmds.setAttr('%s.operation' % dropPreMD, 2)
    cmds.setAttr('%s.input1X' % dropPreMD, 1)
    cmds.connectAttr('%s.output1D' % dropTotalPMA, '%s.input2X' % dropPreMD, f=1)

    # 添加体积控制
    volumeRatioMD = cmds.createNode('multiplyDivide', n='%sVolumeRatioMD' % baseCurve)
    cmds.connectAttr('%s.output' % totalLengthMDL, '%s.input1X' % volumeRatioMD, f=1)
    cmds.connectAttr('%s.outputR' % stretchyBC, '%s.input2X' % volumeRatioMD, f=1)
    cmds.setAttr('%s.operation' % volumeRatioMD, 2)

    volumeSizeMD = cmds.createNode('multiplyDivide', n='%sVolumeSizeMD' % baseCurve)
    cmds.connectAttr('%s.outputX' % volumeRatioMD, '%s.input1X' % volumeSizeMD, f=1)
    cmds.setAttr('%s.input2X' % volumeSizeMD, .333333333)
    cmds.setAttr('%s.operation' % volumeSizeMD, 3)

    # volumeSizeMDL = cmds.createNode('multDoubleLinear',n = '%sVolumeSizeMDL'%baseCurve)
    baseVolumeMDL = cmds.createNode('multDoubleLinear', n='%sVolumeBaseMDL' % baseCurve)
    cmds.setAttr('%s.input1' % baseVolumeMDL, 1)
    cmds.setAttr('%s.input2' % baseVolumeMDL, 1)
    jointNum = len(joints)

    ratioInfos = getRatioValues(jointNum, 3)

    headValues = ratioInfos.get('head')
    tailValues = ratioInfos.get('tail')
    centerValues = ratioInfos.get('center')
    sidesValues = ratioInfos.get('sides')

    basePositionGrp = '%sPositionOft' % baseCurve
    if not cmds.objExists(basePositionGrp):
        basePositionGrp = cmds.createNode('transform', n=basePositionGrp)

    targetPositionGrp = '%sPositionOft' % targetCurve
    if not cmds.objExists(targetPositionGrp):
        targetPositionGrp = cmds.createNode('transform', n=targetPositionGrp)

    preDropMDL = None
    preDropPMA = None

    connectInfos = {}

    # 添加圆锥变形控制节点
    preConeMD = cmds.createNode('multiplyDivide', n='%sConePreMD' % baseCurve)
    cmds.setAttr('%s.operation' % preConeMD, 2)
    cmds.setAttr('%s.input2' % preConeMD, jointNum - 1, jointNum - 1, jointNum - 1, type='double3')
    cmds.connectAttr('%s.coneU' % controller, '%s.input1X' % preConeMD, f=1)
    cmds.connectAttr('%s.coneV' % controller, '%s.input1Y' % preConeMD, f=1)

    coneUChoiceMD = cmds.createNode('multiplyDivide', n='%sConeUChoiceMD' % baseCurve)
    cmds.setAttr('%s.input2' % coneUChoiceMD, 1, -1, 1, type='double3')
    cmds.connectAttr('%s.outputX' % preConeMD, '%s.input1X' % coneUChoiceMD, f=1)
    cmds.connectAttr('%s.outputX' % preConeMD, '%s.input1Y' % coneUChoiceMD, f=1)

    coneVChoiceMD = cmds.createNode('multiplyDivide', n='%sConeVChoiceMD' % baseCurve)
    cmds.setAttr('%s.input2' % coneVChoiceMD, 1, -1, 1, type='double3')
    cmds.connectAttr('%s.outputY' % preConeMD, '%s.input1X' % coneVChoiceMD, f=1)
    cmds.connectAttr('%s.outputY' % preConeMD, '%s.input1Y' % coneVChoiceMD, f=1)

    coneUScaleCD = cmds.createNode('condition', n='%sConeUScaleCD' % baseCurve)
    cmds.setAttr('%s.operation' % coneUScaleCD, 5)
    cmds.connectAttr('%s.ox' % coneUChoiceMD, '%s.colorIfTrueR' % coneUScaleCD, f=1)
    cmds.connectAttr('%s.oy' % coneUChoiceMD, '%s.colorIfFalseR' % coneUScaleCD, f=1)
    cmds.connectAttr('%s.coneU' % controller, '%s.secondTerm' % coneUScaleCD, f=1)

    coneVScaleCD = cmds.createNode('condition', n='%sConeVScaleCD' % baseCurve)
    cmds.setAttr('%s.operation' % coneVScaleCD, 5)
    cmds.connectAttr('%s.ox' % coneVChoiceMD, '%s.colorIfTrueR' % coneVScaleCD, f=1)
    cmds.connectAttr('%s.oy' % coneVChoiceMD, '%s.colorIfFalseR' % coneVScaleCD, f=1)
    cmds.connectAttr('%s.coneV' % controller, '%s.secondTerm' % coneVScaleCD, f=1)

    nodes = [totalLengthCI, globalScaleMDL, totalLengthMDL, stretchyBC, distancePMA, distanceCL, distancePercentMD,
             slideMDL, dropMDL, dropPMA, dropTotalPMA, dropPreMD, volumeRatioMD, volumeSizeMD, baseVolumeMDL, preConeMD,
             coneUChoiceMD, coneVChoiceMD, coneUScaleCD, coneVScaleCD]

    for i in range(jointNum):
        nodes_tmp = []
        jnt = joints[i].split('|')[-1]
        targetMP = cmds.createNode('motionPath', n='%sTargetMP' % jnt)
        cmds.connectAttr('%s.worldSpace[0]' % targetShape, '%s.geometryPath' % targetMP, f=1)
        tarPos = cmds.createNode('transform', n='%sTargetPos' % jnt)
        cmds.parent(tarPos, targetPositionGrp)
        cmds.connectAttr('%s.allCoordinates' % targetMP, '%s.translate' % tarPos, f=1)
        cmds.connectAttr('%s.r' % targetMP, '%s.r' % tarPos, f=1)
        cmds.connectAttr('%s.rotateOrder' % targetMP, '%s.rotateOrder' % tarPos, f=1)
        cmds.connectAttr('%s.message' % targetMP, '%s.specifiedManipLocation' % tarPos, f=1)
        cmds.setAttr('%s.fractionMode' % targetMP, 1)
        cmds.setAttr('%s.follow' % targetMP, 1)
        cmds.setAttr('%s.uValue' % targetMP, percentInfos[i])

        baseMP = cmds.createNode('motionPath', n='%sBaseMP' % jnt)
        cmds.connectAttr('%s.worldSpace[0]' % baseShape, '%s.geometryPath' % baseMP, f=1)
        cmds.connectAttr('%s.uValue' % targetMP, '%s.uValue' % baseMP, f=1)
        cmds.setAttr('%s.fractionMode' % baseMP, 1)
        cmds.setAttr('%s.follow' % baseMP, 1)

        cmds.setAttr('%s.worldUpType' % baseMP, 1)
        cmds.connectAttr('%s.worldMatrix[0]' % tarPos, '%s.worldUpMatrix' % baseMP, f=1)

        basePos = cmds.createNode('transform', n='%sBasePos' % jnt)
        cmds.parent(basePos, basePositionGrp)
        cmds.connectAttr('%s.allCoordinates' % baseMP, '%s.translate' % basePos, f=1)
        cmds.connectAttr('%s.r' % baseMP, '%s.r' % basePos, f=1)
        cmds.connectAttr('%s.rotateOrder' % baseMP, '%s.rotateOrder' % basePos, f=1)
        cmds.connectAttr('%s.message' % baseMP, '%s.specifiedManipLocation' % basePos, f=1)

        oftPMA = cmds.createNode('plusMinusAverage', n='%sOffsetPMA' % jnt)
        if i == 0:
            cmds.setAttr('%s.input1D[0]' % oftPMA, percentInfos[i])

        if i != 0:
            dropoffMDL = cmds.createNode('multDoubleLinear', n='%sDropoffMDL' % basePos)
            if preDropMDL:
                cmds.connectAttr('%s.output' % preDropMDL, '%s.input1' % dropoffMDL, f=1)
            else:
                cmds.setAttr('%s.input1' % dropoffMDL, 1)
            cmds.connectAttr('%s.output1D' % dropPMA, '%s.input2' % dropoffMDL, f=1)
            cmds.connectAttr('%s.output' % dropoffMDL, '%s.input1D[%d]' % (dropTotalPMA, i - 1), f=1)
            percentMDL = cmds.createNode('multDoubleLinear', n='%sDropoffPercentMDL' % basePos)
            cmds.connectAttr('%s.output' % dropoffMDL, '%s.input1' % percentMDL, f=1)
            cmds.connectAttr('%s.outputX' % dropPreMD, '%s.input2' % percentMDL, f=1)
            dropPrePMA = cmds.createNode('plusMinusAverage', n='%sDropPercentPMA' % basePos)

            if preDropPMA:
                cmds.connectAttr('%s.output1D' % preDropPMA, '%s.input1D[0]' % dropPrePMA, f=1)
            else:
                cmds.setAttr('%s.input1D[0]' % dropPrePMA, 0)

            cmds.connectAttr('%s.output' % percentMDL, '%s.input1D[1]' % dropPrePMA, f=1)

            preDropPMA = dropPrePMA
            preDropMDL = dropoffMDL

            cmds.connectAttr('%s.output1D' % dropPrePMA, '%s.input1D[0]' % oftPMA, f=1)
            # cmds.setAttr('%s.input1D[2]'%oftPMA,- cmds.getAttr('%s.output1D'%dropPrePMA))
            nodes_tmp = [dropoffMDL, percentMDL, dropPrePMA]

        valueCL = cmds.createNode('clamp', n='%sValueCL' % jnt)
        cmds.setAttr('%s.maxR' % valueCL, 1)
        cmds.connectAttr('%s.output1D' % oftPMA, '%s.inputR' % valueCL, f=1)

        currentLengthMDL = cmds.createNode('multDoubleLinear', n='%sCurrentLengthMDL' % jnt)
        cmds.connectAttr('%s.outputR' % stretchyBC, '%s.input1' % currentLengthMDL, f=1)
        cmds.connectAttr('%s.outputR' % valueCL, '%s.input2' % currentLengthMDL, f=1)

        newPerMD = cmds.createNode('multiplyDivide', n='%sNewPercentMD' % jnt)
        cmds.setAttr('%s.operation' % newPerMD, 2)
        cmds.connectAttr('%s.output' % currentLengthMDL, '%s.input1X' % newPerMD, f=1)
        cmds.connectAttr('%s.arcLength' % totalLengthCI, '%s.input2X' % newPerMD, f=1)

        newPerPMA = cmds.createNode('plusMinusAverage', n='%sNewPercentPMA' % jnt)

        cmds.connectAttr('%s.output' % slideMDL, '%s.input1D[0]' % newPerPMA, f=1)
        cmds.connectAttr('%s.outputX' % newPerMD, '%s.input1D[1]' % newPerPMA, f=1)

        newPreCL = cmds.createNode('clamp', n='%sNewPercentCL' % jnt)
        cmds.setAttr('%s.maxR' % newPreCL, 1)
        cmds.connectAttr('%s.output1D' % newPerPMA, '%s.inputR' % newPreCL)

        cmds.connectAttr('%s.outputR' % newPreCL, '%s.uValue' % targetMP, f=1)

        # 添加twist/roll属性
        twistMDL = cmds.createNode('multDoubleLinear', n='%sFrontTwistMDL' % jnt)
        cmds.setAttr('%s.input1' % twistMDL, i + 1, l=1)
        cmds.connectAttr('%s.twist' % controller, '%s.input2' % twistMDL, f=1)

        twistPMA = cmds.createNode('plusMinusAverage', n='%sTwistPMA' % jnt)
        cmds.connectAttr('%s.output' % twistMDL, '%s.input1D[0]' % twistPMA, f=1)
        cmds.connectAttr('%s.roll' % controller, '%s.input1D[1]' % twistPMA, f=1)

        twistUC = cmds.createNode('unitConversion', n='%sTwistUC' % jnt)
        cmds.setAttr('%s.conversionFactor' % twistUC, conversion)
        cmds.connectAttr('%s.output1D' % twistPMA, '%s.input' % twistUC, f=1)
        cmds.connectAttr('%s.output' % twistUC, '%s.frontTwist' % baseMP, f=1)

        # 添加体积属性控制=============================================
        switchCC = cmds.createNode('choice', n='%sVolumeCC' % jnt)
        cmds.connectAttr('%s.volume' % controller, '%s.selector' % switchCC, f=1)

        volumeMultMDL = cmds.createNode('multDoubleLinear', n='%sVolumeMultiplierMDL' % jnt)
        cmds.connectAttr('%s.output' % switchCC, '%s.input2' % volumeMultMDL, f=1)
        cmds.connectAttr('%s.volumeMultiplier' % controller, '%s.input1' % volumeMultMDL, f=1)

        # 无变形
        cmds.connectAttr('%s.output' % baseVolumeMDL, '%s.input[0]' % switchCC, f=1)

        # 整体变形
        cmds.connectAttr('%s.outputX' % volumeSizeMD, '%s.input[1]' % switchCC, f=1)

        # 首部变形
        headPowMD = cmds.createNode('multiplyDivide', n='%sVolumeHeadMD' % jnt)
        cmds.setAttr('%s.operation' % headPowMD, 3)
        cmds.connectAttr('%s.outputX' % volumeSizeMD, '%s.input1X' % headPowMD, f=1)
        cmds.setAttr('%s.input2X' % headPowMD, headValues.get(i))
        cmds.connectAttr('%s.outputX' % headPowMD, '%s.input[2]' % switchCC, f=1)

        # 尾部变形
        tailPowMD = cmds.createNode('multiplyDivide', n='%sVolumeTailMD' % jnt)
        cmds.setAttr('%s.operation' % tailPowMD, 3)
        cmds.connectAttr('%s.outputX' % volumeSizeMD, '%s.input1X' % tailPowMD, f=1)
        cmds.setAttr('%s.input2X' % tailPowMD, tailValues.get(i))
        cmds.connectAttr('%s.outputX' % tailPowMD, '%s.input[3]' % switchCC, f=1)

        # 中心变形
        centerPowMD = cmds.createNode('multiplyDivide', n='%sVolumeCenterMD' % jnt)
        cmds.setAttr('%s.operation' % centerPowMD, 3)
        cmds.connectAttr('%s.outputX' % volumeSizeMD, '%s.input1X' % centerPowMD, f=1)
        cmds.setAttr('%s.input2X' % centerPowMD, centerValues.get(i))
        cmds.connectAttr('%s.outputX' % centerPowMD, '%s.input[4]' % switchCC, f=1)

        # 首位变形
        sidesPowMD = cmds.createNode('multiplyDivide', n='%sVolumeSidesMD' % jnt)
        cmds.setAttr('%s.operation' % sidesPowMD, 3)
        cmds.connectAttr('%s.outputX' % volumeSizeMD, '%s.input1X' % sidesPowMD, f=1)
        cmds.setAttr('%s.input2X' % sidesPowMD, sidesValues.get(i))
        cmds.connectAttr('%s.outputX' % sidesPowMD, '%s.input[5]' % switchCC, f=1)

        # 添加圆锥变形控制=============================================
        coneUSideMD = cmds.createNode('multiplyDivide', n='%sConeUSidesMD' % jnt)
        cmds.setAttr('%s.input1' % coneUSideMD, i, jointNum - 1 - i, 0, type='double3')
        cmds.connectAttr('%s.outColorR' % coneUScaleCD, '%s.input2X' % coneUSideMD, f=1)
        cmds.connectAttr('%s.outColorR' % coneUScaleCD, '%s.input2Y' % coneUSideMD, f=1)

        coneUChoiceBC = cmds.createNode('blendColors', n='%sConeUSideChoiceBC' % jnt)
        cmds.connectAttr('%s.outColorG' % coneUScaleCD, '%s.blender' % coneUChoiceBC, f=1)
        cmds.connectAttr('%s.outputX' % coneUSideMD, '%s.color1R' % coneUChoiceBC, f=1)
        cmds.connectAttr('%s.outputY' % coneUSideMD, '%s.color2R' % coneUChoiceBC, f=1)

        coneUBaseADL = cmds.createNode('addDoubleLinear', n='%sConeUBaseADL' % jnt)
        cmds.setAttr('%s.input1' % coneUBaseADL, 1, l=1)
        cmds.connectAttr('%s.outputR' % coneUChoiceBC, '%s.input2' % coneUBaseADL, f=1)

        volumeUTotalMDL = cmds.createNode('multDoubleLinear', n='%sVolumeUTotalMDL' % jnt)
        cmds.connectAttr('%s.output' % volumeMultMDL, '%s.input1' % volumeUTotalMDL, f=1)
        cmds.connectAttr('%s.output' % coneUBaseADL, '%s.input2' % volumeUTotalMDL, f=1)

        coneVSideMD = cmds.createNode('multiplyDivide', n='%sConeVSidesMD' % jnt)
        cmds.setAttr('%s.input1' % coneVSideMD, i, jointNum - 1 - i, 0, type='double3')
        cmds.connectAttr('%s.outColorR' % coneVScaleCD, '%s.input2X' % coneVSideMD, f=1)
        cmds.connectAttr('%s.outColorR' % coneVScaleCD, '%s.input2Y' % coneVSideMD, f=1)

        coneVChoiceBC = cmds.createNode('blendColors', n='%sConeVSideChoiceBC' % jnt)
        cmds.connectAttr('%s.outColorG' % coneVScaleCD, '%s.blender' % coneVChoiceBC, f=1)
        cmds.connectAttr('%s.outputX' % coneVSideMD, '%s.color1R' % coneVChoiceBC, f=1)
        cmds.connectAttr('%s.outputY' % coneVSideMD, '%s.color2R' % coneVChoiceBC, f=1)

        coneVBaseADL = cmds.createNode('addDoubleLinear', n='%sConeVBaseADL' % jnt)
        cmds.setAttr('%s.input1' % coneVBaseADL, 1, l=1)
        cmds.connectAttr('%s.outputR' % coneVChoiceBC, '%s.input2' % coneVBaseADL, f=1)

        volumeVTotalMDL = cmds.createNode('multDoubleLinear', n='%sVolumeVTotalMDL' % jnt)
        cmds.connectAttr('%s.output' % volumeMultMDL, '%s.input1' % volumeVTotalMDL, f=1)
        cmds.connectAttr('%s.output' % coneVBaseADL, '%s.input2' % volumeVTotalMDL, f=1)

        # 连接到输出位置POS
        cmds.connectAttr('%s.output' % volumeUTotalMDL, '%s.sy' % basePos, f=1)
        cmds.connectAttr('%s.output' % volumeVTotalMDL, '%s.sz' % basePos, f=1)

        connectInfos[basePos] = joints[i]
        nodes += nodes_tmp
        nodes += [globalSwitchCD, targetMP, baseMP, oftPMA, valueCL, currentLengthMDL, newPerMD, newPerPMA, newPreCL,
                  twistMDL, twistPMA, twistUC, switchCC, volumeMultMDL, headPowMD, tailPowMD, centerPowMD, sidesPowMD,
                  coneUSideMD, coneUChoiceBC, coneUBaseADL, volumeUTotalMDL, coneVSideMD, coneVChoiceBC, coneVBaseADL,
                  volumeVTotalMDL]

        lockChannels(tarPos)
        lockChannels(basePos)

    for key, value in connectInfos.iteritems():
        con = cmds.parentConstraint(key, value, w=1, mo=offset)
        # scon = cmds.scaleConstraint(key,value,w = 1)
        constraints += con
        # constraints += scon
        cmds.connectAttr('%s.s' % key, '%s.s' % value, f=1)

    return {'positionGrp': [basePositionGrp, targetPositionGrp], 'constraints': constraints, 'nodes': nodes}


def getUnitConversionValue():
    # 获取转换数值
    curUnit = cmds.currentUnit(q=1, l=1)
    sizeInfos = {'cm': 1, 'm': .01, 'mm': 10}
    multValue = sizeInfos.get(curUnit, 1) / (180.0 / math.pi)
    return multValue


def getPositionPercent(objs):
    # 获取每个物体所在位置相对于整曲线的百分比
    lengths = [myMath.vectorCrossProduct(cmds.xform(objs[i], q=1, ws=1, t=1), cmds.xform(objs[i + 1], q=1, ws=1, t=1))
               for i in range(len(objs) - 1)]
    total = sum(lengths)
    infos = [sum(lengths[:i]) / total for i in range(len(objs))]
    return infos


def getRatioValues(num, ratio=1):
    # 获取缩放比例数值
    headValues = {}
    tailValues = {}
    centerValues = {}
    sidesValues = {}
    half = num / 2
    if num % 2:
        half += 1

    for i in range(num):
        if i == 0:
            tailValues[i] = 0
        else:
            tailValues[i] = 1 + ratio * 1.0 / (num - 2) * (i - 1)

        if i == num - 1:
            headValues[i] = 0
        else:
            headValues[i] = 1 + ratio * 1.0 / (num - 2) * (num - i - 2)

        if i not in centerValues.keys():
            if i == 0:
                centerValues[i] = 0
            else:
                centerValues[i] = 1 + ratio * 1.0 / (half - 2) * (i - 1)
        if i not in sidesValues.keys():
            if i == half - 1:
                sidesValues[i] = 0
            else:
                sidesValues[i] = 1 + ratio * 1.0 / (half - 2) * (half - i - 2)
        m = num - i - 1
        if m not in centerValues.keys():
            centerValues[m] = centerValues[i]
        if m not in sidesValues.keys():
            sidesValues[m] = sidesValues[i]

    return {'head': headValues, 'tail': tailValues, 'center': centerValues, 'sides': sidesValues}


# =====================================新版骨骼链工具=====================================

def vectorCrossProduct(vector1, vector2):
    # 求向量叉积
    x = pow(vector1[0] - vector2[0], 2)
    y = pow(vector1[1] - vector2[1], 2)
    z = pow(vector1[2] - vector2[2], 2)
    infos = pow(x + y + z, 0.5)
    return infos


def matchTransform(base, target):
    """
    匹配物体位置信息
    :param base: 要调整位置的物体
    :param target: 目标物体
    :return:
    """
    translate = cmds.xform(target, q=True, t=True, ws=True)
    rotate = cmds.xform(target, q=True, ro=True, ws=True)
    scale = cmds.xform(target, q=True, s=True, ws=True)
    cmds.xform(base, ws=True, t=translate, ro=rotate, s=scale)


class ScaleRatio(object):
    def __init__(self, number, ratio=1):
        self.number = number
        self.ratio = ratio
        self.__ratioInfos = {}
        self.compute()

    @property
    def head(self):
        return self.__ratioInfos.get('head')

    @property
    def tail(self):
        return self.__ratioInfos.get('tail')

    @property
    def center(self):
        return self.__ratioInfos.get('center')

    @property
    def side(self):
        return self.__ratioInfos.get('side')

    def compute(self):
        # 获取缩放比例数值
        headValues = {}
        tailValues = {}
        centerValues = {}
        sidesValues = {}
        half = self.number / 2
        if self.number % 2:
            half += 1

        for i in range(self.number):
            if i == 0:
                tailValues[i] = 0
            else:
                tailValues[i] = 1 + self.ratio * 1.0 / (self.number - 2) * (i - 1)

            if i == self.number - 1:
                headValues[i] = 0
            else:
                headValues[i] = 1 + self.ratio * 1.0 / (self.number - 2) * (self.number - i - 2)

            if i not in centerValues.keys():
                if i == 0:
                    centerValues[i] = 0
                else:
                    centerValues[i] = 1 + self.ratio * 1.0 / (half - 2) * (i - 1)
            if i not in sidesValues.keys():
                if i == half - 1:
                    sidesValues[i] = 0
                else:
                    sidesValues[i] = 1 + self.ratio * 1.0 / (half - 2) * (half - i - 2)
            m = self.number - i - 1
            if m not in centerValues.keys():
                centerValues[m] = centerValues[i]
            if m not in sidesValues.keys():
                sidesValues[m] = sidesValues[i]

        self.__ratioInfos = {'head': headValues, 'tail': tailValues, 'center': centerValues, 'side': sidesValues}


class MotionSystem(object):
    def __init__(self, baseCurve, targetCurve, joints, controller, globalScaleLoc, basePositionsGroup,
                 targetPositionsGroup, constraintsGroup, keepOffset=True):
        self.baseCurve = baseCurve
        self.targetCurve = targetCurve
        self.joints = joints
        self.controller = controller
        self.globalScaleLoc = globalScaleLoc
        self.keepOffset = keepOffset
        self.basePositionsGroup = basePositionsGroup
        self.targetPositionsGroup = targetPositionsGroup
        self.constraintsGroup = constraintsGroup
        self.__conversionValue = 0
        self.__length = 0
        self.__scaleRatio = None
        self.__allNodes = []
        self.__positionsPercent = []

    @property
    def jointCount(self):
        return len(self.joints)

    @property
    def scaleRatio(self):
        if not self.__scaleRatio:
            self.__scaleRatio = ScaleRatio(self.jointCount, 3)
        return self.__scaleRatio

    @property
    def conversionValue(self):
        # 获取转换数值
        if self.__conversionValue == 0:
            curUnit = cmds.currentUnit(q=1, l=1)
            sizeInfos = {'cm': 1, 'm': .01, 'mm': 10}
            self.__conversionValue = sizeInfos.get(curUnit, 1) / (180.0 / math.pi)
        return self.__conversionValue

    @property
    def totalLengthCI(self):
        name = '%sTotalLengthCI' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('curveInfo', n=name)
        baseShape = cmds.listRelatives(self.baseCurve, s=1)[0]
        cmds.connectAttr('%s.worldSpace[0]' % baseShape, '%s.inputCurve' % name, f=1)
        return name

    @property
    def length(self):
        self.__length = cmds.getAttr('%s.arcLength' % self.totalLengthCI)
        return self.__length

    @property
    def globalSwitchCD(self):
        name = '%sGlobalScaleSwitchCD' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('condition', n=name)
        cmds.connectAttr('%s.blackBox' % self.globalScaleLoc, '%s.firstTerm' % name, f=1)
        cmds.connectAttr('%s.size' % self.controller, '%s.colorIfFalseR' % name, f=1)
        return name

    @property
    def globalScaleMDL(self):
        name = '%sGlobalScaleMDL' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('multDoubleLinear', n=name)
        cmds.connectAttr('%s.outColorR' % self.globalSwitchCD, '%s.input1' % name, f=1)
        cmds.connectAttr('%s.sx' % self.globalScaleLoc, '%s.input2' % name, f=1)
        return name

    @property
    def totalLengthMDL(self):
        name = '%sTotalLengthMDL' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('multDoubleLinear', n=name)
            cmds.setAttr('%s.input1' % name, self.length, l=1)
        cmds.connectAttr('%s.output' % self.globalScaleMDL, '%s.input2' % name, f=1)
        return name

    @property
    def stretchyBC(self):
        name = '%sStretchyBC' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('blendColors', n=name)
        cmds.connectAttr('%s.arcLength' % self.totalLengthCI, '%s.color1R' % name, f=1)
        cmds.connectAttr('%s.output' % self.totalLengthMDL, '%s.color2R' % name, f=1)
        cmds.connectAttr('%s.stretch' % self.controller, '%s.blender' % name, f=1)
        return name

    @property
    def distancePMA(self):
        name = '%sDistancePMA' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('plusMinusAverage', n=name)
        cmds.setAttr('%s.operation' % name, 2)
        cmds.connectAttr('%s.arcLength' % self.totalLengthCI, '%s.input1D[0]' % name, f=1)
        cmds.connectAttr('%s.outputR' % self.stretchyBC, '%s.input1D[1]' % name, f=1)
        return name

    @property
    def distanceCL(self):
        name = '%sDistanceCL' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('clamp', n=name)
        cmds.setAttr('%s.maxR' % name, 999999999)
        cmds.connectAttr('%s.output1D' % self.distancePMA, '%s.inputR' % name, f=1)
        return name

    @property
    def distancePercentMD(self):
        name = '%sDistancePercentMD' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('multiplyDivide', n=name)
        cmds.setAttr('%s.operation' % name, 2)
        cmds.connectAttr('%s.outputR' % self.distanceCL, '%s.input1X' % name, f=1)
        cmds.connectAttr('%s.arcLength' % self.totalLengthCI, '%s.input2X' % name, f=1)
        return name

    @property
    def slideMDL(self):
        name = '%sSlideMDL' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('multDoubleLinear', n=name)
        cmds.connectAttr('%s.outputX' % self.distancePercentMD, '%s.input1' % name, f=1)
        cmds.connectAttr('%s.slide' % self.controller, '%s.input2' % name, f=1)
        return name

    @property
    def decayMDL(self):
        name = '%sDecayMDL' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('multDoubleLinear', n=name)
        cmds.setAttr('%s.input1' % name, 0.01)
        cmds.connectAttr('%s.decay' % self.controller, '%s.input2' % name, f=1)
        return name

    @property
    def decayPMA(self):
        name = '%sDecayPMA' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('plusMinusAverage', n=name)
        cmds.setAttr('%s.input1D[0]' % name, 1)
        cmds.connectAttr('%s.output' % self.decayMDL, '%s.input1D[1]' % name, f=1)
        return name

    @property
    def decayTotalPMA(self):
        name = '%sDecayTotalPMA' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('plusMinusAverage', n=name)
        return name

    @property
    def decayPercentMD(self):
        name = '%sDecayPercentMD' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('multiplyDivide', n=name)
        cmds.setAttr('%s.operation' % name, 2)
        cmds.setAttr('%s.input1X' % name, 1)
        cmds.connectAttr('%s.output1D' % self.decayTotalPMA, '%s.input2X' % name, f=1)
        return name

    @property
    def volumeRatioMD(self):
        name = '%sVolumeRatioMD' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('multiplyDivide', n=name)
        cmds.connectAttr('%s.output' % self.totalLengthMDL, '%s.input1X' % name, f=1)
        cmds.connectAttr('%s.outputR' % self.stretchyBC, '%s.input2X' % name, f=1)
        cmds.setAttr('%s.operation' % name, 2)
        return name

    @property
    def volumeSizeMD(self):
        name = '%sVolumeSizeMD' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('multiplyDivide', n=name)
        cmds.connectAttr('%s.outputX' % self.volumeRatioMD, '%s.input1X' % name, f=1)
        cmds.setAttr('%s.input2X' % name, .333333333)
        cmds.setAttr('%s.operation' % name, 3)
        return name

    @property
    def baseVolumeMDL(self):
        name = '%sVolumeBaseMDL' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('multDoubleLinear', n=name)
        cmds.setAttr('%s.input1' % name, 1)
        cmds.setAttr('%s.input2' % name, 1)
        return name

    @property
    def preConeMD(self):
        name = '%sConePreMD' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('multiplyDivide', n=name)
        cmds.setAttr('%s.operation' % name, 2)
        cmds.setAttr('%s.input2' % name, self.jointCount - 1, self.jointCount - 1, self.jointCount - 1, type='double3')
        cmds.connectAttr('%s.coneU' % self.controller, '%s.input1X' % name, f=1)
        cmds.connectAttr('%s.coneV' % self.controller, '%s.input1Y' % name, f=1)
        return name

    @property
    def coneUChoiceMD(self):
        name = '%sConeUChoiceMD' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('multiplyDivide', n=name)
        cmds.setAttr('%s.input2' % name, 1, -1, 1, type='double3')
        cmds.connectAttr('%s.outputX' % self.preConeMD, '%s.input1X' % name, f=1)
        cmds.connectAttr('%s.outputX' % self.preConeMD, '%s.input1Y' % name, f=1)
        return name

    @property
    def coneVChoiceMD(self):
        name = '%sConeVChoiceMD' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('multiplyDivide', n=name)
        cmds.setAttr('%s.input2' % name, 1, -1, 1, type='double3')
        cmds.connectAttr('%s.outputY' % self.preConeMD, '%s.input1X' % name, f=1)
        cmds.connectAttr('%s.outputY' % self.preConeMD, '%s.input1Y' % name, f=1)
        return name

    @property
    def coneUScaleCD(self):
        name = '%sConeUScaleCD' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('condition', n=name)
        cmds.setAttr('%s.operation' % name, 5)
        cmds.connectAttr('%s.ox' % self.coneUChoiceMD, '%s.colorIfTrueR' % name, f=1)
        cmds.connectAttr('%s.oy' % self.coneUChoiceMD, '%s.colorIfFalseR' % name, f=1)
        cmds.connectAttr('%s.coneU' % self.controller, '%s.secondTerm' % name, f=1)
        return name

    @property
    def coneVScaleCD(self):
        name = '%sConeVScaleCD' % self.baseCurve
        if not cmds.objExists(name):
            cmds.createNode('condition', n=name)
        cmds.setAttr('%s.operation' % name, 5)
        cmds.connectAttr('%s.ox' % self.coneVChoiceMD, '%s.colorIfTrueR' % name, f=1)
        cmds.connectAttr('%s.oy' % self.coneVChoiceMD, '%s.colorIfFalseR' % name, f=1)
        cmds.connectAttr('%s.coneV' % self.controller, '%s.secondTerm' % name, f=1)
        return name

    @property
    def allNodes(self):
        if not self.__allNodes:
            self.__allNodes = [self.totalLengthCI,
                               self.globalSwitchCD,
                               self.globalScaleMDL,
                               self.totalLengthMDL,
                               self.stretchyBC,
                               self.distancePMA,
                               self.distanceCL,
                               self.distancePercentMD,
                               self.slideMDL,
                               self.decayMDL,
                               self.decayPMA,
                               self.decayTotalPMA,
                               self.decayPercentMD,
                               self.volumeRatioMD,
                               self.volumeSizeMD,
                               self.baseVolumeMDL,
                               self.preConeMD,
                               self.coneUChoiceMD,
                               self.coneVChoiceMD,
                               self.coneUScaleCD,
                               self.coneVScaleCD]
        return self.__allNodes

    @property
    def positionsPercent(self):
        # 获取每个物体所在位置相对于整曲线的百分比
        if not self.__positionsPercent:
            lengths = [vectorCrossProduct(cmds.xform(self.joints[i], q=1, ws=1, t=1),
                                          cmds.xform(self.joints[i + 1], q=1, ws=1, t=1))
                       for i in range(self.jointCount - 1)]
            total = sum(lengths)
            self.__positionsPercent = [sum(lengths[:i]) / total for i in range(self.jointCount)]
        return self.__positionsPercent

    def createControlPositions(self):
        # 创建控制点
        baseShape = cmds.listRelatives(self.baseCurve, s=1)[0]
        targetShape = cmds.listRelatives(self.targetCurve, s=1)[0]

        preDropMDL = None
        preDropPMA = None
        connectInfos = {}
        for i in range(self.jointCount):
            nodes_tmp = []
            name = self.joints[i].split('|')[-1]
            targetMP = cmds.createNode('motionPath', n='%sTargetMP' % name)
            cmds.connectAttr('%s.worldSpace[0]' % targetShape, '%s.geometryPath' % targetMP, f=1)
            tarPos = cmds.createNode('transform', n='%sTargetPos' % name)
            cmds.parent(tarPos, self.targetPositionsGroup)
            cmds.connectAttr('%s.allCoordinates' % targetMP, '%s.translate' % tarPos, f=1)
            cmds.connectAttr('%s.r' % targetMP, '%s.r' % tarPos, f=1)
            cmds.connectAttr('%s.rotateOrder' % targetMP, '%s.rotateOrder' % tarPos, f=1)
            cmds.connectAttr('%s.message' % targetMP, '%s.specifiedManipLocation' % tarPos, f=1)
            cmds.setAttr('%s.fractionMode' % targetMP, 1)
            cmds.setAttr('%s.follow' % targetMP, 1)
            cmds.setAttr('%s.uValue' % targetMP, self.positionsPercent[i])

            baseMP = cmds.createNode('motionPath', n='%sBaseMP' % name)
            cmds.connectAttr('%s.worldSpace[0]' % baseShape, '%s.geometryPath' % baseMP, f=1)
            cmds.connectAttr('%s.uValue' % targetMP, '%s.uValue' % baseMP, f=1)
            cmds.setAttr('%s.fractionMode' % baseMP, 1)
            cmds.setAttr('%s.follow' % baseMP, 1)

            cmds.setAttr('%s.worldUpType' % baseMP, 1)
            cmds.connectAttr('%s.worldMatrix[0]' % tarPos, '%s.worldUpMatrix' % baseMP, f=1)

            basePos = cmds.createNode('transform', n='%sBasePos' % name)
            cmds.parent(basePos, self.basePositionsGroup)
            cmds.connectAttr('%s.allCoordinates' % baseMP, '%s.translate' % basePos, f=1)
            cmds.connectAttr('%s.r' % baseMP, '%s.r' % basePos, f=1)
            cmds.connectAttr('%s.rotateOrder' % baseMP, '%s.rotateOrder' % basePos, f=1)
            cmds.connectAttr('%s.message' % baseMP, '%s.specifiedManipLocation' % basePos, f=1)

            oftPMA = cmds.createNode('plusMinusAverage', n='%sOffsetPMA' % name)
            if i == 0:
                cmds.setAttr('%s.input1D[0]' % oftPMA, self.positionsPercent[i])

            if i != 0:
                dropoffMDL = cmds.createNode('multDoubleLinear', n='%sDropoffMDL' % basePos)
                if preDropMDL:
                    cmds.connectAttr('%s.output' % preDropMDL, '%s.input1' % dropoffMDL, f=1)
                else:
                    cmds.setAttr('%s.input1' % dropoffMDL, 1)
                cmds.connectAttr('%s.output1D' % self.decayPMA, '%s.input2' % dropoffMDL, f=1)
                cmds.connectAttr('%s.output' % dropoffMDL, '%s.input1D[%d]' % (self.decayTotalPMA, i - 1), f=1)
                percentMDL = cmds.createNode('multDoubleLinear', n='%sDropoffPercentMDL' % basePos)
                cmds.connectAttr('%s.output' % dropoffMDL, '%s.input1' % percentMDL, f=1)
                cmds.connectAttr('%s.outputX' % self.decayPercentMD, '%s.input2' % percentMDL, f=1)
                dropPrePMA = cmds.createNode('plusMinusAverage', n='%sDropPercentPMA' % basePos)

                if preDropPMA:
                    cmds.connectAttr('%s.output1D' % preDropPMA, '%s.input1D[0]' % dropPrePMA, f=1)
                else:
                    cmds.setAttr('%s.input1D[0]' % dropPrePMA, 0)

                cmds.connectAttr('%s.output' % percentMDL, '%s.input1D[1]' % dropPrePMA, f=1)

                preDropPMA = dropPrePMA
                preDropMDL = dropoffMDL

                cmds.connectAttr('%s.output1D' % dropPrePMA, '%s.input1D[0]' % oftPMA, f=1)
                # cmds.setAttr('%s.input1D[2]'%oftPMA,- cmds.getAttr('%s.output1D'%dropPrePMA))
                nodes_tmp = [dropoffMDL, percentMDL, dropPrePMA]

            valueCL = cmds.createNode('clamp', n='%sValueCL' % name)
            cmds.setAttr('%s.maxR' % valueCL, 1)
            cmds.connectAttr('%s.output1D' % oftPMA, '%s.inputR' % valueCL, f=1)

            currentLengthMDL = cmds.createNode('multDoubleLinear', n='%sCurrentLengthMDL' % name)
            cmds.connectAttr('%s.outputR' % self.stretchyBC, '%s.input1' % currentLengthMDL, f=1)
            cmds.connectAttr('%s.outputR' % valueCL, '%s.input2' % currentLengthMDL, f=1)

            newPerMD = cmds.createNode('multiplyDivide', n='%sNewPercentMD' % name)
            cmds.setAttr('%s.operation' % newPerMD, 2)
            cmds.connectAttr('%s.output' % currentLengthMDL, '%s.input1X' % newPerMD, f=1)
            cmds.connectAttr('%s.arcLength' % self.totalLengthCI, '%s.input2X' % newPerMD, f=1)

            newPerPMA = cmds.createNode('plusMinusAverage', n='%sNewPercentPMA' % name)

            cmds.connectAttr('%s.output' % self.slideMDL, '%s.input1D[0]' % newPerPMA, f=1)
            cmds.connectAttr('%s.outputX' % newPerMD, '%s.input1D[1]' % newPerPMA, f=1)

            newPreCL = cmds.createNode('clamp', n='%sNewPercentCL' % name)
            cmds.setAttr('%s.maxR' % newPreCL, 1)
            cmds.connectAttr('%s.output1D' % newPerPMA, '%s.inputR' % newPreCL)

            cmds.connectAttr('%s.outputR' % newPreCL, '%s.uValue' % targetMP, f=1)

            # 添加twist/roll属性
            twistMDL = cmds.createNode('multDoubleLinear', n='%sFrontTwistMDL' % name)
            cmds.setAttr('%s.input1' % twistMDL, i + 1, l=1)
            cmds.connectAttr('%s.twist' % self.controller, '%s.input2' % twistMDL, f=1)

            twistPMA = cmds.createNode('plusMinusAverage', n='%sTwistPMA' % name)
            cmds.connectAttr('%s.output' % twistMDL, '%s.input1D[0]' % twistPMA, f=1)
            cmds.connectAttr('%s.roll' % self.controller, '%s.input1D[1]' % twistPMA, f=1)

            twistUC = cmds.createNode('unitConversion', n='%sTwistUC' % name)
            cmds.setAttr('%s.conversionFactor' % twistUC, self.conversionValue)
            cmds.connectAttr('%s.output1D' % twistPMA, '%s.input' % twistUC, f=1)
            cmds.connectAttr('%s.output' % twistUC, '%s.frontTwist' % baseMP, f=1)

            # 添加体积属性控制=============================================
            switchCC = cmds.createNode('choice', n='%sVolumeCC' % name)
            cmds.connectAttr('%s.volume' % self.controller, '%s.selector' % switchCC, f=1)

            volumeMultMDL = cmds.createNode('multDoubleLinear', n='%sVolumeMultiplierMDL' % name)
            cmds.connectAttr('%s.output' % switchCC, '%s.input2' % volumeMultMDL, f=1)
            cmds.connectAttr('%s.volumeMultiplier' % self.controller, '%s.input1' % volumeMultMDL, f=1)

            # 无变形
            cmds.connectAttr('%s.output' % self.baseVolumeMDL, '%s.input[0]' % switchCC, f=1)

            # 整体变形
            cmds.connectAttr('%s.outputX' % self.volumeSizeMD, '%s.input[1]' % switchCC, f=1)

            # 首部变形
            headPowMD = cmds.createNode('multiplyDivide', n='%sVolumeHeadMD' % name)
            cmds.setAttr('%s.operation' % headPowMD, 3)
            cmds.connectAttr('%s.outputX' % self.volumeSizeMD, '%s.input1X' % headPowMD, f=1)
            cmds.setAttr('%s.input2X' % headPowMD, self.scaleRatio.head.get(i))
            cmds.connectAttr('%s.outputX' % headPowMD, '%s.input[2]' % switchCC, f=1)

            # 尾部变形
            tailPowMD = cmds.createNode('multiplyDivide', n='%sVolumeTailMD' % name)
            cmds.setAttr('%s.operation' % tailPowMD, 3)
            cmds.connectAttr('%s.outputX' % self.volumeSizeMD, '%s.input1X' % tailPowMD, f=1)
            cmds.setAttr('%s.input2X' % tailPowMD, self.scaleRatio.tail.get(i))
            cmds.connectAttr('%s.outputX' % tailPowMD, '%s.input[3]' % switchCC, f=1)

            # 中心变形
            centerPowMD = cmds.createNode('multiplyDivide', n='%sVolumeCenterMD' % name)
            cmds.setAttr('%s.operation' % centerPowMD, 3)
            cmds.connectAttr('%s.outputX' % self.volumeSizeMD, '%s.input1X' % centerPowMD, f=1)
            cmds.setAttr('%s.input2X' % centerPowMD, self.scaleRatio.center.get(i))
            cmds.connectAttr('%s.outputX' % centerPowMD, '%s.input[4]' % switchCC, f=1)

            # 首位变形
            sidesPowMD = cmds.createNode('multiplyDivide', n='%sVolumeSidesMD' % name)
            cmds.setAttr('%s.operation' % sidesPowMD, 3)
            cmds.connectAttr('%s.outputX' % self.volumeSizeMD, '%s.input1X' % sidesPowMD, f=1)
            cmds.setAttr('%s.input2X' % sidesPowMD, self.scaleRatio.side.get(i))
            cmds.connectAttr('%s.outputX' % sidesPowMD, '%s.input[5]' % switchCC, f=1)

            # 添加圆锥变形控制=============================================
            coneUSideMD = cmds.createNode('multiplyDivide', n='%sConeUSidesMD' % name)
            cmds.setAttr('%s.input1' % coneUSideMD, i, self.jointCount - 1 - i, 0, type='double3')
            cmds.connectAttr('%s.outColorR' % self.coneUScaleCD, '%s.input2X' % coneUSideMD, f=1)
            cmds.connectAttr('%s.outColorR' % self.coneUScaleCD, '%s.input2Y' % coneUSideMD, f=1)

            coneUChoiceBC = cmds.createNode('blendColors', n='%sConeUSideChoiceBC' % name)
            cmds.connectAttr('%s.outColorG' % self.coneUScaleCD, '%s.blender' % coneUChoiceBC, f=1)
            cmds.connectAttr('%s.outputX' % coneUSideMD, '%s.color1R' % coneUChoiceBC, f=1)
            cmds.connectAttr('%s.outputY' % coneUSideMD, '%s.color2R' % coneUChoiceBC, f=1)

            coneUBaseADL = cmds.createNode('addDoubleLinear', n='%sConeUBaseADL' % name)
            cmds.setAttr('%s.input1' % coneUBaseADL, 1, l=1)
            cmds.connectAttr('%s.outputR' % coneUChoiceBC, '%s.input2' % coneUBaseADL, f=1)

            volumeUTotalMDL = cmds.createNode('multDoubleLinear', n='%sVolumeUTotalMDL' % name)
            cmds.connectAttr('%s.output' % volumeMultMDL, '%s.input1' % volumeUTotalMDL, f=1)
            cmds.connectAttr('%s.output' % coneUBaseADL, '%s.input2' % volumeUTotalMDL, f=1)

            coneVSideMD = cmds.createNode('multiplyDivide', n='%sConeVSidesMD' % name)
            cmds.setAttr('%s.input1' % coneVSideMD, i, self.jointCount - 1 - i, 0, type='double3')
            cmds.connectAttr('%s.outColorR' % self.coneVScaleCD, '%s.input2X' % coneVSideMD, f=1)
            cmds.connectAttr('%s.outColorR' % self.coneVScaleCD, '%s.input2Y' % coneVSideMD, f=1)

            coneVChoiceBC = cmds.createNode('blendColors', n='%sConeVSideChoiceBC' % name)
            cmds.connectAttr('%s.outColorG' % self.coneVScaleCD, '%s.blender' % coneVChoiceBC, f=1)
            cmds.connectAttr('%s.outputX' % coneVSideMD, '%s.color1R' % coneVChoiceBC, f=1)
            cmds.connectAttr('%s.outputY' % coneVSideMD, '%s.color2R' % coneVChoiceBC, f=1)

            coneVBaseADL = cmds.createNode('addDoubleLinear', n='%sConeVBaseADL' % name)
            cmds.setAttr('%s.input1' % coneVBaseADL, 1, l=1)
            cmds.connectAttr('%s.outputR' % coneVChoiceBC, '%s.input2' % coneVBaseADL, f=1)

            volumeVTotalMDL = cmds.createNode('multDoubleLinear', n='%sVolumeVTotalMDL' % name)
            cmds.connectAttr('%s.output' % volumeMultMDL, '%s.input1' % volumeVTotalMDL, f=1)
            cmds.connectAttr('%s.output' % coneVBaseADL, '%s.input2' % volumeVTotalMDL, f=1)

            # 连接到输出位置POS
            cmds.connectAttr('%s.output' % volumeUTotalMDL, '%s.sy' % basePos, f=1)
            cmds.connectAttr('%s.output' % volumeVTotalMDL, '%s.sz' % basePos, f=1)

            connectInfos[basePos] = self.joints[i]
            self.__allNodes += nodes_tmp
            self.__allNodes += [self.globalSwitchCD, targetMP, baseMP, oftPMA, valueCL, currentLengthMDL, newPerMD,
                                newPerPMA, newPreCL, twistMDL, twistPMA, twistUC, switchCC, volumeMultMDL, headPowMD,
                                tailPowMD, centerPowMD, sidesPowMD, coneUSideMD, coneUChoiceBC, coneUBaseADL,
                                volumeUTotalMDL, coneVSideMD, coneVChoiceBC, coneVBaseADL, volumeVTotalMDL]

            lockChannels(tarPos)
            lockChannels(basePos)
        for key, value in connectInfos.iteritems():
            con = cmds.parentConstraint(key, value, w=1, mo=self.keepOffset)
            cmds.connectAttr('%s.s' % key, '%s.s' % value, f=1)
            parent.fitParent(con[0], self.constraintsGroup)


class SplineSystem(object):
    def __init__(self, rootJoint, **kwargs):
        self.rootJoint = rootJoint
        self.controllerNumber = kwargs.get('controllerNumber', kwargs.get('cn', 4))
        self.upVector = kwargs.get('upVector', kwargs.get('uv', [0, 1, 0]))
        self.aimVector = kwargs.get('aimVector', kwargs.get('av', [1, 0, 0]))
        self.upObject = kwargs.get('upObject', kwargs.get('uo', None))
        self.axis = kwargs.get('axis', kwargs.get('a', 0))
        self.keepOffset = kwargs.get('keepOffset', kwargs.get('ko', True))
        self.mainColor = kwargs.get('mainColor', kwargs.get('mc', 6))
        self.rollColor = kwargs.get('rollColor', kwargs.get('rc', 18))
        self.fkColor = kwargs.get('fkColor', kwargs.get('fkc', 14))
        self.ikColor = kwargs.get('ikColor', kwargs.get('ikc', 20))
        self.addToSet = kwargs.get('addToSet', kwargs.get('ats', False))
        self.setName = kwargs.get('setName', kwargs.get('sn', ''))

        self.__joints = []
        self._locations = []
        self._controlLocations = []
        self._distance = 0
        self.__fkControllers = []
        self.__ikControllers = []
        self.__motionSystem = None
        self.__mainSet = None
        self.__fkControllerSet = None
        self.__ikControllerSet = None
        self.__controllerSet = None
        self.__deformSet = None

    @property
    def joints(self):
        if cmds.objExists(self.rootJoint):
            if not self.__joints:
                self.__joints = getSplineJoints(self.rootJoint)
        else:
            self.__joints = []
        return self.__joints

    @property
    def name(self):
        name = self.rootJoint
        if name:
            while True:
                if name[-1].isdigit():
                    name = name[:-1]
                else:
                    break
        return name

    @property
    def mainGroup(self):
        name = '%sSplineGroup' % self.name
        if not cmds.objExists(name):
            cmds.createNode('transform', n=name)
        if not cmds.objExists('%s.Author' % name):
            cmds.addAttr(name, ln='Author', dt='string')
            cmds.setAttr('%s.Author' % name, 'Jesse Chou', type='string', l=1)
        if not cmds.objExists('%s.Mail' % name):
            cmds.addAttr(name, ln='Mail', dt='string')
            cmds.setAttr('%s.Mail' % name, 'JesseChou0612@gmail.com or 375714316@qq.com', type='string', l=1)
        return name

    @property
    def rigSystem(self):
        rig = '%sRigSystem' % self.name
        if not cmds.objExists(rig):
            cmds.createNode('transform', n=rig)
            cmds.setAttr('%s.v' % rig, 0, l=True)
            cmds.setAttr('%s.inheritsTransform' % rig, 0)
        parent.fitParent(rig, self.mainGroup)
        lockChannels(rig)
        return rig

    @property
    def deformSystem(self):
        deform = '%sDeformSystem' % self.name
        if not cmds.objExists(deform):
            cmds.createNode('transform', n=deform)
        parent.fitParent(deform, self.mainGroup)
        return deform

    @property
    def controlSystem(self):
        control = '%sControllersGrp' % self.name
        if not cmds.objExists(control):
            cmds.createNode('transform', n=control)
        parent.fitParent(control, self.mainGroup)
        return control

    @property
    def globalScaleLocator(self):
        loc = '%sGlobalScaleLoc' % self.name
        if not cmds.objExists(loc):
            cmds.container(type='dagContainer', ind=['inputs', 'outputs'], includeShaders=True,
                           includeHierarchyBelow=True, includeTransform=True, n=loc)
            cmds.setAttr('%s.iconName' % loc, 'out_transform.png', type='string', l=1)
            cmds.setAttr('%s.blackBox' % loc, 1, l=1)
            cmds.setAttr('%s.inheritsTransform' % loc)
            cmds.addAttr(loc, ln='Author', dt='string')
            cmds.setAttr('%s.Author' % loc, 'Jesse Chou', type='string', l=1)
            cmds.addAttr(loc, ln='Mail', dt='string')
            cmds.setAttr('%s.Mail' % loc, 'JesseChou0612@gmail.com or 375714316@qq.com', type='string', l=1)

        parent.fitParent(loc, self.rigSystem)
        cons = cmds.listConnections(loc, s=True, d=False, type='scaleConstraint') or []
        cons = list(set(cons))
        if not cons:
            cons = cmds.scaleConstraint(self.mainController, loc)
        for con in cons:
            parent.fitParent(con, self.constraintsGroup)
        lockChannels(loc)
        return loc

    @property
    def constraintsGroup(self):
        con = '%sConstraintsGrp' % self.name
        if not cmds.objExists(con):
            cmds.createNode('transform', n=con)
        parent.fitParent(con, self.rigSystem)
        return con

    @property
    def fkControllersGroup(self):
        fk = '%sFKControllersGrp' % self.name
        if not cmds.objExists(fk):
            cmds.createNode('transform', n=fk)
        parent.fitParent(fk, self.controlSystem)
        return fk

    @property
    def ikControllersGroup(self):
        ik = '%sIKControllersGrp' % self.name
        if not cmds.objExists(ik):
            cmds.createNode('transform', n=ik)
            cmds.setAttr('%s.inheritsTransform' % ik, 0)
        parent.fitParent(ik, self.controlSystem)
        return ik

    @property
    def baseCurve(self):
        curve = '%sBaseCrv' % self.name
        if not cmds.objExists(curve):
            pos = [cmds.xform(jnt, q=1, ws=1, t=1) for jnt in self.joints]
            createSplineCurve(pos, self.controllerNumber, curve)
        parent.fitParent(curve, self.rigSystem)
        return curve

    @property
    def targetCurve(self):
        curve = '%sTargetCrv' % self.name
        if not cmds.objExists(curve):
            pos = [cmds.xform(jnt, q=1, ws=1, t=1) for jnt in self.joints]
            createSplineCurve(pos, self.controllerNumber, curve)
        parent.fitParent(curve, self.rigSystem)
        return curve

    @property
    def handleGroup(self):
        handle = '%sHandleGroup' % self.name
        if not cmds.objExists(handle):
            cmds.createNode('transform', n=handle)
        parent.fitParent(handle, self.rigSystem)
        return handle

    @property
    def locationGroup(self):
        location = '%sLocationGroup' % self.name
        if not cmds.objExists(location):
            cmds.createNode('transform', n=location)
        parent.fitParent(location, self.rigSystem)
        return location

    @property
    def mainController(self):
        controller = '%sMainCtr' % self.name
        if not cmds.objExists(controller):
            ctr = controllerManager.Controller(controller, groups=['Ext', 'Tra', 'Oft'], post='',
                                               color=7, groupEnable=True)
            ctr.create(37)
            cmds.setAttr('%s.rz' % controller, 90)
            if not self._distance:
                self.getControllerDistance()
            cmds.setAttr('%s.s' % controller, self._distance * .7, self._distance * .7, self._distance * .7,
                         type='double3')
            cmds.makeIdentity(controller, r=1, a=1, t=1, s=1)
        mainGroup = '%sOft' % controller
        matchTransform(mainGroup, self._controlLocations[0])
        parent.fitParent(mainGroup, self.controlSystem)
        return controller

    @property
    def controlAttrs(self):
        attrs = [{'name': 'mainColor', 'type': 'long', 'min': 0, 'max': 31, 'value': 6, 'key': False},
                 {'name': 'rollColor', 'type': 'long', 'min': 0, 'max': 31, 'value': 18, 'key': False},
                 {'name': 'fkColor', 'type': 'long', 'min': 0, 'max': 31, 'value': 14, 'key': False},
                 {'name': 'ikColor', 'type': 'long', 'min': 0, 'max': 31, 'value': 20, 'key': False},
                 {'name': 'deformVis', 'type': 'bool', 'value': True, 'key': False},
                 {'name': 'switch', 'type': 'enum', 'items': 'FIK:FK:IK', 'key': True},
                 {'name': 'size', 'type': 'double', 'min': 0.001, 'value': 1, 'key': True},
                 {'name': 'stretch', 'type': 'double', 'min': 0, 'max': 1, 'value': 0, 'key': True},
                 {'name': 'volume', 'type': 'enum', 'items': 'None:Full:Head:Tail:Center:Sides:', 'key': True},
                 {'name': 'coneU', 'type': 'double', 'key': True},
                 {'name': 'coneV', 'type': 'double', 'key': True},
                 {'name': 'volumeMultiplier', 'type': 'double', 'value': 1, 'min': 0.001, 'key': True},
                 {'name': 'roll', 'type': 'double', 'key': True},
                 {'name': 'twist', 'type': 'double', 'key': True},
                 {'name': 'slide', 'type': 'double', 'min': 0, 'max': 1, 'value': 0, 'key': True},
                 {'name': 'decay', 'type': 'double', 'key': True},
                 {'name': 'ikFollow', 'type': 'enum', 'items': 'None:Head:Full:', 'key': True, 'value': 2}]
        return attrs

    @property
    def rollController(self):
        name = '%sRoll' % self.name
        if not cmds.objExists(name):
            ctr = controllerManager.Controller(name, groups=['Oft'], post='', color=19, groupEnable=True)
            ctr.create(20)
            if not self._distance:
                self.getControllerDistance()
            cmds.setAttr('%s.s' % name, self._distance * .32, self._distance * .32, self._distance * .32,
                         type='double3')
            cmds.makeIdentity(name, r=1, a=1, t=1, s=1)
            attributes.edit(name, ['%s%s' % (x, y) for x in 'ts' for y in 'xyz'] + ['v'], [], 1)
        oft = '%sOft' % name
        cons = cmds.listConnections(oft, s=True, d=False, type='parentConstraint')
        if not cons:
            cons = cmds.parentConstraint(self.mainController, oft, w=1)
        parent.fitParent(oft, self.fkControllersGroup)
        parent.fitParent(cons[0], self.constraintsGroup)
        return name

    @property
    def fkControllers(self):
        return self.__fkControllers

    @property
    def ikControllers(self):
        return self.__ikControllers

    @property
    def fikSwitchCdn(self):
        node = '%sFIKSwitchCD' % self.name
        if not cmds.objExists(node):
            cmds.createNode('condition', n=node)
        cmds.setAttr('%s.operation' % node, 0)
        cmds.setAttr('%s.secondTerm' % node, 0)
        cmds.setAttr('%s.colorIfTrue' % node, 1, 1, 0, type='double3')
        cmds.setAttr('%s.colorIfFalse' % node, 0, 0, 0, type='double3')
        cmds.connectAttr('%s.switch' % self.mainController, '%s.firstTerm' % node, f=1)
        return node

    @property
    def fkSwitchCdn(self):
        node = '%sFKSwitchCDN' % self.name
        if not cmds.objExists(node):
            cmds.createNode('condition', n=node)
        cmds.setAttr('%s.operation' % node, 0)
        cmds.setAttr('%s.secondTerm' % node, 1)
        cmds.setAttr('%s.colorIfTrue' % node, 1, 0, 0, type='double3')
        cmds.connectAttr('%s.switch' % self.mainController, '%s.firstTerm' % node, f=1)
        cmds.connectAttr('%s.outColor' % self.fikSwitchCdn, '%s.colorIfFalse' % node, f=1)
        return node

    @property
    def ikSwitchCdn(self):
        node = '%sIKSwitchCDN' % self.name
        if not cmds.objExists(node):
            cmds.createNode('condition', n=node)
        cmds.setAttr('%s.operation' % node, 0)
        cmds.setAttr('%s.secondTerm' % node, 2)
        cmds.setAttr('%s.colorIfTrue' % node, 0, 1, 1, type='double3')
        cmds.connectAttr('%s.switch' % self.mainController, '%s.firstTerm' % node, f=1)
        cmds.connectAttr('%s.outColor' % self.fkSwitchCdn, '%s.colorIfFalse' % node, f=1)
        cmds.connectAttr('%s.outColorR' % node, '%s.v' % self.fkControllersGroup, f=1)
        cmds.connectAttr('%s.outColorG' % node, '%s.v' % self.ikControllersGroup, f=1)
        # cmds.connectAttr('%s.outColorB' % node, '%s.v' % IKTip_grp, f=1)
        return node

    @property
    def switchRv(self):
        name = '%sSwitchRV' % self.name
        if not cmds.objExists(name):
            cmds.createNode('reverse', n=name)
        cmds.connectAttr('%s.outColorR' % self.ikSwitchCdn, '%s.inputX' % name, f=1)
        return name

    @property
    def ikFollowAllCdn(self):
        name = '%sIkFollowAllCDN' % self.name
        if not cmds.objExists(name):
            cmds.createNode('condition', n=name)
        cmds.setAttr('%s.secondTerm' % name, 2)
        cmds.setAttr('%s.colorIfTrueR' % name, 1)
        cmds.setAttr('%s.colorIfFalseR' % name, 0)
        return name

    @property
    def ikFollowHeadCdn(self):
        name = '%sIkFollowHeadCDN' % self.name
        if not cmds.objExists(name):
            cmds.createNode('condition', n=name)
        cmds.setAttr('%s.secondTerm' % name, 1)
        cmds.setAttr('%s.colorIfTrueR' % name, 1)
        cmds.setAttr('%s.colorIfFalseR' % name, 0)
        return name

    @property
    def positionsGroup(self):
        name = '%sPositionsGrp' % self.name
        if not cmds.objExists(name):
            cmds.createNode('transform', n=name)
        parent.fitParent(name, self.rigSystem)
        return name

    @property
    def basePositionsGroup(self):
        name = '%sBasePositionsGrp' % self.name
        if not cmds.objExists(name):
            cmds.createNode('transform', n=name)
        parent.fitParent(name, self.positionsGroup)
        return name

    @property
    def targetPositionsGroup(self):
        name = '%stargetPositionsGrp' % self.name
        if not cmds.objExists(name):
            cmds.createNode('transform', n=name)
        parent.fitParent(name, self.positionsGroup)
        return name

    @property
    def motionSystem(self):
        if not self.__motionSystem:
            self.__motionSystem = MotionSystem(self.baseCurve, self.targetCurve, self.joints, self.mainController,
                                               self.globalScaleLocator, self.basePositionsGroup,
                                               self.targetPositionsGroup, self.constraintsGroup, self.keepOffset)
        return self.__motionSystem

    @property
    def mainSet(self):
        self.__mainSet = '%sSet' % self.name
        checkSet(self.__mainSet)
        return self.__mainSet

    @property
    def fkControllerSet(self):
        self.__fkControllerSet = '%sFkSet' % self.name
        checkSet(self.__fkControllerSet)
        return self.__fkControllerSet

    @property
    def ikControllerSet(self):
        self.__ikControllerSet = '%sIkSet' % self.name
        checkSet(self.__ikControllerSet)
        return self.__ikControllerSet

    @property
    def controllerSet(self):
        self.__controllerSet = '%sControllerSet' % self.name
        checkSet(self.__controllerSet)
        return self.__controllerSet

    @property
    def deformSet(self):
        self.__deformSet = '%sDeformSet' % self.name
        checkSet(self.__deformSet)
        return self.__deformSet

    def createLocations(self):
        """
        创建基础控制点
        :return:
        """
        self._locations = []
        baseShape = cmds.listRelatives(self.baseCurve, s=1, typ='nurbsCurve')[0]
        tarShape = cmds.listRelatives(self.targetCurve, s=1, typ='nurbsCurve')[0]
        tcps = cmds.ls('%s.controlPoints[*]' % tarShape, fl=1)
        length = cmds.arclen(baseShape, ch=0)
        cps = cmds.ls('%s.controlPoints[*]' % baseShape, fl=1)
        num = len(cps)
        offset = length * 1.0 / num
        n = 1
        for i in range(num):
            position = cmds.xform(cps[i], q=1, ws=1, t=1)
            if i == 1:
                nam_cp = '%sPositionExt%d_cp' % (self.name, n - 1)
                nam_aim = '%sPositionExt%d_aim' % (self.name, n - 1)
            elif i == num - 2:
                nam_cp = '%sPositionExt%d_cp' % (self.name, n)
                nam_aim = '%sPositionExt%d_aim' % (self.name, n)
            else:
                nam_cp = '%sPosition%d_cp' % (self.name, n)
                nam_aim = '%sPosition%d_aim' % (self.name, n)
                n += 1
            pos_cp = cmds.spaceLocator(n=nam_cp, p=[0, 0, 0])[0]
            cmds.setAttr('%s.v' % pos_cp, 0)
            pos_aim = cmds.spaceLocator(n=nam_aim, p=[0, 0, 0])[0]
            cmds.setAttr('%s.v' % pos_aim, 0)
            cmds.setAttr('%s.ty' % pos_aim, offset)
            cmds.parent(pos_aim, pos_cp)
            cmds.xform(pos_cp, ws=1, t=position)
            shape = cmds.listRelatives(nam_cp, s=1)[0]
            cmds.connectAttr('%s.worldPosition[0]' % shape, cps[i])
            aimShape = cmds.listRelatives(nam_aim, s=1)[0]
            cmds.connectAttr('%s.worldPosition[0]' % aimShape, tcps[i])

            self._locations.append(pos_cp)
        return self._locations

    def setAxis(self):
        """
        #设置控制点方向
        :return:None
        """
        delObjs = []
        upObj = self.upObject
        if not upObj:
            upObj = cmds.createNode('transform')
            upOft = cmds.group(upObj)
            cmds.setAttr('%s.ty' % upObj, 10000)
            matchTransform(upOft, self.rootJoint)
            delObjs += [upOft]

        if self.axis == 0:
            nums = len(self._locations)
            for i in range(nums - 1):
                cmds.delete(
                    cmds.aimConstraint(self._locations[i + 1], self._locations[i], aim=self.aimVector, u=self.upVector,
                                       wut='object', wuo=upObj))
            cmds.delete(cmds.orientConstraint(self._locations[-2], self._locations[-1], w=1, mo=0))

        if self.axis == 1:
            for obj in self._locations:
                cmds.delete(
                    cmds.tangentConstraint(self.baseCurve, obj, aim=self.aimVector, u=self.upVector, wut='object',
                                           wuo=upObj))
        if delObjs:
            cmds.delete(delObjs)

    def correctSideLocations(self):
        """
        # 修正首尾附加控制点
        :return:
        """
        # 修正首位附加点
        self._controlLocations = []
        # 首节点
        startDB = cmds.createNode('distanceBetween', n='%sStartDB' % self.name)
        start1Shape = cmds.listRelatives(self._locations[0], s=1)[0]
        start2Shape = cmds.listRelatives(self._locations[2], s=1)[0]
        cmds.connectAttr('%s.worldPosition[0]' % start1Shape, '%s.point1' % startDB, f=1)
        cmds.connectAttr('%s.worldPosition[0]' % start2Shape, '%s.point2' % startDB, f=1)
        startSR = cmds.createNode('setRange', n='%sStartSR' % self.name)
        cmds.connectAttr('%s.distance' % startDB, '%s.valueX' % startSR, f=1)
        cmds.setAttr('%s.oldMaxX' % startSR, cmds.getAttr('%s.distance' % startDB) * 1.01)
        length = vectorCrossProduct(cmds.xform(self._locations[0], q=1, t=1, ws=1),
                                    cmds.xform(self._locations[1], q=1, t=1, ws=1))
        cmds.setAttr('%s.maxX' % startSR, length)
        cmds.parent(self._locations[1], self._locations[0])
        cmds.connectAttr('%s.outValueX' % startSR, '%s.translateX' % self._locations[1], f=1)

        # 尾节点
        endDB = cmds.createNode('distanceBetween', n='%sEendDB' % self.name)
        end1Shape = cmds.listRelatives(self._locations[-1], s=1)[0]
        end2Shape = cmds.listRelatives(self._locations[-3], s=1)[0]
        cmds.connectAttr('%s.worldPosition[0]' % end1Shape, '%s.point1' % endDB, f=1)
        cmds.connectAttr('%s.worldPosition[0]' % end2Shape, '%s.point2' % endDB, f=1)
        endSR = cmds.createNode('setRange', n='%sEndSR' % self.name)

        cmds.connectAttr('%s.distance' % endDB, '%s.valueX' % endSR, f=1)
        cmds.setAttr('%s.oldMaxX' % endSR, cmds.getAttr('%s.distance' % endDB) * 1.01)
        length = vectorCrossProduct(cmds.xform(self._locations[0], q=1, t=1, ws=1),
                                    cmds.xform(self._locations[1], q=1, t=1, ws=1))
        cmds.setAttr('%s.maxX' % endSR, length * -1)
        cmds.parent(self._locations[-2], self._locations[-1])

        cmds.connectAttr('%s.outValueX' % endSR, '%s.translateX' % self._locations[-2], f=1)
        for location in self._locations:
            if location not in [self._locations[1], self._locations[-2]]:
                self._controlLocations.append(location)
        return self._controlLocations

    def createControlHandle(self):
        """
        为曲线的控制点，添加组别，并放置到合适的组别里
        :return:
        """
        for location in self._controlLocations:
            name = location.replace('_cp', '')
            ext = cmds.createNode('transform', n='%sExt' % name)
            tra = cmds.group(ext, n='%sTra' % name)
            oft = cmds.group(tra, n='%sOft' % name)
            matchTransform(oft, location)
            parent.fitParent(location, ext)
            parent.fitParent(oft, self.locationGroup)

    def getControllerDistance(self):
        """
        获取控制器间距，用来确定控制器大小
        :return: 间距距离
        """
        lengths = [vectorCrossProduct(cmds.xform(self._controlLocations[i], q=1, ws=1, t=1),
                                      cmds.xform(self._controlLocations[i + 1], q=1, ws=1, t=1)) for i in
                   range(len(self._controlLocations) - 1)]
        self._distance = max(lengths)
        return self._distance

    def addControlAttrs(self):
        # 为控制器添加控制属性
        for attr in self.controlAttrs:
            name = attr.get('name')
            typ = attr.get('type')
            args = {'ln': name, 'at': typ}
            if typ == 'enum':
                args['en'] = attr.get('items')
            if 'min' in attr.keys():
                args['min'] = attr.get('min')
            if 'max' in attr.keys():
                args['max'] = attr.get('max')
            if 'value' in attr.keys():
                args['dv'] = attr.get('value')
            cmds.addAttr(self.mainController, **args)
            key = attr.get('key')
            if key:
                cmds.setAttr('%s.%s' % (self.mainController, name), e=True, l=False, k=True)
            else:
                cmds.setAttr('%s.%s' % (self.mainController, name), e=True, l=False, k=False, cb=True)

    def createFkControllers(self):
        # 创建FK控制器
        par = self.fkControllersGroup
        self.__fkControllers = []
        for i in range(len(self._controlLocations)):
            name = '%s%dFK' % (self.name, i + 1)
            if not cmds.objExists(name):
                ctr = controllerManager.Controller(name, groups=['Ext', 'Tra', 'Oft'], post='', color=15,
                                                   groupEnable=True)
                ctr.create(28)
                cmds.setAttr('%s.rz' % name, 90)
                cmds.setAttr('%s.s' % name, self._distance * .5, self._distance * .5, self._distance * .5,
                             type='double3')
                cmds.makeIdentity(name, r=1, a=1, t=1, s=1)
                attributes.edit(name, ['sx', 'sy', 'sz', 'v'], [], 1)
            oft = '%sOft' % name
            tra = '%sTra' % name

            matchTransform(oft, self._controlLocations[i])
            cmds.connectAttr('%s.r' % self.rollController, '%s.r' % tra, f=1)
            cmds.parent(oft, par)
            par = name
            if i == 0:
                cons = cmds.listConnections('%s.tx' % oft, s=True, d=False, type='parentConstraint')
                if not cons:
                    cons = cmds.parentConstraint(self.mainController, oft, w=1, mo=1)
                parent.fitParent(cons[0], self.constraintsGroup)
            self.__fkControllers.append(name)

    def createIkControllers(self):
        # 创建IK控制器
        for i in range(len(self._controlLocations)):
            name = '%s%dIK' % (self.name, i + 1)
            if not cmds.objExists(name):
                ctr = controllerManager.Controller(name, groups=['Ext', 'Tra', 'Con', 'Oft'], post='', color=21,
                                                   groupEnable=True)
                ctr.create(11)
                cmds.setAttr('%s.s' % name, self._distance * .3, self._distance * .3, self._distance * .3,
                             type='double3')
                cmds.makeIdentity(name, r=1, a=1, t=1, s=1)
                attributes.edit(name, ['sx', 'sy', 'sz', 'v'], [], 1)
            oft = '%sOft' % name
            con = '%sCon' % name
            tra = '%sTra' % name
            matchTransform(oft, self._controlLocations[i])
            parent.fitParent(oft, self.ikControllersGroup)
            locationTra = self._controlLocations[i].replace('_cp', 'Tra')
            constraints = cmds.listConnections('%s.tx' % locationTra, s=True, d=False, type='parentConstraint')
            if not constraints:
                constraints = cmds.parentConstraint(name, locationTra, w=1, mo=1)
            parent.fitParent(constraints[0], self.constraintsGroup)
            traCons = cmds.listConnections('%s.tx' % tra, s=True, d=False, type='parentConstraint')
            if not traCons:
                traCons = cmds.parentConstraint(con, self.fkControllers[i], tra, w=1, mo=0)
            parent.fitParent(traCons[0], self.constraintsGroup)
            cmds.connectAttr('%s.outputX' % self.switchRv, '%s.target[0].targetWeight' % traCons[0], f=1)
            cmds.connectAttr('%s.outColorR' % self.ikSwitchCdn, '%s.target[1].targetWeight' % traCons[0], f=1)
            if i == 0:
                cons = cmds.listConnections('%s.tx' % oft, s=True, d=False, type='parentConstraint')
                if not cons:
                    cons = cmds.parentConstraint(self.mainController, oft, w=1, mo=1)
                cmds.connectAttr('%s.ikFollow' % self.mainController, '%s.firstTerm' % self.ikFollowHeadCdn, f=True)
                cmds.connectAttr('%s.outColorR' % self.ikFollowHeadCdn, '%s.target[0].targetWeight' % cons[0], f=True)
                parent.fitParent(cons[0], self.constraintsGroup)
            self.__ikControllers.append(name)
        constraint = cmds.parentConstraint(self.mainController, self.ikControllersGroup, w=1, mo=True)
        cmds.connectAttr('%s.ikFollow' % self.mainController, '%s.firstTerm' % self.ikFollowAllCdn, f=True)
        cmds.connectAttr('%s.outColorR' % self.ikFollowAllCdn, '%s.target[0].targetWeight' % constraint[0], f=True)
        parent.fitParent(constraint[0], self.constraintsGroup)

    def connectControllerColor(self, attr, controllers):
        for controller in controllers:
            shapes = cmds.listRelatives(controller, s=True)
            if shapes:
                for shape in shapes:
                    cmds.setAttr('%s.ove' % shape, True)
                    cmds.connectAttr('%s.%s' % (self.mainController, attr), '%s.ovc' % shape, f=True)

    def connectControllersColor(self):
        self.connectControllerColor('mainColor', [self.mainController])
        self.connectControllerColor('rollColor', [self.rollController])
        self.connectControllerColor('fkColor', [self.fkControllers])
        self.connectControllerColor('ikColor', [self.ikControllers])
        cmds.setAttr('%s.mainColor' % self.mainController, self.mainColor)
        cmds.setAttr('%s.rollColor' % self.mainController, self.rollColor)
        cmds.setAttr('%s.fkColor' % self.mainController, self.fkColor)
        cmds.setAttr('%s.ikColor' % self.mainController, self.ikColor)

    def fitScaleConstraint(self):
        for node in [self.locationGroup, self.globalScaleLocator, self.deformSystem, self.fkControllersGroup,
                     self.ikControllersGroup]:
            cons = cmds.listConnections(node, s=True, d=False, type='scaleConstraint') or []
            cons = list(set(cons))
            if not cons:
                cons = cmds.scaleConstraint(self.mainController, node, w=1)
            for con in cons:
                parent.fitParent(con, self.constraintsGroup)

    def appendToSet(self):
        # 将控制器和上层组，添加到控制器选择集中，将骨骼添加到影响物选择集中
        for fk in self.fkControllers:
            cmds.sets(fk, add=self.fkControllerSet)
            ext = '%sExt' % fk
            if cmds.objExists(ext):
                cmds.sets(ext, add=self.fkControllerSet)

        for ik in self.ikControllers:
            cmds.sets(ik, add=self.ikControllerSet)
            ext = '%sExt' % ik
            if cmds.objExists(ext):
                cmds.sets(ext, add=self.ikControllerSet)

        nodes = [self.fkControllerSet, self.ikControllerSet, self.rollController, self.mainController]
        cmds.sets(nodes, add=self.controllerSet)

        cmds.sets(self.joints, add=self.deformSet)

        cmds.sets(self.controllerSet, self.deformSet, add=self.mainSet)

    def appendToMainSet(self):
        # 添加至整体选择集
        if self.addToSet and self.setName:
            checkSet(self.setName)
            if cmds.nodeType(self.setName) == 'objectSet':
                cmds.sets(self.mainSet, add=self.setName)

    def createSplineSystem(self, **kwargs):
        """
        #创建骨骼链绑定
        :param kwargs:  axis => 轴向类型
                        upObject => 朝向物体
                        offset => 保持偏移
                        upVector => 向上向量
                        aimVector => 目标向量
        :return:
        """
        self.axis = kwargs.get('axis', self.axis)
        self.upObject = kwargs.get('upObject', kwargs.get('uo', self.upObject))
        self.keepOffset = kwargs.get('offset', kwargs.get('o', self.keepOffset))
        self.upVector = kwargs.get('upVector', kwargs.get('uv', self.upVector))
        self.aimVector = kwargs.get('aimVector', kwargs.get('av', self.aimVector))

        self.mainColor = kwargs.get('mainColor', kwargs.get('mc', self.mainColor))
        self.rollColor = kwargs.get('rollColor', kwargs.get('rc', self.rollColor))
        self.fkColor = kwargs.get('fkColor', kwargs.get('fkc', self.fkColor))
        self.ikColor = kwargs.get('ikColor', kwargs.get('ikc', self.ikColor))

        self.addToSet = kwargs.get('addToSet', kwargs.get('ats', self.addToSet))
        self.setName = kwargs.get('setName', kwargs.get('sn', self.setName))

        # 把骨骼放到对应的组里
        parent.fitParent(self.rootJoint, self.deformSystem)
        # 创建控制点
        self.createLocations()
        # 匹配控制点轴向
        self.setAxis()
        # 修正首尾控制点
        self.correctSideLocations()
        # 创建控制组别
        self.createControlHandle()
        # 创建主控制器
        self.addControlAttrs()
        # 创建fk控制器
        self.createFkControllers()
        # 创建IK控制器
        self.createIkControllers()
        # 连接所有控制器颜色属性
        self.connectControllersColor()
        # 创建motion系统
        self.motionSystem.createControlPositions()
        # 适配缩放控制
        self.fitScaleConstraint()
        # 添加到控制器set中
        self.appendToSet()
        # 添加到指定set中
        self.appendToMainSet()

        cmds.connectAttr('%s.deformVis' % self.mainController, '%s.v' % self.deformSystem, f=1)
        cmds.container(self.globalScaleLocator, e=1, f=1, addNode=self.motionSystem.allNodes)


def getSplineJoints(start, style=0):
    """
    # 获取骨骼链层级信息
    start: the start joint name
    style: get style, 0 => max, 1 => min
    """
    infos = [start]
    children = cmds.listRelatives(start, c=1, f=1) or []
    length = 0
    child_infos = []
    for child in children:
        infs = getSplineJoints(child, style)
        if style == 0:
            if len(infs) > length:
                length = len(infs)
                child_infos = infs
        if style == 1:
            if length == 0:
                length = len(infs)
                child_infos = infs
            else:
                if len(infs) < length:
                    length = len(infs)
                    child_infos = infs
    infos += child_infos
    return infos


def lockChannels(obj):
    # 锁定并隐藏物体通道属性
    for attr in setting.CHANNEL_BASE_ATTRS:
        cmds.setAttr('%s.%s' % (obj, attr), e=1, l=1, k=0)
    return None


def createSplineCurve(positions, number, name):
    """
    #创建曲线
    :param positions: 曲线的各个点位置
    :param number: 创建曲线的点数
    :param name: 曲线名称
    :return:
    """
    crv = cmds.curve(d=1, n=name, p=positions)
    shape = cmds.listRelatives(crv, s=1)[0]
    cmds.rename(shape, '%sShape' % crv)
    cmds.rebuildCurve(crv, s=number - 1, d=3, kr=0)
    cmds.setAttr('%s.v' % crv, 0)
    lockChannels(crv)
    return crv


def getSelectionSets():
    # 获取选择set
    selectionSets = cmds.ls(sl=True, type='objectSet')
    if selectionSets:
        return selectionSets[0]


def checkSet(name):
    if not cmds.objExists(name):
        cmds.sets(em=True, n=name)
    return name


def showInMaya():
    from python.core import mayaPyside
    kws = {'name': 'ToolkitBasedCurveMainWindow',
           'title': u'曲线创建工具主窗口 Ver 2.0.0',
           'width': 500,
           'height': 480}
    return mayaPyside.showInMaya(MainWindow, **kws)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec_())
