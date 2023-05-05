# _*_ coding:cp936 _*_
"""
Scripts :    python.tools.rigging.skinToolkit
Author  :    JesseChou
Date    :    2017��3��2��
QQ      :    375714316
E-Mail  :    JesseChou0612@gmail.com or 375714316@qq.com
"""
from maya import cmds, mel
from PySide2 import QtWidgets, QtCore, QtGui
from python.core import GetPath

global VERTEX_WEIGHTS


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle(u'��Ƥ���߰� Ver 2.0.1')
        self.__modifyMode = 0
        self.__transferLabels = [u'ԭʼӰ����', u'Ŀ��Ӱ����']
        self.__transferInfluences = {'source': [], 'target': []}
        self.__successfulTips = True
        self.checkPlugins()
        self.createWidgets()
        self.createMenus()
        self.createLayouts()
        self.createConnections()
        self.__smoothBrush = SmoothWeightsBrush()

    @property
    def iconPath(self):
        return '%sskinToolkit' % GetPath().pipelineToolkit.icons

    @property
    def requirePlugins(self):
        return ['skinWeights.py']

    def checkPlugins(self):
        for plugin in self.requirePlugins:
            require = cmds.pluginInfo(plugin, q=True, l=True)
            if not require:
                try:
                    cmds.loadPlugin(plugin)
                except Exception as e:
                    print(e)

    def getIcon(self, icon):
        return QtGui.QIcon('%s/%s' % (self.iconPath, icon))

    def createWidgets(self):
        # �༭Ȩ������
        self._modifyWeightGB_ = QtWidgets.QGroupBox()
        self._modifyWeightGB_.setTitle(u'Ȩ�ر༭')
        self._modifyWeightGB_.setAlignment(QtCore.Qt.AlignCenter)
        self._resetWeightRB_ = QtWidgets.QRadioButton(u'����')
        self._resetWeightRB_.setChecked(True)
        self._addWeightRB_ = QtWidgets.QRadioButton(u'����')
        self._scaleWeightRB_ = QtWidgets.QRadioButton(u'����')

        self._modifyWeightPB_ = QtWidgets.QPushButton(u'���� Ȩ��')
        self._weightValueDSB_ = QtWidgets.QDoubleSpinBox()
        self._weightValueDSB_.setSingleStep(.025)
        self._weightValueDSB_.setDecimals(4)
        self._weightValueSL_ = QtWidgets.QSlider()
        self._weightValueSL_.setRange(0, 10000)
        self._weightValueSL_.setOrientation(QtCore.Qt.Horizontal)

        self._fastWeightGB_ = QtWidgets.QGroupBox()
        self._fastWeightGB_.setTitle(u'����Ȩ��')
        self._fastWeightGB_.setAlignment(QtCore.Qt.AlignCenter)
        self._weight0PB_ = QtWidgets.QPushButton(u'0')
        self._weight10PB_ = QtWidgets.QPushButton(u'0.1')
        self._weight20PB_ = QtWidgets.QPushButton(u'0.2')
        self._weight30PB_ = QtWidgets.QPushButton(u'0.3')
        self._weight40PB_ = QtWidgets.QPushButton(u'0.4')
        self._weight50PB_ = QtWidgets.QPushButton(u'0.5')
        self._weight60PB_ = QtWidgets.QPushButton(u'0.6')
        self._weight70PB_ = QtWidgets.QPushButton(u'0.7')
        self._weight80PB_ = QtWidgets.QPushButton(u'0.8')
        self._weight90PB_ = QtWidgets.QPushButton(u'0.9')
        self._weight100PB_ = QtWidgets.QPushButton(u'1')

        self._transferWeightGB_ = QtWidgets.QGroupBox()
        self._transferWeightGB_.setTitle(u'����Ȩ��')
        self._transferWeightGB_.setAlignment(QtCore.Qt.AlignCenter)
        self._transferInfluencesTW_ = QtWidgets.QTableWidget()
        self._transferInfluencesTW_.setColumnCount(2)
        self._transferInfluencesTW_.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        horizontalHeader = self._transferInfluencesTW_.horizontalHeader()
        horizontalHeader.setVisible(True)
        horizontalHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        horizontalHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self._transferInfluencesTW_.verticalHeader().setVisible(False)
        self._transferInfluencesTW_.setCornerButtonEnabled(False)
        self._transferInfluencesTW_.setHorizontalHeaderLabels(self.__transferLabels)
        self._transferWeightPB_ = QtWidgets.QPushButton(u'����Ȩ��')
        self._transferWeightPB_.setEnabled(False)

        # Ȩ�ص�����������
        self._storeWeightGB_ = QtWidgets.QGroupBox()
        self._storeWeightGB_.setTitle(u'����/����Ȩ��')
        self._storeWeightGB_.setAlignment(QtCore.Qt.AlignCenter)
        self._exportWeightPB_ = QtWidgets.QPushButton(u'����Ȩ��')
        self._importWeightPB_ = QtWidgets.QPushButton(u'����Ȩ��')
        self._batchExportWeightPB_ = QtWidgets.QPushButton(u'��������Ȩ��')
        self._batchImportWeightPB_ = QtWidgets.QPushButton(u'��������Ȩ��')

        # ���ӹ�������
        self._plusToolkitGB_ = QtWidgets.QGroupBox()
        self._plusToolkitGB_.setTitle(u'���ӹ���')
        self._plusToolkitGB_.setAlignment(QtCore.Qt.AlignCenter)
        self._switchWeightColorPB_ = QtWidgets.QPushButton(u'�л�Ȩ����ɫ')
        self._prueSmallWeightPB_ = QtWidgets.QPushButton(u'���΢Ȩ��')
        self._smoothBrushPB_ = QtWidgets.QPushButton(u'ƽ��Ȩ�ر�ˢ')
        self._skinCopyWeightPB_ = QtWidgets.QPushButton(u'��Ƥ����Ȩ��')
        self._batchSkinCopyPB_ = QtWidgets.QPushButton(u'������Ƥ����')
        self._copyVertexWeightPB_ = QtWidgets.QPushButton(u'������Ȩ��')
        self._pasteVertexWeightPB_ = QtWidgets.QPushButton(u'ճ����Ȩ��')
        self._vertexToTotalPB_ = QtWidgets.QPushButton(u'��Ȩ�ص�����')
        self._switchJointDisplayPB_ = QtWidgets.QPushButton(u'�л���������')

        # Ӱ��������
        self._influencesGB_ = QtWidgets.QGroupBox()
        self._influencesGB_.setTitle(u'Ӱ����')
        self._influencesGB_.setAlignment(QtCore.Qt.AlignCenter)
        self._appendInfluencesPB_ = QtWidgets.QPushButton(u'')
        self._appendInfluencesPB_.setIcon(self.getIcon('append.png'))
        self._appendInfluencesPB_.setToolTip(u'���Ӱ����(Ĭ��Ȩ��)')
        self._appendInfluences0PB_ = QtWidgets.QPushButton(u'')
        self._appendInfluences0PB_.setIcon(self.getIcon('append0.png'))
        self._appendInfluences0PB_.setToolTip(u'���Ӱ����(0Ȩ��)')
        self._removeInfluencesPB_ = QtWidgets.QPushButton(u'')
        self._removeInfluencesPB_.setIcon(self.getIcon('remove.png'))
        self._removeInfluencesPB_.setToolTip(u'�Ƴ�Ӱ����')
        self._selectInfluencesPB_ = QtWidgets.QPushButton(u'')
        self._selectInfluencesPB_.setIcon(self.getIcon('select.png'))
        self._selectInfluencesPB_.setToolTip(u'ѡ��Ӱ����')
        self._findInfluencesPB_ = QtWidgets.QPushButton(u'')
        self._findInfluencesPB_.setIcon(self.getIcon('find.png'))
        self._findInfluencesPB_.setToolTip(u'����Ӱ����')
        self._lockInfluencesPB_ = QtWidgets.QPushButton(u'')
        self._lockInfluencesPB_.setIcon(self.getIcon('lock.png'))
        self._lockInfluencesPB_.setToolTip(u'����Ӱ����Ȩ��')
        self._unlockInfluencesPB_ = QtWidgets.QPushButton(u'')
        self._unlockInfluencesPB_.setIcon(self.getIcon('unlock.png'))
        self._unlockInfluencesPB_.setToolTip(u'����Ӱ����Ȩ��')
        self._influencesTW_ = QtWidgets.QTreeWidget()
        self._influencesTW_.header().setVisible(False)
        self._influencesTW_.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def createLayouts(self):
        self._mainLayout_ = QtWidgets.QHBoxLayout(self)

        weightLayout = QtWidgets.QVBoxLayout()

        # �༭Ȩ�����
        weightLay = QtWidgets.QVBoxLayout(self._modifyWeightGB_)
        modifyModeLay = QtWidgets.QFormLayout()
        modeLay = QtWidgets.QHBoxLayout()
        modeLay.addWidget(self._resetWeightRB_)
        modeLay.addWidget(self._addWeightRB_)
        modeLay.addWidget(self._scaleWeightRB_)
        modifyModeLay.addRow(u'�༭ģʽ', modeLay)
        weightLay.addLayout(modifyModeLay)

        valueLay = QtWidgets.QHBoxLayout()
        valueLay.addWidget(self._modifyWeightPB_)
        valueLay.addWidget(self._weightValueDSB_)
        valueLay.addWidget(self._weightValueSL_)

        weightLay.addLayout(valueLay)
        fastLay = QtWidgets.QGridLayout(self._fastWeightGB_)

        fastLay.addWidget(self._weight10PB_, 0, 0, 1, 2)
        fastLay.addWidget(self._weight20PB_, 0, 2, 1, 2)
        fastLay.addWidget(self._weight30PB_, 0, 4, 1, 2)

        fastLay.addWidget(self._weight40PB_, 1, 0, 1, 2)
        fastLay.addWidget(self._weight50PB_, 1, 2, 1, 2)
        fastLay.addWidget(self._weight60PB_, 1, 4, 1, 2)

        fastLay.addWidget(self._weight70PB_, 2, 0, 1, 2)
        fastLay.addWidget(self._weight80PB_, 2, 2, 1, 2)
        fastLay.addWidget(self._weight90PB_, 2, 4, 1, 2)

        fastLay.addWidget(self._weight0PB_, 3, 0, 1, 3)
        fastLay.addWidget(self._weight100PB_, 3, 3, 1, 3)

        weightLay.addWidget(self._fastWeightGB_)

        # Ȩ�ص����������
        storeLay = QtWidgets.QGridLayout(self._storeWeightGB_)
        storeLay.addWidget(self._exportWeightPB_, 0, 0)
        storeLay.addWidget(self._importWeightPB_, 0, 1)
        storeLay.addWidget(self._batchExportWeightPB_, 1, 0)
        storeLay.addWidget(self._batchImportWeightPB_, 1, 1)

        # ����Ȩ�����
        transferLay = QtWidgets.QVBoxLayout(self._transferWeightGB_)
        transferLay.addWidget(self._transferInfluencesTW_)
        transferLay.addWidget(self._transferWeightPB_)

        # ���ӹ������
        plusLay = QtWidgets.QGridLayout(self._plusToolkitGB_)
        plusLay.addWidget(self._switchWeightColorPB_, 0, 0)
        plusLay.addWidget(self._skinCopyWeightPB_, 0, 1)
        plusLay.addWidget(self._batchSkinCopyPB_, 0, 2)

        plusLay.addWidget(self._prueSmallWeightPB_, 1, 0)
        plusLay.addWidget(self._smoothBrushPB_, 1, 1)
        plusLay.addWidget(self._switchJointDisplayPB_, 1, 2)

        plusLay.addWidget(self._copyVertexWeightPB_, 2, 0)
        plusLay.addWidget(self._pasteVertexWeightPB_, 2, 1)
        plusLay.addWidget(self._vertexToTotalPB_, 2, 2)

        # Ӱ�������
        influencesLay = QtWidgets.QVBoxLayout(self._influencesGB_)
        infToolLay = QtWidgets.QHBoxLayout()

        infToolLay.addWidget(self._findInfluencesPB_)
        infToolLay.addWidget(self._lockInfluencesPB_)
        infToolLay.addWidget(self._unlockInfluencesPB_)
        infToolLay.addWidget(self._appendInfluences0PB_)
        infToolLay.addWidget(self._appendInfluencesPB_)
        infToolLay.addWidget(self._removeInfluencesPB_)
        infToolLay.addWidget(self._selectInfluencesPB_)

        influencesLay.addLayout(infToolLay)
        influencesLay.addWidget(self._influencesTW_)

        weightLayout.addWidget(self._modifyWeightGB_)
        weightLayout.addWidget(self._storeWeightGB_)
        weightLayout.addWidget(self._transferWeightGB_)
        weightLayout.addWidget(self._plusToolkitGB_)

        self._mainLayout_.addLayout(weightLayout)
        self._mainLayout_.addWidget(self._influencesGB_)

    def createMenus(self):
        # ���������˵�
        self._influencesPopMenu_ = QtWidgets.QMenu()
        self._appendInfluencesAC_ = QtWidgets.QAction(u'������', self)
        self._removeInfluencesAC_ = QtWidgets.QAction(u'�Ƴ���ѡ', self)
        self._clearInfluencesAC_ = QtWidgets.QAction(u'���Ӱ����', self)
        self._analyseInfluencesAC_ = QtWidgets.QAction(u'�ı�����', self)
        self._prefixFindSourceAC_ = QtWidgets.QAction(u'ǰ׺��ԭʼ', self)
        self._prefixFindTargetAC_ = QtWidgets.QAction(u'ǰ׺��Ŀ��', self)

        self._influencesPopMenu_.addAction(self._appendInfluencesAC_)
        self._influencesPopMenu_.addAction(self._removeInfluencesAC_)
        self._influencesPopMenu_.addSeparator()
        self._influencesPopMenu_.addAction(self._prefixFindSourceAC_)
        self._influencesPopMenu_.addAction(self._prefixFindTargetAC_)
        self._influencesPopMenu_.addSeparator()
        self._influencesPopMenu_.addAction(self._analyseInfluencesAC_)
        self._influencesPopMenu_.addAction(self._clearInfluencesAC_)

    def influencesMenu(self, point):
        # ��ʾ�����˵�
        self._influencesPopMenu_.exec_(self._transferInfluencesTW_.mapToGlobal(point))

    def createConnections(self):
        self._weightValueSL_.valueChanged.connect(self.changeWeightValueSL)
        self._weightValueDSB_.valueChanged.connect(self.changeWeightValueDSB)
        self._resetWeightRB_.toggled.connect(self.changeModifyMode)
        self._addWeightRB_.toggled.connect(self.changeModifyMode)
        self._scaleWeightRB_.toggled.connect(self.changeModifyMode)

        self._weight0PB_.clicked.connect(self.fastSetWeight)
        self._weight10PB_.clicked.connect(self.fastSetWeight)
        self._weight20PB_.clicked.connect(self.fastSetWeight)
        self._weight30PB_.clicked.connect(self.fastSetWeight)
        self._weight40PB_.clicked.connect(self.fastSetWeight)
        self._weight50PB_.clicked.connect(self.fastSetWeight)
        self._weight60PB_.clicked.connect(self.fastSetWeight)
        self._weight70PB_.clicked.connect(self.fastSetWeight)
        self._weight80PB_.clicked.connect(self.fastSetWeight)
        self._weight90PB_.clicked.connect(self.fastSetWeight)
        self._weight100PB_.clicked.connect(self.fastSetWeight)

        self._modifyWeightPB_.clicked.connect(self.modifyWeight)
        self._exportWeightPB_.clicked.connect(self.exportWeights)
        self._batchExportWeightPB_.clicked.connect(self.batchExport)
        self._importWeightPB_.clicked.connect(self.importWeights)
        self._batchImportWeightPB_.clicked.connect(self.batchImport)
        self._switchWeightColorPB_.clicked.connect(self.switchWeightColor)
        self._prueSmallWeightPB_.clicked.connect(self.pruneWeights)
        self._skinCopyWeightPB_.clicked.connect(self.skinAndCopy)
        self._batchSkinCopyPB_.clicked.connect(self.batchSkinAndCopy)
        self._smoothBrushPB_.clicked.connect(self.smoothWeightsPainter)
        self._switchJointDisplayPB_.clicked.connect(self.switchJointDrawStyle)
        self._copyVertexWeightPB_.clicked.connect(copyVertexWeights)
        self._pasteVertexWeightPB_.clicked.connect(pasteVertexWeights)
        self._vertexToTotalPB_.clicked.connect(copyVertexWeightToAll)

        self._appendInfluencesPB_.clicked.connect(self.appendInfluences)
        self._appendInfluences0PB_.clicked.connect(self.appendInfluences0)
        self._removeInfluencesPB_.clicked.connect(self.removeInfluences)
        self._selectInfluencesPB_.clicked.connect(self.selectInfluences)
        self._findInfluencesPB_.clicked.connect(self.findInfluences)
        self._lockInfluencesPB_.clicked.connect(self.lockInfluences)
        self._unlockInfluencesPB_.clicked.connect(self.unlockInfluences)
        # self._influencesTW_.itemClicked.connect(self.selectInfluencesItems)
        self._influencesTW_.currentItemChanged.connect(self.selectInfluencesItems)
        self._transferInfluencesTW_.customContextMenuRequested.connect(self.influencesMenu)

        self._appendInfluencesAC_.triggered.connect(self.appendTransferInfluences)
        self._removeInfluencesAC_.triggered.connect(self.removeTransferInfluences)
        self._clearInfluencesAC_.triggered.connect(self.clearTransferInfluences)
        self._analyseInfluencesAC_.triggered.connect(self.analyseTransferInfluences)
        self._prefixFindSourceAC_.triggered.connect(self.prefixFindSourceInfluences)
        self._prefixFindTargetAC_.triggered.connect(self.prefixFindTargetInfluences)

    def changeWeightValueDSB(self, *args):
        self._weightValueSL_.setValue(int(self._weightValueDSB_.value() * 10000))

    def changeWeightValueSL(self, *args):
        self._weightValueDSB_.setValue(self._weightValueSL_.value() * 0.0001)

    def changeModifyMode(self, *args):
        if self._resetWeightRB_.isChecked():
            self.__modifyMode = 0
            self._modifyWeightPB_.setText(u'%s Ȩ��' % self._resetWeightRB_.text())
        if self._addWeightRB_.isChecked():
            self.__modifyMode = 1
            self._modifyWeightPB_.setText(u'%s Ȩ��' % self._addWeightRB_.text())
        if self._scaleWeightRB_.isChecked():
            self.__modifyMode = 2
            self._modifyWeightPB_.setText(u'%s Ȩ��' % self._scaleWeightRB_.text())

    def fastSetWeight(self, *args):
        item = self.sender()
        label = item.text()
        print label
        setVertexWeight(float(label), 0)

    def modifyWeight(self, *args):
        weight = self._weightValueDSB_.value()
        setVertexWeight(weight, self.__modifyMode)

    def exportWeights(self, *args):
        # ����Ȩ��
        if cmds.ls(sl=True):
            path = QtWidgets.QFileDialog.getSaveFileName(self, u'ָ���洢�ļ�', '', 'Skin Weight(*.zsw)')
            if path[0]:
                cmds.exportSkinWeights(p=path[0], m=False)
                if self.__successfulTips:
                    QtWidgets.QMessageBox.information(self, u'�����ɹ�', u'��ѡ����Ȩ�ص�����ɣ�')

    def batchExport(self, *args):
        # ��������Ȩ��
        if cmds.ls(sl=True):
            path = QtWidgets.QFileDialog.getSaveFileName(self, u'ָ���洢�ļ�', '', 'Multi Skin Weight(*.msw)')
            if path[0]:
                cmds.exportSkinWeights(p=path[0], m=True)
                if self.__successfulTips:
                    QtWidgets.QMessageBox.information(self, u'�����ɹ�', u'��ѡ����Ȩ������������ɣ�')

    def importWeights(self, *args):
        # ����Ȩ��
        if cmds.ls(sl=True):
            path = QtWidgets.QFileDialog.getOpenFileName(self, u'ָ��Ȩ���ļ�', '', 'Skin Weight(*.zsw)')
            if path[0]:
                judge = cmds.importSkinWeights(p=path[0], m=False)

                if judge == 1 and self.__successfulTips:
                    QtWidgets.QMessageBox.information(self, u'����ɹ�', u'��ѡ����Ȩ�ص�����ɣ�')
                if judge == 2:
                    QtWidgets.QMessageBox.warning(self, u'Ȩ���ļ�����', u'��ָ�����ļ������ɱ����������Ȩ����Ϣ�ļ���')

    def batchImport(self, *args):
        # ��������Ȩ��
        if cmds.ls(sl=True):
            path = QtWidgets.QFileDialog.getOpenFileName(self, u'ָ������Ȩ���ļ�', '', 'Multi Skin Weight(*.msw)')
            if path[0]:
                judge, infos = cmds.importSkinWeights(p=path[0], m=True)
                if judge == 1:
                    infos = eval(infos)
                    if infos:
                        QtWidgets.QMessageBox.warning(self, u'��ʾ��Ϣ', u'��������û��Ȩ����Ϣ\r\n%s' % (str(infos)))
                    else:
                        if self.__successfulTips:
                            QtWidgets.QMessageBox.information(self, u'����ɹ�', u'��ѡ����Ȩ������������ɣ�')
                if judge == 2:
                    QtWidgets.QMessageBox.warning(self, u'Ȩ���ļ�����',
                                                  u'��ָ�����ļ������ɱ��������������Ȩ����Ϣ�ļ���')

    def setOptionVar(self, optionName):
        value, judge = QtWidgets.QInputDialog.getDouble(self, u'ȷ����ֵ', u'��������СȨ��ֵ[0~1]', 0.001, 0, 1, 3)
        if judge:
            cmds.optionVar(fv=[optionName, value])

    def switchWeightColor(self, *args):
        # �л�Ȩ����ʾ
        if not cmds.optionVar(exists='switchSkinColorMinValue'):
            self.setOptionVar('switchSkinColorMinValue')
        value = cmds.optionVar(q='switchSkinColorMinValue')
        switchColor(1, value)

    def pruneWeights(self, *args):
        # ���΢Ȩ��
        if not cmds.optionVar(exists='pruneSkinWeightsMinValue'):
            self.setOptionVar('pruneSkinWeightsMinValue')
        infos = getSelectionInfos()
        value = cmds.optionVar(q='pruneSkinWeightsMinValue')
        pruneWeights(value, infos['obj'], infos['vertexs'])

    def skinAndCopy(self, *args):
        # ��Ƥ������Ȩ��
        sels = cmds.ls(sl=1)
        if len(sels) > 1:
            if getSkinCluster(sels[-1]):
                for sel in sels[:-1]:
                    skinAndCopy(sel, sels[-1])
            else:
                QtWidgets.QMessageBox.warning(self, u'��ʾ��Ϣ', u'�������ѡ������Ƥ����')
        else:
            QtWidgets.QMessageBox.warning(self, u'��ʾ��Ϣ', u'������ѡ���������ϵ�����ִ�в���')

    def batchSkinAndCopy(self, *args):
        # ����ִ��Ȩ�ؿ���
        sels = cmds.ls(sl=1)
        passObjs = []
        if len(sels):
            pre = ''
            tmps = sels[0].split(':')
            if tmps[0]:
                pre = '%s:' % tmps[0]
            prefix, judge = QtWidgets.QInputDialog.getText(self, u'�ռ����²�', u'�ռ���:', QtWidgets.QLineEdit.Normal,
                                                           pre)
            if judge:
                passObjs = batchSkinAndCopy(prefix, sels)
                '''
                for sel in sels:
                    tar = sel.replace(prefix, '')
                    if cmds.objExists(tar):
                        skinAndCopy(sel, tar)
                    else:
                        passObjs.append(sel.replace(prefix, ''))'''
        if passObjs:
            QtWidgets.QMessageBox.information(self, u'��ʾ��Ϣ',
                                              u'��������δ�ҵ���Ӧģ��:\r\n%s' % ('\n'.join(passObjs)))

    def smoothWeightsPainter(self, *args):
        # ƽ��Ȩ�ر�ˢ
        self.__smoothBrush.paint()

    def switchJointDrawStyle(self, *args):
        sels = cmds.ls(sl=1)
        joints = cmds.listRelatives(sels, ad=1, typ='joint') or []
        sels = cmds.ls(sels, type='joint')
        joints += sels
        if joints:
            style = cmds.getAttr('%s.drawStyle' % joints[0])
            if style == 0:
                switchJointDisplay(joints, 0)
            else:
                switchJointDisplay(joints, 1)

    def appendInfluences(self, *args):
        # ����Ӱ���Ĭ��Ȩ�أ�
        sels = cmds.ls(sl=1)
        if len(sels) > 1:
            appendInfluences(sels[0], sels[1:], 0)

    def appendInfluences0(self, *args):
        # ����Ӱ���0Ȩ�أ�
        sels = cmds.ls(sl=1)
        if len(sels) > 1:
            appendInfluences(sels[0], sels[1:], 1)

    def removeInfluences(self, *args):
        # ȥ��Ӱ����
        sels = cmds.ls(sl=1)
        if len(sels) > 1:
            removeInfluences(sels[0], sels[1:])

    def selectInfluences(self, *args):
        # ѡ��Ӱ����
        objs = cmds.ls(sl=1)
        influs = []
        for obj in objs:
            skinCluster = getSkinCluster(obj)
            if skinCluster:
                influs += cmds.skinCluster(skinCluster, q=1, inf=1) or []
        cmds.select(influs, r=1)

    def findInfluences(self, *args):
        sels = cmds.ls(sl=1)
        influences = []
        self._influencesTW_.clear()
        if sels:
            judge = True
            if '.' in sels[0]:
                judge = False
            if judge:
                skinCluster = getSkinCluster(sels[0])
            else:
                skinCluster = getSkinCluster(sels[0].split('.')[0])
            if skinCluster:
                if judge:
                    influences = cmds.skinCluster(skinCluster, q=True, inf=True)
                else:
                    influences = getComponentsInfluences(skinCluster, sels)
        for inf in influences:
            item = QtWidgets.QTreeWidgetItem(self._influencesTW_)
            item.setText(0, inf)

    def selectInfluencesItems(self, *args):
        allItems = []
        for i in range(self._influencesTW_.topLevelItemCount()):
            item = self._influencesTW_.topLevelItem(i)
            allItems.append(item.text(0))
        selectItems = []
        for item in self._influencesTW_.selectedItems():
            selectItems.append(item.text(0))
        cmds.select(allItems, d=1)
        cmds.select(selectItems, add=1)

    def refreshTransferInfluencesList(self):
        sources = self.__transferInfluences.get('source', [])
        targets = self.__transferInfluences.get('target', [])
        self._transferInfluencesTW_.clear()
        self._transferInfluencesTW_.setHorizontalHeaderLabels(self.__transferLabels)
        self._transferInfluencesTW_.setRowCount(len(sources))

        for i in range(len(sources)):
            sourceItem = QtWidgets.QTableWidgetItem()
            sourceItem.setText(sources[i])
            targetItem = QtWidgets.QTableWidgetItem()
            targetItem.setText(targets[i])
            self._transferInfluencesTW_.setItem(i, 0, sourceItem)
            self._transferInfluencesTW_.setItem(i, 1, targetItem)

    def appendTransferInfluences(self, *args):
        # ���Ӱ����
        sels = cmds.ls(sl=1)
        judge = False
        if len(sels):
            if len(sels) % 2 == 0:
                judge = True
        if judge:
            sources = self.__transferInfluences.get('source', [])
            targets = self.__transferInfluences.get('target', [])
            for i in range(len(sels) / 2):
                if sels[i * 2] not in sources + targets:
                    sources.append(sels[i * 2])
                    targets.append(sels[i * 2 + 1])
            self.refreshTransferInfluencesList()
        else:
            QtWidgets.QMessageBox.information(self, u'��ʾ��Ϣ', u'����һһ��Ӧѡ��Ҫ���ݵ�Ӱ���Ȼ����ִ�д�����!')

    def removeTransferInfluences(self, *args):
        # �Ƴ���ѡӰ����
        selectIndexs = self._transferInfluencesTW_.selectedIndexes()
        indexs = []
        for index in selectIndexs:
            row = index.row()
            if row not in indexs:
                indexs.append(row)
        sources = self.__transferInfluences.get('source', [])
        targets = self.__transferInfluences.get('target', [])
        sourceItems = []
        targetItems = []
        for index in indexs:
            if len(sources) > index:
                sourceItems.append(sources[index])
            if len(targets) > index:
                targetItems.append(targets[index])
        for item in sourceItems:
            sources.remove(item)
        for item in targetItems:
            targets.remove(item)
        self.refreshTransferInfluencesList()

    def clearTransferInfluences(self, *args):
        # ��մ���Ȩ�ص�Ӱ�����б�
        self.__transferInfluences = {}
        self.refreshTransferInfluencesList()

    def analyseTransferInfluences(self, *args):
        text, judge = QtWidgets.QInputDialog.getMultiLineText(self, u'ǰ׺��', u'ǰ׺��:')
        if judge:
            infos = analyseTransferInfluences(text)
            if infos:
                self.mergeTransferInfluences(infos)
                self.refreshTransferInfluencesList()

    def prefixFindSourceInfluences(self, *args):
        infos = self.getPrefixItems()
        if infos:
            self.mergeTransferInfluences({k: v for v, k in infos.items()})
            self.refreshTransferInfluencesList()

    def prefixFindTargetInfluences(self, *args):
        infos = self.getPrefixItems()
        if infos:
            self.mergeTransferInfluences(infos)
            self.refreshTransferInfluencesList()

    def getPrefixItems(self):
        infos = {}
        sels = cmds.ls(sl=1)
        if sels:
            prefix, judge = QtWidgets.QInputDialog.getText(self, u'ǰ׺��', u'ǰ׺��:', QtWidgets.QLineEdit.Normal)
            if judge:
                infos = prefixFindItems(prefix, sels)
                if not infos:
                    QtWidgets.QMessageBox.information(self, u'��ʾ��Ϣ', u'û���ҵ���Ӧ��Ӱ����!')
        return infos

    def mergeTransferInfluences(self, infos):
        sources = self.__transferInfluences.get('source', [])
        targets = self.__transferInfluences.get('target', [])
        for key in infos.keys():
            if key not in sources + targets:
                sources.append(key)
                targets.append(infos[key])
        self.__transferInfluences = {'source': sources, 'target': targets}

    def lockInfluences(self, *args):
        sels = cmds.ls(sl=1)
        lockInfluences(sels, 1)

    def unlockInfluences(self, *args):
        sels = cmds.ls(sl=1)
        lockInfluences(sels, 0)


