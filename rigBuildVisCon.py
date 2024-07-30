#!/usr/bin/env python
# _*_ coding:cp936 _*_
"""
@author: GGboom
@license: MIT
@contact: https://github.com/GGboom-er
@file: rigBuildVisCon.py
@date: 2023/12/13 15:20
@desc: 
"""
import maya.cmds as mc


def getCacheMeshFn( cache='cache' ):
    # 检查cache中的隐藏物体
    if mc.objExists(cache):
        return [i for i in mc.listRelatives('cache', ad=1) if mc.ls(i, ni=1)]
    else:
        return []


def check( meshList=[], attr='v' ):
    '''
    :param meshList:
    :param attr:
    :return: 形节点被隐藏的列表
    '''
    returnList = list()
    for mesh in meshList:
        if not mc.getAttr(mesh + '.' + attr) or mc.listConnections(mesh + '.' + attr, s=1, d=0):
            returnList.append(mesh)

    return returnList


def fix( meshList, attr='v' ):
    '''
    :param meshList:
    :param attr:
    :param visData:
    :return: 上层被连接无法自动修正的物体
    '''
    returnList = list()
    for mesh in meshList:
        if mc.nodeType(mesh) == 'mesh':
            meshTraName = mc.listRelatives(mesh, p=1, type='transform')[0]
            con = mc.listConnections(mesh + '.' + attr, p=1, s=1, d=0) or []
            meshTraNameUPcon = mc.listConnections(meshTraName, p=1, s=1, d=0) or []
            if con:
                if not meshTraNameUPcon:
                    mc.disconnectAttr(con[0], mesh + '.' + attr)
                    mc.setAttr(mesh + '.' + attr, 1)
                    mc.connectAttr(con[0], meshTraName + '.' + attr)
                else:
                    returnList.append(mesh)
            elif not con:
                if not meshTraNameUPcon:
                    mc.setAttr(meshTraName + '.' + attr, mc.getAttr(mesh + '.' + attr))
                mc.setAttr(mesh + '.' + attr, 1)

    return returnList


def checkGroup( name, parent=None ):
    # 检查组别
    if not mc.objExists(name):
        args = {'n': name}
        if parent:
            args['parent'] = parent
        name = mc.createNode('transform', **args)
    else:
        if parent:
            pars = mc.listRelatives(name, p=True, f=True)
            if pars:
                if pars[0].split('|')[-1] != parent.split('|')[-1]:
                    mc.parent(name, parent)
            else:
                mc.parent(name, parent)
    return name


def convertCacheHierarchyVis():
    result = False
    cache = 'cache'
    if mc.objExists(cache):
        par = mc.listRelatives(cache, p=True)
        nodes = mc.listRelatives(cache, ad=True, type='transform')
        nodes.insert(0, cache)
        if par:
            par = par[0]
        data = checkGroup('data', par)
        visData = checkGroup('visData', data)
        for attr in ['%s%s' % (x, y) for x in 'trs' for y in 'xyz'] + ['v']:
            mc.setAttr('%s.%s' % (visData, attr), e=True, l=True, k=False)
        attrs = mc.listAttr(visData, ud=True) or []
        for attr in attrs:
            mc.deleteAttr(visData, at=attr)
        for node in nodes:
            ctrAttr = '%s__vis__' % node
            visAttr = '%s.%s' % (visData, ctrAttr)
            if not mc.objExists(visAttr):
                mc.addAttr(visData, at='bool', ln=ctrAttr)
            mc.setAttr(visAttr, e=True, k=True, l=False)
            mc.connectAttr(node + '.v', visAttr)
        result = True
    return result


def showAllGeometry( editVis=[] ):
    visCtr = 'VisibilityCtr'
    nodeList = list()
    if not mc.objExists(visCtr):
        visCtr = 'Prop'
    if editVis:
        if mc.objExists(visCtr):
            if not mc.objExists('%s.showAllGeometry' % visCtr):
                mc.addAttr(visCtr, ln='showAllGeometry', at='bool')
            mc.setAttr('%s.showAllGeometry' % visCtr, e=True, k=True)
            for i in range(len(editVis)):
                switchCD = '%s__CD__SHOWALL__' % editVis[i]
                if not mc.objExists(switchCD):
                    mc.createNode('condition', n=switchCD)
                nodeList.append(switchCD)
                mc.connectAttr('%s.showAllGeometry' % visCtr, '%s.secondTerm' % switchCD, f=True)
                mc.setAttr('%s.firstTerm' % switchCD, 1)
                mc.setAttr('%s.operation' % switchCD, 0)
                mc.setAttr('%s.colorIfTrueR' % switchCD, 1)
                cons = mc.listConnections('%s.v' % (editVis[i]), s=True, d=False, p=True)
                if cons:
                    mc.connectAttr(cons[0], '%s.colorIfFalseR' % switchCD, f=True)
                    mc.disconnectAttr(cons[0], '%s.v' % (editVis[i]))
                else:
                    mc.setAttr('%s.colorIfFalseR' % switchCD, int(mc.getAttr('%s.v' % (editVis[i]))))
                sdkNode = '%s__SDK__SHOWALL__' % editVis[i]
                if not mc.objExists(sdkNode):
                    mc.createNode('animCurveUU', n=sdkNode)
                nodeList.append(sdkNode)
                mc.setKeyframe(sdkNode, float=1, value=1)
                mc.setKeyframe(sdkNode, float=0, value=0)
                mc.connectAttr('%s.outColorR' % switchCD, sdkNode + '.input', f=1)
                mc.connectAttr(sdkNode + '.output', '%s.v' % (editVis[i]))
    return nodeList


def undoShowAllGeometry( ctrl_attr, info ):
    for node in info:
        if mc.nodeType(node) == 'condition':
            con_in = mc.listConnections('%s.colorIfFalseR' % (node), s=True, d=False, p=True)
            con_out = mc.listConnections('%s.outColorR' % (node), c=0, d=1, p=True)
            if con_in:
                mc.connectAttr(con_in[0], con_out[0], f=True)
            elif con_out:
                mc.disconnectAttr('%s.outColorR' % (node), con_out[0])
                mc.setAttr(con_out[0], int(mc.getAttr('%s.colorIfFalseR' % node)))
        elif mc.nodeType(node) == 'animCurveUU':
            con_in = mc.listConnections('%s.input' % (node), s=True, d=False, p=True)
            con_out = mc.listConnections('%s.output' % (node), c=0, d=1, p=True)
            if con_in:
                mc.connectAttr(con_in[0], con_out[0], f=True)
            elif con_out:
                mc.disconnectAttr('%s.output' % (node), con_out[0])
                mc.setAttr(con_out[0], int(mc.getAttr('%s.output' % node)))
        mc.delete(node)
    if mc.objExists(ctrl_attr):
        mc.deleteAttr(ctrl_attr)

def rigbuildVisCon():
    visCtr = 'VisibilityCtr'
    editVis = check(meshList=getCacheMeshFn(cache='cache'), attr='v')
    returnList = fix(editVis, attr='v')
    if returnList:
        return returnList
    if not mc.objExists(visCtr):
        visCtr = 'Prop'
    if mc.objExists(visCtr):
        if mc.objExists('%s.showAllGeometry' % visCtr):
            undoShowAllGeometry('%s.showAllGeometry' % visCtr,
                                [i for i in mc.ls(type=['condition','animCurveUU']) if '__CD__SHOWALL__' in i or '__SDK__SHOWALL__' in i])

        showAllGeometry(check(meshList=getCacheMeshFn(cache='cache'), attr='v'))
        t = convertCacheHierarchyVis()
        return t
