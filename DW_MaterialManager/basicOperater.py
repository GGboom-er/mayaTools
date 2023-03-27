#encoding:utf-8
#basic material functions
import maya.cmds as mc
import pymel.core as pm

class FileNode():
    def __init__(self):
        self.defaultAttr = None
        self.specificAttrName = None

        self.fileTextureName = None
        self.colorSpace = None
        self.asColor = None
        self.udim = False

        self.specificFileNode = None
        self.bumpNode = None
        self.outNode = None
        self.outAttr = None

        self.udimMode = 3 #mari
    def getFileInfoFrom(self,userDefinedPath,materialName,defaultAttr,specificAttrName):
        self.defaultAttr = defaultAttr
        self.specificAttrName = specificAttrName

        def __setFileTextureName():
            if userDefinedPath == '':
                projectPath = mc.workspace(o =1 ,q =1)
                targetPath = projectPath + r'/' + 'sourceimages/'

            elif userDefinedPath[:2] == r'//' or userDefinedPath[:2] == r'\\' :
                relativePath = userDefinedPath[2:]
                projectPath = mc.workspace(o =1 ,q =1)
                targetPath = projectPath + r'/' + 'sourceimages/' + relativePath + r'\\'
            else:
                targetPath = userDefinedPath + r'\\'

            allFileNames = mc.getFileList(folder = targetPath)
            haveThisTexture = False
            if allFileNames is not None:
                for fileName in allFileNames:

                    if materialName in fileName and specificAttrName in fileName:
                        haveThisTexture = True
                        self.fileTextureName = targetPath + fileName
                        break
                if not haveThisTexture:
                    mc.warning('no ' + self.specificAttrName + ' texture exist' )
            else:
                mc.error('the folder is empty')

        def __setColorSpace():
            sRGBColorSpace = ['diffuseColor','primaryReflectionColor','pureColor']
            if defaultAttr in sRGBColorSpace:
                self.colorSpace = 'sRGB'
            else:
                self.colorSpace = 'Raw'
        def __setOutputUseColorBool():
            outUsingColor = ['diffuseColor','primaryReflectionColor','pureColor']
            if defaultAttr in outUsingColor:
                self.asColor = True
            else:
                self.asColor = False
        __setFileTextureName()
        __setColorSpace()
        __setOutputUseColorBool()

    def createFileNode(self,usingMayaColorManagement,isUdim):
        mayaVersion = int(mc.about(version = 1)[:4])
        if self.fileTextureName is not None:
            if self.defaultAttr is None:
                self.defaultAttr = 'unname'
            try:
                fileNode = mc.shadingNode('file',at = 1,icm = 1,n = self.defaultAttr)
            except:
                fileNode = mc.shadingNode('file',at = 1,n = self.defaultAttr)


            if isUdim:
                if mayaVersion > 2015:
                    mc.setAttr(fileNode + '.uvTilingMode',self.udimMode)
                else:
                    self.fileTextureName = self.fileTextureName.rpartition('.')[0][:-4] + '<UDIM>.' + self.fileTextureName.rpartition('.')[2]

            mc.setAttr(fileNode + '.alphaIsLuminance',1)
            mc.setAttr(fileNode + '.fileTextureName',self.fileTextureName,type = 'string')

            usingGammaNode = False
            gammaCorrectNode = None
            if usingMayaColorManagement:
                mc.setAttr(fileNode + '.colorSpace',self.colorSpace,type = 'string')
            else:
                if self.colorSpace =='sRGB':
                    usingGammaNode = True
                    gammaCorrectNode = mc.shadingNode('gammaCorrect',au = 1)
                    mc.setAttr(gammaCorrectNode + '.gammaX',0.454)
                    mc.setAttr(gammaCorrectNode + '.gammaY',0.454)
                    mc.setAttr(gammaCorrectNode + '.gammaZ',0.454)
                    mc.connectAttr(fileNode + '.outColor',gammaCorrectNode + '.value')

            if self.asColor:
                if not usingGammaNode:
                    self.outAttr = fileNode + '.outColor'
                else:
                    self.outAttr = gammaCorrectNode + '.outValue'
            else:
                if not usingGammaNode:
                    self.outAttr = fileNode +'.outAlpha'
                else:
                    self.outAttr = gammaCorrectNode + '.outValue.outValueX'
            if not usingGammaNode:
                self.outNode = fileNode
            else:
                self.outNode = gammaCorrectNode

            if self.defaultAttr == 'bump':
                bump2dNode = mc.shadingNode('bump2d',au = 1)
                self.bumpNode = bump2dNode
                mc.setAttr(bump2dNode + '.bumpInterp', 1)
                mc.connectAttr(self.outAttr,bump2dNode + '.bumpValue')
                self.outAttr = bump2dNode + '.outNormal'
                self.outNode = bump2dNode

            self.specificFileNode = fileNode
            return self
