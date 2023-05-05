# _*_ coding:utf-8
"""
Scripts :    python.plug_ins.skinWeightsCmd
Author  :    JesseChou
Date    :    2021/9/3
QQ      :    375714316
E-Mail  :    JesseChou0612@gmail.cOpenMaya. or 375714316@qq.cOpenMaya.
"""
from maya.api import OpenMaya, OpenMayaAnim
from maya import cmds
import shelve
import os


def getSelectionInfos():
    """
    # get selection infos
    :return: {model，vertex list}
    """
    infos = {}
    sels = cmds.ls(sl=1, fl=1)
    temps = {}
    for sel in sels:
        model = sel.split('.')[0]
        if '.vtx[' in sel:
            if not temps.has_key(model):
                temps[model] = []
            index = int(sel.split('[')[-1].split(']')[0])
            temps[model].append(index)
        if '.' not in sel:
            if not temps.has_key(sel):
                temps[model] = []
    if temps:
        model = temps.keys()[0]
        infos['geometry'] = model
        infos['vertexs'] = temps.get(model, [])
    return infos


class SkinWeights(object):
    def __init__(self, obj):
        self.obj = obj
        self.__object = None
        self.__shapeNode = None
        self.__shapeType = None
        self.__skinCluster = None
        self.__influences = []
        self.__influenceNum = 0
        self.__weights = None
        self.__vertexNum = 0

    @property
    def apiNode(self):
        if not self.__object:
            selectionList = OpenMaya.MSelectionList()
            selectionList.add(self.obj)
            self.__object = selectionList.getDependNode(0)
        return self.__object

    @property
    def shapeNode(self):
        if not self.__shapeNode:
            apiType = self.apiNode.apiType()
            if apiType == OpenMaya.MFn.kTransform:
                transNode = OpenMaya.MFnTransform(self.apiNode)
                shape = transNode.getPath().extendToShape()
                self.__shapeNode = shape.node()
                self.__shapeType = shape.apiType()
            elif apiType == OpenMaya.MFn.kMesh:
                self.__shapeNode = self.apiNode
                self.__shapeType = OpenMaya.MFn.kMesh
            elif apiType == OpenMaya.MFn.kNurbsSurface:
                self.__shapeNode = self.apiNode
                self.__shapeType = OpenMaya.MFn.kNurbsSurface
        return self.__shapeNode

    @property
    def shapeType(self):
        if self.shapeNode:
            return self.__shapeType

    @property
    def skinCluster(self):
        if not self.__skinCluster:
            itSkin = OpenMaya.MItDependencyGraph(self.shapeNode,
                                                 OpenMaya.MFn.kSkinClusterFilter,
                                                 OpenMaya.MItDependencyGraph.kUpstream,
                                                 OpenMaya.MItDependencyGraph.kBreadthFirst,
                                                 OpenMaya.MItDependencyGraph.kPlugLevel)
            skinClusters = OpenMaya.MObjectArray()
            while not itSkin.isDone():
                skinCluster = itSkin.currentNode()
                skinClusters.append(skinCluster)
                itSkin.next()
            if skinClusters:
                self.__skinCluster = skinClusters[0]
        return self.__skinCluster

    @property
    def vertexNum(self):
        return self.__vertexNum

    @property
    def influences(self):
        return self.__influences

    @property
    def weights(self):
        return self.__weights

    def getComponents(self, vertexs=[]):
        shape = None
        if self.shapeType == OpenMaya.MFn.kMesh:
            shape = OpenMaya.MFnMesh(self.shapeNode)
            component = OpenMaya.MFnSingleIndexedComponent()
            component.create(OpenMaya.MFn.kMeshVertComponent)
            if vertexs:
                component.addElements(vertexs)
            else:
                meshVerItFn = OpenMaya.MItMeshVertex(self.shapeNode)
                component.addElements(range(meshVerItFn.count()))
        elif self.shapeType == OpenMaya.MFn.kNurbsSurface:
            shape = OpenMaya.MFnNurbsSurface(self.shapeNode)
            surfaceCvItFn = OpenMaya.MItSurfaceCV(self.shapeNode)
            component = OpenMaya.MFnDoubleIndexedComponent()
            component.create(OpenMaya.MFn.kSurfaceCVComponent)
            inds = []
            while not surfaceCvItFn.isDone():
                while not surfaceCvItFn.isRowDone():
                    num1 = OpenMaya.intPtr()
                    num2 = OpenMaya.intPtr()
                    surfaceCvItFn.getIndex(num1, num2)
                    inds.append([num1.value(), num2.value()])
                    surfaceCvItFn.next()
                surfaceCvItFn.nextRow()
            component.addElements(inds)
        return shape, component

    def getWeights(self):
        if self.skinCluster:
            skinCluster = OpenMayaAnim.MFnSkinCluster(self.skinCluster)
            shape, vertexComp = self.getComponents()
            self.__influences = skinCluster.influenceObjects()
            self.__vertexNum = vertexComp.elementCount
            self.__weights, self.__influenceNum = skinCluster.getWeights(shape.getPath(), vertexComp.object())

    def setWeights(self, influences, weights, vertexs=[]):
        if self.skinCluster:
            skinCluster = OpenMayaAnim.MFnSkinCluster(self.skinCluster)
            shape, vertexComp = self.getComponents(vertexs)
            newWeights = weights
            if vertexs:
                newWeights = []
                numInfluences = len(influences)
                for vertex in vertexs:
                    newWeights += weights[numInfluences * vertex:numInfluences * (vertex + 1)]
            skinWeights = OpenMaya.MDoubleArray(newWeights)
            skinCluster.setWeights(shape.getPath(), vertexComp.object(), influences, skinWeights)
            return True
        return False

    def getWeightInfos(self):
        if self.skinCluster:
            self.getWeights()
            infos = {'vertexsNum': self.__vertexNum,
                     'influences': [x.fullPathName().split('|')[-1] for x in self.__influences],
                     'weights': list(self.__weights),
                     'shapeType': self.shapeType}
            return infos

    def setWeightInfos(self, infos, vertexs=[]):
        influences = infos.get('influences', [])
        if int(self.shapeType) == int(infos.get('shapeType', OpenMaya.MFn.kMesh)):
            vertexsFn = OpenMaya.MItMeshVertex(self.shapeNode)
            if infos.get('vertexsNum', 0) == vertexsFn.count():
                self.appendInfluences(influences)
                influencesIndices = OpenMaya.MIntArray(self.getInfluencesIndices(influences))
                self.setWeights(influencesIndices, infos.get('weights', []), vertexs)

    def checkJoints(self, influences):
        for influence in influences:
            if not cmds.objExists(influence):
                cmds.joint(n=influence)

    def appendInfluences(self, influences):
        if not self.skinCluster:
            cmds.skinCluster(influences, self.obj, dr=4, bm=0, sm=0, nw=1, wd=0, tsb=1)[0]
        if self.skinCluster:
            self.checkJoints(influences)
            skinCluster = OpenMayaAnim.MFnSkinCluster(self.skinCluster).name()
            baseInfs = cmds.skinCluster(skinCluster, q=1, inf=1) if skinCluster else []
            addInfs = [inf for inf in influences if inf not in baseInfs]
            if addInfs:
                cmds.skinCluster(skinCluster, e=1, ai=addInfs)

    def getInfluencesIndices(self, influences):
        skincluster = OpenMayaAnim.MFnSkinCluster(self.skinCluster)
        allInfluences = [x.fullPathName().split('|')[-1] for x in skincluster.influenceObjects()]
        indices = []
        for influence in influences:
            indices.append(allInfluences.index(influence))
        return indices


