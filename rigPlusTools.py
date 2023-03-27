# _*_ coding:cp936 _*_
"""
Scripts :    python.tools.rigging.rigPlusTools
Author  :    JesseChou
Date    :    2023/1/17 
QQ      :    375714316
E-Mail  :    JesseChou0612@gmail.com or 375714316@qq.com
"""
import copy

from maya import cmds
from PySide2 import QtWidgets, QtCore
from python.tools.rigging import driveBall
import pymel.core as pm
import rig.rigTools as rr
import meshTools.senceInfoFn as ms
import python.meta.rivetConstraint as pmr
reload(ms)
class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.__spinePoints = []
        self.__meshName = None
        self.selList = list()
        self.preset()

    @property
    def spinePoints(self):
        return self.__spinePoints

    def createWidgets(self):
        self._createPlusMeshGB_ = QtWidgets.QGroupBox()
        self._createPlusMeshGB_.setTitle(u'创建附加模型工具')
        self._createPlusMeshGB_.setAlignment(QtCore.Qt.AlignHCenter)
        self._pointsListLW_ = QtWidgets.QListWidget()
        self._closeMeshLB_ = QtWidgets.QLabel(u'模型封口:')
        self._closeMeshCB_ = QtWidgets.QCheckBox()
        self._appendPointPB_ = QtWidgets.QPushButton(u'添加点位')
        self._removePointPB_ = QtWidgets.QPushButton(u'移除点位')
        self._cleanPointsPB_ = QtWidgets.QPushButton(u'清空点位')

        self._createAdditionalMeshPB_ = QtWidgets.QPushButton(u'创建附加模型')
        self._createAdditionalMeshPB_.setMinimumHeight(35)

        self._editMod_ = QtWidgets.QPushButton(u'编辑模型')
        self._editMod_.setMinimumHeight(35)

        self._autoUV_ = QtWidgets.QPushButton(u'铺平UV')
        self._autoUV_.setMinimumHeight(35)

        self._autoSkinWeight_ = QtWidgets.QPushButton(u'骨骼对点权重')
        self._autoSkinWeight_.setMinimumHeight(35)

        # self.Aslider = QtWidgets.QSlider()
        # self.Aslider.setOrientation(QtCore.Qt.Horizontal)
        # self.Aslider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        # self.Aslider.setTickInterval(10)
        # self.Aslider.setMinimum(0)
        # self.Aslider.setMaximum(100)
        self._createRivetConstraintPB_ = QtWidgets.QPushButton(u'铆钉约束')
        self._createRivetConstraintPB_.setMinimumHeight(35)

        self._createDriveBallGB_ = QtWidgets.QGroupBox()
        self._createDriveBallGB_.setTitle(u'创建驱动球工具')
        self._createDriveBallGB_.setAlignment(QtCore.Qt.AlignHCenter)
        self._driveObjLB_ = QtWidgets.QLabel(u'驱动物:')
        self._driveObjLE_ = QtWidgets.QLineEdit()
        self._driveObjPB_ = QtWidgets.QPushButton(u'载入')
        self._parentObjLB_ = QtWidgets.QLabel(u'父物体:')
        self._parentObjLE_ = QtWidgets.QLineEdit()
        self._parentObjPB_ = QtWidgets.QPushButton(u'载入')
        for item in [self._driveObjLE_, self._parentObjLE_]:
            item.setEnabled(False)
        self._createDriveBallPB_ = QtWidgets.QPushButton(u'创建驱动球')
        self._createAdvDriveBallsPB_ = QtWidgets.QPushButton(u'创建ADV驱动球')
        self._createAdvDriveBallsPB_.setMinimumHeight(40)

    def createLayouts(self):
        self._mainLayout_ = QtWidgets.QVBoxLayout(self)

        plusMeshLay = QtWidgets.QVBoxLayout(self._createPlusMeshGB_)
        # plusMeshLay.addWidget(self._createPlusMeshLB_)
        plusMeshLay.addWidget(self._pointsListLW_)
        closeLay = QtWidgets.QHBoxLayout()
        closeLay.addWidget(self._closeMeshLB_)
        closeLay.addWidget(self._closeMeshCB_)
        closeLay.addStretch(True)
        plusMeshLay.addLayout(closeLay)

        modifyLay = QtWidgets.QHBoxLayout()
        modifyLay.addWidget(self._appendPointPB_)
        modifyLay.addWidget(self._removePointPB_)
        modifyLay.addWidget(self._cleanPointsPB_)

        plusMeshLay.addLayout(modifyLay)

        editModLay = QtWidgets.QHBoxLayout()
        editModLay.addWidget(self._createAdditionalMeshPB_)
        editModLay.addWidget(self._editMod_)
        editModLay.addWidget(self._autoUV_)
        editModLay.addWidget(self._autoSkinWeight_)

        plusMeshLay.addLayout(editModLay)
        plusMeshLay.addWidget(self._createRivetConstraintPB_)
        self._mainLayout_.addWidget(self._createPlusMeshGB_)

        driveLayout = QtWidgets.QVBoxLayout(self._createDriveBallGB_)
        baseObjLay = QtWidgets.QHBoxLayout()
        baseObjLay.addWidget(self._driveObjLB_)
        baseObjLay.addWidget(self._driveObjLE_)
        baseObjLay.addWidget(self._driveObjPB_)
        driveLayout.addLayout(baseObjLay)
        parentLay = QtWidgets.QHBoxLayout()
        parentLay.addWidget(self._parentObjLB_)
        parentLay.addWidget(self._parentObjLE_)
        parentLay.addWidget(self._parentObjPB_)
        driveLayout.addLayout(parentLay)
        driveLayout.addWidget(self._createDriveBallPB_)
        driveLayout.addWidget(self._createAdvDriveBallsPB_)
        self._mainLayout_.addWidget(self._createDriveBallGB_)

    def createConnections(self):
        self._appendPointPB_.clicked.connect(self.appendSpine)
        self._removePointPB_.clicked.connect(self.removeSpine)
        self._cleanPointsPB_.clicked.connect(self.clearSpines)
        self._createAdditionalMeshPB_.clicked.connect(self.createSimpleMesh)
        self._driveObjPB_.clicked.connect(self.loadDriveObj)
        self._parentObjPB_.clicked.connect(self.loadParentObj)
        self._createDriveBallPB_.clicked.connect(self.createDriveBall)
        self._createAdvDriveBallsPB_.clicked.connect(self.createAdvDriveBalls)

        self._autoUV_.clicked.connect(self.aotuUV)
        self._autoSkinWeight_.clicked.connect(self.jntToPointWeight)

        self._editMod_.clicked.connect(self.setFollowMod)
        self._createRivetConstraintPB_.clicked.connect(self.createRivetConstraint)
    def preset(self):
        self.createWidgets()
        self.createLayouts()
        self.createConnections()
        self._closeMeshCB_.setChecked(False)
        self._autoSkinWeight_.setEnabled(False)

    def refreshPointList(self):
        # 刷新点位信息
        self._pointsListLW_.clear()
        items = []
        for i in range(len(self.spinePoints)):
            items.append('Spine Point %d' % (i + 1))
        self._pointsListLW_.addItems(items)

    def appendSpine(self):
        # 添加点位
        points,self.sel = getSelectionPoints()

        judge = False
        if len(self.spinePoints) == 0:
            judge = True
        else:
            if len(points) == len(self.spinePoints[0]):
                judge = True
        if judge:
            if points not in self.spinePoints:
                self.__spinePoints.append(points)
                self.refreshPointList()
                self.selList += self.sel
            else:
                QtWidgets.QMessageBox.warning(self, u'点位存在提示',
                                              u'您新添加的点位已经存在\r\n无需重新添加！')
        else:
            QtWidgets.QMessageBox.warning(self, u'点位长度提示',
                                          u'您新添加的点位长度和之前添加的点位长度不同\r\n请重新确认！')

    def removeSpine(self):
        items = self._pointsListLW_.selectedIndexes()
        if items:
            judge = QtWidgets.QMessageBox.question(self, u'移除点位',
                                                   u'您确定要清空所有点位信息吗？\r\n该操作不可撤回，请谨慎选择!')
            if judge == QtWidgets.QMessageBox.StandardButton.Yes:
                row = items[0].row()
                self.__spinePoints.pop(row)
                self.refreshPointList()

    def clearSpines(self):
        judge = QtWidgets.QMessageBox.question(self, u'清空点位',
                                               u'您确定要移除所选点位信息吗？\r\n该操作不可撤回，请谨慎选择!')
        if judge == QtWidgets.QMessageBox.StandardButton.Yes:
            self.__spinePoints = []
            self.selList = list()
            self.__meshName = None
            self._autoSkinWeight_.setEnabled(False)
            self.refreshPointList()

    def createSimpleMesh(self):
        if self.spinePoints :
            selTypeDict = dict()
            for obj in self.selList:
                objType = cmds.nodeType(obj)
                if objType not in selTypeDict.keys():
                    selTypeDict[objType] = []
                selTypeDict[objType].append(obj)
            if selTypeDict.keys() == ['joint']:
                suffix = 'SkinMod'
                self._autoSkinWeight_.setEnabled(True)
            else:
                suffix = 'FollowMod'
                self._autoSkinWeight_.setEnabled(False)
            simpleMesh = SimpleMesh(h=len(self.spinePoints), v=len(self.spinePoints[0]), p=self.spinePoints,
                                    cm=self._closeMeshCB_.isChecked())

            self.__meshName = simpleMesh.createMesh(suffix)
            self.selJoint = self.selList
            #self.selList = list()
            # self.__spinePoints = []
            # self.refreshPointList()
    def loadDriveObj(self):
        sels = cmds.ls(sl=True)
        if sels:
            self._driveObjLE_.setText(sels[0])
        else:
            self._driveObjLE_.setText('')

    def loadParentObj(self):
        sels = cmds.ls(sl=True)
        if sels:
            self._parentObjLE_.setText(sels[0])
        else:
            self._parentObjLE_.setText('')

    def createDriveBall(self):
        baseObj = self._driveObjLE_.text()
        parentObj = self._parentObjLE_.text()
        if baseObj and parentObj:
            driveBall.createDriveBall(baseObj, parentObj, baseObj, driveBall.checkDriveBallSystem())

    def createAdvDriveBalls(self):
        balls = driveBall.AdvDriveBallSystem()
        balls.create()
    def setFollowMod( self ):
        if self.__meshName:
            if cmds.objExists(self.__meshName):
                setFollowMod(self.__meshName)
    def aotuUV( self ):
        if self.__meshName:
            if cmds.objExists(self.__meshName):
                aotuUV(self.__meshName)
    def jntToPointWeight( self ):
        if self.__meshName:
            cmds.DeleteHistory(self.__meshName)
            meshShapeName = cmds.ls(self.__meshName,dag =1,type ='mesh')[0]
            if meshShapeName:
                if cmds.objExists(meshShapeName):
                    try:
                        cmds.select(self.selJoint)
                        jntToPointWeight(meshShapeName, self.selJoint)
                    except Exception as e:
                      print (e)

    def createRivetConstraint( self ):
        if self.__meshName and self.selList:
            pass
        else:
            sels = cmds.ls(sl=1)
            if len(sels) > 1:
                self.__meshName = sels[-1]
                self.selList = sels[:-1]

        selCtrl = [ctrl.replace('IK','IKExt') for ctrl in self.selList if cmds.listRelatives(ctrl,p =1) == [ctrl.replace('IK','IKExt')]]
        print self.__meshName,selCtrl
        if cmds.objExists(self.__meshName) and cmds.ls(self.__meshName, dag=1, type='mesh'):
            createRivetConstraint(model = self.__meshName,ctrlGrp = selCtrl,pivot=0, offset=True)

