# _*_ coding:cp936 _*_
"""
Scripts :    python.tools.gadget.libraryCache
Author  :    JesseChou
Date    :    2022/2/28
QQ      :    375714316
E-Mail  :    JesseChou0612@gmail.com or 375714316@qq.com
"""
import os
import sys
import time
def checkModulePath():
    MODULE_PATHS = [r'C:\Python27\Lib\site-packages',
                    r'P:\Maya\Modules\Modules_Public\pipeline\scripts',
                    r'P:\Maya\Modules\Modules_Public\pipeline\scripts\ppas_layout_tool',
                    r'P:\Maya\Modules\Modules_Public\pipeline\scripts\ppas_layout_tool\ppstools\cgtw_',
                    r'P:\Maya\Modules\Modules_Public\pipeline\scripts\ppas_layout_tool\ppstools',
                    'P:\Maya\Modules\Modules_Public\PipelineToolkit\scripts']
    for path in MODULE_PATHS:
        if path not in sys.path:
            sys.path.append(path)

checkModulePath()
from maya import cmds, mel
import pymel.core as pm
from python.cache5 import cache, exportCache
from Qt import QtWidgets
from python.library import tableItemPanel
from python.core import boundingBox, directory
from python.tools.gadget import lightingCommand
from dayu_path import DayuPath



try:
    import cgtw2

    t_tw = cgtw2.tw()
except Exception as e:
    print (e)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.__currentProject = ''
        self.__currentAssetType = ''
        self.__assetInfos = {}
        self.__assetTW = None
        self.__result = {}
        self.columnCount = 4
        self.createWidgets()
        self.createLayout()
        self.createConnections()
        self.preset()

    @property
    def currentProject(self):
        return self.__currentProject

    @property
    def currentAssetType(self):
        return self.__currentAssetType

    @property
    def assetInfos(self):
        return self.__assetInfos

    @property
    def assetList(self):
        return self.assetInfos.get(self.currentProject, {}).get(self.currentAssetType, {})

    @property
    def assetTW(self):
        if not self.__assetTW:
            self.__assetTW = tableItemPanel.TableItemPanel(self, 4)
        return self.__assetTW

    @property
    def result(self):
        return self.__result

    def createWidgets(self):
        self._projectLB_ = QtWidgets.QLabel(u'项目:')
        self._projectCB_ = QtWidgets.QComboBox()
        self._assetTypeLB_ = QtWidgets.QLabel(u'类型:')
        self._assetTypeCB_ = QtWidgets.QComboBox()
        self._clearInfosPB_ = QtWidgets.QPushButton(u'重置选择信息')
        self._startLibraryPB_ = QtWidgets.QPushButton(u'开始入库测试')
        self._startLibraryPB_.setMinimumHeight(35)

    def createLayout(self):
        self._mainLayout_ = QtWidgets.QVBoxLayout(self)
        projectLay = QtWidgets.QHBoxLayout()
        projectLay.addWidget(self._projectLB_)
        projectLay.addWidget(self._projectCB_)
        projectLay.addWidget(self._assetTypeLB_)
        projectLay.addWidget(self._assetTypeCB_)
        projectLay.addStretch(True)
        projectLay.addWidget(self._clearInfosPB_)

        self._mainLayout_.addLayout(projectLay)
        self._mainLayout_.addWidget(self.assetTW)
        self._mainLayout_.addWidget(self._startLibraryPB_)

    def createConnections(self):
        self._projectCB_.currentTextChanged.connect(self.changeProject)
        self._assetTypeCB_.currentTextChanged.connect(self.changeAssetType)
        self._startLibraryPB_.clicked.connect(self.startLibrary)
        self._clearInfosPB_.clicked.connect(self.resetAssetInfos)

    def preset(self):
        self.refreshProjectCB()

    def refreshProjectCB(self):
        projects = getProjectList()
        project = self._projectCB_.currentText()
        for pro in projects:
            if pro not in self.assetInfos.keys():
                self.__assetInfos[pro] = {}
        self._projectCB_.clear()
        self._projectCB_.addItems(projects)
        if project in projects:
            self._projectCB_.setCurrentText(project)

    def changeProject(self):
        self.__currentProject = self._projectCB_.currentText()
        self.refreshAssetTypeCB()
        setCurrentProject(self.currentProject)

    def refreshAssetTypeCB(self):
        assetTypes = getAssetTypeList(self.currentProject)
        for typ in assetTypes:
            if typ not in self.assetInfos.get(self.currentProject, {}).keys():
                self.__assetInfos[self.currentProject][typ] = {}

        assetType = self._assetTypeCB_.currentText()
        self._assetTypeCB_.clear()
        self._assetTypeCB_.addItems(assetTypes)
        if assetType in assetTypes:
            self._assetTypeCB_.setCurrentText(assetType)

    def changeAssetType(self):
        self.__currentAssetType = self._assetTypeCB_.currentText()
        assets = getAssetList(self.currentProject, self.currentAssetType)
        for asset in assets:
            if asset not in self.assetInfos.get(self.currentProject, {}).get(self.currentAssetType, {}).keys():
                self.__assetInfos[self.currentProject][self.currentAssetType][asset] = False
        self.assetTW.setItemInfos(self.assetList)

    def resetAssetInfos(self):
        infos = {}
        for project, projInfos in self.assetInfos.iteritems():
            infos[project] = {}
            for assetType, typeInfos in projInfos.iteritems():
                infos[project][assetType] = {}
                for asset in typeInfos.keys():
                    infos[project][assetType][asset] = False
        self.__assetInfos = infos
        self.assetTW.setItemInfos(self.assetList)

    def startLibrary(self):
        localTime = time.localtime()
        tim = '%02d%02d%02d' % (localTime.tm_hour, localTime.tm_min, localTime.tm_sec)
        print self.assetInfos
        self.__result = batchTestAssetCache(self.assetInfos, tim)
        if self.result:

            logText, renderCmds = analyseLibraryResult(self.result)
            logFolder = getWorkFolder(self._projectCB_.currentText(), tim)
            with open('%s/result.txt' % logFolder, 'w') as f:
                f.write(logText.encode('utf8'))
            with open('%s/renderCmd.bat' % logFolder, 'w') as f:
                f.write(renderCmds)
            directory.openFolder(logFolder)

