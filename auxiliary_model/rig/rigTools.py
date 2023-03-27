# _*_ coding:cp936 _*_
import maya.OpenMayaAnim as omA
import maya.OpenMaya as om
import pymel.core as pm

def jntToPointWeight(objShapeName,jnt = []):
    if objShapeName and jnt:

        objMesh = pm.PyNode(objShapeName)
        objList = jnt
        skinNode = pm.general.PyNode(pm.mel.findRelatedSkinCluster(objMesh))
        cpmNode = pm.createNode("closestPointOnMesh")
        objMesh.worldMesh >> cpmNode.inMesh

        influenceDictInfo = dict()
        for i in objList:
            obj = i
            print obj
            cpmNode.inPosition.set(pm.xform(obj, q=1, ws=1, t=1))
            closePoint = cpmNode.getAttr("closestVertexIndex")

            if closePoint > -1:
                pm.skinPercent(skinNode,objMesh.vtx[closePoint],transformValue=(obj,1))
                influenceDictInfo[obj] = objMesh.vtx[closePoint]

        pm.delete(cpmNode)


