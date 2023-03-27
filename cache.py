# _*_ coding:cp936 _*_
"""
Scripts :    python.cache5.cache
Author  :    JesseChou
Date    :    2019年4月20日
QQ      :    375714316
E-Mail  :    JesseChou0612@gmail.com or 375714316@qq.com
"""
import json
import os

from maya import cmds
from python.cache5 import checkGroups, mayaFileIO, utils, cachePlus
from python.core import setting
from python.meta import cgtw

AUTO_UPDATE_NODE = setting.AUTO_UPDATE_NODE


# 缓存基类
class Cache(object):
    def __init__(self, namespace, cachePath, dataPath, renderPath, crowds=False, autoReload=False, debug=False):
        self.__namespace = namespace
        self.__cachePath = cachePath
        self.__dataPath = dataPath
        self.__renderPath = renderPath
        self.__crowds = crowds
        self.__reloadNode = AUTO_UPDATE_NODE
        self.__assetGroups = None
        self.__mismatchShapes = {}
        self.__mismatchTransforms = {}
        self.__matchShapes = {}
        self.__matchTransforms = {}
        self.__surplusCacheNodes = []
        self.__surplusRenderNodes = []
        self.__surplusCacheTransforms = []
        self.__surplusRenderTransforms = []
        self.__abcCacheNode = None
        self.__abcDataNode = None
        self.__remove = None
        self.autoReload = autoReload
        self.debug = debug

    @property
    def namespace(self):
        return self.__namespace

    @property
    def cachePath(self):
        return self.__cachePath

    @property
    def dataPath(self):
        if not self.__dataPath:
            self.__dataPath = ''
        return self.__dataPath

    @property
    def renderPath(self):
        return self.__renderPath

    @property
    def cacheNamespace(self):
        return '%s_cache' % self.namespace

    @property
    def dataNamespace(self):
        return '%s_data' % self.namespace

    @property
    def cachePathExists(self):
        return os.path.exists(self.cachePath)

    @property
    def dataPathExists(self):
        return os.path.exists(self.dataPath)

    @property
    def renderPathExists(self):
        return os.path.exists(self.renderPath)

    @property
    def crowds(self):
        return self.__crowds

    @property
    def renderParent(self):
        return '%s:Geometry' % self.namespace

    @property
    def renderExists(self):
        # 检查渲染文件是否存在
        if cmds.objExists(self.renderParent):
            children = cmds.listRelatives(self.renderParent, c=1)
            if children:
                return True
        return False

    @property
    def cacheParent(self):
        return self.assetGroups.get('cache')

    @property
    def dataParent(self):
        return self.assetGroups.get('data')

    @property
    def cacheExists(self):
        # 检查缓存文件是否存在
        self.__abcCacheNode = None
        if cmds.objExists(self.cacheParent):
            children = cmds.listRelatives(self.cacheParent, ad=True)
            if children:
                cons = cmds.listConnections(children, s=True, d=True, p=False, t='AlembicNode') or []
                if cons:
                    self.__abcCacheNode = cons[0]
                return True
        return False

    @property
    def dataExists(self):
        # 检查缓存文件是否存在
        self.__abcDataNode = None
        if cmds.objExists(self.dataParent):
            children = cmds.listRelatives(self.dataParent, ad=True)
            if children:
                cons = cmds.listConnections(children, s=True, d=True, p=False, t='AlembicNode') or []
                if cons:
                    self.__abcDataNode = cons[0]
                return True
        return False

    @property
    def assetGroups(self):
        # 检查所需组别
        if not self.__assetGroups:
            parent = ''
            if self.crowds:
                parent = checkGroups.checkGroup('CROWDS_CACHE_GROUP')
            self.__assetGroups = checkGroups.checkAssetCacheGroup(self.namespace, parent)
        return self.__assetGroups

    @property
    def mismatchShapes(self):
        return self.__mismatchShapes

    @property
    def mismatchTransforms(self):
        return self.__mismatchTransforms

    @property
    def matchShapes(self):
        return self.__matchShapes

    @property
    def matchTransforms(self):
        return self.__matchTransforms

    @property
    def surplusCacheNodes(self):
        return self.__surplusCacheNodes

    @property
    def surplusCacheTransforms(self):
        return self.__surplusCacheTransforms

    @property
    def surplusRenderNodes(self):
        return self.__surplusRenderNodes

    @property
    def surplusRenderTransforms(self):
        return self.__surplusRenderTransforms

    @property
    def abcCacheNode(self):
        return self.__abcCacheNode

    @property
    def abcDataNode(self):
        return self.__abcDataNode

    @property
    def remove(self):
        if not self.__remove:
            self.__remove = utils.RemoveCache(self.namespace, self.cacheNamespace, self.dataNamespace)
        return self.__remove

    def __repr__(self):
        return self.cachePath

    @staticmethod
    def loadAbc(path, namespace, parent):
        abcNode = None
        abcNodes = cmds.ls('AlembicNode')
        mayaFileIO.importMayaFile(namespace, path, parent, 'abc')
        nodes = [x for x in cmds.ls('AlembicNode') if x not in abcNodes]
        if nodes:
            abcNode = nodes[0]
        return abcNode

    def loadCache(self):
        # 载入缓存
        self.__abcCacheNode = None
        if self.cachePathExists and not self.cacheExists:
            self.__abcCacheNode = self.loadAbc(self.cachePath, self.cacheNamespace, self.cacheParent)
            if self.renderExists:
                self.connectCacheToRender()
        return self.abcCacheNode

    def loadData(self):
        # 载入数据缓存
        self.__abcDataNode = None
        if self.dataPathExists and not self.dataExists:
            self.__abcDataNode = self.loadAbc(self.dataPath, self.dataNamespace, self.dataParent)
            if self.renderExists:
                self.connectCacheToRender()
        return self.abcDataNode

    def loadRender(self):
        # 载入渲染文件
        if self.renderPathExists and not self.renderExists:
            tempsGrp = cmds.createNode('transform', n='importCacheTempGrp')
            mayaFileIO.importMayaFile(self.namespace, self.renderPath, tempsGrp, 'ma')
            nodes = cmds.listRelatives(tempsGrp, ad=1, typ='transform')
            cacheNodes = []
            for node in ['%s:%s' % (self.namespace, x) for x in ['cache', 'data', 'simulation']]:
                if node in nodes:
                    cacheNodes.append(node)
            if cacheNodes:
                print ('cacheNodes\r\n', cacheNodes)
                cmds.parent(cacheNodes, self.assetGroups.get('geometry'))
            cmds.delete(tempsGrp)
            if self.cacheExists or self.dataExists:
                self.connectCacheToRender()
        return None

    def connectCacheToRender(self):
        # 连接缓存和渲染模型
        if self.cacheExists and self.renderExists:
            matchInfos = connectModels(self.cacheNamespace, self.namespace)
            self.__mismatchShapes = matchInfos.get('mismatchShapes', {})
            self.__mismatchTransforms = matchInfos.get('mismatchTransforms', {})
            self.__matchShapes = matchInfos.get('matchShapes', {})
            self.__matchTransforms = matchInfos.get('matchTransforms', {})
            self.__surplusCacheNodes = matchInfos.get('surplusCacheNodes', [])
            self.__surplusRenderNodes = matchInfos.get('surplusRenderNodes', [])
            self.__surplusCacheTransforms = matchInfos.get('surplusCacheTransforms', [])
            self.__surplusRenderTransforms = matchInfos.get('surplusRenderTransforms', [])

            cacheGroup = self.assetGroups.get('cache')
            utils.switchGroupVis(cacheGroup, False)

        if self.dataExists and self.renderExists:
            matchInfos = connectModels(self.dataNamespace, self.namespace)
            dataGroup = self.assetGroups.get('data')
            utils.switchGroupVis(dataGroup, False)

        return None

    def loadAsset(self):
        # 载入资产
        self.loadCache()
        self.loadData()
        self.loadRender()
        return None

    def removeCache(self):
        # 移除缓存
        return self.remove.removeCache()

    def removeData(self):
        # 移除数据缓存
        return self.remove.removeData()

    def removeRender(self):
        # 移除渲染文件
        objs = self.remove.removeRender(['Group', 'Cache', 'Geometry'])
        cache = '%s:Cache' % self.namespace
        if cmds.objExists(cache):
            utils.switchGroupVis(cache, True)
        return objs

    def removeAsset(self):
        # 移除整个资产
        objs = self.removeCache()
        objs += self.removeData()
        objs += self.removeRender()
        return objs


