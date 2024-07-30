import maya.cmds as mc
import mayaTools.ng as ng
import tempfile
import json

reload(ng)


def outputMeshPnt( path=r'X:\Project\cat11\pub\lgt_comp\lgt_asset\chr', assetname='whitetiger',
                   checkGrp='whitetiger_styledMesh_Grp' ):
    assectPath = path + '/%s' % assetname
    if os.path.exists(assectPath):
        assectFile = sorted([assectPath + '\\' + i for i in os.listdir(assectPath) if i.endswith('.ma')])
        cmds.file(assectFile[-1], o=True, ignoreVersion=True, f=1)
        meshList = cmds.ls(checkGrp, type='mesh', dag=1)
        meshPntInfoDict = dict()
        for mesh in meshList:
            meshPntInfoDict[str(mesh)] = ng.ExportNgJson(mesh).meshInfo()['mesh']['vertPositions']
        ng.ExportNgJson().export(info=meshPntInfoDict, path=tempfile.gettempdir() + '/%s' % assetname)
        if os.path.exists(tempfile.gettempdir() + '/%s.json' % assetname):
            return tempfile.gettempdir() + '/%s.json' % assetname
        else:
            return None


def checkCache( pathList=[], checkName='whitetiger', checkGrp='cache' ):
    returnList = list()
    assetInfo = outputMeshPnt(assetname=checkName, checkGrp=checkGrp)
    if assetInfo:
        print assetInfo
        for path in pathList:
            abc_files = [f for f in os.listdir(path) if f.endswith('cache.abc')]
            for abc_file in abc_files:
                abcname = abc_file.split('_')[2]
                if abcname == checkName:
                    cachepath = os.path.join(path, abc_file)
                    cmds.file(cachepath, o=True, ignoreVersion=True, f=1)
                    meshList = cmds.ls(checkGrp, type='mesh', dag=1)
                    with open(assetInfo, 'r') as f:
                        info = json.load(f)
                    checkMeshList = [mesh for mesh in meshList if
                                     ng.ExportNgJson(mesh).meshInfo()['mesh']['vertPositions'] != info[mesh]]
                    if checkMeshList:
                        returnList.append((path, checkName, checkMeshList))
                    else:
                        returnList.append((path, checkName, True))
    else:
        returnList.append((checkName, 'no create json', None))
    return returnList


aa = checkCache(pathList=[r'X:\Project\cat11\cache\shot\sc01\cam008\ani\task_ani\v003'], checkName='whitetiger',
                checkGrp='whitetiger_styledMesh_Grp')