class SmoothWeightsBrush(object):
    def __init__(self):
        self.command = """
            global string $smoothSkinWeightsBrushSel[];
            global proc smoothSkinWeightsBrush(string $context) {
                artUserPaintCtx -e -ic "init_smoothSkinWeightsBrush" -svc "set_smoothSkinWeightsBrush" -fc "" -gvc "" -gsc "" -gac "" -tcc "" $context;
            }
            global proc init_smoothSkinWeightsBrush(string $name) {
                global string $smoothSkinWeightsBrushSel[];
                $smoothSkinWeightsBrushSel = {};
                string $sel[] = `ls -sl -fl`;
                string $obj[] = `ls -sl -o`;
                $objName = $obj[0];
                int $i = 0;
                for($vtx in $sel) {
                    string $buffer[];
                    int $number = `tokenize $vtx ".[]" $buffer`;
                    $smoothSkinWeightsBrushSel[$i] = $buffer[2];
                    $i++;
                    if ($number != 0)
                    $objName = $buffer[0];
                }  
            }
            global proc set_smoothSkinWeightsBrush(int $slot, int $index, float $val) {
                global string $smoothSkinWeightsBrushSel[];
                if($smoothSkinWeightsBrushSel[0] != "") {
                    if(!stringArrayContains($index, $smoothSkinWeightsBrushSel))
                        return; 
                }
                smoothSkinWeights -i $index -v $val;     
            }
            """
        mel.eval(self.command)

    def paint(self):
        cmds.ScriptPaintTool()
        cmds.artUserPaintCtx(cmds.currentCtx(), e=1, tsc='smoothSkinWeightsBrush')