def setClipPlane(cameraShape, near=1, far=10000000):
    """
    设置相机视距
    :param cameraShape: 相机形节点
    :param near: 最近距离
    :param far: 最远距离
    :return:
    """
    for attr in ['nearClipPlane', 'farClipPlane']:
        lock = cmds.getAttr('%s.%s' % (cameraShape, attr), l=True)
        if lock:
            try:
                cmds.setAttr('%s.%s' % (cameraShape, attr), e=True, l=False)
            except Exception as e:
                print (e)
        cons = cmds.listConnections('%s.%s' % (cameraShape, attr), s=True, d=True, p=True)
        if cons:
            try:
                cmds.disconnectAttr(cons[0], '%s.%s' % (cameraShape, attr))
            except Exception as e:
                print (e)
    try:
        cmds.setAttr('%s.nearClipPlane' % cameraShape, near)
    except Exception as e:
        print (e)
    try:
        cmds.setAttr('%s.farClipPlane' % cameraShape, far)
    except Exception as e:
        print (e)


class CameraCache(Cache):
    # 相机缓存
    def __init__(self, namespace, cachePath):
        super(CameraCache, self).__init__(namespace, cachePath, '', '')
        self.__reloadAttr = '__cameraCache__'
        self.__assetGroups = None

    @property
    def cacheNamespace(self):
        return ''

    @property
    def assetGroups(self):
        # 检查所需组别
        if not self.__assetGroups:
            self.__assetGroups = checkGroups.checkCameraCacheGroup()
        return self.__assetGroups

    @property
    def cacheParent(self):
        return 'CAMERA_CACHE'

    def loadCache(self):
        """
        导入相机  直接导入， 不做属性关联处理
        :return:
        """
        if self.cachePathExists and not self.cacheExists:
            mayaFileIO.importMayaFile(self.cacheNamespace, self.cachePath, self.assetGroups.get('cache'), 'abc')
            shapes = cmds.listRelatives(self.assetGroups.get('cache'), ad=1, typ='camera')
            self.__cameraCacheShape = None if not shapes else shapes[0]
            self.__cameraCacheTransform = None if not self.__cameraCacheShape else \
                cmds.listRelatives(self.__cameraCacheShape, p=1)[0]
            setClipPlane(self.__cameraCacheShape)
        return None

    def removeCache(self):
        objs = self.remove.removeCache()
        cacGrp = self.assetGroups.get('cache')
        if cmds.objExists(cacGrp):
            children = cmds.listRelatives(cacGrp, c=1)
            for child in children:
                cmds.lockNode(child, l=0)
                cmds.delete(child)
        return objs


