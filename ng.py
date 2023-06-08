import ngSkinTools2.api as api
import pymel.core as pm
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as omAnim
import json
import maya.cmds as mc


class EditNgTools(object):
    '''
    import mayaTools.ng as ng
    reload(ng)
    test = ng.ExportNgJson('pPlane1')
    ng.ExportNgJson.export(test.outputInfo(),path = r'C:\Users\yuweiming\Desktop/testjson')

    '''

    def __init__( self, mesh=None ):
        selection_list = om.MSelectionList()
        selection_list.add(mesh)
        dag_path = selection_list.getDagPath(0)
        self._mesh = om.MFnMesh(dag_path)

        self._skinInfluencesInfo = dict()
        if not self.layers.list():
            self.layers.add("base weights")

    @property
    def mesh( self ):
        return self._mesh

    @mesh.setter
    def mesh( self, name ):
        selection_list = om.MSelectionList()
        selection_list.add(name)
        dag_path = selection_list.getDagPath(0)
        self._mesh = om.MFnMesh(dag_path)

    @property
    def layers( self ):
        return api.layers.init_layers(self.mesh.fullPathName())

    @property
    def skinInfluences( self ):
        '''
        {jointIndex:[vtx1,vtx2,vtx3]}
        :return: skinCluster weight
        '''
        print self.mesh
        self._skinInfluencesInfo = EditNgTools.getSkinClusterInfo(self.mesh)
        return self._skinInfluencesInfo

    @skinInfluences.setter
    def skinInfluences( self, layer ):
        influences = api.list_influences(self.mesh.fullPathName())
        self._skinInfluencesInfo = dict()
        for i in influences:
            self._skinInfluencesInfo[i.logicalIndex] = layer.get_weights(i.logicalIndex)

    @property
    def jointList( self ):
        return self.layers.list_influences()

    def layersInfo( self ):
        layersAllDict = dict()
        layersAllDict['layers'] = []
        for layer in self.layers.list():
            layersDict = dict()
            layersDict['id'] = layer.id
            layersDict['name'] = layer.name
            layersDict['enabled'] = layer.enabled
            layersDict['opacity'] = layer.opacity
            layersDict['index'] = layer.index
            layersDict['paintTarget'] = layer.paint_target
            layersDict['parentId'] = layer.parent_id
            layersDict['children'] = layer.children
            layersDict['effects'] = {'mirrorMask'   : layer.effects.mirror_mask,
                                     'mirrorWeights': layer.effects.mirror_weights,
                                     'mirrorDq'     : layer.effects.mirror_dq}
            self.skinInfluences = layer
            layersDict['influences'] = self._skinInfluencesInfo
            layersAllDict['layers'].append(layersDict)
        return layersAllDict

    def influencesInfo( self ):
        influencesAllDict = dict()
        influencesAllDict['influences'] = []
        for influences in self.layers.list_influences():
            influencesDict = dict()
            influencesDict['pivot'] = influences.pivot
            influencesDict['path'] = influences.path
            influencesDict['index'] = influences.logicalIndex
            influencesDict['labelText'] = influences.labelText
            influencesDict['labelSide'] = [k for (k, v) in influences.SIDE_MAP.items() if v == influences.labelSide][0]
            influencesAllDict['influences'].append(influencesDict)
        return influencesAllDict

    def meshInfo( self ):
        meshInfoDict = dict()
        meshInfoDict['mesh'] = {}
        if mc.objExists(self.mesh.fullPathName()):
            meshInfoDict['mesh']['triangles'] = list(self.mesh.getTriangles()[1])
            vtxPnt = list()
            for i in self.mesh.getPoints(space=4):
                vtxPnt += i.x, i.y, i.z
            meshInfoDict['mesh']['vertPositions'] = vtxPnt
        return meshInfoDict

    def outputInfo( self ):
        allInfo = dict()
        meshInfo = self.meshInfo()
        influencesInfo = self.influencesInfo()
        layersInfo = self.layersInfo()
        allInfo.update(meshInfo)
        allInfo.update(influencesInfo)
        allInfo.update(layersInfo)
        return allInfo

    def addLayer( self, layerName='', influence={}, forceEmpty=False, parentName=None ):
        '''
        :param layerName:
        :param influence: {'0':[vtx1,vtx2,vtx3]}
        :return: layer
        '''
        if layerName not in [l.name for l in self.layers.list()]:
            newLayer = self.layers.add(layerName, forceEmpty, parentName)  # parent
            if influence:
                for i, w in influence.items():
                    newLayer.set_weights(i, w)
            newLayer.reload()
        else:
            return [l for l in self.layers.list() if l.name == layerName][0]
        return newLayer

    def editLayerMask( self, layer, influence='', influenceWeightList=[] ):
        '''
        :param layer:
        :param influence: mask or 0
        :param influenceWeightList: [1]*100
        :return: layer
        '''
        layer.set_weights(influence, influenceWeightList)
        layer.reload()
        return layer

    def delLayer( self, layerName ):
        layer = [l for l in self.layers.list() if l.name == layerName]
        if not layer:
            layer[0] = layerName
        try:
            self.layers.delete(layer[0])
        except:
            pass

    def buildLayer( self ):
        jointNameList = [jnt.path_name() for jnt in self.jointList]
        skininfo = self.skinInfluences
        layerNameListList = [layer.name for layer in self.layers.list()]
        jntIndex = {i.path: i.logicalIndex for i in self.layers.list_influences()}

        layerDict = {jnt.split('|')[-1]: self.addLayer(jnt.split('|')[-1], {jntIndex[jnt]: [1] * self.mesh.numVertices})
                     for jnt in jointNameList if jnt.split('|')[-1]
                     not in layerNameListList}
        setMaskWeight = [(layer.set_weights('mask', skininfo[layer.get_used_influences()[0]]), layer.reload()) for layer
                         in self.layers.list()]

        for jnt in jointNameList:
            try:
                layerDict[jnt.split('|')[-1]].parent = layerDict[jnt.split('|')[-2]]
            except:
                pass

    @staticmethod
    def export( info, path, type='json' ):
        with open(path + '.' + type, "w") as f:
            json.dump(info, f, sort_keys=True, separators=(',', ':\n'))

    @staticmethod
    def getSkinClusterInfo( mesh ):
        weightInfo = dict()
        if pm.mel.findRelatedSkinCluster(mesh.name()):
            sel = om.MSelectionList()
            sel.add(pm.mel.findRelatedSkinCluster(mesh.name()))
            skinClusterNode = omAnim.MFnSkinCluster(sel.getDependNode(0))
            influeceList = skinClusterNode.influenceObjects()
            comp_ids = [c for c in range(mesh.numVertices)]
            single_fn = om.MFnSingleIndexedComponent()
            shape_comp = single_fn.create(om.MFn.kMeshVertComponent)
            single_fn.addElements(comp_ids)
            for i in range(influeceList.__len__()):
                info = skinClusterNode.getWeights(mesh.dagPath(), shape_comp, i)
                # weightInfo[str(i)] = [info[v] for v in range(info.__len__())]
                weightInfo[i] = list(info)
        return weightInfo