def getProjectList():
    """
    # 获取所有项目列表
    :return: cgtw中所有的项目列表
    """
    try:
        from ppas_layout_tool.ppstools.cgtw_ import util
        reload(util)
        result = [p.get('project.entity') for p in util.get_project()]
    except Exception as e:
        print(e)
        result = []
    return result


def getAssetTypeList(project):
    """
    # 获取所有资产类型列表
    :param project: 项目名称
    :return: 该项目下，包含的资产类型
    """
    try:
        import asset_util
        reload(asset_util)
        typeList = list(asset_util.get_asset_type(project))
        for typ in typeList:
            if typ.lower() not in ['chr', 'prp']:
                typeList.remove(typ)
        return typeList
    except Exception as e:
        print(e)
    return []


def getAssetList(project, assetType):
    """
    # 根据项目，资产类型获取所有对应的资产列表
    :param project: 项目
    :param assetType: 资产类型
    :return: 对应的资产列表
    """
    try:
        import asset_util
        reload(asset_util)
        result = asset_util.get_asset_dict(project)
        asset_list = [k for k, v in result.items() if v == assetType]
        assets = []
        temps = asset_util.get_asset_step_status(project, asset_list, ['rig', 'lib', 'lgt', 'atp'])
        for key, value in temps.iteritems():
            if value.get('rig') == 'lock' and value.get('lgt') == 'lock' and value.get('lib') != 'lock':
                assets.append(key)
        return assets
    except Exception as e:
        print(e)
    return []


