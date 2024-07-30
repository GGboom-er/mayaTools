#coding=utf-8

try:
    from importlib import reload 
except:
    from imp import reload 
finally:
    pass

import os,sys 

import maya.cmds as cmds 
import maya.mel as mel 


# 根据当前选中物体或元素查询关联的蒙皮节点 
def get_skinCluster_node(Elements=None): 
    Selected = cmds.ls(sl=True,fl=True) 
    if Elements == None: 
        Elements = Selected 
    if not len(Elements): 
        return 
    History = cmds.listHistory(Elements) 
    SkinNode = None 
    for node in History: 
        if cmds.nodeType(node)=='skinCluster': 
            SkinNode = node 
            break 
    return (SkinNode) 


# 求两坐标的中点坐标 
def get_midpoint_position(coord1, coord2): 
    x = (coord1[0] + coord2[0]) / 2 
    y = (coord1[1] + coord2[1]) / 2 
    z = (coord1[2] + coord2[2]) / 2   
    return (x, y, z) 

def get_midpoint_positions(objects):
    world_positions = []
    for obj in objects:
        pos = cmds.xform(obj, q=True, ws=True, t=True)
        world_positions.append(pos)#extend
    
    midpoints = [] 
    for i in range(1,len(world_positions)): 
        midpoint_x = (world_positions[i-1][0] + world_positions[i][0]) / 2.0 
        midpoint_y = (world_positions[i-1][1] + world_positions[i][1]) / 2.0 
        midpoint_z = (world_positions[i-1][2] + world_positions[i][2]) / 2.0 
        midpoints.append([midpoint_x, midpoint_y, midpoint_z]) 
    return midpoints
    
def get_midpoint_positions(objects):
    world_positions = []
    for obj in objects:
        pos = cmds.xform(obj, q=True, ws=True, t=True)
        world_positions.append(pos)#extend
    
    midpoints = [] 
    for i in range(1,len(world_positions)): 
        midpoint_x = (world_positions[i-1][0] + world_positions[i][0]) / 2.0 
        midpoint_y = (world_positions[i-1][1] + world_positions[i][1]) / 2.0 
        midpoint_z = (world_positions[i-1][2] + world_positions[i][2]) / 2.0 
        midpoints.append([midpoint_x, midpoint_y, midpoint_z]) 
    return midpoints


# Param = analyseParameter('M_Head_base.vtx[410]','loftedSurface1') 
# Param = analyseParameter('M_Head_base.vtx[410]','PolyEdges_Convert_1_Curve') 