def exportSkinWeights(path):
    """
    # export skin weights infos
    :param path: the file to store skin weights
    :return:
    """
    judge = False
    sels = cmds.ls(sl=1)
    if sels:
        skin = SkinWeights(sels[0])
        if skin.skinCluster:
            weights = skin.getWeightInfos()
            infos = shelve.open(path, 'c')
            infos['tool'] = 'Skin Exporter'
            infos['version'] = '2.0'
            infos['author'] = 'zhoujunjie'
            infos['email'] = '375714316@qq.com'
            for key, value in weights.iteritems():
                infos[str(key)] = value
            infos.close()
            judge = True
    return judge


def batchExportSkinWeights(path):
    """
    # batch export skin weights infos
    :param path: the file to store skin weights
    :return:
    """
    failedList = []
    weightInfos = {}
    for sel in cmds.ls(sl=1):
        skin = SkinWeights(sel)
        if skin.skinCluster:
            skin.getWeights()
            weightInfos[sel.split('|')[-1]] = {
                'vertexsNum': skin.vertexNum,
                'influences': [x.fullPathName().split('|')[-1] for x in skin.influences],
                'weights': list(skin.weights),
                'shapeType': skin.shapeType}
        else:
            failedList.append(sel)
    if weightInfos:
        infos = shelve.open(path, 'c')
        infos['tool'] = 'Multiply Skin Exporter'
        infos['version'] = '2.0'
        infos['author'] = 'zhoujunjie'
        infos['email'] = '375714316@qq.com'
        for key, value in weightInfos.iteritems():
            infos[str(key)] = value
        infos.close()
    return failedList