def getSelectionPoints():
    # 获取所选物体的点位信息
    points = []
    sel = cmds.ls(sl=True)
    for obj in sel:
        point = cmds.xform(obj, q=True, ws=True, t=True)
        points.append(point)


    return points,sel
def jntToPointWeight(objSahpeName,jntList = []):
    skinClusterNode = pm.mel.findRelatedSkinCluster(objSahpeName)
    if not skinClusterNode:
        skinList = copy.deepcopy(jntList)
        skinList.append(objSahpeName)
        skinNode = pm.skinCluster(skinList, tsb=1, sw=1, omi=1, inf=1)
        skinNode.setMaximumInfluences(1)
    rr.jntToPointWeight(objSahpeName,jntList)

def setFollowMod(sel):
    obj, objCom = ms.getMeshComponents(sel, type=0x8000, where=1)
    areaSize = ms.meshSize(obj)
    ExtrudeEdgeNode = ms.autoExtrudeEdge(objCom, areaSize)
    obj, ExobjCom = ms.getMeshComponents(sel, type=0x8000, where=2)

    PolyBevelNode = ms.autoPolyBevel(ExobjCom)

    return ExtrudeEdgeNode,PolyBevelNode
def aotuUV(obj):
    ms.autoUV(obj)
    cmds.delete(obj,ch =1)

