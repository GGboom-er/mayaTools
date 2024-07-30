import pymel.core as pm
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as omAnim
import maya.cmds as mc
class Utils:
    @staticmethod
    def undoable( function ):
        '''
        function decorator, makes function contents undoable in one go
        '''

        @wraps(function)
        def result( *args, **kargs ):
            mc.undoInfo(openChunk=True)
            try:
                return function(*args, **kargs)
            finally:
                mc.undoInfo(closeChunk=True)

        return result

    @staticmethod
    def getMObjectForNode( nodeName ):
        sel = om.MSelectionList()
        sel.add(nodeName)
        obj = sel.getDependNode(0)
        return obj

    @staticmethod
    def getDagPathForNode( nodeName ):
        sel = om.MSelectionList()
        sel.add(nodeName)
        result = sel.getDagPath(0)
        if not result.isValid():
            raise mc.warning("node %s does not exist" % nodeName)
        return result
