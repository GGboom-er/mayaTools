# _*_ coding:cp936 _*_
"""
Scripts :    python.tools.gadget.libraryCache
Author  :    JesseChou
Date    :    2022/2/28
QQ      :    375714316
E-Mail  :    JesseChou0612@gmail.com or 375714316@qq.com
"""
import os
import sys

import time
import maya.mel as mel
from PySide2 import QtWidgets, QtCore, QtGui
class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.__currentProject = ''
        self.__currentAssetType = ''
        self.__assetInfos = {}
        self.__assetTW = None
        self.__result = {}
        self.columnCount = 4
        self.createWidgets()
        self.createLayout()
        self.createConnections()
        self.preset()

    @property
    def currentProject(self):
        return self.__currentProject

    @property
    def currentAssetType(self):
        return self.__currentAssetType

    @property
    def assetInfos(self):
        return self.__assetInfos

    @property
    def assetList(self):
        return self.assetInfos.get(self.currentProject, {}).get(self.currentAssetType, {})

    @property
    def assetTW(self):
        # if not self.__assetTW:
        #     self.__assetTW = tableItemPanel.TableItemPanel(self, 4)
        return self.__assetTW

    @property
    def result(self):
        return self.__result

    def createWidgets(self):
        self._projectLB_ = QtWidgets.QLabel(u'项目:')
        self._projectCB_ = QtWidgets.QComboBox()
        self._assetTypeLB_ = QtWidgets.QLabel(u'类型:')
        self._assetTypeCB_ = QtWidgets.QComboBox()
        self._clearInfosPB_ = QtWidgets.QPushButton(u'重置选择信息')
        self._startLibraryPB_ = QtWidgets.QPushButton(u'开始入库测试')
        self._startLibraryPB_.setMinimumHeight(35)

    def createLayout(self):
        self._mainLayout_ = QtWidgets.QVBoxLayout(self)
        projectLay = QtWidgets.QHBoxLayout()
        projectLay.addWidget(self._projectLB_)
        projectLay.addWidget(self._projectCB_)
        projectLay.addWidget(self._assetTypeLB_)
        projectLay.addWidget(self._assetTypeCB_)
        projectLay.addStretch(True)
        projectLay.addWidget(self._clearInfosPB_)

        self._mainLayout_.addLayout(projectLay)
        self._mainLayout_.addWidget(self.assetTW)
        self._mainLayout_.addWidget(self._startLibraryPB_)

    # def createConnections(self):
    #     self._projectCB_.currentTextChanged.connect(self.changeProject)
    #     self._assetTypeCB_.currentTextChanged.connect(self.changeAssetType)
    #     self._startLibraryPB_.clicked.connect(self.startLibrary)
    #     self._clearInfosPB_.clicked.connect(self.resetAssetInfos)

    def preset(self):
        self.refreshProjectCB()

    def refreshProjectCB(self):
        projects = getProjectList()
        project = self._projectCB_.currentText()
        for pro in projects:
            if pro not in self.assetInfos.keys():
                self.__assetInfos[pro] = {}
        self._projectCB_.clear()
        self._projectCB_.addItems(projects)
        if project in projects:
            self._projectCB_.setCurrentText(project)

    def changeProject(self):
        self.__currentProject = self._projectCB_.currentText()
        self.refreshAssetTypeCB()
        setCurrentProject(self.currentProject)

    def refreshAssetTypeCB(self):
        assetTypes = getAssetTypeList(self.currentProject)
        for typ in assetTypes:
            if typ not in self.assetInfos.get(self.currentProject, {}).keys():
                self.__assetInfos[self.currentProject][typ] = {}

        assetType = self._assetTypeCB_.currentText()
        self._assetTypeCB_.clear()
        self._assetTypeCB_.addItems(assetTypes)
        if assetType in assetTypes:
            self._assetTypeCB_.setCurrentText(assetType)

    def changeAssetType(self):
        self.__currentAssetType = self._assetTypeCB_.currentText()
        assets = getAssetList(self.currentProject, self.currentAssetType)
        for asset in assets:
            if asset not in self.assetInfos.get(self.currentProject, {}).get(self.currentAssetType, {}).keys():
                self.__assetInfos[self.currentProject][self.currentAssetType][asset] = False
        self.assetTW.setItemInfos(self.assetList)

    def resetAssetInfos(self):
        infos = {}
        for project, projInfos in self.assetInfos.iteritems():
            infos[project] = {}
            for assetType, typeInfos in projInfos.iteritems():
                infos[project][assetType] = {}
                for asset in typeInfos.keys():
                    infos[project][assetType][asset] = False
        self.__assetInfos = infos
        self.assetTW.setItemInfos(self.assetList)

    def startLibrary(self):
        localTime = time.localtime()
        tim = '%02d%02d%02d' % (localTime.tm_hour, localTime.tm_min, localTime.tm_sec)
        print tim
        # self.__result = batchTestAssetCache(self.assetInfos, tim)
        # if self.result:
        #
        #     logText, renderCmds = analyseLibraryResult(self.result)
        #     logFolder = getWorkFolder(self._projectCB_.currentText(), tim)
        #     with open('%s/result.txt' % logFolder, 'w') as f:
        #         f.write(logText.encode('utf8'))
        #     with open('%s/renderCmd.bat' % logFolder, 'w') as f:
        #         f.write(renderCmds)
        #     directory.openFolder(logFolder)