def generateAnimation(namespace):
    cacheGrp = '%s:cache' % namespace
    mainCtr = '%s:Main' % namespace
    if cmds.objExists(cacheGrp) and cmds.objExists(mainCtr):
        objs = cmds.listRelatives(cacheGrp, ad=True, typ='transform')
        bbx = boundingBox.get(objs)
        if bbx:
            length = max(bbx[3] - bbx[0], bbx[4] - bbx[1], bbx[5] - bbx[2])
            cmds.playbackOptions(aet=21, ast=1, max=21, min=1)
            cmds.setKeyframe(mainCtr, at='translate', t=[1, 21])
            cmds.setKeyframe(mainCtr, at='rotate', t=[1, 21])
            cmds.setKeyframe(mainCtr, at='scale', t=[1, 21])
            # cmds.setKeyframe(mainCtr, at='ty', v=length * 1.5, t=[21])
            cmds.setKeyframe(mainCtr, at='ry', v=360, t=[21])
            cmds.setKeyframe(mainCtr, at='scale', v=1.5, t=[21])
            cmds.xform(mainCtr, t=[0, length * 1.5, 0], ws=True)
            cmds.setKeyframe(mainCtr, at='ty', t=[21])

            cmds.currentTime(21)
            newBbx = boundingBox.get(objs)
            totalBbx = [min(bbx[0], newBbx[0]),
                        min(bbx[1], newBbx[1]),
                        min(bbx[2], newBbx[2]),
                        max(bbx[3], newBbx[3]),
                        max(bbx[4], newBbx[4]),
                        max(bbx[5], newBbx[5])]
            bbxBox = createMatchBox(totalBbx, namespace)
            # cmds.setAttr('%s.s' % bbxBox, 0.75, 0.75, 0.75, typ='double3')
            cmds.makeIdentity(bbxBox, a=1, t=1, r=1, s=1, n=0, pn=1)
            createMatchCamera(bbxBox)
            cmds.delete(bbxBox)
            return True
    return False


def createMatchBox(bbx, namespace):
    """
    # 创建匹配边界盒子
    :param bbx: 边界盒数值
    :param namespace: 空间名
    :return: 生成的盒子模型
    """
    cmds.lockNode(':initialShadingGroup', l=False, lu=False)
    box = '%s:matchBoundingBox' % namespace
    if not cmds.objExists(box):
        box = cmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ch=0, n=box)[0]
    cmds.xform('%s.vtx[0]' % box, t=[bbx[0], bbx[1], bbx[5]], ws=1)
    cmds.xform('%s.vtx[1]' % box, t=[bbx[3], bbx[1], bbx[5]], ws=1)
    cmds.xform('%s.vtx[2]' % box, t=[bbx[0], bbx[4], bbx[5]], ws=1)
    cmds.xform('%s.vtx[3]' % box, t=[bbx[3], bbx[4], bbx[5]], ws=1)
    cmds.xform('%s.vtx[4]' % box, t=[bbx[0], bbx[4], bbx[2]], ws=1)
    cmds.xform('%s.vtx[5]' % box, t=[bbx[3], bbx[4], bbx[2]], ws=1)
    cmds.xform('%s.vtx[6]' % box, t=[bbx[0], bbx[1], bbx[2]], ws=1)
    cmds.xform('%s.vtx[7]' % box, t=[bbx[3], bbx[1], bbx[2]], ws=1)
    return box


def createMatchCamera(box):
    matchCamera = 'anim_camera'
    if not cmds.objExists(matchCamera):
        cameraShape = cmds.createNode('camera', n='%sShape' % matchCamera)
        matchCamera = cmds.listRelatives(cameraShape, p=1)[0]
    # cmds.setAttr('%s.t' % matchCamera, 100, 100, 100, typ='double3')
    # cmds.setAttr('%s.r' % matchCamera, -34.6, 43.6, 0, typ='double3')
    cmds.setAttr('%s.rx' % matchCamera, -25)

    #cmds.lookThru(matchCamera)
    cmds.select(box, r=1)
    cmds.viewFit(matchCamera)
    cmds.setKeyframe(matchCamera, at='t')
    cmds.setKeyframe(matchCamera, at='r')