def getSelectionInfos(sels=None):
    # ��ȡ��ѡ��Ϣ
    if not sels:
        sels = cmds.ls(sl=1, fl=1)
    if sels:
        obj = None
        vertexs = []
        infs = []
        if len(sels) > 1:
            for sel in sels:
                if '.vtx[' in sel:
                    tmps = sel.split('.vtx[')
                    if not obj:
                        obj = tmps[0]
                    vertexs.append(int(tmps[1][:-1]))
                else:
                    infs.append(sel)
        if len(sels) == 1:
            obj = sels[0]
        return {'obj': obj, 'vertexs': vertexs, 'influences': infs}
    else:
        return


def getSkinCluster(obj):
    # ��ȡָ�������skincluster
    skinClusters = cmds.ls(cmds.listHistory(obj, f=0, pdo=1), type='skinCluster')
    skinCluster = skinClusters[0] if skinClusters else None
    return skinCluster


def copyVertexWeights():
    # ������Ȩ��
    global VERTEX_WEIGHTS
    sels = cmds.ls(sl=1, fl=1)
    if sels:
        skinCluster = getSkinCluster(sels[0].split('.')[0])
        if skinCluster:
            influences = cmds.skinCluster(skinCluster, q=1, inf=1)
            values = cmds.skinPercent(skinCluster, q=1, v=1)
            VERTEX_WEIGHTS = {'influences': influences, 'weights': values}
        else:
            VERTEX_WEIGHTS = None
    else:
        VERTEX_WEIGHTS = None