def createRivetConstraint(model = '',ctrlGrp = [],pivot=0, offset=True):
    # 创建铆钉约束
    if len(ctrlGrp) > 1:
        mesh = pmr.getModelMesh(model)
        if mesh:
            pmr.createConstraints(model, ctrlGrp, pivot, offset)
            pass
        else:
            cmds.warning('Please select the rivet polygon at last!!!')
    else:
        cmds.warning('Please select at least one object and one polygon model to execute this command!!!')
class SimpleMesh(object):
    def __init__(self, **kwargs):
        self.__horizontal = kwargs.get('horizontal', kwargs.get('h', 2))
        self.__vertical = kwargs.get('vertical', kwargs.get('v', 3))
        self.__positions = kwargs.get('positions', kwargs.get('p', []))
        self.__closeMesh = kwargs.get('closeMesh', kwargs.get('cm', True))
        self.__plane = None

    @property
    def horizontal(self):
        return self.__horizontal

    @property
    def vertical(self):
        return self.__vertical

    @property
    def positions(self):
        if not self.__positions:
            pass
        return self.__positions

    @property
    def closeMesh(self):
        return self.__closeMesh

    @property
    def plane(self):
        return self.__plane

    def createMesh(self,suffix = ''):
        hor = self.horizontal + 1 if self.closeMesh else self.horizontal
        self.__plane = cmds.polyPlane(sx=hor - 1, sy=self.vertical - 1, ax=[0, 0, 1], ch=False, cuv=2,
                                      name='simpleMesh'+'_'+suffix)[0]
        if self.plane:
            for h in range(hor):
                for v in range(self.vertical):
                    if self.closeMesh and h == hor - 1:
                        point = self.positions[0][v]
                    else:
                        point = self.positions[h][v]
                    cmds.xform('%s.vtx[%d]' % (self.plane, h + v * hor), ws=True, t=point)
            if self.closeMesh:
                items = []
                for v in range(self.vertical):
                    items += [v * hor, (v + 1) * hor - 1]
                vertexList = ['%s.vtx[%d]' % (self.plane, x) for x in items]
                cmds.polyMergeVertex(vertexList, d=0.01, am=1, ch=False)
        return self.__plane



def showInMaya():
    from python.core import mayaPyside
    kwargs = {'title': u'绑定附加工具',
              'name': 'RiggingPlusTools',
              'width': 600,
              'height': 400}
    return mayaPyside.showInMaya(MainWindow, **kwargs)


if __name__ == '__main__':
    points = [[[-0.5, 10.0, 0.0], [-0.5, 0.5, 0.0], [-0.5, 0, 0.0]],
              [[0, 1.0, 0.0], [0, 0.5, 0.0], [0, 0, 0.0]],
              [[0.5, 10.0, 0.0], [0.5, 0.5, 0.0], [0.5, 0, 0.0]]]
    self = SimpleMesh(h=2, v=5, p=points)
    self.createMesh()
