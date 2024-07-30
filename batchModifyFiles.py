# _*_ coding:cp936 _*_
"""
Scripts :    python.tools.generals.batchModifyFiles
Author  :    JesseChou
Date    :    2018年4月18日
QQ      :    375714316
E-Mail  :    JesseChou0612@gmail.com or 375714316@qq.com
"""

import functools
import getpass
import os
import json

from maya import cmds, mel
from python.core import directory, GetPath, xmlDictConvertor, setting
from python.meta import window
from PySide2 import QtWidgets, QtCore, QtGui

MANAGER_LIST = setting.MANAGER_LIST


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle(u'批量处理文件主窗口')
        self.__configInfos = {}
        self.__panelConfig = {}
        self.__configMode = 0
        self.createWidgets()
        self.createLayouts()
        self.createConnections()
        self.preset()

    @property
    def configPath(self):
        return '%sbatchModify.json' % GetPath().pipelineToolkit.config

    @property
    def config(self):
        if not self.__configInfos:
            if os.path.isfile(self.configPath):
                with open(self.configPath, 'r') as f:
                    self.__configInfos = json.load(f)
        return self.__configInfos

    @property
    def isManager(self):
        mode = False
        user = getpass.getuser()
        if user in MANAGER_LIST:
            mode = True
        return mode

    def createWidgets(self):
        self._configListWT_ = QtWidgets.QWidget()
        self._configListLB_ = QtWidgets.QLabel(u'工具配置列表')
        self._configListLB_.setAlignment(QtCore.Qt.AlignCenter)
        self._configListLW_ = QtWidgets.QListWidget()

        self._configSettingWT_ = QtWidgets.QWidget()
        self._configSettingLB_ = QtWidgets.QLabel(u'配置详情')
        self._configSettingLB_.setAlignment(QtCore.Qt.AlignCenter)
        self._configDescriptionPTE_ = QtWidgets.QPlainTextEdit()
        self._modifyModeBG_ = QtWidgets.QButtonGroup()
        self._saveModeRB_ = QtWidgets.QRadioButton(u'保存文件')
        self._saveAsModeRB_ = QtWidgets.QRadioButton(u'另存文件')
        self._saveAsModeRB_.setChecked(True)
        self._nothingModeRB_ = QtWidgets.QRadioButton(u'无操作')
        self._modifyModeBG_.addButton(self._saveModeRB_, 0)
        self._modifyModeBG_.addButton(self._saveAsModeRB_, 1)
        self._modifyModeBG_.addButton(self._nothingModeRB_, 2)
        self._saveFormatCB_ = QtWidgets.QComboBox()
        self._saveFormatCB_.addItems(['ma', 'mb'])
        self._saveSuffixLE_ = QtWidgets.QLineEdit()
        self._fitFormatMaCB_ = QtWidgets.QCheckBox(u'Ma')
        self._fitFormatMbCB_ = QtWidgets.QCheckBox(u'Mb')
        self._fitFormatFbxCB_ = QtWidgets.QCheckBox(u'Fbx')
        self._fitFormatAbcCB_ = QtWidgets.QCheckBox(u'Abc')
        self._basePathLE_ = QtWidgets.QLineEdit()
        self._basePathLE_.setEnabled(False)
        self._basePathPB_ = QtWidgets.QPushButton(u'浏览')
        self._targetPathLE_ = QtWidgets.QLineEdit()
        self._targetPathLE_.setEnabled(False)
        self._targetPathPB_ = QtWidgets.QPushButton(u'浏览')
        self._recursionCB_ = QtWidgets.QCheckBox('')
        self._parametersLE_ = QtWidgets.QLineEdit()
        self._scriptTypeCB_ = QtWidgets.QComboBox()
        self._scriptTypeCB_.addItems(['python', 'mel'])
        self._commandPTE_ = QtWidgets.QPlainTextEdit()
        self._commandPTE_.setWordWrapMode(QtGui.QTextOption.NoWrap)

        self._appendConfigPB_ = QtWidgets.QPushButton(u'增加配置')
        self._editConfigPB_ = QtWidgets.QPushButton(u'编辑配置')
        self._editConfigPB_.setCheckable(True)
        self._removeConfigPB_ = QtWidgets.QPushButton(u'移除配置')

        self._execCurrentPB_ = QtWidgets.QPushButton(u'当前场景执行')
        self._execCurrentPB_.setMinimumHeight(30)
        self._batchExecCommandPB_ = QtWidgets.QPushButton(u'批量处理文件')
        self._batchExecCommandPB_.setMinimumHeight(40)

        self._mainSplitterST_ = QtWidgets.QSplitter()
        self._mainSplitterST_.addWidget(self._configListWT_)
        self._mainSplitterST_.addWidget(self._configSettingWT_)
        self._mainSplitterST_.setSizes([150, 450])
        self._mainSplitterST_.setStretchFactor(0, 0)
        self._mainSplitterST_.setStretchFactor(1, 100)

    def createLayouts(self):
        self._mainLayout_ = QtWidgets.QVBoxLayout(self)

        configListLay = QtWidgets.QVBoxLayout(self._configListWT_)
        configListLay.addWidget(self._configListLB_)
        line1 = QtWidgets.QFrame()
        line1.setFrameShape(QtWidgets.QFrame.HLine)
        line1.setFrameShadow(QtWidgets.QFrame.Sunken)
        configListLay.addWidget(line1)
        configListLay.addWidget(self._configListLW_)

        settingLay = QtWidgets.QVBoxLayout(self._configSettingWT_)
        settingLay.addWidget(self._configSettingLB_)
        line2 = QtWidgets.QFrame()
        line2.setFrameShape(QtWidgets.QFrame.HLine)
        line2.setFrameShadow(QtWidgets.QFrame.Sunken)
        settingLay.addWidget(line2)

        configLay = QtWidgets.QFormLayout()
        configLay.addRow(u'工具描述:', self._configDescriptionPTE_)
        modeLay = QtWidgets.QHBoxLayout()
        modeLay.addWidget(self._saveModeRB_)
        modeLay.addWidget(self._saveAsModeRB_)
        modeLay.addWidget(self._nothingModeRB_)
        configLay.addRow(u'存储模式:', modeLay)

        saveAsLay = QtWidgets.QHBoxLayout()
        saveAsLay.addWidget(self._saveSuffixLE_)
        saveAsLay.addWidget(self._saveFormatCB_)

        configLay.addRow(u'后缀/格式:', saveAsLay)

        fomatLay = QtWidgets.QHBoxLayout()
        fomatLay.addWidget(self._fitFormatMaCB_)
        fomatLay.addWidget(self._fitFormatMbCB_)
        fomatLay.addWidget(self._fitFormatFbxCB_)
        fomatLay.addWidget(self._fitFormatAbcCB_)

        configLay.addRow(u'匹配格式:', fomatLay)

        basePathLay = QtWidgets.QHBoxLayout()
        basePathLay.addWidget(self._basePathLE_)
        basePathLay.addWidget(self._basePathPB_)
        configLay.addRow(u'基础路径:', basePathLay)

        targetPathLay = QtWidgets.QHBoxLayout()
        targetPathLay.addWidget(self._targetPathLE_)
        targetPathLay.addWidget(self._targetPathPB_)
        configLay.addRow(u'目标路径:', targetPathLay)
        configLay.addRow(u'递归目录', self._recursionCB_)
        configLay.addRow(u'命令语言:', self._scriptTypeCB_)
        configLay.addRow(u'执行参数:', self._parametersLE_)
        configLay.addRow(u'执行命令:', self._commandPTE_)

        settingLay.addLayout(configLay)
        if self.isManager:
            buttonLay = QtWidgets.QHBoxLayout()
            buttonLay.addWidget(self._appendConfigPB_)
            buttonLay.addWidget(self._editConfigPB_)
            buttonLay.addWidget(self._removeConfigPB_)
            settingLay.addLayout(buttonLay)
        settingLay.addWidget(self._execCurrentPB_)
        settingLay.addWidget(self._batchExecCommandPB_)

        self._mainLayout_.addWidget(self._mainSplitterST_)

    def createConnections(self):
        self._modifyModeBG_.buttonToggled.connect(self.changeModifyMode)
        self._basePathPB_.clicked.connect(self.browserBasePath)
        self._targetPathPB_.clicked.connect(self.browserTargetPath)
        self._configListLW_.currentItemChanged.connect(self.changeConfigItem)
        self._configListLW_.itemClicked.connect(self.changeConfigItem)
        self._appendConfigPB_.clicked.connect(self.appendConfigDialog)
        self._editConfigPB_.clicked.connect(self.editConfigDialog)
        self._removeConfigPB_.clicked.connect(self.removeConfig)
        self._execCurrentPB_.clicked.connect(self.execCommand)
        self._batchExecCommandPB_.clicked.connect(self.startBatch)

    def preset(self):
        self.refreshConfigList()

    def changeModifyMode(self):
        index = self._modifyModeBG_.checkedId()
        state = False
        if index == 1:
            state = True
        self._saveFormatCB_.setEnabled(state)
        self._saveSuffixLE_.setEnabled(state)

    def browserBasePath(self):
        path = QtWidgets.QFileDialog.getExistingDirectory()
        self._basePathLE_.setText(path)

    def browserTargetPath(self):
        path = QtWidgets.QFileDialog.getExistingDirectory()
        self._targetPathLE_.setText(path)

    def getPanelInfos(self):
        formats = [self._fitFormatMaCB_.isChecked(), self._fitFormatMbCB_.isChecked(),
                   self._fitFormatFbxCB_.isChecked(), self._fitFormatAbcCB_.isChecked()]
        if formats == [False, False, False, False]:
            formats = [True, True, False, False]
        self.__panelConfig = {'description': self._configDescriptionPTE_.toPlainText(),
                              'modifyMode': self._modifyModeBG_.checkedId(),
                              'suffix': self._saveSuffixLE_.text() or '_modify',
                              'format': self._saveFormatCB_.currentText() or 'ma',
                              'formats': formats,
                              'basePath': self._basePathLE_.text(),
                              'targetPath': self._targetPathLE_.text(),
                              'recursion': self._recursionCB_.isChecked(),
                              'code': self._scriptTypeCB_.currentText() or 'python',
                              'parameters': self._parametersLE_.text(),
                              'command': self._commandPTE_.toPlainText()}
        return self.__panelConfig

    def setPanelInfos(self, infos):
        self._configDescriptionPTE_.setPlainText(infos.get('description', ''))
        button = self._modifyModeBG_.button(infos.get('modifyMode', 1))
        button.setChecked(True)
        self._saveSuffixLE_.setText(infos.get('suffix', '_modify'))
        self._saveFormatCB_.setCurrentText(infos.get('format', 'ma'))
        formats = infos.get('formats', [True, True, False, False])
        buttons = [self._fitFormatMaCB_, self._fitFormatMbCB_, self._fitFormatFbxCB_, self._fitFormatAbcCB_]
        for i in range(len(formats)):
            button = buttons[i]
            button.setChecked(formats[i])
        self._basePathLE_.setText(infos.get('basePath', ''))
        self._targetPathLE_.setText(infos.get('targetPath', ''))
        self._recursionCB_.setChecked(infos.get('recursion', False))
        self._scriptTypeCB_.setCurrentText(infos.get('code', 'python'))
        self._parametersLE_.setText(infos.get('parameters', ''))
        self._commandPTE_.setPlainText(infos.get('command'))

    def setPanelEnable(self, infos={}):
        self._configDescriptionPTE_.setEnabled(infos.get('descriptionEnable', True))
        for button in [self._saveModeRB_, self._saveAsModeRB_, self._nothingModeRB_]:
            button.setEnabled(infos.get('modifyModeEnable', True))
        self._saveSuffixLE_.setEnabled(infos.get('suffixEnable', True))
        self._saveFormatCB_.setEnabled(infos.get('formatEnable', True))
        for button in [self._fitFormatMaCB_, self._fitFormatMbCB_, self._fitFormatFbxCB_, self._fitFormatAbcCB_]:
            button.setEnabled(infos.get('formatsEnable', True))
        #self._basePathLE_.setEnabled(infos.get('basePathEnable', True))
        self._basePathPB_.setEnabled(infos.get('basePathEnable', True))
        #self._targetPathLE_.setEnabled(infos.get('targetPathEnable', True))
        self._targetPathPB_.setEnabled(infos.get('targetPathEnable', True))
        self._recursionCB_.setEnabled(infos.get('recursionEnable', True))
        self._scriptTypeCB_.setEnabled(infos.get('codeEnable', True))
        self._parametersLE_.setEnabled(infos.get('parametersEnable', True))
        self._commandPTE_.setEnabled(infos.get('commandEnable', True))

    def refreshConfigList(self, currentItem=None):
        self._configListLW_.clear()
        configs = self.config.keys()
        configs.sort()
        configs.insert(0, 'custom')
        currentRow = 0
        index = 0
        for item in configs:
            configLWI = QtWidgets.QListWidgetItem()
            configLWI.setText(item)
            self._configListLW_.addItem(configLWI)
            if item == currentItem:
                currentRow = index
            index += 1
        self._configListLW_.setCurrentRow(currentRow)

    def changeConfigItem(self):
        config, infos = self.getCurrentConfigInfos()
        self.__configMode = 0
        self.setPanelInfos(infos)
        self.setPanelEnable(infos)
        self._editConfigPB_.setChecked(self.__configMode)

    def getCurrentConfigInfos(self):
        currentItem = self._configListLW_.currentItem()
        config = 'custom'
        infos = {}
        if currentItem:
            config = currentItem.text()
            infos = self.config.get(config, self.getPanelInfos())
        return [config, infos]

    def appendConfigDialog(self):
        # 增加配置信息对话框
        dialog = QtWidgets.QDialog(self)

        def createWidgets():
            self._lockAttributeLB_ = QtWidgets.QLabel(u'属性锁定设置')
            self._lockAttributeLB_.setAlignment(QtCore.Qt.AlignCenter)
            self._descriptionLockCB_ = QtWidgets.QCheckBox(u'描述信息')
            self._modifyModeLockCB_ = QtWidgets.QCheckBox(u'编辑模式')
            self._suffixLockCB_ = QtWidgets.QCheckBox(u'后缀字符')
            self._saveFormatLockCB_ = QtWidgets.QCheckBox(u'保存格式')
            self._fitFormatsLockCB_ = QtWidgets.QCheckBox(u'适配格式')
            self._basePathLockCB_ = QtWidgets.QCheckBox(u'基础路径')
            self._targetPathLockCB_ = QtWidgets.QCheckBox(u'目标路径')
            self._recursionLockCB_ = QtWidgets.QCheckBox(u'递归目录')
            self._scriptTypeLockCB_ = QtWidgets.QCheckBox(u'脚本语言')
            self._parametersLockCB_ = QtWidgets.QCheckBox(u'执行参数')
            self._commandLockCB_ = QtWidgets.QCheckBox(u'执行命令')

            self._configNameLE_ = QtWidgets.QLineEdit()
            if self.__configMode:
                self._configNameLE_.setEnabled(False)
            label = [u'添加配置', u'编辑配置'][self.__configMode]
            self._appendConfigPB_ = QtWidgets.QPushButton(label)

            self._cancelAppendPB_ = QtWidgets.QPushButton(u'取消')

        def createLayout():
            layout = QtWidgets.QVBoxLayout(dialog)
            lockLay = QtWidgets.QGridLayout()
            lockLay.addWidget(self._descriptionLockCB_, 0, 0)
            lockLay.addWidget(self._modifyModeLockCB_, 1, 0)
            lockLay.addWidget(self._suffixLockCB_, 1, 1)
            lockLay.addWidget(self._saveFormatLockCB_, 2, 0)

            lockLay.addWidget(self._fitFormatsLockCB_, 2, 1)
            lockLay.addWidget(self._basePathLockCB_, 3, 0)
            lockLay.addWidget(self._targetPathLockCB_, 3, 1)
            lockLay.addWidget(self._recursionLockCB_, 4, 0)

            lockLay.addWidget(self._scriptTypeLockCB_, 4, 1)
            lockLay.addWidget(self._parametersLockCB_, 5, 0)
            lockLay.addWidget(self._commandLockCB_, 5, 1)

            layout.addWidget(self._lockAttributeLB_)
            line1 = QtWidgets.QFrame()
            line1.setFrameShape(QtWidgets.QFrame.HLine)
            line1.setFrameShadow(QtWidgets.QFrame.Sunken)
            layout.addWidget(line1)
            layout.addLayout(lockLay)

            line2 = QtWidgets.QFrame()
            line2.setFrameShape(QtWidgets.QFrame.HLine)
            line2.setFrameShadow(QtWidgets.QFrame.Sunken)
            layout.addWidget(line2)

            nameLay = QtWidgets.QFormLayout()
            nameLay.addRow(u'配置名称:', self._configNameLE_)

            layout.addLayout(nameLay)
            layout.addWidget(self._appendConfigPB_)
            layout.addWidget(self._cancelAppendPB_)
            return layout

        def createConnections():
            self._appendConfigPB_.clicked.connect(appendConfig)
            self._cancelAppendPB_.clicked.connect(closeDialog)

        def preset():
            config, infos = self.getCurrentConfigInfos()
            self._descriptionLockCB_.setChecked(not infos.get('descriptionEnable', False))
            self._modifyModeLockCB_.setChecked(not infos.get('modifyModeEnable', True))
            self._suffixLockCB_.setChecked(not infos.get('suffixEnable', True))
            self._saveFormatLockCB_.setChecked(not infos.get('formatEnable', True))
            self._fitFormatsLockCB_.setChecked(not infos.get('formatsEnable', True))
            self._basePathLockCB_.setChecked(not infos.get('basePathEnable', True))
            self._targetPathLockCB_.setChecked(not infos.get('targetPathEnable', True))
            self._recursionLockCB_.setChecked(not infos.get('recursionEnable', True))
            self._scriptTypeLockCB_.setChecked(not infos.get('codeEnable', True))
            self._parametersLockCB_.setChecked(not infos.get('parametersEnable', True))
            self._commandLockCB_.setChecked(not infos.get('commandEnable', True))
            if self.__configMode == 1:
                self._configNameLE_.setText(config)

        def closeDialog():
            dialog.deleteLater()

        def getLockInfos():
            infos = {'descriptionEnable': not self._descriptionLockCB_.isChecked(),
                     'modifyModeEnable': not self._modifyModeLockCB_.isChecked(),
                     'suffixEnable': not self._suffixLockCB_.isChecked(),
                     'formatEnable': not self._saveFormatLockCB_.isChecked(),
                     'formatsEnable': not self._fitFormatsLockCB_.isChecked(),
                     'basePathEnable': not self._basePathLockCB_.isChecked(),
                     'targetPathEnable': not self._targetPathLockCB_.isChecked(),
                     'recursionEnable': not self._recursionLockCB_.isChecked(),
                     'codeEnable': not self._scriptTypeLockCB_.isChecked(),
                     'parametersEnable': not self._parametersLockCB_.isChecked(),
                     'commandEnable': not self._commandLockCB_.isChecked()}
            return infos

        def appendConfig():
            name = self._configNameLE_.text()
            if name.lower() != 'custom':
                judge = True
                configList = [x.lower() for x in self.config.keys()]
                if self.__configMode == 0:
                    if name in configList:
                        judge = False
                if judge:
                    infos = self.getPanelInfos()
                    for key, value in getLockInfos().iteritems():
                        infos[key] = value
                    self.__configInfos[name] = infos
                    self.saveConfig()
                    self.__configMode = 0
                    closeDialog()
                    self.refreshConfigList(name)

                else:
                    QtWidgets.QMessageBox.warning(self, u'命名冲突', u'%s 配置名称已经存在，请重新指定一个配置名称！' % name)
            else:
                QtWidgets.QMessageBox.warning(self, u'命名冲突', u'custom 为系统默认命名，无法作为配置名称使用！')

        createWidgets()
        createLayout()
        createConnections()
        preset()
        dialog.exec_()

    def editConfigDialog(self):
        config, infos = self.getCurrentConfigInfos()
        if config.lower() != 'custom':
            if self.__configMode == 0:
                self._editConfigPB_.setChecked(True)
                self.setPanelEnable({})
                self.__configMode = 1
            else:
                self.__configMode = 1
                self.appendConfigDialog()
        self._editConfigPB_.setChecked(self.__configMode)

    def removeConfig(self):
        config, infos = self.getCurrentConfigInfos()
        if config != 'custom':
            judge = QtWidgets.QMessageBox.question(self, u'信息确认', u'您确定要移除选中的配置信息吗？\r\n该操作无法撤销，请谨慎操作！')
            if judge == QtWidgets.QMessageBox.StandardButton.Yes:
                self.__configInfos.pop(config)
                self.saveConfig()
                self.refreshConfigList()
        else:
            QtWidgets.QMessageBox.warning(self, u'信息提示', u'custom 为工具内置配置，无法执行删除操作！')

    def saveConfig(self):
        text = json.dumps(self.config)
        with open(self.configPath, 'w') as f:
            f.write(text)

    def execCommand(self):
        infos = self.getPanelInfos()
        postfix = infos.get('suffix')
        fmt = infos.get('format')
        basePath = infos.get('basePath')
        targetPath = infos.get('targetPath') or basePath
        command = infos.get('command')
        code = infos.get('code')
        parameters = infos.get('parameters')
        judge = execCommand(b=basePath, t=targetPath, c=command, s=code, p=postfix, ef=fmt, parameters=parameters)
        return judge

    def startBatch(self):
        infos = self.getPanelInfos()
        mode = infos.get('modifyMode') + 1
        postfix = infos.get('suffix')
        fmts = infos.get('formats')
        fmt = infos.get('format')
        basePath = infos.get('basePath')
        targetPath = infos.get('targetPath') or basePath
        command = infos.get('command')
        code = infos.get('code')
        recursion = infos.get('recursion')
        parameters = infos.get('parameters')

        formats = []
        fms = ['ma', 'mb', 'fbx', 'abc']
        for i in range(4):
            if fmts[i]:
                formats.append(fms[i])

        if os.path.isdir(basePath):
            if formats:
                infos = batchModify(b=basePath, t=targetPath, c=command, s=code, p=postfix, f=formats, m=mode,
                                    r=recursion, ef=fmt, parameters=parameters)
                print """batchModify(b=%s, t=%s, c=%s, s=%s, p=%s, f=%s, m=%d, r=%s, ef=%s, parameters=%s)""" % (
                    basePath, targetPath, command, code, postfix, formats, mode, recursion, fmt, parameters)
                fo = open('%s\\infos.log' % targetPath, 'w')
                fo.write(str(infos))
                fo.close()
            else:
                QtWidgets.QMessageBox.warning(self, u'文件格式错误', u'请指定要进行批处理的文件格式！')
        else:
            QtWidgets.QMessageBox.warning(self, u'路径错误', u'请指定一个正确的文件路径！')
        return None