def getProjectList():
    """
    # 获取所有项目列表
    :return: cgtw中所有的项目列表
    """
    try:
        from ppas_layout_tool.ppstools.cgtw_ import util
        reload(util)
        result = [p.get('project.entity') for p in util.get_project()]
    except Exception as e:
        print(e)
        result = []
    return result

def getAssetList(project, assetType):
    """
    # 根据项目，资产类型获取所有对应的资产列表
    :param project: 项目
    :param assetType: 资产类型
    :return: 对应的资产列表
    """
    try:
        import asset_util
        reload(asset_util)
        result = asset_util.get_asset_dict(project)
        asset_list = [k for k, v in result.items() if v == assetType]
        assets = []
        temps = asset_util.get_asset_step_status(project, asset_list, ['rig', 'lib', 'lgt', 'atp'])
        for key, value in temps.iteritems():
            if value.get('rig') == 'lock' and value.get('lgt') == 'lock' and value.get('lib') != 'lock':
                assets.append(key)
        return assets
    except Exception as e:
        print(e)
    return []

def setCurrentProject(project):
    mel.eval('setProject "X:/Project/%s"' % project)

def getAssetTypeList(project):
    """
    # 获取所有资产类型列表
    :param project: 项目名称
    :return: 该项目下，包含的资产类型
    """
    try:
        import asset_util
        reload(asset_util)
        typeList = list(asset_util.get_asset_type(project))
        for typ in typeList:
            if typ.lower() not in ['chr', 'prp']:
                typeList.remove(typ)
        return typeList
    except Exception as e:
        print(e)
    return []


app = QtWidgets.QApplication(sys.argv)
wnd = MainWindow()
wnd.show()
sys.exit(app.exec_())

# !/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt


class FirstDemoWidget(QWidget):
    def __init__( self, parent=None ):
        super(FirstDemoWidget, self).__init__(parent)
        self.setWindowTitle("pyside2 test")  #
        # self.setWindowIcon(QIcon(r"C:\Users\Admin\Pictures\wnd.jpg")) #
        self.resize(600, 400)  #

        layout = QVBoxLayout()
        layout.addWidget(QLabel("hello", self), alignment=Qt.AlignCenter)  #
        self.setLayout(layout)


app = QApplication(sys.argv)
wnd = FirstDemoWidget()
wnd.show()
sys.exit(app.exec_())