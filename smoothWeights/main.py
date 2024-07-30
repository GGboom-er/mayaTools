# -*- coding:utf-8 -*-
import os
from functools import partial
import shiboken2 as sip
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2 import QtUiTools
import pymel.all as pm

context = "smoothWeightsContext1"
file_path = os.path.dirname(__file__) + "/main.ui"
plugin_path = "{0}/plug-ins/maya{1}_win64/plug-ins/smoothWeights.mll".format(os.path.dirname(__file__), pm.about(version=True))


def get_maya_window():
    import maya.OpenMayaUI as mui
    main_window = mui.MQtUtil.mainWindow()
    sip_name = sip.__name__
    return sip.wrapInstance(int(main_window), QWidget)


def setRange(x=0.0, oldmin=0.0, oldmax=1.0, newmin=-1, newmax=1.0):
    if oldmin < oldmax:
        realoldmin = oldmin
        realoldmax = oldmax
        realnewmin = newmin
        realnewmax = newmax
    elif oldmin > oldmax:
        realoldmin = oldmax
        realoldmax = oldmin
        realnewmin = newmax
        realnewmax = newmin
    else:
        return x
    if x < realoldmin:
        result = realnewmin
    elif x > realoldmax:
        result = realnewmax
    else:
        result = (realnewmin + (realnewmax - realnewmin) * (x - oldmin) / (oldmax - oldmin))
    return result