# 获取物体相对于一个曲线或曲面的uValue值 
def analyseParameter(Element,nurbsObject,FractionMode=True): 
    nurbsObjectShape = cmds.listRelatives(nurbsObject,s=True)[0] 
    uValue = None

    if cmds.nodeType(nurbsObjectShape) == 'nurbsCurve':
        CurveShape = nurbsObjectShape
        # 获取uValue(0-#)
        NearestNode = cmds.createNode('nearestPointOnCurve')
        cmds.connectAttr("%s.worldSpace[0]"%CurveShape, "%s.inputCurve"%NearestNode)
        Pos = cmds.xform(Element,q=True,ws=True,t=True)
        cmds.setAttr("%s.inPosition"%NearestNode,Pos[0],Pos[1],Pos[2],type='float3')
        uValue = cmds.getAttr("%s.parameter"%NearestNode) 
        cmds.delete(NearestNode)

        # 获取曲线总长
        CurveInfoNode = cmds.createNode('curveInfo')
        cmds.connectAttr('%s.worldSpace[0]'%CurveShape,'%s.inputCurve'%CurveInfoNode)
        CurveLen = cmds.getAttr('%s.arcLength'%CurveInfoNode)
        cmds.delete(CurveInfoNode)

        if not CurveLen:
            cmds.warning('曲线没有长度.') 
            return

        # 截取弧长
        DimensionNode = cmds.createNode('arcLengthDimension')
        cmds.connectAttr('%s.worldSpace[0]'%CurveShape,'%s.nurbsGeometry'%DimensionNode)
        cmds.setAttr('%s.uParamValue'%DimensionNode,uValue)
        ArcLen = cmds.getAttr('%s.arcLength'%DimensionNode)
        try:
            cmds.delete(DimensionNode)
            cmds.delete(DimensionNode.replace('Shape',''))
        except:
            pass

        #计算uValue(0-1)
        Parameter = ArcLen/CurveLen 
        if FractionMode == True:
            uValue = Parameter 

    elif cmds.nodeType(nurbsObjectShape) == 'nurbsSurface':
        SurfaceShape = nurbsObjectShape
        NearestNode = cmds.createNode('closestPointOnSurface')
        cmds.connectAttr("%s.worldSpace[0]"%SurfaceShape, "%s.inputSurface"%NearestNode)
        Pos = cmds.xform(Element,q=True,ws=True,t=True)
        cmds.setAttr("%s.inPosition"%NearestNode,Pos[0],Pos[1],Pos[2],type='float3')
        uValue = cmds.getAttr("%s.parameter"%NearestNode)
        cmds.delete(NearestNode)
        # 截取弧长
        DimensionNode = cmds.createNode('arcLengthDimension')
        cmds.connectAttr('%s.worldSpace[0]'%SurfaceShape,'%s.nurbsGeometry'%DimensionNode)
        cmds.setAttr('%s.uParamValue'%DimensionNode,uValue)
        ArcLen = cmds.getAttr('%s.arcLength'%DimensionNode)
        try:
            cmds.delete(DimensionNode)
            cmds.delete(DimensionNode.replace('Shape',''))
        except:
            pass
        # 获取曲线总长
        SpansU = cmds.getAttr('%s.spans'%SurfaceShape)
        DimensionNode = cmds.createNode('arcLengthDimension')
        cmds.connectAttr('%s.worldSpace[0]'%SurfaceShape,'%s.nurbsGeometry'%DimensionNode)
        cmds.setAttr('%s.uParamValue'%DimensionNode,SpansU)
        CurveLen = cmds.getAttr('%s.arcLength'%DimensionNode)
        try:
            cmds.delete(DimensionNode)
            cmds.delete(DimensionNode.replace('Shape',''))
        except:
            pass

        #计算uValue(0-1)
        Parameter = ArcLen/CurveLen 
        if FractionMode == True: 
            uValue = Parameter 

    return uValue 


def move_to_nurbsObject(fitNode,nurbsObject,uValue=0,vValue=0,FractionMode=True): 
    nurbsObjectShape = cmds.listRelatives(nurbsObject,s=True)[0] 
    Pos = [] 
    if cmds.nodeType(nurbsObjectShape) == 'nurbsCurve':
        PinNode = cmds.createNode('motionPath') 
        cmds.setAttr (PinNode+".fractionMode",FractionMode) 
        cmds.setAttr (PinNode+".uValue",uValue) 
        cmds.connectAttr(nurbsObjectShape+".worldSpace", PinNode+".geometryPath") 
        Pos = cmds.getAttr(PinNode+".allCoordinates")[0] 
        cmds.delete(PinNode) 
    elif cmds.nodeType(nurbsObjectShape) == 'nurbsSurface':
        PinNode = cmds.createNode('follicle') 
        cmds.connectAttr(nurbsObjectShape+".local", PinNode+".inputSurface") 
        cmds.connectAttr(nurbsObjectShape+".worldMatrix", PinNode+".inputWorldMatrix") 
        cmds.setAttr (PinNode+".parameterV",vValue) 
        cmds.setAttr (PinNode+".parameter",uValue) 
        Pos = cmds.getAttr(PinNode+".outTranslate")[0] 
        cmds.delete(PinNode) 
    cmds.xform(fitNode,t=Pos,ws=True) 


#
def reCreateCurve(crv=''):
    sel = cmds.ls(sl=True) 
    if crv == '': 
        crv=sel[0] 
    size = cmds.getAttr( crv +'.controlPoints', size=True) 
    vecList = [] 
    for i in range(0,size,1): 
        vec = cmds.xform(crv+'.cv['+str(i)+']',q=True,ws=True,t=True) 
        vecList.append(vec) 
    cmds.delete(crv) 
    crv = cmds.curve(p=vecList,name=crv) 
    return (crv) 


def create_joint_curve(joints,curve_name='curve#',curve_degree=1): 
    # 获取关节的位置信息 
    joint_positions = [cmds.xform(j, q=True, ws=True, translation=True) for j in joints] 
    # 创建一阶贝塞尔曲线 
    curve = cmds.curve(d=curve_degree, p=joint_positions, name=curve_name) 
    return curve 