def exportAssetCache(project, assetType, asset, subFolder):
    """
    参考进来 rig master 文件
    """
    print asset
    if project and asset:
        namespaces = []
        cmds.file(new=True, f=True)
        try:
            from import_asset_tool import import_asset_lib
            reload(import_asset_lib)
            namespaces = import_asset_lib.slot_ref_asset(project, {asset: 1}, 'rig', is_vef_status=True,
                                                         folder_sign='rig_publish')
        except Exception as e:
            print(e)
        if namespaces:

            if generateAnimation(namespaces[0]):
                newPath = getFilePath(project, assetType, asset, subFolder, 0)
                cmds.file(rn=newPath)
                cmds.file(save=True, type='mayaAscii', f=True)
                # 写入信息
                # from ppstools.layout_manager import layout_widget
                # reload(layout_widget)
                # cls = layout_widget.WorkspaceManager()
                # cls.slot_write_set_info(show_info=False)
                slot_write_set_info()
                import pymel.core as pm
                node = pm.PyNode('defaultObjectSet')
                print(node)
                node.width.set(2048)
                node.height.set(2048)
                exportCache.exportCacheSingle()
                return True
def slot_write_set_info():
    """
    输出信息到 defaultObjectSet 节点上 ， 导出cache会使用
    """
    import pymel.core as pm
    import maya.cmds as cmds
    stem = DayuPath(pm.sceneName().__str__()).stem
    project, sequence, shot, pipeline_step, task_name, version = stem.split('_')
    linear = pm.currentUnit(query=True, linear=True)
    angular = pm.currentUnit(fullName=True, query=True, angle=True)
    start, end = cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)
    width = cmds.getAttr('defaultResolution.width')
    height = cmds.getAttr('defaultResolution.height')

    # 查询 cgtw
    is_simulation = False
    is_motion_blur = False
    task_status = 'Approve'
    # 扫描文件 记录资产出去
    info_dict = {
        'project': project,
        'asset_type': sequence,
        'asset': shot,
        'type': 'asset' if sequence in ['chr', 'prp', 'env', 'env'] else 'shot',
        'sequence': sequence,
        'shot': shot,
        'pipeline_step': pipeline_step,
        'task_name': task_name,
        'version': version,
        'linear': linear,
        'angular': angular,
        'startFrame': int(start),
        'endFrame': int(end),
        'width': int(width),
        'height': int(height),
        'fps': int(pm.mel.currentTimeUnitToFPS()),
        'is_simulation': is_simulation,
        'is_motion_blur': is_motion_blur,
        'task_status': task_status,
        'assets': get_ref_node_dict(),
    }
    info_dict.update({'shot_tag': None})

    node = pm.PyNode('defaultObjectSet')
    for attr, value in info_dict.items():
        if isinstance(value, bool):
            if not pm.attributeQuery(attr, node=node, exists=True):
                node.addAttr(attr, at='bool', hidden=False)
            node.attr(attr).set(value)
        elif isinstance(value, int):
            if not pm.attributeQuery(attr, node=node, exists=True):
                node.addAttr(attr, at='long', hidden=False)
            node.attr(attr).set(value)
        else:
            if not pm.attributeQuery(attr, node=node, exists=True):
                node.addAttr(attr, dt='string', hidden=False)
            node.attr(attr).set(str(value))
def _get_info(node, attr_name):
    import ast
    import pymel.core as pm
    node = pm.PyNode(node)
    if node:
        attr = getattr(node, attr_name, None)
        if attr:
            return ast.literal_eval(attr.get())
    return None