class Caches(object):
    def __init__(self, assetDisk='S:', autoUpdate=False, tempRender=False, **kwargs):
        self._assetDisk_ = assetDisk
        self._autoUpdate_ = autoUpdate
        self.tempRender = tempRender
        self.__disk = kwargs.get('disk', 'X:')
        self.__root = kwargs.get('root', 'Project')
        self.__cacheFolder = kwargs.get('cacheFolder', 'cache')
        self.__project = kwargs.get('project')
        self.__sequence = kwargs.get('sequence')
        self.__shot = kwargs.get('shot', '')
        self.__assetType = kwargs.get('assetType')
        self.__asset = kwargs.get('asset')
        self.__stage = kwargs.get('stage', 'ani')
        self.__task = kwargs.get('task', 'ani')
        self.__subtask = kwargs.get('subtask')
        self.__type = kwargs.get('type', 'shot')

        self.__cachePath = None
        self.__reloadNode = AUTO_UPDATE_NODE

        self.__assetInfos = {}
        self.__localInfos = {}
        self.__cameraInfos = {}
        self.__assetCaches = {}
        self.__cameraCaches = {}
        self.__mismatchShapes = {}
        self.__mismatchTransforms = {}
        self.__matchShapes = {}
        self.__matchTransforms = {}
        self.__surplusCacheNodes = {}
        self.__surplusRenderNodes = {}
        self.__surplusCacheTransforms = {}
        self.__surplusRenderTransforms = {}

        self.__newestCache = {}
        self.__newestData = {}
        self.__newestRender = {}
        self.__newestCamera = {}
        self.__scenes = None
        self._updated = False
        self.__ghostInfos = {}
        self.__ghostCache = None
        self.__cgtwIsStarted = True if cgtw.t_tw else False

        utils.loadAbcPlugin()
        self.analyse()

    @property
    def cgtwIsStarted(self):
        return self.__cgtwIsStarted

    @property
    def disk(self):
        # 项目盘符
        return self.__disk

    @property
    def root(self):
        # 项目根目录
        return self.__root

    @property
    def cacheFolder(self):
        # 缓存文件夹
        return self.__cacheFolder

    @property
    def project(self):
        # 项目名称
        return self.__project

    @property
    def type(self):
        # 缓存类型,asset,shot
        return self.__type

    @property
    def sequence(self):
        # 场次
        return self.__sequence

    @property
    def shot(self):
        # 镜头号
        return self.__shot

    @property
    def assetType(self):
        # 资产类型
        return self.__assetType

    @property
    def asset(self):
        # 资产名称
        return self.__asset

    @property
    def stage(self):
        # 阶段
        return self.__stage

    @property
    def task(self):
        # 任务
        return self.__task

    @property
    def subtask(self):
        # 子任务
        return self.__subtask

    @property
    def cachePath(self):
        if not self.__cachePath:
            stage = self.stage
            if stage == 'ly':
                stage = 'ani'
            kws = {'disk': self.disk, 'root': self.root, 'cacheFolder': self.cacheFolder, 'project': self.project,
                   'sequence': self.sequence, 'shot': self.shot, 'assetType': self.assetType, 'asset': self.asset,
                   'stage': stage, 'task': self.task, 'subtask': self.subtask, 'type': self.type}

            self.__cachePath = utils.CachePath(**kws)
        return self.__cachePath

    @property
    def autoUpdateNode(self):
        # 创建自动载入缓存节点
        node = self.__reloadNode
        if not cmds.objExists(node):
            self.__reloadNode = checkUpdateNode(self.__reloadNode)
        return self.__reloadNode

    @property
    def localInfos(self):
        # 获取缓存记录的缓存参数
        if not self.newestPath:
            self.__localInfos = None
        return self.__localInfos

    @property
    def cameraInfos(self):
        # 获取缓存记录的摄像机信息
        if not self.newestPath:
            self.__cameraInfos = {}
        return self.__cameraInfos

    @property
    def assetInfos(self):
        # 资产缓存
        if not self.newestPath:
            self.__assetInfos = {}
        return self.__assetInfos

    @property
    def cameraCaches(self):
        # 相机缓存
        self.__cameraCaches = {}
        for key, value in self.newestCamera.iteritems():
            self.__cameraCaches[key] = CameraCache(key, value)
        return self.__cameraCaches

    @property
    def assetCaches(self):
        if self.assetInfos:
            assets = self.assetInfos.assets.keys()
            caches = self.__assetCaches.keys()
            assets.sort()
            caches.sort()
            if assets != caches:
                for key, value in self.assetInfos.assets.iteritems():
                    cachePath = self.newestCache.get(key)
                    dataPath = self.newestData.get(key)
                    renderPath = self.newestRender.get(key)
                    if cachePath and renderPath:
                        self.__assetCaches[key] = Cache(key, cachePath, dataPath, renderPath,
                                                        crowds=value.get('crowds'))
        else:
            self.__assetCaches = {}
        return self.__assetCaches

    @property
    def mismatchShapes(self):
        return self.__mismatchShapes

    @property
    def mismatchTransforms(self):
        return self.__mismatchTransforms

    @property
    def matchShapes(self):
        return self.__matchShapes

    @property
    def matchTransforms(self):
        return self.__matchTransforms

    @property
    def surplusCacheNodes(self):
        return self.__surplusCacheNodes

    @property
    def surplusCacheTransforms(self):
        return self.__surplusCacheTransforms

    @property
    def surplusRenderNodes(self):
        return self.__surplusRenderNodes

    @property
    def surplusRenderTransforms(self):
        return self.__surplusRenderTransforms

    @property
    def tasks(self):
        return ['ani', 'sim', 'ly', 'cache']

    @property
    def cacheInfosFile(self):
        path = ''
        if self.type == 'shot':
            stageList = ['sim', 'ani', 'ly']
            taskList = ['sim', 'ani', 'ly']
            judge = False
            for stage in stageList:
                for task in taskList:
                    self.cachePath.setInfos(stage=stage, task=task)
                    path = self.cachePath.getCacheFile('last')
                    self.cachePath.restore()
                    if os.path.isfile(path):
                        judge = True
                        break
                if judge:
                    break
        else:
            self.cachePath.setInfos(stage='lib', task='lib')
            path = self.cachePath.getCacheFile('last')
            self.cachePath.restore()
        return path

    @property
    def newestPath(self):
        path = ''
        if self.type == 'shot':
            stageList = ['sim', 'ani', 'ly']
            taskList = ['sim', 'ani', 'ly']
            judge = False
            for stage in stageList:
                for task in taskList:
                    self.cachePath.setInfos(stage=stage, task=task)
                    path = self.cachePath.getVersionPath('last')
                    self.cachePath.restore()
                    if os.path.isdir(path):
                        judge = True
                        break
                if judge:
                    break
        else:
            self.cachePath.setInfos(stage='lib', task='lib')
            path = self.cachePath.getVersionPath('last')
            self.cachePath.restore()
        return path
        # return self.cachePath.getVersionPath('last')

    @property
    def newestCache(self):
        if not self.__newestCache and self.assetInfos:
            for key, value in self.assetInfos.assets.iteritems():
                cachePath = None
                if self.type == 'shot':
                    if self.cgtwIsStarted:
                        tasks = utils.getTaskStatus(self.project, self.sequence, self.shot)
                        # cachePath = self.cachePath.getFinalFile(key, 'cache', tasks, tasks)
                        if tasks:
                            cachePath = self.cachePath.getFinalFile(key, 'cache', tasks, ['sim', 'ani', 'ly'])
                else:
                    cachePath = self.cachePath.getFile('%s__cache' % key, 'last', stage='lib', task='lib')
                #if os.path.isfile(cachePath):
                self.__newestCache[key] = cachePath
        return self.__newestCache

    @property
    def newestData(self):
        if not self.__newestData and self.assetInfos:
            for key, value in self.assetInfos.assets.iteritems():
                cachePath = None
                if self.type == 'shot':
                    if self.cgtwIsStarted:
                        tasks = utils.getTaskStatus(self.project, self.sequence, self.shot)
                        # cachePath = self.cachePath.getFinalFile(key, 'data', tasks, tasks)
                        if tasks:
                            cachePath = self.cachePath.getFinalFile(key, 'data', tasks, ['sim', 'ani', 'ly'])

                else:
                    cachePath = self.cachePath.getFile('%s__data' % key, 'last', stage='lib', task='lib')
                # if os.path.isfile(cachePath):
                self.__newestData[key] = cachePath
        return self.__newestData

    @property
    def newestRender(self):
        if not self.__newestRender and self.assetInfos:
            for key, value in self.assetInfos.assets.iteritems():
                libFile = None
                if self.cgtwIsStarted:
                    libFile = cgtw.getAssetLibFile(value.get('project'), value.get('asset'), self.tempRender)
                if libFile:
                    renderPath = libFile.get('lib_file')
                    if os.path.isfile(renderPath):
                        self.__newestRender[key] = renderPath
        return self.__newestRender

    @property
    def newestCamera(self):
        if not self.__newestCamera and self.cameraInfos:
            if self.type == 'shot':
                for camera in self.cameraInfos:
                    if self.cgtwIsStarted:
                        tasks = utils.getTaskStatus(self.project, self.sequence, self.shot)
                        if tasks:
                            cameraPath = self.cachePath.getFinalFile(camera, '', tasks, tasks)
                            # if os.path.isfile(cameraPath):
                            self.__newestCamera[camera] = cameraPath
            else:
                self.cachePath.setInfos(stage='lib', task='lib')
                folder = self.cachePath.getPath('last')
                for camera in self.cameraInfos:
                    cameraPath = '%s/%s.abc' % (folder, camera)
                    if os.path.isfile(cameraPath):
                        self.__newestCamera[camera] = cameraPath
                self.cachePath.restore()
        return self.__newestCamera

    @property
    def ghostInfos(self):
        return self.__ghostInfos

    @property
    def ghostCache(self):
        if not self.__ghostCache:
            self.__ghostCache = cachePlus.GhostCache('%s/ghostCache.abc' % os.path.dirname(self.cacheInfosFile),
                                                     self.ghostInfos)
        return self.__ghostCache

    def analyse(self):
        if self._autoUpdate_ and self.cgtwIsStarted:
            self.getInfosFromScenes()
            self.updateAllCaches()
        else:
            if os.path.isfile(self.cacheInfosFile):
                with open(self.cacheInfosFile, 'r') as f:
                    infos = json.loads(f.read())
                    self.__localInfos = utils.LocalInfos('', infos.get('local', {}))
                    self.__cameraInfos = infos.get('camera', [])
                    self.__assetInfos = utils.AssetInfos(infos.get('asset', {}))
                    self.__ghostInfos = infos.get('ghost', {})

    def getInfosFromScenes(self):
        if cmds.objExists('%s.localInfos' % self.autoUpdateNode):
            local = cmds.getAttr('%s.localInfos' % self.autoUpdateNode)
            try:
                infs = eval(local)
                self.__localInfos = utils.LocalInfos('', infs)
                self.__cachePath = utils.CachePath(**infs)
                self.__project = self.localInfos.project
                self.__sequence = self.localInfos.sequence
                self.__shot = self.localInfos.shot
            except Exception as e:
                print (e)
        if cmds.objExists('%s.assetInfos' % self.autoUpdateNode):
            asset = cmds.getAttr('%s.assetInfos' % self.autoUpdateNode)
            try:
                self.__assetInfos = utils.AssetInfos(eval(asset))
            except Exception as e:
                print (e)
        if cmds.objExists('%s.cameraInfos' % self.autoUpdateNode):
            camera = cmds.getAttr('%s.cameraInfos' % self.autoUpdateNode)
            try:
                self.__cameraInfos = eval(camera)
            except Exception as e:
                print (e)

    def setUpdateInfos(self):
        # 设置更新缓存信息
        if not self._updated:
            cmds.lockNode(self.autoUpdateNode, l=0)
            for attr in ['localInfos', 'assetInfos', 'cameraInfos']:
                cmds.setAttr('%s.%s' % (self.autoUpdateNode, attr), l=0)
            cmds.setAttr('%s.localInfos' % self.autoUpdateNode, str(self.localInfos.get(False)), l=1, type='string')
            cmds.setAttr('%s.assetInfos' % self.autoUpdateNode, str(self.assetInfos.get()), l=1, type='string')
            cmds.setAttr('%s.cameraInfos' % self.autoUpdateNode, str(self.cameraInfos), l=1, type='string')
            cmds.lockNode(self.autoUpdateNode, l=1)
            self._updated = True
        return None

    def getNewestPath(self, stage='ani', task='ani'):
        cachePath = self.cachePath.getPath('last', stage=stage, task=task)
        return cachePath

    def loadCache(self, node):
        # 载入缓存
        asset = self.assetCaches.get(node, None)
        if asset:
            self.setUpdateInfos()
            asset.loadCache()
            self.analyseMatchInfos(node, asset)
        camera = self.cameraCaches.get(node, None)
        if camera:
            camera.loadCache()
        return None

    def loadRender(self, namespace):
        # 载入渲染文件
        cache = self.assetCaches.get(namespace, None)
        if cache:
            cache.loadRender()
            self.analyseMatchInfos(namespace, cache)
        camera = self.cameraCaches.get(namespace, None)
        if camera:
            camera.loadRender()
        return None

    def loadAllCaches(self):
        # 载入所有缓存
        for key in self.cameraCaches.keys() + self.assetCaches.keys():
            self.loadCache(key)
        return None

    def loadAllRenders(self):
        # 载入所有渲染文件
        for key in self.cameraCaches.keys() + self.assetCaches.keys():
            self.loadRender(key)
        return None

    def loadAsset(self, namespace):
        # 载入整个资产
        cache = self.assetCaches.get(namespace, None)
        if cache:
            self.setUpdateInfos()
            cache.loadAsset()
            self.analyseMatchInfos(namespace, cache)
        camera = self.cameraCaches.get(namespace, None)
        if camera:
            camera.loadAsset()
        return None

    def loadAllAssets(self):
        # 载入所有资产
        for key in self.cameraCaches.keys() + self.assetCaches.keys():
            self.loadAsset(key)
        return None

    def connectCacheToRender(self, namespace):
        # 连接缓存和渲染文件
        cache = self.assetCaches.get(namespace, None)
        if cache:
            cache.connectCacheToRender()
            self.analyseMatchInfos(namespace, cache)
        camera = self.cameraCaches.get(namespace, None)
        if camera:
            camera.connectCacheToRender()
        return None

    def connectAllAssets(self):
        # 连接所有资产
        for key in self.cameraCaches.keys() + self.assetCaches.keys():
            self.connectCacheToRender(key)
        return None

    def removeCache(self, namespace):
        # 移除缓存
        objs = []
        cache = self.assetCaches.get(namespace, None)
        if cache:
            objs += cache.removeCache()
        camera = self.cameraCaches.get(namespace, None)
        if camera:
            objs += camera.removeCache()
        return objs

    def removeRender(self, namespace):
        # 移除渲染文件
        objs = []
        cache = self.assetCaches.get(namespace, None)
        if cache:
            objs += cache.removeRender()

        camera = self.cameraCaches.get(namespace, None)
        if camera:
            objs += camera.removeRender()

        return objs

    def removeAsset(self, namespace):
        # 移除资产
        objs = []
        cache = self.assetCaches.get(namespace, None)
        if cache:
            objs += cache.removeAsset()

        camera = self.cameraCaches.get(namespace, None)
        if camera:
            objs += camera.removeAsset()
        return objs

    def removeAllCaches(self):
        # 移除所有缓存
        objs = []
        for key in self.cameraCaches.keys() + self.assetCaches.keys():
            objs += self.removeCache(key)
        return objs

    def removeAllRenders(self):
        # 移除所有渲染模型
        objs = []
        for key in self.cameraCaches.keys() + self.assetCaches.keys():
            objs += self.removeRender(key)

        return objs

    def removeAllAssets(self):
        # 移除所有资产
        objs = []
        for key in self.cameraCaches.keys() + self.assetCaches.keys():
            objs += self.removeAsset(key)
        return objs

    def updateCache(self, namespace):
        # 升级指定缓存
        if namespace in self.assetCaches.keys():
            cache = self.assetCaches.get(namespace, None)
            if cache:
                # 判断cache缓存是否需要更新
                cacheFile = self.newestCache.get(namespace)
                judge = True
                if cache.cacheExists:
                    if cache.abcCacheNode:
                        if cmds.getAttr('%s.abc_File' % cache.abcCacheNode) == cacheFile:
                            judge = False
                if judge:
                    replaceCache(cacheFile, cache.cacheNamespace, cache.cacheParent)

                # 判断data缓存是否需要更新
                dataFile = self.newestData.get(namespace)
                judge = True
                if cache.dataExists:
                    if cache.abcDataNode:
                        if cmds.getAttr('%s.abc_File' % cache.abcDataNode) == dataFile:
                            judge = False
                if judge:
                    replaceCache(dataFile, cache.dataNamespace, cache.dataParent)

        if namespace in self.cameraCaches.keys():
            cache = self.cameraCaches.get(namespace, None)
            if cache:
                cacheFile = self.newestCamera.get(namespace)
                judge = True
                if cache.cacheExists:
                    if cache.abcCacheNode:
                        if cmds.getAttr('%s.abc_File' % cache.abcCacheNode) == cacheFile:
                            judge = False
                if judge:
                    replaceCache(cacheFile, cache.cacheNamespace, cache.cacheParent)
                    shapes = cmds.listRelatives('anim_camera', s=True)
                    setClipPlane(shapes[0])

    def updateAllCaches(self):
        # 升级所有缓存
        print (u'开始检测并升级缓存 %s'%(u'》'*50))
        for key in self.assetCaches.keys() + self.cameraCaches.keys():
            self.updateCache(key)
        self.setScenesInfos()
        utils.refreshCacheVis(self.assetCaches.keys())

    def replaceCache(self, name, version='last', stage='', task=''):
        # 替换缓存
        cachePath = self.cachePath.getFile(name, version, stage=stage or self.stage, task=task or self.task)
        cache = self.assetCaches.get(name)
        if cache.cacheExists and os.path.isfile(cachePath):
            abcPath = cmds.getAttr('%s.abc_File' % cache.abcNode)
            if abcPath != cachePath:
                replaceCache(cachePath, cache.cacheNamespace, cache.cacheParent)

    def importCache(self):
        # 导入缓存
        self.loadAllAssets()
        self.ghostCache.loadGhost()
        self.setScenesInfos()
        utils.fixPencilNodes()
        return None

    def setScenesInfos(self):
        # 设置场景信息
        if self.localInfos:
            self.localInfos.setToScenes()
        self.saveCacheInfos()

    def analyseMatchInfos(self, key, cls):
        if cls.mismatchShapes:
            self.__mismatchShapes[key] = cls.mismatchShapes
        if cls.mismatchTransforms:
            self.__mismatchTransforms[key] = cls.mismatchTransforms
        if cls.matchShapes:
            self.__matchShapes[key] = cls.matchShapes
        if cls.matchTransforms:
            self.__matchTransforms[key] = cls.matchTransforms
        if cls.surplusCacheNodes:
            self.__surplusCacheNodes[key] = cls.surplusCacheNodes
        if cls.surplusRenderNodes:
            self.__surplusRenderNodes[key] = cls.surplusRenderNodes
        if cls.surplusCacheTransforms:
            self.__surplusCacheTransforms[key] = cls.surplusCacheTransforms
        if cls.surplusRenderTransforms:
            self.__surplusRenderTransforms[key] = cls.surplusRenderTransforms

    def saveCacheInfos(self):
        # 将当前缓存信息存储到当前文件内，以方便后续直接调用
        infos = {'project': self.project,
                 'type': self.type,
                 'sequence': self.sequence,
                 'shot': self.shot,
                 'assetType': self.assetType,
                 'asset': self.asset,
                 'stage': self.stage,
                 'task': self.task}
        setCacheInfos(infos)