def pasteVertexWeights():
    # ճ����Ȩ��
    global VERTEX_WEIGHTS
    sels = cmds.ls(sl=1)
    if VERTEX_WEIGHTS and sels:
        skinCluster = getSkinCluster(sels[0].split('.')[0])
        if skinCluster:
            baseInfs = VERTEX_WEIGHTS['influences']
            weights = VERTEX_WEIGHTS['weights']
            influences = cmds.skinCluster(skinCluster, q=1, inf=1)
            infs = [x for x in VERTEX_WEIGHTS['influences'] if x not in influences]
            if infs:
                cmds.skinCluster(skinCluster, e=1, ai=infs, wt=0)
            cmds.skinPercent(skinCluster, sels, tv=[[baseInfs[i], weights[i]] for i in range(len(baseInfs))])
        cmds.select(sels, r=1)


def copyVertexWeightToAll():
    # ������Ȩ�ص���������
    sels = cmds.ls(sl=1, fl=1)
    if sels:
        copyVertexWeights()
        vtx = sels[0]
        cmds.select('%s.vtx[*]' % vtx.split('.')[0], r=1)
        pasteVertexWeights()


def copyVertexAround():
    # ������ѡ�����ĵ�Ȩ�ص���ѡ�ı�
    infos = getCenterVertex()
    centers = infos.get('center')
    if centers:
        cmds.select(centers, r=1)
        copyVertexWeights()
        cmds.select(infos.get('bound', []), r=1)
        pasteVertexWeights()