class UI(window.Main):
    # 主界面
    def __init__(self, langue=-1):
        self._langue = langue
        self._block = 'batchModifyFiles'
        self.configPath = '%s/batchComand.xml' % GetPath().pipelineToolkit.config
        self._widgets = {'uiWD': {'t': 'Batch Modify Main Window'},
                         'layCL': {},
                         'modeRBG': {'l': 'mode:', 'la': '["save","save as","Nothing"]', 'sl': '1'},
                         'filePathTFBG': {'l': 'File Path:', 'bl': 'Browser'},
                         'targetPathTFBG': {'l': 'Target Path:', 'bl': 'Browser'},
                         'statBatchBT': {'l': 'Start Batch'},
                         'formatsCBG': {'l': 'Fromats:', 'la': '["ma","mb","fbx","abc"]', 'v1': '1', 'v2': '1',
                                        'v3': '0', 'v4': '0'},
                         'postfixTFG': {'l': 'postfix:', 'tx': '_modify', 'en': '0'},
                         'formatTFG': {'l': 'format:', 'tx': '', 'en': '0'},
                         'formatPM': {},
                         'recursionTX': {'l': 'Recursion:'},
                         'recursionCB': {'v': '1'},
                         'appendPresetCL': {},
                         'appendPresetCL': {},
                         'modeEnTX': {'l': 'Lock Mode:'},
                         'modeEnCB': {},
                         'postfixENTX': {'l': 'Lock Postfix:'},
                         'postfixENCB': {},
                         'formatEnTX': {'l': 'Lock Format:'},
                         'formatEnCB': {},
                         'formatsEnTX': {'l': 'Lock Formats:'},
                         'formatsEnCB': {},
                         'baseEnTX': {'l': 'Lock Base Path:'},
                         'baseEnCB': {},
                         'targetEnTX': {'l': 'Lock Target Path:'},
                         'targetEnCB': {},
                         'commandEnTX': {'l': 'Lock Command:'},
                         'commandEnCB': {},
                         'recursionEnTX': {'l': 'Lock Recursion:'},
                         'recursionEnCB': {},
                         'lockTitleTX': {'l': 'Lock Attribute'},
                         'appendBT': {'l': 'Append Preset'},
                         'appendNameTFG': {'l': 'Preset Name:'},
                         'execCommandBT': {'l': 'Exec Command Current'},
                         'commandTX': {'l': 'Command:'},
                         'commandSF': {},
                         'commandBT': {},
                         'commandRCL': {},
                         'appendLabelTFG': {'l': 'Label:'},
                         'toolkitTitleTX': {'l': 'Batch Modify Files Toolkit'},
                         'configListTX': {'l': 'Config List'},
                         'configListTSL': {},
                         'configSettingTX': {'l': 'Config Setting'},
                         'configDescriptionTX': {'l': 'Description:'},
                         'configDescriptionSF': {},
                         'parametersTFG': {'l': 'Parameters:'},
                         'parametersEnTX': {'l': 'Lock Parameters:'},
                         'parametersEnCB': {},
                         'descriptionEnTX': {'l': 'Lock Description:'},
                         'descriptionEnCB': {},
                         'managerRCL': {},
                         'editConfigITCB': {'l': 'Edit Config'},
                         'appendConfigITB': {'l': 'Append Config'},
                         'removeConfigITB': {'l': 'Remove Config'},
                         'cancelBT': {'l': 'Cancel'},
                         '': {}
                         }
        self.basePath = ''
        self.targetPath = ''
        self.baseEnable = True
        self.targetEnable = True
        self.configInfos = {}
        self.currentConfig = {}
        self.editMode = False
        self.currentName = 'custom'
        self.code = 'python'

    # 主布局
    def _layout(self, parentUI):
        if cmds.columnLayout(self.layCL, ex=1):
            cmds.deleteUI(self.layCL)

        self.layCL = cmds.columnLayout(self.layCL, p=parentUI, adj=1)

        cmds.text(self.toolkitTitleTX, l=self.toolkitTitleTX_l, fn='boldLabelFont', h=27)
        cmds.separator(st='in', h=13)

        cmds.paneLayout(cn='vertical2')

        cmds.frameLayout(lv=0)

        cmds.text(self.configListTX, l=self.configListTX_l)
        cmds.separator(st='in', h=8)
        cmds.textScrollList(self.configListTSL, sc=lambda *args: self.changeConfig())

        cmds.setParent('..')

        cmds.frameLayout(lv=0)

        cmds.text(self.configSettingTX, l=self.configSettingTX_l)
        cmds.separator(st='in', h=8)

        cmds.rowColumnLayout(nc=2, cw=[(1, 75), (2, 250)])
        cmds.columnLayout(adj=1)
        cmds.text(self.configDescriptionTX, l=self.configDescriptionTX_l, al='right')
        cmds.setParent('..')
        cmds.scrollField(self.configDescriptionSF, h=75, ww=1)
        cmds.setParent('..')

        cmds.separator(st='in', h=8)

        cmds.radioButtonGrp(self.modeRBG, l=self.modeRBG_l, nrb=3, la3=eval(self.modeRBG_la), cw4=[75, 100, 100, 100],
                            sl=int(self.modeRBG_sl), h=22, cc=lambda *args: self.changeMode())

        cmds.rowColumnLayout(nc=2, cw=[(1, 200), (2, 200)])
        cmds.textFieldGrp(self.postfixTFG, l=self.postfixTFG_l, tx=self.postfixTFG_tx, cw2=[75, 120],
                          en=int(self.postfixTFG_en), cc=lambda *args: self._store())
        cmds.textFieldGrp(self.formatTFG, l=self.formatTFG_l, tx=self.formatTFG_tx, cw2=[75, 120], ed=0,
                          en=int(self.formatTFG_en))
        cmds.popupMenu(self.formatPM, p=self.formatTFG, b=1)
        self.refreshFormatPM()
        cmds.setParent('..')

        cmds.checkBoxGrp(self.formatsCBG, l=self.formatsCBG_l, ncb=4, la4=eval(self.formatsCBG_la),
                         cw5=[75, 75, 75, 75, 75], v1=eval(self.formatsCBG_v1), v2=eval(self.formatsCBG_v2) \
                         , v3=eval(self.formatsCBG_v3), v4=eval(self.formatsCBG_v4), cc=lambda *args: self._store())
        cmds.textFieldButtonGrp(self.filePathTFBG, l=self.filePathTFBG_l, tx=self.basePath, bl=self.filePathTFBG_bl,
                                cw3=[75, 250, 50], ed=0, en=self.baseEnable, \
                                bc=lambda *args: self._browserFolder(self.filePathTFBG, okc='select'))
        cmds.textFieldButtonGrp(self.targetPathTFBG, l=self.targetPathTFBG_l, bl=self.targetPathTFBG_bl,
                                tx=self.targetPath, cw3=[75, 250, 50], ed=0, en=self.targetEnable, \
                                bc=lambda *args: self._browserFolder(self.targetPathTFBG, okc='select'))
        cmds.textFieldGrp(self.parametersTFG, l=self.parametersTFG_l, tx='', cw2=[75, 250])

        cmds.rowColumnLayout(self.commandRCL, nc=3, cw=[(1, 75), (2, 250), (3, 75)])
        cmds.columnLayout(adj=1)
        cmds.text(self.commandTX, l=self.commandTX_l, al='right')
        cmds.setParent('..')
        cmds.scrollField(self.commandSF, h=150)
        cmds.columnLayout(adj=1)
        cmds.button(self.commandBT, l=self.code, en=0, c=lambda *args: self.changeCode())
        cmds.setParent('..')
        cmds.setParent('..')

        cmds.rowColumnLayout(nc=2, cw=[(1, 75), (2, 250)])
        cmds.text(self.recursionTX, l=self.recursionTX_l, al='right')
        cmds.checkBox(self.recursionCB, v=int(self.recursionCB_v), l='')
        cmds.setParent('..')

        cmds.separator(st='in', h=12)

        cmds.rowColumnLayout(self.managerRCL, vis=self.checkManagerMode(), nc=3, cw=[(1, 130), (2, 135), (3, 130)])
        cmds.iconTextCheckBox(self.editConfigITCB, l=self.editConfigITCB_l, st='textOnly', v=self.editMode,
                              onc=lambda *args: self.switchEditMode(0),
                              ofc=lambda *args: self.switchEditMode(1))
        cmds.iconTextButton(self.appendConfigITB, l=self.appendConfigITB_l, st='textOnly',
                            c=lambda *args: self.appendPreset())
        cmds.iconTextButton(self.removeConfigITB, l=self.removeConfigITB_l, st='textOnly', en=False,
                            c=lambda *args: self.removeConfig())
        cmds.setParent('..')

        cmds.button(self.execCommandBT, l=self.execCommandBT_l, h=30, c=lambda *args: self.execCommand())
        cmds.button(self.statBatchBT, l=self.statBatchBT_l, h=35, c=lambda *args: self.startBatch())

        cmds.setParent('..')

        cmds.setParent('..')
        self.refreshConfigList()
        return self.layCL

    # 检查是否为管理员模式
    def checkManagerMode(self):
        mode = False
        user = getpass.getuser()
        if user in MANAGER_LIST:
            mode = True
        return mode

    # 更改执行模式
    def changeMode(self):
        mode = cmds.radioButtonGrp(self.modeRBG, q=1, sl=1)
        cmds.textFieldGrp(self.formatTFG, e=1, en=1 if mode == 2 else 0)
        cmds.textFieldGrp(self.postfixTFG, e=1, en=1 if mode == 2 else 0)
        self._store()
        return None

    # 刷新导出格式PM
    def refreshFormatPM(self):
        PM = self.formatPM
        cmds.popupMenu(PM, e=1, dai=1)
        for f in ['ma', 'mb']:
            cmds.menuItem(l=f, p=PM, c=functools.partial(self.changeFormat, f))
        return None

    # 更改导出格式
    def changeFormat(self, f, *args):
        cmds.textFieldGrp(self.formatTFG, e=1, tx=f)
        return None

    # 更改语言类型
    def changeCode(self):
        if self.code == 'python':
            self.code = 'mel'
        else:
            self.code = 'python'
        cmds.button(self.commandBT, e=1, l=self.code)
        return None

    # 刷新配置列表
    def refreshConfigList(self):
        self.configInfos = self.getConfigInfos()
        keys = self.configInfos.keys()
        keys.sort()
        keys.insert(0, 'custom')
        cmds.textScrollList(self.configListTSL, e=1, ra=1, a=keys)
        if self.currentName in keys:
            cmds.textScrollList(self.configListTSL, e=1, si=self.currentName)
        else:
            cmds.textScrollList(self.configListTSL, e=1, si=keys[0])
        self.changeConfig()
        return None

    # 获取当前配置名称
    def getCurrentConfigName(self):
        self.currentName = cmds.textScrollList(self.configListTSL, q=1, si=1)[0]

    # 更改列表配置
    def changeConfig(self):
        self.editMode = False
        self.getCurrentConfigName()
        self.currentConfig = self.configInfos.get(self.currentName, {})
        self.changePreset()
        return None

    # 获取配置信息
    def getConfigInfos(self):
        infos = {}
        if not os.path.isfile(self.configPath):
            commandValue = {'text': '', 'attrib': {}, 'tag': 'commandList', 'tail': '',
                            'children': []}
            if not os.path.isdir(os.path.dirname(self.configPath)):
                os.makedirs(os.path.dirname(self.configPath))
            xmlDictConvertor.dict2xml(commandValue, self.configPath)

        tmps = xmlDictConvertor.xml2dict(self.configPath)
        for tmp in tmps.get('children', []):
            infos[tmp.get('tag', '')] = tmp.get('attrib', {})
        return infos

    # 更改预置信息
    def changePreset(self, *args):
        editEn = True
        if self.currentName == 'custom':
            editEn = False
        cmds.iconTextCheckBox(self.editConfigITCB, e=1, v=self.editMode, en=editEn)
        cmds.iconTextButton(self.removeConfigITB, e=1, en=editEn)

        mode = self.currentConfig.get('mode')
        if mode not in [None, '-1']:
            cmds.radioButtonGrp(self.modeRBG, e=1, sl=int(mode))

        modeEnable = self.currentConfig.get('modeEnable')
        if modeEnable not in [None, '-1']:
            cmds.radioButtonGrp(self.modeRBG, e=1, en=int(modeEnable))
        else:
            cmds.radioButtonGrp(self.modeRBG, e=1, en=1)

        postfix = self.currentConfig.get('postfix')
        if postfix not in [None, '-1']:
            cmds.textFieldGrp(self.postfixTFG, e=1, tx=postfix)
        postfixEnable = self.currentConfig.get('postfixEnable')
        if postfixEnable not in [None, '-1']:
            cmds.textFieldGrp(self.postfixTFG, e=1, en=int(postfixEnable))
        else:
            cmds.textFieldGrp(self.postfixTFG, e=1, en=1)

        formats = self.currentConfig.get('formats')
        if formats not in [None, '-1']:
            values = eval(formats)
            for i in range(4):
                txt = 'cmds.checkBoxGrp(self.formatsCBG,e = 1,v%d = %d)' % (i + 1, values[i])
                eval(txt)
        formatsEnable = self.currentConfig.get('formatsEnable')
        if formatsEnable not in [None, '-1']:
            cmds.checkBoxGrp(self.formatsCBG, e=1, en=int(formatsEnable))
        else:
            cmds.checkBoxGrp(self.formatsCBG, e=1, en=1)

        basePath = self.currentConfig.get('basePath')
        if basePath not in [None, '-1']:
            cmds.textFieldButtonGrp(self.filePathTFBG, e=1, tx=basePath)
        baseEnable = self.currentConfig.get('baseEnable')
        if baseEnable not in [None, '-1']:
            cmds.textFieldButtonGrp(self.filePathTFBG, e=1, en=int(baseEnable))
        else:
            cmds.textFieldButtonGrp(self.filePathTFBG, e=1, en=1)

        targetPath = self.currentConfig.get('targetPath')
        if targetPath not in [None, '-1']:
            cmds.textFieldButtonGrp(self.targetPathTFBG, e=1, tx=targetPath)
        targetEnable = self.currentConfig.get('targetEnable')
        if targetEnable not in [None, '-1']:
            cmds.textFieldButtonGrp(self.targetPathTFBG, e=1, en=int(targetEnable))
        else:
            cmds.textFieldButtonGrp(self.targetPathTFBG, e=1, en=1)

        command = self.currentConfig.get('command')
        self.code = self.currentConfig.get('code')
        if command not in [None, '-1']:
            cmds.scrollField(self.commandSF, e=1, tx=command)
            cmds.button(self.commandBT, e=1, l=self.code)

        commandEnable = self.currentConfig.get('commandEnable')
        if commandEnable not in [None, '-1']:
            cmds.rowColumnLayout(self.commandRCL, e=1, en=int(commandEnable))
        else:
            cmds.rowColumnLayout(self.commandRCL, e=1, en=1)

        recursion = self.currentConfig.get('recursion')
        if recursion not in [None, '-1']:
            cmds.checkBox(self.recursionCB, e=1, v=int(recursion))
        recursionEnable = self.currentConfig.get('recursionEnable')
        if recursionEnable not in [None, '-1']:
            cmds.checkBox(self.recursionCB, e=1, en=int(recursionEnable))
        else:
            cmds.checkBox(self.recursionCB, e=1, en=1)

        self.changeMode()

        fmat = self.currentConfig.get('format')
        if fmat not in [None, '-1']:
            cmds.textFieldGrp(self.formatTFG, e=1, tx=fmat)

        formatEnable = self.currentConfig.get('formatEnable')
        if formatEnable not in [None, '-1']:
            cmds.textFieldGrp(self.formatTFG, e=1, en=int(formatEnable))
        else:
            cmds.textFieldGrp(self.formatTFG, e=1, en=1)

        desc = self.currentConfig.get('description', self.currentConfig.get('label'))
        if desc not in [None, '-1']:
            cmds.scrollField(self.configDescriptionSF, e=1, tx=desc)

        descEnable = self.currentConfig.get('descriptionEnable')
        if descEnable not in [None, '-1']:
            cmds.scrollField(self.configDescriptionSF, e=1, ed=int(descEnable))
        else:
            cmds.scrollField(self.configDescriptionSF, e=1, ed=1)

        para = self.currentConfig.get('parameters')
        if para not in [None, '-1']:
            cmds.textFieldGrp(self.parametersTFG, e=1, tx=para)

        paraEnable = self.currentConfig.get('parametersEnable')
        if paraEnable not in [None, '-1']:
            cmds.textFieldGrp(self.parametersTFG, e=1, en=int(paraEnable))
        else:
            cmds.textFieldGrp(self.parametersTFG, e=1, en=1)

        return None

    # 清空设置面板
    def clearSettingPanel(self):
        cmds.radioButtonGrp(self.modeRBG, e=1, sl=1, en=1)
        cmds.textFieldGrp(self.postfixTFG, e=1, tx='', en=1)
        cmds.checkBoxGrp(self.formatsCBG, e=1, en=1)
        cmds.textFieldButtonGrp(self.filePathTFBG, e=1, tx='', en=1)
        cmds.textFieldButtonGrp(self.targetPathTFBG, e=1, tx='', en=1)
        cmds.scrollField(self.commandSF, e=1, tx='', en=1)
        cmds.rowColumnLayout(self.commandRCL, e=1, en=1)
        cmds.checkBox(self.recursionCB, e=1, v=0, en=1)
        cmds.textFieldGrp(self.formatTFG, e=1, tx='ma', en=1)
        cmds.scrollField(self.configDescriptionSF, e=1, tx='', en=1)
        return None

    # 解锁设置面板
    def unlockSettingPanel(self):
        cmds.radioButtonGrp(self.modeRBG, e=1, en=1)
        cmds.textFieldGrp(self.postfixTFG, e=1, en=1)
        cmds.checkBoxGrp(self.formatsCBG, e=1, en=1)
        cmds.textFieldButtonGrp(self.filePathTFBG, e=1, en=1)
        cmds.textFieldButtonGrp(self.targetPathTFBG, e=1, en=1)
        cmds.textFieldGrp(self.parametersTFG, e=1, en=1)
        cmds.scrollField(self.commandSF, e=1, en=1)
        cmds.rowColumnLayout(self.commandRCL, e=1, en=1)
        cmds.checkBox(self.recursionCB, e=1, en=1)
        cmds.textFieldGrp(self.formatTFG, e=1, en=1)
        cmds.scrollField(self.configDescriptionSF, e=1, ed=1)
        return None

    # 切换编辑模式
    def switchEditMode(self, mode=0):
        if mode == 0:
            self.editMode = True
            self.unlockSettingPanel()
        if mode == 1:
            infos = self.appendPreset()
            if infos == 'cancel':
                cmds.iconTextCheckBox(self.editConfigITCB, e=1, v=True)
        return None

    # 添加配置信息
    def appendPreset(self):
        result = None
        infos = self.analyseInfos()
        if infos.get('command'):
            result = self.appendDialog()
        else:
            cmds.confirmDialog(m='Please enter the execute code..', t='None Scripts', b=['OK'])
        return result

    # 添加配置窗口
    def appendPresetLay(self, parentUI):
        if cmds.columnLayout(self.appendPresetCL, ex=1):
            cmds.deleteUI(self.appendPresetCL)

        self.appendPresetCL = cmds.columnLayout(self.appendPresetCL, adj=1, p=parentUI, w=320)

        cmds.text(self.lockTitleTX, l=self.lockTitleTX_l, fn='boldLabelFont', h=25)
        cmds.separator(st='in')
        cmds.frameLayout(lv=0)
        cmds.rowColumnLayout(nc=4, cw=[(1, 100), (2, 50), (3, 100), (4, 50)])

        cmds.text(self.modeEnTX, l=self.modeEnTX_l, al='right')
        cmds.checkBox(self.modeEnCB, l='', v=0)

        cmds.text(self.postfixENTX, l=self.postfixENTX_l, al='right')
        cmds.checkBox(self.postfixENCB, l='', v=0)

        cmds.text(l='', h=10)
        cmds.text(l='', h=10)
        cmds.text(l='', h=10)
        cmds.text(l='', h=10)

        cmds.text(self.formatEnTX, l=self.formatEnTX_l, al='right')
        cmds.checkBox(self.formatEnCB, l='', v=0)

        cmds.text(self.formatsEnTX, l=self.formatsEnTX_l, al='right')
        cmds.checkBox(self.formatsEnCB, l='', v=0)

        cmds.text(l='', h=10)
        cmds.text(l='', h=10)
        cmds.text(l='', h=10)
        cmds.text(l='', h=10)

        cmds.text(self.baseEnTX, l=self.baseEnTX_l, al='right')
        cmds.checkBox(self.baseEnCB, l='', v=0)

        cmds.text(self.targetEnTX, l=self.targetEnTX_l, al='right')
        cmds.checkBox(self.targetEnCB, l='', v=0)

        cmds.text(l='', h=10)
        cmds.text(l='', h=10)
        cmds.text(l='', h=10)
        cmds.text(l='', h=10)

        cmds.text(self.commandEnTX, l=self.commandEnTX_l, al='right')
        cmds.checkBox(self.commandEnCB, l='', v=0)

        cmds.text(self.parametersEnTX, l=self.parametersEnTX_l, al='right')
        cmds.checkBox(self.parametersEnCB, l='', v=0)

        cmds.text(l='', h=10)
        cmds.text(l='', h=10)
        cmds.text(l='', h=10)
        cmds.text(l='', h=10)

        cmds.text(self.recursionEnTX, l=self.recursionEnTX_l, al='right')
        cmds.checkBox(self.recursionEnCB, l='', v=0)

        cmds.text(self.descriptionEnTX, l=self.descriptionEnTX_l, al='right')
        cmds.checkBox(self.descriptionEnCB, l='', v=1)

        cmds.setParent('..')
        cmds.setParent('..')
        cmds.separator(st='in')
        cmds.textFieldGrp(self.appendNameTFG, l=self.appendNameTFG_l, tx='', cw2=[100, 150])
        # cmds.textFieldGrp(self.appendLabelTFG,l = self.appendLabelTFG_l,tx = '',cw2 = [100,150])

        cmds.separator(st='in')
        cmds.button(self.appendBT, l=self.appendBT_l, h=33, bgc=[.25, .665, .561],
                    c=lambda *args: self.appendPresetCmd())
        cmds.button(self.cancelBT, l=self.cancelBT_l, h=25, bgc=[.85, .165, .161],
                    c=lambda *args: self.appendPresetCmd(1))
        cmds.setParent('..')

        self.fitConfigLockPanel()

        if cmds.radioButtonGrp(self.modeRBG, q=1, sl=1) == 2:
            cmds.checkBox(self.postfixENCB, e=1, v=0, en=1)
            cmds.checkBox(self.formatEnCB, e=1, v=0, en=1)
        else:
            cmds.checkBox(self.postfixENCB, e=1, v=1, en=0)
            cmds.checkBox(self.formatEnCB, e=1, v=1, en=0)

        return self.appendPresetCL

    # 适配添加信息
    def fitConfigLockPanel(self):
        if self.editMode:
            cmds.checkBox(self.modeEnCB, e=1, v=abs(1 - int(self.currentConfig.get('modeEnable', 1))))
            cmds.checkBox(self.postfixENCB, e=1, v=abs(1 - int(self.currentConfig.get('postfixEnable', 1))))
            cmds.checkBox(self.formatEnCB, e=1, v=abs(1 - int(self.currentConfig.get('formatEnable', 1))))
            cmds.checkBox(self.formatsEnCB, e=1, v=abs(1 - int(self.currentConfig.get('formatsEnable', 1))))
            cmds.checkBox(self.baseEnCB, e=1, v=abs(1 - int(self.currentConfig.get('baseEnable', 1))))
            cmds.checkBox(self.targetEnCB, e=1, v=abs(1 - int(self.currentConfig.get('targetEnable', 1))))
            cmds.checkBox(self.commandEnCB, e=1, v=abs(1 - int(self.currentConfig.get('commandEnable', 1))))
            cmds.checkBox(self.parametersEnCB, e=1, v=abs(1 - int(self.currentConfig.get('parametersEnable', 1))))
            cmds.checkBox(self.recursionEnCB, e=1, v=abs(1 - int(self.currentConfig.get('recursionEnable', 1))))
            cmds.checkBox(self.descriptionEnCB, e=1, v=abs(1 - int(self.currentConfig.get('descriptionEnable', 1))))
            cmds.textFieldGrp(self.appendNameTFG, e=1, tx=self.currentName)
        return None

    # 添加预置对话框
    def appendDialog(self):
        infos = self._dialog(lay=self.appendPresetLay,
                             w=30,
                             h=300,
                             t='Append Preset')
        return infos

    # 添加预置信息执行命令
    def appendPresetCmd(self, mode=0):
        if mode == 0:
            name = cmds.textFieldGrp(self.appendNameTFG, q=1, tx=1).lower()
            judge = 0
            if name:
                if name != 'custom':
                    if self.editMode:
                        judge = 1
                    else:
                        base_inf = xmlDictConvertor.xml2dict(self.configPath)
                        items = xmlDictConvertor.getChildren(base_inf)
                        if name not in items:
                            judge = 1
                        else:
                            con = cmds.confirmDialog(
                                m='The name you entered already exists, do you want to replace it?', t='Exists Name',
                                b=['Cancel', 'OK'])
                            if con == 'OK':
                                judge = 1
                else:
                    cmds.confirmDialog(m='"custom" is built in name. Please choose another name..', t='None Custom',
                                       b=['OK'])
            else:
                cmds.confirmDialog(m='Please enter a valid name..', t='None Name', b=['OK'])

            if judge:
                infos = self.analyseInfos()
                if infos.get('command'):
                    lockInfos = self.getLockInfos()
                    tmps = {}
                    for k, v in infos.iteritems():
                        try:
                            tmps[k] = str(v)
                        except:
                            tmps[k] = v
                    for k, v in lockInfos.iteritems():
                        tmps[k] = str(v)
                    self.currentConfig = tmps
                    self.currentName = name
                    self.appendConfig()
                    cmds.layoutDialog(dis="ok")
                    self.refreshConfigList()
                else:
                    cmds.confirmDialog(m='Please enter the file path and execute the code..', t='None Path Or Scripts',
                                       b=['OK'])
        if mode == 1:
            cmds.layoutDialog(dis="cancel")
        return None

    # 添加配置信息
    def appendConfig(self):
        base_inf = xmlDictConvertor.xml2dict(self.configPath)
        items = xmlDictConvertor.getChildren(base_inf)
        if self.currentName not in items:
            base_inf['children'].append({'tag': self.currentName, 'attrib': self.currentConfig})
        else:
            index = items.index(self.currentName)
            base_inf['children'][index] = {'tag': self.currentName, 'attrib': self.currentConfig}
        xmlDictConvertor.dict2xml(base_inf, self.configPath)

    # 移除配置信息
    def removeConfig(self):
        confirm = cmds.confirmDialog(t='Remove Config',
                                     m='Do you want to remove this configuration? This operation is undoable!',
                                     b=['cancel', 'OK'], db='cancel')
        if confirm == 'OK':
            base_inf = xmlDictConvertor.xml2dict(self.configPath)
            items = xmlDictConvertor.getChildren(base_inf)
            index = items.index(self.currentName)
            base_inf['children'].pop(index)
            xmlDictConvertor.dict2xml(base_inf, self.configPath)
            self.currentName = 'custom'
            self.refreshConfigList()
        return None

    # 获取锁定信息
    def getLockInfos(self):
        modeEn = int(not cmds.checkBox(self.modeEnCB, q=1, v=1))
        postfixEN = int(not cmds.checkBox(self.postfixENCB, q=1, v=1))
        formatEn = int(not cmds.checkBox(self.formatEnCB, q=1, v=1))
        formatsEn = int(not cmds.checkBox(self.formatsEnCB, q=1, v=1))
        baseEn = int(not cmds.checkBox(self.baseEnCB, q=1, v=1))
        targetEn = int(not cmds.checkBox(self.targetEnCB, q=1, v=1))
        commandEn = int(not cmds.checkBox(self.commandEnCB, q=1, v=1))
        recursionEn = int(not cmds.checkBox(self.recursionEnCB, q=1, v=1))
        parametersEn = int(not cmds.checkBox(self.parametersEnCB, q=1, v=1))
        descriptionEn = int(not cmds.checkBox(self.descriptionEnCB, q=1, v=1))

        infos = {'modeEnable': modeEn, 'formatEnable': formatEn, 'postfixEnable': postfixEN, 'formatsEnable': formatsEn,
                 'baseEnable': baseEn, 'targetEnable': targetEn,
                 'commandEnable': commandEn, 'recursionEnable': recursionEn, 'parametersEnable': parametersEn,
                 'descriptionEnable': descriptionEn}
        return infos

    # 获取当前信息
    def analyseInfos(self):
        mode = cmds.radioButtonGrp(self.modeRBG, q=1, sl=1)
        postfix = cmds.textFieldGrp(self.postfixTFG, q=1, tx=1)
        e_format = cmds.textFieldGrp(self.formatTFG, q=1, tx=1)
        formats = []
        for i in range(1, 5):
            formats.append(int(eval('cmds.checkBoxGrp(self.formatsCBG,q = 1,v%d = 1)' % i)))

        basePath = cmds.textFieldButtonGrp(self.filePathTFBG, q=1, tx=1)
        targetPath = cmds.textFieldButtonGrp(self.targetPathTFBG, q=1, tx=1)
        command = cmds.scrollField(self.commandSF, q=1, tx=1)

        recursion = int(cmds.checkBox(self.recursionCB, q=1, v=1))
        description = cmds.scrollField(self.configDescriptionSF, q=1, tx=1)
        parameters = cmds.textFieldGrp(self.parametersTFG, q=1, tx=1)

        return {'mode': mode, 'postfix': postfix, 'format': e_format, 'formats': formats, 'basePath': basePath,
                'targetPath': targetPath, 'command': command, 'code': self.code,
                'recursion': recursion, 'description': description, 'parameters': parameters}

    # 执行命令
    def execCommand(self):
        infos = self.analyseInfos()
        postfix = infos.get('postfix')
        fmt = infos.get('format')
        basePath = infos.get('basePath')
        targetPath = infos.get('targetPath') or basePath
        command = infos.get('command')
        code = infos.get('code')
        parameters = infos.get('parameters')
        judge = execCommand(b=basePath, t=targetPath, c=command, s=code, p=postfix, ef=fmt, parameters=parameters)
        return judge

    # 批量执行
    def startBatch(self):
        infos = self.analyseInfos()
        mode = infos.get('mode')
        postfix = infos.get('postfix')
        fmts = infos.get('formats')
        fmt = infos.get('format')
        basePath = infos.get('basePath')
        targetPath = infos.get('targetPath') or basePath
        command = infos.get('command')
        code = infos.get('code')
        recursion = infos.get('recursion')
        parameters = infos.get('parameters')

        formats = []
        fms = ['ma', 'mb', 'fbx', 'abc']
        for i in range(4):
            if fmts[i]:
                formats.append(fms[i])

        if os.path.isdir(basePath):
            if formats:
                infos = batchModify(b=basePath, t=targetPath, c=command, s=code, p=postfix, f=formats, m=mode,
                                    r=recursion, ef=fmt, parameters=parameters)
                print """batchModify(b=%s, t=%s, c=%s, s=%s, p=%s, f=%s, m=%d,
                                    r=%s, ef=%s, parameters=%s)""" % (
                    basePath, targetPath, command, code, postfix, formats, mode, recursion, fmt, parameters)
                fo = open('%s\\infos.log' % targetPath, 'w')
                fo.write(str(infos))
                fo.close()
            else:
                cmds.confirmDialog(m='Please specify the format of the file to be modified...', b=['OK'],
                                   t='Specify Format')
        else:
            cmds.confirmDialog(m='Please specify a valid file path...', b=['OK'], t='Invalid Path')
        return None