def getMatchInfos(cacheNs, renderNs):
    # 获取缓存物体和渲染物体匹配信息
    surplusCacheNodes = []
    surplusCacheTransforms = []
    matchShapes = {}
    matchTransforms = {}
    cacheNodes = cmds.ls('%s:*' % cacheNs, typ=setting.CACHE_NODE_TYPE)
    surplusRenderNodes = cmds.ls('%s:*' % renderNs, typ=setting.CACHE_NODE_TYPE)
    cacheTransforms = cmds.ls('%s:*' % cacheNs, typ='transform')
    surplusRenderTransforms = cmds.ls('%s:*' % renderNs, typ='transform')
    for trans in cacheTransforms:
        transNew = trans.replace('%s:' % cacheNs, '%s:' % renderNs)
        if transNew in surplusRenderTransforms:
            matchTransforms[trans] = transNew
            surplusRenderTransforms.remove(transNew)
        else:
            surplusCacheTransforms.append(trans)
    for node in cacheNodes:
        nodeNew = node.replace('%s:' % cacheNs, '%s:' % renderNs)
        if nodeNew in surplusRenderNodes:
            matchShapes[node] = nodeNew
            surplusRenderNodes.remove(nodeNew)
        else:
            nodeNew = node.replace('%s:' % cacheNs, '%s:' % renderNs).replace('Deformed', '')
            if nodeNew in surplusRenderNodes:
                matchShapes[node] = nodeNew
                surplusRenderNodes.remove(nodeNew)
            else:
                surplusCacheNodes.append(node)
    return {'surplusCacheNodes': surplusCacheNodes,
            'surplusRenderNodes': surplusRenderNodes,
            'surplusCacheTransforms': surplusCacheTransforms,
            'surplusRenderTransforms': surplusRenderTransforms,
            'matchShapes': matchShapes,
            'matchTransforms': matchTransforms}