def get_ref_node_dict():
    PPS_SECRET = 'PPS_SECRET'
    import pymel.core as pm
    asset_dict = {}
    for node in pm.ls(type='reference'):
        ref_file = node.referenceFile()
        if not ref_file:
            continue

        # 如果是未加载的ref文件 跳过
        if not node.isLoaded():
            continue
        if _get_info(node, PPS_SECRET):
            data = _get_info(node, PPS_SECRET)
            # 如果是场景文件  跳过
            if data.get('asset_type_entity') == 'env' or data.get('asset.asset_tag'):
                continue
            cache_level = node.nodes()[0].name().replace('Group', 'cache')
            data.update(
                {
                    'referenceNode': node.name(),
                    'namespace': node.nodes()[0].namespace(),
                    'cache': cache_level if pm.objExists(cache_level) else ''
                 }
            )
            asset_dict.setdefault(node.name(), data)
    return asset_dict

def exportAssetCacheFn( project, assetType, asset, subFolder ):
    """
    参考进来 rig master 文件
    23.2.8去除创建窗口
    """
    if project and asset:
        namespaces = []
        cmds.file(new=True, f=True)
        try:
            from import_asset_tool import import_asset_lib
            reload(import_asset_lib)
            namespaces = import_asset_lib.slot_ref_asset(project, {asset: 1}, 'rig', is_vef_status=True,
                                                         folder_sign='rig_publish')
        except Exception as e:
            print(e)
        if namespaces:

            if generateAnimation(namespaces[0]):
                newPath = getFilePath(project, assetType, asset, subFolder, 0)
                cmds.file(rn=newPath)
                cmds.file(save=True, type='mayaAscii', f=True)
                # 写入信息
                # from ppstools.layout_manager import layout_widget
                # reload(layout_widget)
                # cls = layout_widget.WorkspaceManager()
                # cls.slot_write_set_info(show_info=False)
                slot_write_set_info()
                import pymel.core as pm
                node = pm.PyNode('defaultObjectSet')
                print(node)
                node.width.set(2048)
                node.height.set(2048)
                exportCache.exportCacheSingle()
                return True
def importAssetCache(project, assetType, asset, subFolder):
    judge = False
    mismatch = {}
    cmds.file(new=True, f=True)
    cacheName = '%s_%s_%s_lib_lib_v001' % (project, assetType, asset)
    caches = cache.importCache(cacheName, True)
    if caches:
        if caches.mismatchTransforms:
            mismatch['mismatchTransforms'] = caches.mismatchTransforms
        if caches.mismatchShapes:
            mismatch['mismatchShapes'] = caches.mismatchShapes
        renderPath = getFilePath(project, assetType, asset, subFolder, 1)
        cmds.file(rn=renderPath)
        cmds.file(save=True, f=True, typ='mayaAscii', options='v=0;')
        judge = True
    return judge, mismatch, renderPath


def testAssetCache(project, assetType, asset, subFolder):
    """
    根据给出的信息，测试缓存
    :param project: 项目名称
    :param assetType: 资产类型
    :param asset: 资产名称
    :return: 测试结果，不匹配信息![](C:/Users/ZHOUJU~1/AppData/Local/Temp/7f2703c40f1f.png)
            0 => 未成功出缓存
            1 => 成功出缓存，但是导入缓存失败
            2 => 成功出缓存，成功导入缓存
    """
    judge = 0
    infos = {}
    renderCmd = ''
    exp = exportAssetCache(project, assetType, asset, subFolder)
    if exp:
        judge, infos, renderPath = importAssetCache(project, assetType, asset, subFolder)
        if judge:
            # print project, assetType, asset
            execLightingCmd()
            renderCmd = lightingCommand.generateRenderCommand(renderPath)
            cmds.file(save=True, f=True, typ='mayaAscii', options='v=0;')
        judge = int(judge) + 1
    return judge, infos, renderCmd