def getCenterVertex():
    # ��ȡ��ѡ�ߵ����ĵ�
    edges = cmds.ls(sl=1, fl=1)
    cmds.ConvertSelectionToVertices()
    vertexs = cmds.ls(sl=1, fl=1)
    centerVers = None
    for edge in edges:
        cmds.select(edge, r=1)
        cmds.ConvertSelectionToVertices()
        vers = cmds.ls(sl=1, fl=1)
        if not centerVers:
            centerVers = vers
        else:
            centerVers = [x for x in centerVers if x in vers]
    cmds.select(edges, r=1)
    return {'center': centerVers, 'bound': [x for x in vertexs if x not in centerVers]}


def appendInfluences(obj, influences, mode=0, style=0):
    """
    ���Ӱ����
    :param obj: Ҫ���Ӱ���������
    :param influences: Ҫ��ӵ�Ӱ����
    :param mode: ���ģʽ
                0 => Ĭ��Ȩ��ֵ
                1 => ����Ȩ��ֵΪ0
    :param style: ��ӷ�ʽ
                0 => ���ģʽ
                1 => �滻ģʽ
    """
    skinCluster = getSkinCluster(obj)
    if not skinCluster:
        skinCluster = cmds.skinCluster(influences, obj, dr=4, bm=0, sm=0, nw=1, wd=0, tsb=1)[0]
    else:
        baseInfs = cmds.skinCluster(skinCluster, q=1, inf=1)
        influences = [inf for inf in influences if inf not in baseInfs]
        if mode:
            cmds.skinCluster(skinCluster, e=1, ai=influences, wt=0)
        else:
            cmds.skinCluster(skinCluster, e=1, ai=influences)
        if style:
            infs = [inf for inf in baseInfs if inf not in influences]
            cmds.skinCluster(skinCluster, e=1, ri=infs)
    return skinCluster