def connectModels(cacheNs, renderNs):
    # 连接缓存和渲染模型
    matchInfos = getMatchInfos(cacheNs, renderNs)
    matchTransforms = {}
    mismatchTransforms = {}
    matchShapes = {}
    mismatchShapes = {}
    surplusRenderNodes = matchInfos.get('surplusRenderNodes', [])
    transforms = matchInfos.get('matchTransforms', {})
    shapes = matchInfos.get('matchShapes', {})
    for key, value in transforms.items():
        judge = True
        userAttr = cmds.listAttr(key, ud=True) or []
        for attr in setting.CHANNEL_BASE_ATTRS + userAttr:
            conAttr = '%s.%s' % (value, attr)
            if cmds.objExists(conAttr):
                cons = cmds.listConnections(conAttr, s=True, d=False) or []
                if not cons:
                    try:
                        cmds.connectAttr('%s.%s' % (key, attr), '%s.%s' % (value, attr), f=1)
                    except Exception as e:
                        print (e)
                        try:
                            cmds.setAttr('%s.%s' % (value, attr), cmds.getAttr('%s.%s' % (key, attr)), type='string')
                        except Exception as e:
                            print(e)
                            judge = False
                            print ('could not connect attr :', '%s.%s' % (key, attr), 'to', '%s.%s' % (value, attr))
            else:
                judge = False
        if judge:
            matchTransforms[key] = value
        else:
            mismatchTransforms[key] = value
            # transforms.pop(key)

    for key, value in shapes.items():
        utils.disableRenderStats(key)
        preMesh = getFrontMesh(value, value)
        if preMesh in surplusRenderNodes:
            surplusRenderNodes.remove(preMesh)
        try:
            bsName = '%s__bs__' % value
            if cmds.objExists(bsName):
                cmds.delete(bsName)
            if preMesh:
                attr = cmds.getAttr('%s.intermediateObject' % preMesh)
                if attr:
                    cmds.setAttr('%s.intermediateObject' % preMesh, 0)
                bs = cmds.blendShape(key, preMesh, n=bsName)[0]
                cmds.setAttr('%s.w[0]' % bs, 1)
                cmds.setAttr('%s.intermediateObject' % preMesh, attr)
            else:
                bs = cmds.blendShape(key, value, n=bsName)[0]
                cmds.setAttr('%s.w[0]' % bs, 1)
            matchShapes[key] = value
        except Exception as e:
            mismatchShapes[key] = value
            print (e)
            # shapes.pop(key)
            # print (node, '===========>>>>>>>>>>>', tar_node)
    matchInfos['matchTransforms'] = matchTransforms
    matchInfos['matchShapes'] = matchShapes
    matchInfos['mismatchTransforms'] = mismatchTransforms
    matchInfos['mismatchShapes'] = mismatchShapes
    matchInfos['surplusRenderNodes'] = surplusRenderNodes
    return matchInfos