def testAssetCacheFn(project, assetType, asset, subFolder):
    """
    根据给出的信息，测试缓存
    :param project: 项目名称
    :param assetType: 资产类型
    :param asset: 资产名称
    :return: 测试结果，不匹配信息![](C:/Users/ZHOUJU~1/AppData/Local/Temp/7f2703c40f1f.png)
            0 => 未成功出缓存
            1 => 成功出缓存，但是导入缓存失败
            2 => 成功出缓存，成功导入缓存
    """
    judge = 0
    infos = {}
    renderCmd = ''
    exp = exportAssetCacheFn(project, assetType, asset, subFolder)
    if exp:
        judge, infos, renderPath = importAssetCache(project, assetType, asset, subFolder)
        if judge:
            # print project, assetType, asset
            execLightingCmd()
            renderCmd = lightingCommand.generateRenderCommand(renderPath)
            cmds.file(save=True, f=True, typ='mayaAscii', options='v=0;')
        judge = int(judge) + 1
    return judge, infos, renderCmd
def batchTestAssetCache(infos, subFolder):
    result = {}
    for project, assetTypes in infos.iteritems():
        typeTemps = {}
        for assetType, assets in assetTypes.iteritems():
            assetTemps = {}
            for asset, value in assets.iteritems():
                if value:
                    judge, mismatch, renderCmd = testAssetCache(project, assetType, asset, subFolder)
                    assetTemps[asset] = {'judge': judge, 'mismatch': mismatch, 'renderCmd': renderCmd}
            if assetTemps:
                typeTemps[assetType] = assetTemps
        if typeTemps:
            result[project] = typeTemps
    return result
def batchTestAssetCacheFn(infos, subFolder):
    result = {}
    for project, assetTypes in infos.iteritems():
        typeTemps = {}
        for assetType, assets in assetTypes.iteritems():
            assetTemps = {}
            for asset, value in assets.iteritems():
                if value:
                    judge, mismatch, renderCmd = testAssetCacheFn(project, assetType, asset, subFolder)
                    assetTemps[asset] = {'judge': judge, 'mismatch': mismatch, 'renderCmd': renderCmd}
            if assetTemps:
                typeTemps[assetType] = assetTemps
        if typeTemps:
            result[project] = typeTemps
    return result

def setCurrentProject(project):
    mel.eval('setProject "X:/Project/%s"' % project)


def execLightingCmd():
    lightingCommand.renderSetting()
    cmds.select('ASSET_CACHE_GROUP', r=1)
    #Create_color_layer_abc_test(2, "")

def Create_color_layer_abc_test(i, name, *args):
    if i == 2:
        prfix = "AbcTest"
    all_sel = pm.ls(sl=1)
    layerNode = pm.createRenderLayer(name=prfix + "_n_color", number=1, makeCurrent=1, noRecurse=1)
    #cmds.editRenderLayerAdjustment("redshiftOptions.lightSamplesOverrideEnable")
    cmds.connectAttr("redshiftOptions.lightSamplesOverrideEnable", layerNode._name + '.adjustments[0].plug')
    cmds.connectAttr("redshiftOptions.lightSamplesOverrideEnable", 'defaultRenderLayer' + '.adjustments[0].plug')

    pm.setAttr("redshiftOptions.lightSamplesOverrideEnable", 0)
    if pm.objExists("Rs_color_light") != 1:
        mel.eval('redshiftCreateDomeLight()')
        color_light = pm.ls(sl=1)
        pm.rename(color_light[0], "Rs_color_light")
    light_name = pm.ls(regex="*" + "Rs_color_light" + "(\\w*|\\d*|_)")
    light_shape = light_name[0].getShape()
    pm.setAttr(light_shape + ".on", 0)
    cmds.editRenderLayerAdjustment(light_shape + ".on")
    pm.setAttr(light_shape + ".on", 1)
    pm.setAttr(light_shape + ".samples", 1)
    pm.setAttr(light_shape + ".affectsSpecular", 0)
    pm.setAttr(light_shape + ".shadow", 0)
    pm.setAttr(light_shape + ".lodVisibility", 0)
    pm.setAttr(light_shape + ".background_enable", 0)
    pm.setAttr(light_name[1] + ".visibility", 1)
    curret_renderlayer = cmds.editRenderLayerGlobals(q=1, currentRenderLayer=1)
    pm.editRenderLayerMembers(curret_renderlayer, light_name, noRecurse=1)
    ###############################################################################
    cmds.editRenderLayerAdjustment("redshiftOptions.reflectionRaysEnable")
    pm.setAttr("redshiftOptions.reflectionRaysEnable", 0)
    cmds.editRenderLayerAdjustment("redshiftOptions.subsurfaceScatteringEnable")
    pm.setAttr("redshiftOptions.subsurfaceScatteringEnable", 0)
    cmds.editRenderLayerAdjustment("redshiftOptions.emissionEnable")
    pm.setAttr("redshiftOptions.emissionEnable", 0)
    pm.select(cl=1)
    pm.select(all_sel)
    mel.eval("renderLayerEditorRenderable RenderLayerTab \"defaultRenderLayer\" \"0\"")
    all = pm.ls(type="RedshiftMaterial")
    for x in all:
        cmds.editRenderLayerAdjustment(x + ".transl_weight")
        pm.setAttr(x + ".transl_weight", 0)