def execCommand(**kwargs):
    """
    # 执行命令
    :param kwargs:
            command/c   执行命令
            style/s     命令语言类型，支持python和mel
            basepath/b  基础路径
            targetpath/t    目标路径
            postfix/p       后缀名
            exportFormat/ef 导出格式
            parameters      执行命令附加命令参数
    :return:
    """
    command = kwargs.get('command', kwargs.get('c', ''))
    style = kwargs.get('style', kwargs.get('s', ''))
    basepath = kwargs.get('basepath', kwargs.get('b', ''))
    targetpath = kwargs.get('targetpath', kwargs.get('t', basepath))
    postfix = kwargs.get('postfix', kwargs.get('p', ''))
    ef = kwargs.get('exportFormat', kwargs.get('ef', ''))
    parameters = kwargs.get('parameters')

    args = {'bm_basepath': basepath, 'bm_targetpath': targetpath, 'bm_postfix': postfix, 'bm_format': ef}

    arg_t = parameters
    for k, v in args.items():
        if style == 'python':
            if arg_t:
                arg_t += ', %s = ' % k
            else:
                arg_t = '%s = ' % k
            if type(v) in [str, unicode]:
                arg_t += '"%s"' % v
            else:
                arg_t += str(v)
        if style == 'mel':
            arg_t += '-%s %s' % (k, v)

    com_txt = command.replace('{BMFArgs}', arg_t)

    print com_txt
    try:
        if style == 'python':
            exec (com_txt)
        if style == 'mel':
            mel.eval(command)
        judge = 1
    except:
        judge = 0
    return judge