def removeInfluences(obj, influences):
    """
    ���Ӱ����
    :param obj: Ҫ�Ƴ�Ӱ���������
    :param influences: Ҫ�Ƴ���Ӱ����
    """
    skinCluster = getSkinCluster(obj)
    cmds.skinCluster(skinCluster, e=1, ri=influences)


def lockInfluences(influences, mode=0):
    """
    ����Ӱ����Ȩ��
    :param influences: Ҫ������Ӱ����
   :param  mode: ����ģʽ
            0 => ����
            1 => ����
    """
    for inf in influences:
        attr = '%s.liw' % inf
        if cmds.objExists(attr):
            cmds.setAttr(attr, mode)


def setSkinWeights(obj, vertexs, influences, weight, mode):
    """
    ������ƤȨ��ֵ
    :param obj: ��Ҫ����Ȩ�ص�����
    :param vertexs: ��Ҫ����Ȩ�صĵ�����
    :param influences: ��Ҫ����Ȩ�ص�Ӱ����
    :param weight: Ҫ���õ�Ȩ��ֵ
    :param mode: ����ģʽ, 0 => �滻, 1 => ����, 2 => ����
    """
    skinCluster = getSkinCluster(obj)
    appendInfluences(obj, influences, 1)
    if cmds.getAttr('%s.normalizeWeights' % skinCluster) == 1:
        if weight * len(influences) > 1:
            cmds.error('�������Ȩ��ֵ�����뽵��Ȩ��ֵ��Ȩ�������޸�Ϊ post!!!')
    for index in vertexs:
        if mode == 0:
            cmds.skinPercent(skinCluster, '%s.vtx[%d]' % (obj, index), tv=[[inf, weight] for inf in influences])
        if mode == 1:
            cmds.skinPercent(skinCluster, '%s.vtx[%d]' % (obj, index), r=1, tv=[[inf, weight] for inf in influences])
        if mode == 2:
            cmds.skinPercent(skinCluster, '%s.vtx[%d]' % (obj, index), r=1, tv=[[inf, -weight] for inf in influences])


