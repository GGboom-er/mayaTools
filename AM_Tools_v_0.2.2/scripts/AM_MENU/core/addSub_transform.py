import sys
import maya.standalone as std
std.initialize(name='python')
import maya.cmds as cmds
import pymel.core as pm
filename = sys.argv[1]
ctl_name = sys.argv[2]
deep = sys.argv[3]




def addSub_transform( filename , ctl_name , deep):
    
    deep = int(deep)
    try:
        cmds.file(filename , open=True,  pmt=False , force=True)

        ctrl = getNode(ctl_name)
        parent = ctrl.getParent(deep)
        child = ctrl.getParent(deep-1)
        name = '%s_space_cons'%ctrl.name()
        _grp = pm.PyNode(pm.createNode("transform", n=name))
        _grp.setTransformation(child.getMatrix(worldSpace=True))

        parent.addChild(_grp)
        _grp.addChild(child)

        cmds.file( save=True , force=True )
    
    except Exception, e:
        sys.stderr.write(str(e))
        sys.exit(-1)





def getNode(nodeName):
    try:
        return pm.PyNode(nodeName)

    except pm.MayaNodeError:
        return None


addSub_transform( filename , ctl_name , deep)