def getMaterialsFromSelectedObjects(*args):
    selected = mc.ls(sl = 1)
    shapes = mc.ls(selected,dag = 1, s = 1)
    allInputNodes = []
    if shapes == []:
        pass
    else:
        for shape in shapes:

            sg = mc.listConnections(shape,type = 'shadingEngine')

            if sg is not None:
                inputNodes = mc.listConnections(sg,s = 1, d = 0)
                for inputNode in inputNodes:
                    allInputNodes.append(inputNode)

        materials = mc.ls(allInputNodes,materials = 1)
        materials = [material for material in materials if mc.objectType(material) != 'displacementShader']
        materials = list(set(materials))
        return materials

#no matter the selected is objects or materials
def getMaterialFromSelected(*args):
    #try to get materials from selected objects
    materials = getMaterialsFromSelectedObjects()
    isMaterial = False
    #if get no material,means no object selected ,but materials
    if materials == None:
        materials = []
        sels = mc.ls(sl = 1)
        isMaterial = True
        for sel in sels:
            materials.append(sel)
            
    return materials
def createShadingGroup_connectDisplacement(targetMaterial,disNode):
    newSgNode = mc.sets(renderable = 1,empty = 1,name = targetMaterial + 'SG')
    #connect
    mc.connectAttr(targetMaterial + '.outColor',newSgNode + '.surfaceShader',f = 1)
    if disNode is not '':
        try:
            mc.connectAttr(disNode + '.out',newSgNode + '.displacementShader',f = 1)
        except:
            mc.connectAttr(disNode + '.displacement',newSgNode + '.displacementShader',f = 1)
    return newSgNode

def assignMaterialWithDisplacement(origMaterial,targetMaterial,sels = None):
    assigned = False
    #get sgNode
    try:
        sgNodes = mc.listConnections(origMaterial,s = 0,d = 1,type = 'shadingEngine')
        if sgNodes is not None:
            assigned = True
        else:
            assigned =False
        sgNode = ''
        for temp in sgNodes:
            if 'particle' not in sgNode.lower():
                sgNode = temp
    except:
        print origMaterial + ' is not assigned,ignore'
    #get disNode
    if assigned:
        disNode = ''
        inputNodes = mc.listConnections(sgNode,s = 1,d = 0)
        for inputNode in inputNodes:
            attrs = mc.listConnections(inputNode,p = 1,d = 1,s = 0)
            if attrs is not None:
                for attr in attrs:
                    if 'displacementShader' in attr:
                        disNode = inputNode
                        break
        #get object     
        if sels is None:       
            mc.hyperShade(objects = origMaterial)
            objects = mc.ls(sl =1)
        else:
            objects = sels

        #create newSgNode 
        newSgNode = mc.sets(renderable = 1,empty = 1,name = targetMaterial + 'SG')
        #connect
        
        #if the targetMaterial is lambert1 ,
        #then the lambert1 is connected to the targetMaterial by default ,there will be error
        try:
            mc.connectAttr(targetMaterial + '.outColor',newSgNode + '.surfaceShader',f = 1)
        except:
            pass
        if disNode is not '':
            try:
                mc.connectAttr(disNode + '.out',newSgNode + '.displacementShader',f = 1)
            except:
                mc.connectAttr(disNode + '.displacement',newSgNode + '.displacementShader',f = 1)
        #assign
        mc.sets(objects,e = 1,forceElement = newSgNode)
        return newSgNode