def setVertexWeight(weight, mode):
    # Ϊ��ѡ������Ȩ��
    infos = getSelectionInfos()
    if infos:
        setSkinWeights(infos['obj'], infos['vertexs'], infos['influences'], weight, mode)


def switchColor(value1=1, value2=0.001):
    if cmds.artAttrSkinPaintCtx('artAttrSkinContext', q=1, colorrangeupper=1) != value1:
        cmds.artAttrSkinPaintCtx('artAttrSkinContext', e=1, colorrangeupper=value1)
    else:
        cmds.artAttrSkinPaintCtx('artAttrSkinContext', e=1, colorrangeupper=value2)


def pruneWeights(value, obj, vertexs=[]):
    """
    ȥ������ָ����ֵ��Ȩ����Ϣ
    :param obj: ��Ҫ����Ȩ�ص�����
    :param vertexs: ��Ҫ����Ȩ�صĵ�����,Ĭ��Ϊȫ����
    :param value: Ȩ���ٽ�ֵ�����ڸ���ֵ��Ȩ�ػᱻ�����
    """
    skinCluster = getSkinCluster(obj)
    if skinCluster:
        if not vertexs:
            vertexs = range(cmds.getAttr('%s.vrts' % obj, s=1))
        cmds.skinPercent(skinCluster, ['%s.vtx[%d]' % (obj, i) for i in vertexs], prw=value)