def getFrontMesh(node, exNode):
    # 获取历史节点前置mesh
    infos = None
    if cmds.nodeType(node) in ['mesh']:
        cons = cmds.listConnections('%s.inMesh' % node, s=1, d=0, p=1) or []
    else:
        cons = cmds.listConnections(node, s=1, d=0, p=1) or []
    for con in cons:
        obj = con.split('.')[0]
        if cmds.nodeType(obj) not in ['objectSet', 'shadingEngine', 'groupId']:
            if obj != exNode:
                if cmds.nodeType(obj) == 'mesh':
                    infos = obj
                    break
                else:
                    infos = getFrontMesh(obj, exNode)
                    if infos:
                        break
    return infos


# ============================================缓存更新功能============================================
def checkUpdateNode(name):
    melScript = 'python("import python.cache5.cache as cache");\npython("cache.Caches(autoUpdate=True)");'
    cmds.scriptNode(bs=melScript, n=name, st=1)
    cmds.addAttr(name, ln='localInfos', dt='string', h=True)
    cmds.addAttr(name, ln='assetInfos', dt='string', h=True)
    cmds.addAttr(name, ln='cameraInfos', dt='string', h=True)
    return name


def replaceCache(abcPath, abcNamespace, abcParent):
    # 重新载入缓存
    if os.path.isfile(str(abcPath)):
        parentObj = '__temporary__Parent'
        if not cmds.objExists(parentObj):
            cmds.createNode('transform', n=parentObj)
        tmpNs = '__temporary___%s' % abcNamespace
        mayaFileIO.importMayaFile(tmpNs, abcPath, parentObj, 'abc')
        tNodes = cmds.ls('%s:*' % tmpNs, type='transform')
        shapes = cmds.listRelatives(tNodes, s=1) or []
        delNodes = []
        for node in tNodes + shapes:
            judge = False
            utils.disableRenderStats(node)
            oldObj = node.replace('__temporary___', '')
            if cmds.objExists(oldObj):
                judge = True
            if not judge:
                if oldObj.startswith(':'):
                    oldObj = oldObj[1:]
                    if cmds.objExists(oldObj):
                        judge = True
                if not judge:
                    oldObj = oldObj.replace(':', '___')
                    if cmds.objExists(oldObj):
                        judge = True
            if judge:
                switchConnectionAttrs(oldObj, node)
                delNodes.append(oldObj)

        for node in delNodes:
            try:
                cmds.lockNode(node, l=0)
                cmds.delete(node)
            except Exception as e:
                print(e)
        replaceNamespace(tmpNs, abcNamespace)
        node = cmds.listRelatives(parentObj, c=1)
        cmds.parent(node, abcParent)
        for nod in node:
            for attr in 'trs':
                value = 1 if attr == 's' else 0
                try:
                    cmds.setAttr('%s.%s' % (nod, attr), value, value, value, type='double3')
                except Exception as e:
                    print (e)
        cmds.delete(parentObj)
    return None