def importSkinWeights(path):
    """
    # import skin weights infos
    :param path:the file stored skin weights
    :return:
    """
    judge = 0
    selectInfos = getSelectionInfos()
    if selectInfos:
        weights = {}
        infos = shelve.open(path, 'r')
        if infos.get('tool') == 'Skin Exporter':
            for key, value in infos.iteritems():
                weights[key] = value
            skin = SkinWeights(selectInfos.get('geometry'))
            skin.setWeightInfos(weights, selectInfos.get('vertexs', []))
            judge = 1
        else:
            judge = 2
            # print 'The file is not a valid skin weights document created by "Skin Exporter"!'
        infos.close()
    return judge


def batchImportSkinWeights(path):
    """
    # batch import skin weights infos
    :param path:the file stored skin weights
    :return:
    """
    judge = 0
    failedList = []
    sels = cmds.ls(sl=1)
    if sels:
        infos = shelve.open(path, 'r')
        if infos.get('tool') == 'Multiply Skin Exporter':
            for sel in sels:
                if infos.has_key(str(sel)):
                    skin = SkinWeights(sel)
                    skin.setWeightInfos(infos.get(str(sel)), [])
                else:
                    failedList.append(sel)
            judge = 1
        else:
            judge = 2
            # print 'The file is not a valid skin weights document created by "Multiply Skin Exporter"!'
        infos.close()
    return judge, failedList


class ExportSkinWeights(OpenMaya.MPxCommand):
    pluginCmdName = "exportSkinWeights"
    multiFlag = '-m'
    multiLongFlag = '-multi'
    pathFlag = '-p'
    pathLongFlag = '-path'

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return ExportSkinWeights()

    @staticmethod
    def syntaxCreator():
        syntax = OpenMaya.MSyntax()
        syntax.addFlag(ExportSkinWeights.multiFlag, ExportSkinWeights.multiLongFlag, OpenMaya.MSyntax.kBoolean)
        syntax.addFlag(ExportSkinWeights.pathFlag, ExportSkinWeights.pathLongFlag, OpenMaya.MSyntax.kString)
        return syntax

    def doIt(self, args):
        argData = OpenMaya.MArgDatabase(self.syntax(), args)
        multi = False
        if argData.isFlagSet(self.multiFlag):
            multi = argData.flagArgumentBool(self.multiFlag, 0)

        if argData.isFlagSet(self.pathFlag):
            path = argData.flagArgumentString(self.pathFlag, 0)

        folder = os.path.dirname(path)
        if not os.path.isdir(folder):
            try:
                os.makedirs(folder)
            except:
                pass
        if os.path.isdir(folder):
            if multi:
                batchExportSkinWeights(path)
            else:
                exportSkinWeights(path)


class ImportSkinWeights(OpenMaya.MPxCommand):
    pluginCmdName = "importSkinWeights"
    pathFlag = '-p'
    pathLongFlag = '-path'
    multiFlag = '-m'
    multiLongFlag = '-multi'

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return ImportSkinWeights()

    @staticmethod
    def syntaxCreator():
        syntax = OpenMaya.MSyntax()
        syntax.addFlag(ImportSkinWeights.multiFlag, ImportSkinWeights.multiLongFlag, OpenMaya.MSyntax.kBoolean)
        syntax.addFlag(ImportSkinWeights.pathFlag, ImportSkinWeights.pathLongFlag, OpenMaya.MSyntax.kString)
        return syntax

    def doIt(self, args):
        argData = OpenMaya.MArgDatabase(self.syntax(), args)
        multi = False
        if argData.isFlagSet(self.multiFlag):
            multi = argData.flagArgumentBool(self.multiFlag, 0)

        if argData.isFlagSet(self.pathFlag):
            path = argData.flagArgumentString(self.pathFlag, 0)

        if os.path.isfile(path):
            if multi:
                judge, failedList = batchImportSkinWeights(path)
                self.appendToResult(int(judge))
                self.appendToResult(str(failedList))
            else:
                judge = importSkinWeights(path)
                self.setResult(int(judge))


