# _*_ coding:cp936 _*_
#!/usr/bin/env python
import maya.cmds as mc


def getCacheMeshFn( cache='cache' ):
    # 检查cache中的隐藏物体
    if mc.objExists(cache):

        return [i for i in mc.listRelatives('cache', ad=1, type='mesh') if mc.ls(i, type='mesh', ni=1)]
    else:
        return []


def check():
    '''
    :param meshList:
    :param attr:
    :return: 形节点被隐藏的列表
    '''
    attr = 'v'
    meshList = getCacheMeshFn()
    returnList = list()
    for mesh in meshList:
        if not mc.getAttr(mesh + '.' + attr):
            returnList.append(mesh)

    return returnList


def fix(meshList):
    '''
    :param meshList:
    :param attr:
    :param visData:
    :return: 上层被连接无法自动修正的物体
    '''
    attr = 'v'
    visData = 'visData'
    returnList = list()
    for mesh in meshList:
        meshTraName = mc.listRelatives(mesh, p=1)[0]
        meshVisAttr = mc.getAttr(mesh + '.' + attr)
        con = mc.listConnections(mesh + '.' + attr, p=1, s=1, d=0) or []
        if con:
            mc.disconnectAttr(con[0], mesh + '.' + attr)
        mc.setAttr(mesh + '.' + attr, 1)
        visDataAttr = visData + '.' + meshTraName + '__vis__'
        if mc.objExists(visDataAttr):
            visDataDWcon = mc.listConnections(visDataAttr, p=1, s=0, d=1) or []
            if visDataDWcon:
                visDataUPcon = mc.listConnections(visDataAttr, p=1, s=1, d=0) or []
                if not visDataUPcon:
                    mc.setAttr(visDataAttr, meshVisAttr)
                    if con:
                        mc.connectAttr(con[0], visDataAttr)
                else:
                    returnList.append(meshTraName)
        else:
            meshTraNameUPcon = mc.listConnections(meshTraName, p=1, s=1, d=0) or []
            if not meshTraNameUPcon:
                if con:
                    mc.connectAttr(con[0], meshTraName + '.' + attr)
                else:
                    mc.setAttr(meshTraName + '.' + attr, meshVisAttr)
            else:
                #returnList.append(meshTraName)
                try:
                    mc.setAttr(meshTraNameUPcon[0],meshVisAttr)
                except Exception as e:
                    print (e)
    return returnList

if __name__ == '__main__':
    bb = check()
    fix(bb)