def switchConnectionAttrs(baseObj, targetObj):
    # 切换连接属性
    baseInfs = getOutputConnections(baseObj)
    tarInfs = getOutputConnections(targetObj)

    for key, value in baseInfs.iteritems():
        newAttr = key.replace(baseObj, targetObj)
        for atr in value:
            try:
                cmds.connectAttr(newAttr, atr, f=1)
            except:
                pass

    for key, value in tarInfs.iteritems():
        newAttr = key.replace(targetObj, baseObj)
        for atr in value:
            try:
                cmds.connectAttr(newAttr, atr, f=1)
            except:
                pass
    return None


def getOutputConnections(obj):
    # 获取连接信息
    infos = {}
    cons = cmds.listConnections(obj, s=0, d=1, p=1) or []
    for con in cons:
        cns = cmds.listConnections(con, s=1, d=0, p=1) or []
        for cn in cns:
            if cn.split('.')[0] == obj:
                if cn not in infos.keys():
                    infos[cn] = []
                infos[cn].append(con)
    return infos


def replaceNamespace(baseNs, targetNs):
    # 替换空间名
    nodes = cmds.ls('%s:*' % baseNs)
    for node in nodes:
        if cmds.objExists(node):
            lock = cmds.lockNode(node, q=1)[0]
            if lock:
                cmds.lockNode(node, l=0)
            nod = cmds.rename(node, node.replace('%s:' % baseNs, '%s:' % targetNs))
            cmds.lockNode(nod, l=lock)
    return None