class SmoothSkinWeights(OpenMaya.MPxCommand):
    pluginCmdName = "smoothSkinWeights"
    indexFlag = "-i"
    indexLongFlag = "-index"
    valueFlag = "-v"
    valueLongFlag = "-value"

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

        # parse by frags
        self.index = None
        self.pressure = None

        # skinCluster related
        self.fnSkin = None
        self.maintainMaxInfluences = True
        self.maxInfluences = 5

        self.component = None
        self.infIndices = None
        self.dagPath = OpenMaya.MDagPath()
        self.oldWeights = OpenMaya.MDoubleArray()

    @staticmethod
    def cmdCreator():
        return SmoothSkinWeights()

    @staticmethod
    def syntaxCreator():
        syntax = OpenMaya.MSyntax()
        syntax.addFlag(SmoothSkinWeights.indexFlag, SmoothSkinWeights.indexLongFlag, OpenMaya.MSyntax.kLong)
        syntax.addFlag(SmoothSkinWeights.valueFlag, SmoothSkinWeights.valueLongFlag, OpenMaya.MSyntax.kDouble)
        return syntax

    def isUndoable(self):
        return True

    def doIt(self, args):
        selection = OpenMaya.MGlobal.getActiveSelectionList()
        if not selection.isEmpty():
            self.dagPath, component = selection.getComponent(0)
            self.dagPath.extendToShape()
            itSkin = OpenMaya.MItDependencyGraph(self.dagPath.node(),
                                                 OpenMaya.MFn.kSkinClusterFilter,
                                                 OpenMaya.MItDependencyGraph.kUpstream,
                                                 OpenMaya.MItDependencyGraph.kBreadthFirst,
                                                 OpenMaya.MItDependencyGraph.kPlugLevel)

            skinClusters = OpenMaya.MObjectArray()
            while not itSkin.isDone():
                skinCluster = itSkin.currentNode()
                skinClusters.append(skinCluster)
                itSkin.next()
            if skinClusters:
                self.fnSkin = OpenMayaAnim.MFnSkinCluster(skinClusters[0])
                mFnDependSkinCluster = OpenMaya.MFnDependencyNode(skinClusters[0])
                self.maintainMaxInfluences = mFnDependSkinCluster.findPlug('maintainMaxInfluences', False).asBool()
                self.maxInfluences = mFnDependSkinCluster.findPlug('maxInfluences', False).asInt()

            if not self.fnSkin:
                OpenMaya.MGlobal.displayError('Cannot find skinCluster node connected to component.')
                return
            if self.maintainMaxInfluences and self.maxInfluences < 1:
                OpenMaya.MGlobal.displayWarning(
                    'Maintain max influences is ON and Max influences is set to 0. No weight will be set.')
                return

            argData = OpenMaya.MArgDatabase(self.syntax(), args)
            if argData.isFlagSet(SmoothSkinWeights.indexFlag):
                self.index = argData.flagArgumentInt(SmoothSkinWeights.indexFlag, 0)
            if argData.isFlagSet(SmoothSkinWeights.valueFlag):
                self.pressure = argData.flagArgumentDouble(SmoothSkinWeights.valueFlag, 0)
            self.smooth()

        else:
            OpenMaya.MGlobal.displayWarning('Please select some vertexs of the polygon at first!')
            return

    def smooth(self):
        self.component = OpenMaya.MFnSingleIndexedComponent().create(OpenMaya.MFn.kMeshVertComponent)
        OpenMaya.MFnSingleIndexedComponent(self.component).addElement(self.index)

        mitVtx = OpenMaya.MItMeshVertex(self.dagPath, self.component)
        surrVtxArray = mitVtx.getConnectedVertices()
        surrComponents = OpenMaya.MFnSingleIndexedComponent().create(OpenMaya.MFn.kMeshVertComponent)
        OpenMaya.MFnSingleIndexedComponent(surrComponents).addElements(surrVtxArray)

        # read weight from single vertex, store to oldWeights
        self.oldWeights, influenceCount = self.fnSkin.getWeights(self.dagPath, self.component)

        # read weight fromthe surrounding vertices, store to surrWeights
        surrWeights, influenceCount = self.fnSkin.getWeights(self.dagPath, surrComponents)

        self.infIndices = OpenMaya.MIntArray(range(influenceCount))

        oldWeight = self.oldWeights
        values = []
        surrVtxCount = len(surrVtxArray)
        pressure_sqr = self.pressure * self.pressure
        pre_mult = (1.0 / surrVtxCount) * (1.0 - self.pressure)

        # the main weight value calculation loop
        for i in xrange(0, influenceCount):
            v = oldWeight[i] * pre_mult
            for w in xrange(0, surrVtxCount):
                # v += surrWeights[i + (w*influenceCount)] * mults[w]
                v += surrWeights[i + (w * influenceCount)] * pressure_sqr
            values.append(v)

        # do maintain max influences if maintainMaxInfluences is checked on the skinCluster node
        if self.maintainMaxInfluences == True:
            # get indices of the top N values
            maxIndexs = sorted(range(influenceCount), key=lambda v: values[v], reverse=True)[:self.maxInfluences]
            maxVals = [0] * influenceCount
            for i in maxIndexs:
                maxVals[i] = values[i]
        else:  # else, just use the calculated list
            maxVals = values

        # normalize
        normList = [w / sum(maxVals) for w in maxVals]

        newWeights = OpenMaya.MDoubleArray(normList)

        # set the final weights throught the skinCluster
        self.oldWeights = self.fnSkin.setWeights(self.dagPath,
                                                 self.component,
                                                 self.infIndices,
                                                 newWeights,
                                                 False,
                                                 True)

    def undoIt(self):
        self.fnSkin.setWeights(self.dagPath,
                               self.component,
                               self.infIndices,
                               self.oldWeights,
                               False,
                               True)

    def redoIt(self):
        self.smooth()