def skinAndCopy(base, target):
    """
    ��Ƥ������Ȩ��
    :param base:����Ȩ�صĻ�������
    :param target:����Ȩ�ص�Ŀ������
    """
    skinCluster = getSkinCluster(target)
    if skinCluster:
        influences = cmds.skinCluster(skinCluster, q=1, inf=1) or []
        if getSkinCluster(base):
            appendInfluences(base, influences, 0)
        else:
            cmds.skinCluster(influences, base, dr=4, bm=0, sm=0, nw=1, wd=0, tsb=1)
        cmds.copySkinWeights(target, base, nm=1, sa='closestPoint', ia='closestJoint')
        # removeUnusedInfluences(skin.getSkinCluster(base))
    else:
        cmds.warning(u'��ָ��һ����Ƥ������Ϊ����Ȩ��Ŀ����!')


def batchSkinAndCopy(prefix, objects=[], log=False):
    """
    ������Ƥ������Ȩ��
    :param log:
    :param prefix: ģ��ǰ׺��
    :param objects: ��Ҫ����Ȩ�ص������б�
    :return:
    """
    passObjs = []
    if not objects:
        temps = cmds.listRelatives(cmds.ls('%s*' % prefix, type='mesh'), p=True)
        objects = list(set(temps))

    for sel in objects:
        tar = sel.replace(prefix, '')
        if log:
            print ('=====>copy skin weight from %s to %s\r\n' % (tar, sel))
        if cmds.objExists(tar):
            skinAndCopy(sel, tar)
        else:
            passObjs.append(sel.replace(prefix, ''))
    return passObjs


def removeUnusedInfluences(skinCluster):
    """
    �Ƴ�����Ӱ����д�����
    :param skinCluster: ��Ҫ�Ƴ�����Ӱ�����skincluster
    :return:
    """
    influs = cmds.skinCluster(skinCluster, q=1, inf=1)
    wtinfs = cmds.skinCluster(skinCluster, q=1, wi=1)
    state = cmds.getAttr('%s.nodeState' % skinCluster)
    cmds.setAttr('%s.nodeState' % skinCluster, 1)
    for inf in influs:
        if inf in wtinfs:
            cmds.skinCluster(skinCluster, e=1, ri=inf)
    cmds.setAttr('%s.nodeState' % skinCluster, state)


def switchJointDisplay(joints, state=False):
    """
    �л���ѡ����Ĺ�����ʾ
    :param joints: ��Ҫ�л��Ĺ����б�
    :param state: ��ʾ״̬
    :return:
    """
    for joint in joints:
        if cmds.nodeType(joint) == 'joint':
            try:
                cmds.setAttr('%s.drawStyle' % joint, 0 if state else 2)
            except:
                pass


def getComponentsInfluences(skinCluster, vertexs):
    """
    ��ȡ���Ӱ����
    :param skinCluster: ��Ҫ��ȡӰ�����skincluster
    :param vertexs: ��Ҫ��ȡӰ����ĵ�����
    :return:
    """
    # python �汾���޷���ȡ���Ӱ�������ֻ�ܸ���mel��ִ��
    # influences = mel.eval('skinPercent -q -t %s %s' % (skinCluster, ' '.join(vertexs)))
    influences = cmds.skinPercent(skinCluster, vertexs, q=True, t=None)
    return influences


def analyseTransferInfluences(text):
    """
    # ͨ�������ı�����ȡӰ���������Ϣ
    :param text: Ӱ��������ı�
    :return: Ӱ��������ֵ�
    """
    infos = {}
    temps = text.split('\n')
    for temp in temps:
        temps = temp.strip().split('\t')
        if len(temps) == 2:
            key = temps[0].strip()
            value = temps[1].strip()
            if key not in infos.keys():
                if key not in infos.values():
                    infos[key] = value
    return infos


def prefixFindItems(prefix, items=[]):
    """
    # ����ǰ׺����
    :param prefix: ǰ׺��
    :param items: ���������б�
    :return: ƥ���ֵ�
    """
    infos = {}
    if not items:
        items = cmds.ls(sl=1)
    for item in items:
        preItem = '%s%s' % (prefix, item)
        if cmds.objExists(preItem):
            infos[item] = preItem
    return infos


def showInMaya():
    from python.core import mayaPyside
    return mayaPyside.showInMaya(MainWindow, n='SkinToolkitMainWindow', t=u'��Ƥ���߰� Ver 2.0.0')
