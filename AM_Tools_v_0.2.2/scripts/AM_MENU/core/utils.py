import pymel.core as pm
import maya.OpenMayaUI as omui
import maya.cmds as mc


def getNamespace(modelName):
    if not modelName:
        return ""
    if len(modelName.split(":")) >= 2:
        nameSpace = ":".join(modelName.split(":")[:-1])
    else:
        nameSpace = ""
    return nameSpace


def uniqueName(nodeName):
    ctl_name = stripNamespace(nodeName.split("|")[-1])
    listItem = mc.ls(ctl_name)
    if len(listItem) > 1:
        return False
    else:
        return True


def stripNamespace(nodeName):
    return nodeName.split(":")[-1]


def getNode(nodeName):
    try:
        return pm.PyNode(nodeName)
    except pm.MayaNodeError:
        return None


def mayaWinUi():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(main_window_ptr), QtWidgets.QMainWindow)


def getMayaVer():
    version = pm.versions.current()
    return version
    
def getMayaVer2():
    version = pm.about(version = True)
    return version
    
    
    