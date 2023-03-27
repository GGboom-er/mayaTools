# _*_ coding:cp936 _*_
import maya.cmds as mc
def getMesh():
    return [i for i in mc.ls(type='transform') if mc.listRelatives(i,c =1,type = 'mesh')]

def deleteSmoothNode(meshList):
    smoothNodeList = list()
    for mesh in meshList:
        historyList = mc.listHistory(mesh,pdo=1,gl =1,f =0,il =1)
        if historyList:
            for node in historyList:
                if mc.nodeType(node) == 'polySmoothFace':
                    mc.setAttr(node+'.divisions',0)
                    mc.delete(mesh,ch =1)
                    smoothNodeList.append(node)
    return smoothNodeList
def getRsMaterial():
    return mc.ls(type='RedshiftMaterial')

def checkRsConnect( RsNode ):
    return mc.listConnections(RsNode + '.diffuse_color')

def delRsColorCorrectionNode():
    rsMaterialNodeList = getRsMaterial()
    delNode = list()
    for rsNode in rsMaterialNodeList:
        preNodeList = checkRsConnect(rsNode)
        if preNodeList:
            for preNode in preNodeList:
                if preNode and mc.nodeType(preNode) == 'RedshiftColorCorrection':
                    preCont = mc.listConnections(preNode + '.input', p=1, d=1)
                    if preCont:
                        mc.connectAttr(preCont[0], rsNode + '.diffuse_color', f=1)
                        mc.delete(preNode)
                        delNode.append(preNode)
    return delNode
#deleteSmoothNode(getMesh())
def meshInfo(obj):
    '''

    :param obj:
        :return:esult: {'edge': 220,
     'edgeComponent': 0,
     'face': 100,
     'faceComponent': 100,
     'shell': 1,
     'triangle': 200,
     'triangleComponent': 0,
     'uvComponent': 0,
     'uvShell': 0,
     'uvcoord': 121,
     'vertex': 121,
     'vertexComponent': 0}
    '''
    mc.polyEvaluate(obj,ae=1)
    mc.polyEvaluate(obj, a=1)#return: 表面积
    pass

def selectNonManifoldVertices():
    """
        Selects the non manifold vertices.
    """

    mc.polySelectConstraint(m=3, t=1, nonmanifold=True)
    mc.polySelectConstraint(m=0)


def expandSelection():
    '''Expands current component selection to its max bounds'''
    oldSize = len(mc.filterExpand(sm=[28,29,31,32,33,34,35]))
    while(1):
        mc.polySelectConstraint(pp=1,t=0x00100)#拓展选择
        newSize = len(mc.filterExpand(sm=[28,29,31,32,33,34,35]))
        if oldSize == newSize: break
        oldSize = newSize

def polySelectTraverse(traversal=1):
    """
    Grow polyComponent selection

    :param traversal: 0 = Off.
                      1 = More : will add current selection border to current selection.
                      2 = Less : will remove current selection border from current selection.
                      3 = Border : will keep only current selection border.
                      4 = Contiguous Edges : Add edges aligned with the current edges selected
    :type traversal: int
    """
    #--- Vertex ---#
    result = mc.polyListComponentConversion(fv=True, tv=True)
    if result:
        mc.polySelectConstraint(pp=traversal, t=0x0001)
    else:
        #--- Edge ---#
        result = mc.polyListComponentConversion(fe=True, te=True)
        if result:
            mc.polySelectConstraint(pp=traversal, t=0x8000)
        else:
            #--- Face ---#
            result = mc.polyListComponentConversion(ff=True, tf=True)
            if result:
                mc.polySelectConstraint(pp=traversal, t=0x0008)
            else:
                #--- Uv ---#
                result = mc.polyListComponentConversion(fuv=True, tuv=True)
                if result:
                    mc.polySelectConstraint(pp=traversal, t=0x0010)



def autoUV(obj):
    '''
    按camera、平铺归一化UV
    :param obj:objName-str
    :return:
    '''
    try:
        mc.polyProjection(obj + '.f[*]', type='planar', md='p', ch=1)
        mc.polyUVSet(luv=1)
        mc.u3dUnfold(obj + '.f[*]', ite=1, p=0, bi=1, tf=1, ms=1024, rs=0)
        mc.polyNormalizeUV(obj + '.f[*]', normalizeType=1, preserveAspectRatio=0, centerOnTile=1, normalizeDirection=0,
                           ch=1)
        return True
    except Exception as e:
        print (e)
        return False

def getMeshComponents(obj,type = 0x8000,where = 1):
    '''

    :param obj:
    :param type: 0x0000(none)
                0x0001(vertex)
                0x8000(edge)
                0x0008(face)
                0x0010(texturecoordinates)
    :param where: 	0(off) 1(on border) 2(inside).
    :return:返回mesh边界内、外
    '''
    try:
        mc.select(obj)
        mc.polySelectConstraint(mode=3, type=type, w=where)
        comList = mc.ls(sl=1, fl=1)
        mc.polySelectConstraint(disable=1)

    except Exception as e:
        print (e)
        comList = None
    return obj,comList

def meshSize(obj):
    '''

    :param obj:
    :return: mesh表面积
    '''
    areaSize = mc.polyEvaluate(obj, a=1)

    return areaSize


def autoExtrudeEdge(objCom, meshSize = 0.0,size=0.001 ):
    '''

    :param objCom:
    :param meshSize:
    :param size:
    :return: 挤出节点
    '''
    try:
        offsetSize = meshSize * size
        node = mc.polyExtrudeEdge(objCom, pvx=0, pvy=0, pvz=0, offset=offsetSize)

    except Exception as e:
        print (e)
        node = None
    return node

def autoPolyBevel(ExobjCom):
    '''

    :param ExobjCom:
    :return: 倒边节点
    '''
    try:
        node = mc.polyBevel3(ExobjCom, fraction=0.3, offsetAsFraction=1, worldSpace=1, smoothingAngle=30,
                      subdivideNgons=1, mergeVertices=1, mergeVertexTolerance=0.0001, miteringAngle=180,
                      angleTolerance=180, segments=2,chamfer = 0,
                      ch=1)
    except Exception as e:
        print (e)
        node = None
    return node


if __name__ == '__main__':
    import meshTools.senceInfoFn as ms
    reload(ms)
    sel = mc.ls(sl=1)
    obj, objCom = ms.getMeshComponents(sel, type=0x8000, where=1)
    areaSize = ms.meshSize(obj)
    ms.autoExtrudeEdge(objCom, areaSize)

    ms.autoUV(obj[0])




