class SmoothWeightsWindow(QMainWindow):
    def __init__(self, parent=get_maya_window()):
        super(SmoothWeightsWindow, self).__init__(parent)
        WINDOW_NAME = 'SmoothSkinToolMainWindow'
        if pm.window(WINDOW_NAME, q=True, ex=True):
            pm.deleteUI(WINDOW_NAME)

        documents_path = os.path.expanduser("~") + "/maya/Settings/SmoothWeightsWindow.ini"
        self.settings = QSettings(documents_path, QSettings.IniFormat)
        if os.path.exists(file_path):
            ui_file = QFile(file_path)
            try:
                ui_file.open(QFile.ReadOnly)
                loader = QtUiTools.QUiLoader()
                self.win = loader.load(ui_file)
            finally:
                ui_file.close()
        else:
            raise ValueError('UI File does not exist on disk at path: {}'.format(file_path))
        self.setObjectName(WINDOW_NAME)
        self.setWindowTitle(WINDOW_NAME)
        self.setCentralWidget(self.win)
        self.win.numSteps.valueChanged.connect(self.numSteps_value_changed)
        self.win.stepSize.valueChanged.connect(self.stepSize_value_changed)
        self.win.volumeAssociationRadius.valueChanged.connect(self.volumeAssociationRadius_value_changed)
        self.win.useVolumeAssociation.stateChanged.connect(self.useVolumeAssociation_cmd)
        self.win.relax_bt.clicked.connect(self.relax_cmd)
        self.win.print_relax_bt.clicked.connect(self.print_relax_cmd)
        self.win.rest_bt.clicked.connect(self.rest_cmd)
        self.win.low_bt.clicked.connect(self.low_cmd)
        self.win.mid_bt.clicked.connect(self.mid_cmd)
        self.win.high_bt.clicked.connect(self.high_cmd)
        if not pm.pluginInfo("smoothWeights", q=True, loaded=True):
            try:
                pm.loadPlugin(plugin_path, quiet=True)
            except:
                pass
        if not pm.contextInfo(context, ex=True):
            pm.mel.eval("smoothWeightsContext")
        self.load_settings()
        self.show()


    def closeEvent(self, event):
        self.save_settings()
        event.accept()

    def load_settings(self):
        self.numSteps = self.settings.value("numSteps", 1)
        self.stepSize = self.settings.value("stepSize", 0.01)
        self.useSoftSelect = self.settings.value("useSoftSelect", False)
        self.nativeSoftSelect = self.settings.value("nativeSoftSelect", False)
        self.softSelectRadius = self.settings.value("softSelectRadius", 1.0)
        self.useVolumeAssociation = self.settings.value("useVolumeAssociation", False)
        self.volumeAssociationRadius = self.settings.value("volumeAssociationRadius", 1.0)
        self.win.numSteps.setValue(int(self.numSteps))
        self.win.stepSize.setValue(float(self.stepSize))
        self.win.useSoftSelect.setChecked(bool(self.useSoftSelect))
        self.win.nativeSoftSelect.setChecked(bool(self.nativeSoftSelect))
        self.win.softSelectRadius.setValue(float(self.softSelectRadius))
        self.win.useVolumeAssociation.setChecked(bool(self.useVolumeAssociation))
        self.win.volumeAssociationRadius.setValue(float(self.volumeAssociationRadius))
        pos = self.settings.value("window_position", None)
        size = self.settings.value("window_size", None)
        if pos is not None and size is not None:
            self.move(pos)
            self.resize(size)

    def save_settings(self):
        self.settings.setValue("numSteps", self.win.numSteps.value())
        self.settings.setValue("stepSize", self.win.stepSize.value())
        self.settings.setValue("useSoftSelect", self.win.useSoftSelect.isChecked())
        self.settings.setValue("nativeSoftSelect", self.win.nativeSoftSelect.isChecked())
        self.settings.setValue("softSelectRadius", self.win.softSelectRadius.value())
        self.settings.setValue("useVolumeAssociation", self.win.useVolumeAssociation.isChecked())
        self.settings.setValue("volumeAssociationRadius", self.win.volumeAssociationRadius.value())
        self.settings.setValue("window_position", self.pos())
        self.settings.setValue("window_size", self.size())

    def relax_cmd(self):
        try:
            args = {'numSteps': self.win.numSteps.value(), 'stepSize': self.win.stepSize.value()}
            if self.win.useSoftSelect.isChecked():
                args['softSelectionRadius'] = self.win.softSelectRadius.value()
            if self.win.nativeSoftSelect.isChecked():
                args['nativeSoftSelection'] = 1;
            if self.win.useVolumeAssociation.isChecked():
                args['abv'] = 1
                args['avr'] = self.win.volumeAssociationRadius.value()
            def makeList(listOrNull):
                if listOrNull is None:
                    return []
                return listOrNull

            objects = makeList(pm.ls(sl=True)) + makeList(pm.ls(hl=True))
            if len(objects) == 0:
                return
            try:
                pm.waitCursor(state=True)
                pm.smoothWeightsCmd(objects, **args)
            finally:
                pm.waitCursor(state=False)
        except:
            pass

    def print_relax_cmd(self):
        # if pm.contextInfo(context, ex=True):
        #     pm.deleteUI(context)
        pm.mel.setToolTo(context)
        # pm.mel.rememberCtxSettings(context)

    def rest_cmd(self):
        self.win.numSteps.setValue(1)

    def low_cmd(self):
        self.win.numSteps.setValue(10)

    def mid_cmd(self):
        self.win.numSteps.setValue(15)

    def high_cmd(self):
        self.win.numSteps.setValue(30)

    def numSteps_value_changed(self, value):
        if value <= 10:
            self.win.stepSize.setValue(0.01)
        else:
            v = setRange(x=value, oldmin=10, oldmax=50, newmin=0.01, newmax=0.3)
            self.win.stepSize.setValue(v)
        if pm.contextInfo(context, ex=True):
            print("numSteps: ", self.win.numSteps.value())
            pm.smoothWeightsContext(context, numSteps=self.win.numSteps.value(), e=1)

    def stepSize_value_changed(self, value):
        if pm.contextInfo(context, ex=True):
            print("stepSize: ", value)
            pm.smoothWeightsContext(context, stepSize=value, e=1)

    def volumeAssociationRadius_value_changed(self, value):
        if self.win.useVolumeAssociation.isChecked() and pm.contextInfo(context, ex=True):
            print("volumeAssociationRadius: ", value)
            pm.smoothWeightsContext(context, associateByVolume=1,
                                    associateByVolumeRadius=self.win.volumeAssociationRadius.value(), e=1)

    def useVolumeAssociation_cmd(self, value):
        if pm.contextInfo(context, ex=True):
            print("useVolumeAssociation: ", value)
            if value:
                pm.smoothWeightsContext(context, associateByVolume=1,
                                        associateByVolumeRadius=self.win.volumeAssociationRadius.value(), e=1)
            else:
                pm.smoothWeightsContext(context, associateByVolume=1, associateByVolumeRadius=0, e=1)


if __name__ == "__main__":
    # import imp
    # import smoothWeights.main as main
    # imp.reload(main)
    # main.SmoothWeightsWindow()
    self = SmoothWeightsWindow()