def flip_curve(Curve = None):
    Sel = cmds.ls(sl=True)
    if not Curve and len(Sel):
        Curve = Sel[0]
        if '.' in Curve:
            Curve = Curve.split('.')[0]
    if not Curve:
        return
        
    N = len(cmds.getAttr('%s.cv[*]'%Curve,s=1))

    L = []
    L_CVS = range(N)
    L_Range = range(N/2)
    for i in L_Range:
        T = cmds.pointPosition('%s.cv[%d]'%(Curve,i))
        cmds.setAttr('%s.controlPoints[%d].xValue'%(Curve,L_CVS[(i+1)*-1]),T[0]*-1)
        cmds.setAttr('%s.controlPoints[%d].yValue'%(Curve,L_CVS[(i+1)*-1]),T[1])
        cmds.setAttr('%s.controlPoints[%d].zValue'%(Curve,L_CVS[(i+1)*-1]),T[2])

    if N%2 == 1:
        cmds.setAttr('%s.controlPoints[%d].xValue'%(Curve,N/2),0) 
    cmds.setAttr ("%s.dispCV"%Curve,True) 



def get_set_member(obj_set): 
    #cmds.select(obj_set,r=True);List = cmds.ls(sl=True) 
    #List = cmds.sets(obj_set,q=True) 
    input_nodes = cmds.listConnections(obj_set, source=True, destination=False) 
    return (input_nodes) 

def sum_of_list(list): 
        total = 0.00 
        for ele in range(0, len(list)):
            total = total + list[ele] 
        return total

# 根据当前选中物体中筛选出顶点或者排除无效选择
def filter_vtx_from_selected(): 
    #list_selected = cmds.ls(sl=True,fl=True) 
    list_selected = order_select() 
    
    returnValue = None 

    if list_selected: 

        # 根据选中的第一个元素判断被选中元素的类型
        first_element = list_selected[0] 
        #print (first_element) 

        
        if '.vtx[' in first_element:
            returnValue = list_selected 
        
        elif '.e[' in first_element:
            vertSel = [] 
            for item in list_selected:
                if cmds.filterExpand(item, sm=32) != "":
                    verts = cmds.polyListComponentConversion(item, fromEdge=True, toVertex=True) 
                    vertSel.extend(verts) 
            returnValue = cmds.ls(vertSel,fl=True) 

        elif '.f[' in first_element:
            vertSel = [] 
            for item in list_selected:
                verts = cmds.polyListComponentConversion(item, fromFace=True, toVertex=True) 
                vertSel.extend(verts) 
            returnValue = cmds.ls(vertSel,fl=True) 
        else:
            vertSel = cmds.ConvertSelectionToVertices()
            returnValue = cmds.ls(vertSel,fl=True) 
            
    return returnValue 

def get_notZero_infWeight_dict(vertexName):

    meshName = vertexName.split('.')[0]
    skinNode = mel.eval( "findRelatedSkinCluster %s" % meshName )
    weightValues = cmds.skinPercent(skinNode,vertexName,q=True,v=True)
    infJoints = cmds.skinCluster(vertexName,q=True,inf=True)

    names = ['Alice', 'Bob', 'Charlie', 'David']
    heights = [1.75, 1.68, 1.58, 1.82]

    dict = {infName: weightValue for infName, weightValue in zip(infJoints, weightValues) if weightValue > 0}
    return (dict) 



def order_select():
    if (cmds.selectPref(tso=True, q=True) == 0):
        cmds.selectPref(tso=True)
    ordered_selected = cmds.ls( orderedSelection=True,fl=1)
    return ordered_selected


class Debug:
    on = True
    @classmethod
    def debug(cls,func):
        def wrapper(*args,**kwargs):
            if cls.on:
                print(u'>>> [{}] start.'.format(func.__name__)) 
            ret = func(*args,**kwargs) 
            if cls.on:
                print(u'>>> [{}] over.'.format(func.__name__)) 
            return ret
        return wrapper
    
    @classmethod
    def open(cls):
        cls.on = True
        print(u'>>>debug open.') 

    @classmethod
    def close(cls):
        cls.on = False
        print(u'>>>debug close.') 