def setCacheInfos(infos):
    """
    将缓存信息存储到当前文件内
    :param infos: 存储的信息内容
    :return:
    """
    attr = 'cacheInfos'
    if not cmds.objExists('defaultObjectSet.%s' % attr):
        cmds.addAttr('defaultObjectSet', dt='string', ln=attr, h=True)
    cmds.setAttr('defaultObjectSet.%s' % attr, e=True, l=False)
    cmds.setAttr('defaultObjectSet.%s' % attr, str(infos), typ='string')
    cmds.setAttr('defaultObjectSet.%s' % attr, e=True, l=True)


def getCacheInfos():
    """
    从场景中获取当前缓存信息内容
    :return: 缓存信息
    """
    infos = {}
    attr = 'cacheInfos'
    if cmds.objExists('defaultObjectSet.%s' % attr):
        value = cmds.getAttr('defaultObjectSet.%s' % attr)
        try:
            infos = eval(value)
        except Exception as e:
            print (e)
    return infos


# ============================================导入缓存功能============================================
def importCache(name, tempRender=False):
    # kws = {'project': 'pipeline', 'sequence': 'sc01', 'shot': 'cam779', 'type': 'shot'}
    # kws = {'project': 'pipeline', 'assetType': 'prp', 'asset': 'tongqian', 'type': 'test'}
    infos = utils.analyseScenesInfos(name)
    if infos:
        self = Caches(tempRender=tempRender, **infos)
        self.importCache()
        return self