def batchModify(**kwargs):
    """
    # 批量修正文件
    :param kwargs:
            basepath/b  基础路径
            targetpath/t    目标路径
            postfix/p       后缀名
            formats/f       文件格式
            mode/m          处理模式
                    1   保存文件
                    2   另存文件
                    3   单独执行命令
            recursion/r 目录递归
            exportFormat/ef 导出格式
    :return:
    """
    # basepath,targetpath,formats,command,style,name,postfix
    basepath = kwargs.get('basepath', kwargs.get('b', ''))
    targetpath = kwargs.get('targetpath', kwargs.get('t', basepath))
    formats = kwargs.get('formats', kwargs.get('f', []))
    postfix = kwargs.get('postfix', kwargs.get('p', ''))
    mode = kwargs.get('mode', kwargs.get('m', 3))
    recursion = kwargs.get('recursion', kwargs.get('r', 1))
    ef = kwargs.get('exportFormat', kwargs.get('ef', ''))

    infos = {'files': {}, 'folders': {}}

    files = directory.listDir(basepath, 4, formats)
    for f in files:
        tmps = {}
        f_p = '%s\\%s' % (basepath, f)
        # b_lst = cmds.ls(assemblies = 1)
        try:
            cmds.file(f_p, o=1, f=1)
            tmps['openFile'] = 1
        except:
            tmps['openFile'] = 0
            pass
        # t_lst = cmds.ls(assemblies = 1)
        # if t_lst != b_lst:

        tmps['execCommand'] = execCommand(**kwargs)

        f_n = '.'.join(f.split('.')[:-1])
        f_s = f.split('.')[-1]

        if mode == 1:
            if f_s.lower() in ['ma', 'mb']:
                cmds.file(s=1, f=1)
                tmps['save'] = 1
            else:
                tmps['save'] = f_s

        if mode == 2:
            t_p = '%s\\%s%s.%s' % (targetpath, f_n, postfix, ef)
            try:
                cmds.file(rn=t_p)
                cmds.file(s=1, type="mayaAscii", op='v=0;')
                tmps['saveAs'] = 1
            except:
                tmps['saveAs'] = 0
        infos['files'][f] = tmps

    if recursion:
        folders = directory.listDir(basepath, 1)
        for folder in folders:
            kwargs['basepath'] = '%s\\%s' % (basepath, folder)
            kwargs['targetpath'] = '%s\\%s' % (targetpath, folder)
            infos['folders'][folder] = batchModify(**kwargs)

    return infos


def showInMaya():
    from python.core import mayaPyside
    return mayaPyside.showInMaya(MainWindow, n='BatchModifyFileMainWindow', t=u'批处理文件主窗口 Ver 2.0.1', w=600, h=700)