def getWorkFolder(project, subFolder,assetName):
    localTime = time.localtime()
    folder = 'X:/Project/%s/work/cache/%d_%02d_%02d/%s/%s/%s' % (
        project, localTime.tm_year, localTime.tm_mon, localTime.tm_mday, t_tw.login.account(), subFolder,assetName)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    return folder

def getFilePath(project, assetType, asset, subFolder, mode=0):
    folder = getWorkFolder(project, subFolder,asset)
    if mode == 0:
        newPath = '%s/%s_%s_%s_lib_lib_v001.ma' % (folder, project, assetType, asset)
    if mode == 1:
        # newPath = '%s/%s_%s_%s_lib_cache_v001.ma' % (folder, project, assetType, asset)
        newPath = '%s/%s.ma' % (folder, asset)
    return newPath


def analyseLibraryResult(infos):
    renderCmds = ''
    successTex = u''
    failTex = ''
    for project, projInfos in infos.iteritems():
        for assetType, typeInfos in projInfos.iteritems():
            for asset, assetInfos in typeInfos.iteritems():
                text = u''
                judge = assetInfos.get('judge')
                mismatch = assetInfos.get('mismatch', {})
                renderCmd = assetInfos.get('renderCmd', '')
                if judge == 0:
                    text += u'\t缓存测试:\t导出失败\r\n'
                if judge == 1:
                    text += u'\t缓存测试:\t导出成功,导入失败\r\n'
                if judge == 2:
                    if mismatch:
                        text += u'\t匹配信息:\t出现不匹配节点\r\n'
                        for key, value in mismatch.get('mismatchTransforms', {}).iteritems():
                            text += u'\t\t%s =====>>>>> %s\r\n' % (key, value)
                        for key, value in mismatch.get('mismatchShapes', {}).iteritems():
                            text += u'\t\t%s =====>>>>> %s\r\n' % (key, value)
                    else:
                        successTex += u'%s_%s_%s \t缓存测试成功\r\n' % (project, assetType, asset)
                        renderCmds += '%s\r\n' % renderCmd
                if text:
                    failTex += u'%s_%s_%s \t缓存测试失败\r\n%s' % (project, assetType, asset, text)

    totalText = '%s\r\n\r\n%s\r\n\r\n%s' % (successTex, '#' * 70, failTex)
    return totalText, renderCmds,judge


def showInMaya():
    from python.core import mayaPyside
    return mayaPyside.showInMaya(MainWindow, n='LibraryCacheWindow', t=u'资产入库工具', w=600, h=600)