def convertMayaDisNodeToRsDisNode(sgNode):
    mayaDisNode = mc.listConnections(sgNode,s = 1,d = 0,type = 'displacementShader')
    disFileNode = mc.listConnections(mayaDisNode,s = 1 , d= 0 ,type = 'file')
    if mayaDisNode is not None:
        mayaDisNode = mayaDisNode[0]
        disDepth = mc.getAttr(mayaDisNode + '.scale')
    if disFileNode is not None:
        disFileNode = disFileNode[0]
        heightOffset = mc.getAttr(disFileNode + '.alphaOffset')
        rsDisNode = mc.shadingNode('RedshiftDisplacement',au = 1)
        #remapHsvNode = mc.shadingNode('remapHsv',au = 1)
        #mc.connectAttr(disFileNode + '.outAlpha' , remapHsvNode + '.color.colorR')
        #mc.connectAttr(disFileNode + '.outAlpha' , remapHsvNode + '.color.colorG')
        #mc.connectAttr(disFileNode + '.outAlpha' , remapHsvNode + '.color.colorB')
        mc.connectAttr(disFileNode + '.outColor' , rsDisNode + '.texMap')
        mc.connectAttr(rsDisNode + '.out',sgNode + '.displacementShader',f = 1)

        mc.setAttr(rsDisNode + '.scale',disDepth)
        mc.setAttr(rsDisNode + '.newrange_min',heightOffset)
        mc.setAttr(rsDisNode + '.newrange_max', 1+ heightOffset)



def connectUVNodeToTextureNode(UVnode,textureNode):
    mc.connectAttr(UVnode +'.outUV',textureNode + '.uvCoord',force = 1)
    mc.connectAttr(UVnode +'.outUvFilterSize',textureNode + '.uvFilterSize',force = 1)
    mc.connectAttr(UVnode +'.coverage',textureNode + '.coverage',force = 1)
    mc.connectAttr(UVnode +'.translateFrame',textureNode + '.translateFrame',force = 1)
    mc.connectAttr(UVnode +'.rotateFrame',textureNode + '.rotateFrame',force = 1)
    mc.connectAttr(UVnode +'.mirrorU',textureNode + '.mirrorU',force = 1)
    mc.connectAttr(UVnode +'.mirrorV',textureNode + '.mirrorV',force = 1)
    mc.connectAttr(UVnode +'.wrapU',textureNode + '.wrapU',force = 1)
    mc.connectAttr(UVnode +'.wrapV',textureNode + '.wrapV',force = 1)
    mc.connectAttr(UVnode +'.repeatUV',textureNode + '.repeatUV',force = 1)
    mc.connectAttr(UVnode +'.vertexUvOne',textureNode + '.vertexUvOne',force = 1)
    mc.connectAttr(UVnode +'.vertexUvTwo',textureNode + '.vertexUvTwo',force = 1)
    mc.connectAttr(UVnode +'.vertexUvThree',textureNode + '.vertexUvThree',force = 1)
    mc.connectAttr(UVnode +'.vertexCameraOne',textureNode + '.vertexCameraOne',force = 1)
    mc.connectAttr(UVnode +'.noiseUV',textureNode + '.noiseUV',force = 1)
    mc.connectAttr(UVnode +'.offset',textureNode + '.offset',force = 1)
    mc.connectAttr(UVnode +'.rotateUV',textureNode + '.rotateUV',force = 1)