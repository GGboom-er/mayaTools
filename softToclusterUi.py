"""
    PS:crate lights ctrl,you can select color and delete light.
    Bottom slide bar the joint size can be controlled.
    2020.7.14
    by:GGboomer
"""


from PySide2 import QtWidgets, QtCore
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import maya.cmds as mc
import maya.OpenMaya as om
import string

def getMayaMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def softSelToCluster(selectionList = []):
    selection = selectionList
    # Strip selection of any attributes
    sel = string.split(selection[0], '.')
    richSel = om.MRichSelection()
    om.MGlobal.getRichSelection(richSel)

    richSelList = om.MSelectionList()
    richSel.getSelection(richSelList)

    path = om.MDagPath()
    component = om.MObject()
    # new a cluster
    clusterNode = mc.cluster(rel=True)
    clusterSet = mc.listConnections(clusterNode, type="objectSet")

    for idx in range(richSelList.length()):
        richSelList.getDagPath(idx, path, component)
        if component.apiType() == om.MFn.kMeshVertComponent:
            componentFn = om.MFnSingleIndexedComponent(component)
            mc.select(selection, r=True)
            for i in range(0, componentFn.elementCount()):
                weight = componentFn.weight(i)
                v = componentFn.element(i)
                w = weight.influence()
                # print "The selection weight of vertex %d is %f." % (v, w)
                vtx = (path.fullPathName() + '.vtx[%d]') % v
                mc.sets(vtx, add=clusterSet[0])
                mc.percent(clusterNode[0], vtx, v=w)

        elif component.apiType() == om.MFn.kSurfaceCVComponent:
            componentFn = om.MFnDoubleIndexedComponent(component)
            mc.select(selection, r=True)
            uArray = om.MIntArray()
            vArray = om.MIntArray()
            componentFn.getElements(uArray, vArray)
            for i in range(0, componentFn.elementCount()):
                weight = componentFn.weight(i)
                w = weight.influence()
                # print "The selection weight of vertex %d is %f." % (v, w)
                vtx = (path.fullPathName() + '.cv[%d][%d]') % (uArray[i], vArray[i])
                mc.sets(vtx, add=clusterSet[0])
                mc.percent(clusterNode[0], vtx, v=w)
    mc.select(clusterNode)
class windowUi(QtWidgets.QDialog):
    """docstring for lightUi"""

    def __init__(self, parent=getMayaMainWindow()):
        super(windowUi, self).__init__(parent)
        self.setWindowTitle('windowUi')
        self.resize(250, 80)
        self.bulidUI()
    def bulidUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        createBtn = QtWidgets.QPushButton('soft To cluster')
        createBtn.clicked.connect(self.DoMake)
        self.layout.addWidget(createBtn)

    def DoMake( self ):
        sel = mc.ls(sl =1)
        if sel:
            softSelToCluster(sel)
if __name__ == '__main__':
    try:
        win.close()
        win.deleteLater()
    except:
        pass
    win = windowUi()
    win.show()
