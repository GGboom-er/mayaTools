# _*_ coding:cp936 _*_
#!/usr/bin/env python
import maya.cmds as mc

def check():
    '''
    :param visCtrl:
    :return: #未使用属性列表
    '''
    unAttrList = list()
    visData = 'visData'
    if mc.objExists(visData):
        visCtrl_AttrList = mc.listAttr(visData, ud=1, k=0, l=0, u=1, v=1) or []
        for attr in visCtrl_AttrList:
            conList = mc.listConnections(visData + '.' + attr, p=1, d=1, s=0)
            if not conList:
                unAttrList.append(attr)
    return unAttrList


def fix(unAttrList=[] ):
    '''

    :param visCtrl:
    :param disAttrList:
    :return:
    '''
    visData = 'visData'
    cache = 'cache'
    for attr in unAttrList[:]:
        if mc.objExists(visData + '.' + attr):
            print attr
            if mc.objExists(attr + '__vis__'):
                mc.connectAttr(visData + '.' + attr, attr + '__vis__')
            else:
                mc.deleteAttr(visData, at=attr)
            unAttrList.remove(attr)
    if mc.objExists(visData) and mc.objExists(cache):
        visDataAttrInfo = mc.listAttr(visData, ud=1)
        nodes = mc.listRelatives(cache, ad=True, type='transform')
        nodes.insert(0, cache)
    if visDataAttrInfo:
        noExitObj = [i.split('__vis__')[0] for i in visDataAttrInfo if not mc.objExists(i.split('__vis__')[0])]
    else:
        noExitObj = []
    if visDataAttrInfo:
        noExitAttr = [i for i in nodes if i + '__vis__' not in visDataAttrInfo]
    else:
        noExitAttr = nodes

    if noExitObj:
        for obj in noExitObj:
            print(obj)
            mc.deleteAttr(visData + '.' + obj + '__vis__')
    if noExitAttr:
        for attr in noExitAttr:
            addvisDataAttr = visData + '.' + attr + '__vis__'
            if not mc.objExists(addvisDataAttr):
                mc.addAttr(visData, at='bool', ln=attr + '__vis__')
                mc.setAttr(visData + '.' + attr + '__vis__', e=True, k=True, l=False)
            mc.setAttr(visData + '.' + attr + '__vis__', 1)
            mc.connectAttr(visData + '.' + attr + '__vis__', attr + '.v', f=1)
    return unAttrList




if __name__ == '__main__':
    info = check()
    returnList = fix(unAttrList=info)