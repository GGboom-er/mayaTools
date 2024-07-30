#encoding:utf-8
import maya.cmds as mc
import maya.mel
import UI
from basicOperater import FileNode
import basicOperater
from materialConverter import Material 
import dataClass

import materialConverter
#global var
mayaVersion = int(mc.about(version = 1)[:4])

textureTemplateUsing = ''
userDefinedPath = ''
materialName = ''
targetMaterialType = None
usingMayaColorManagement = True
isUdim = False
dataDict = None

openGLNormal = True
heightMapAsDisplacement = True
heightMap_8bit = True
affectColorSwitch = False
zeroHeight = 0.5
heightDepth = 0.05



def prepareGlobalVars():
    #global textureTemplateUsing
    #get userDifinedPath from UI input
    global userDefinedPath
    #only get the path info from UI,get the real path used by basicOperater  function getFileInfoFrom line 22
    userDefinedPath = mc.textFieldGrp('userDefinedPathTextField',q= 1 ,tx = 1) 

    #get materialName from UI input
    global materialName 
    materialName = mc.textFieldGrp('materialNameInput',q= 1 ,tx = 1)

    global targetMaterialType
    targetMaterialType = mc.optionMenuGrp('createMaterial',q = 1 ,v = 1)

    global textureTemplateUsing
    textureTemplateUsing = mc.optionMenuGrp('useTemplate',q = 1 ,v = 1)

    global usingMayaColorManagement
    usingMayaColorManagement = mc.checkBox('usingMayaColorManagement',q = 1,v = 1)

    global openGLNormal
    openGLNormal = mc.checkBox('openGLNormal',q = 1 ,v =1)

    global isUdim
    isUdim =  mc.checkBox('udim',q = 1,v = 1)

    global heightMapAsDisplacement
    heightMapAsDisplacement = mc.checkBox('heightMapAsDisplacement',q = 1,v = 1)

    global heightMap_8bit
    heightMap_8bit = mc.checkBox('heightMap_8bit',q = 1,v = 1)



    global zeroHeight
    zeroHeight = float(mc.textFieldGrp('zeroHeight',q = 1, tx = 1 ))

    global heightDepth
    heightDepth = float(mc.textFieldGrp('heightDepth',q = 1,tx = 1))

def __setAbstractMaterial(thisAbstractMaterial,defaultAttr_specificAttr_dict,userDefinedPath,materialName,materialAttrsData,textureTemplatesData,usingMayaColorManagement,isUdim):
    fileNodes = []
    global targetMaterialType

    reverse = None
    haveFresnelTypeTexture = False

    selfOperater = textureTemplatesData[textureTemplateUsing]['primaryReflectionGlossiness']  #rough or gloss
    targetOperater = materialAttrsData[targetMaterialType]['primaryReflectionGlossiness'][1]  #default gloss    reverse rough
    
    if 'rough' in selfOperater.lower() :
        reverse = True
    else:
        reverse = False


    #thisAbstractMaterial.attrs['primaryReflectionBRDF'].value = 'ggx'
    for defaultAttr in defaultAttr_specificAttr_dict.keys():
        specificAttrName = defaultAttr_specificAttr_dict[defaultAttr]

        if specificAttrName != 'none':
            fileNode = FileNode()
            fileNode.getFileInfoFrom(userDefinedPath, materialName, defaultAttr,specificAttrName)
            
            
            fileNode.createFileNode(usingMayaColorManagement,isUdim)
            if defaultAttr == 'primaryReflectionF0' and fileNode.specificFileNode is not None:
                thisAbstractMaterial.primaryFresnelType = 'F0'
                thisAbstractMaterial.primaryF0Attr = materialConverter.Attr(defaultAttr_specificAttr_dict[defaultAttr], 'default')
                thisAbstractMaterial.primaryF0Attr.inputNode = fileNode.outNode
                thisAbstractMaterial.primaryF0Attr.inputAttr = fileNode.outAttr
                haveFresnelTypeTexture = True

            elif defaultAttr == 'primaryReflectionIOR' and fileNode.specificFileNode is not None:
                thisAbstractMaterial.primaryFresnelType = 'IOR'
                thisAbstractMaterial.primaryIORAttr = materialConverter.Attr(defaultAttr_specificAttr_dict[defaultAttr], 'default')
                thisAbstractMaterial.primaryIORAttr.inputNode = fileNode.outNode
                thisAbstractMaterial.primaryIORAttr.inputAttr = fileNode.outAttr
                haveFresnelTypeTexture = True

            elif defaultAttr == 'primaryMetalness' and fileNode.specificFileNode is not None:
                thisAbstractMaterial.primaryFresnelType = 'Metal'
                thisAbstractMaterial.primaryMetalnessAttr = materialConverter.Attr(defaultAttr_specificAttr_dict[defaultAttr], 'default')
                thisAbstractMaterial.primaryMetalnessAttr.inputNode = fileNode.outNode
                thisAbstractMaterial.primaryMetalnessAttr.inputAttr = fileNode.outAttr
                haveFresnelTypeTexture = True

            if fileNode.specificFileNode is not None:
                fileNodes.append(fileNode)
                if fileNode.defaultAttr == 'height':
                    thisAbstractMaterial.heightFileNode = fileNode

            if defaultAttr != 'height':
                if defaultAttr != 'primaryReflectionGlossiness':
                    thisAbstractMaterial.attrs[defaultAttr] = materialConverter.Attr(thisAbstractMaterial.attrs[defaultAttr],materialAttrsData)
                elif defaultAttr== 'primaryReflectionGlossiness' and reverse is not None:
                    if reverse:
                        thisAbstractMaterial.attrs[defaultAttr] = materialConverter.Attr(thisAbstractMaterial.attrs[defaultAttr],'reverse')
                thisAbstractMaterial.attrs[defaultAttr].inputNode = fileNode.outNode
                thisAbstractMaterial.attrs[defaultAttr].inputAttr = fileNode.outAttr
   
    if not haveFresnelTypeTexture:
        if materialAttrsData[targetMaterialType]['primaryReflectionIOR'][0] != 'none':
        #if there are no texture connected to determin the fresnel type ,use ior 1.5 
        #ior is more accuacy than f0, ior has a higher priority
            thisAbstractMaterial.primaryFresnelType = 'IOR'
            thisAbstractMaterial.attrs['primaryReflectionIOR'] = materialConverter.Attr('primaryReflectionIOR','default')
            thisAbstractMaterial.attrs['primaryReflectionIOR'].value = 1.5
        else:
            thisAbstractMaterial.primaryFresnelType = 'F0'
            thisAbstractMaterial.attrs['primaryReflectionF0'] = materialConverter.Attr('primaryReflectionF0','default')
            thisAbstractMaterial.attrs['primaryReflectionF0'].value = 0.04
    return fileNodes

def __createDisplacement_connect(heightFileNode,targetMaterial,heightDepth,heightMap_8bit):
    global zeroHeight
    global targetMaterialType

    disNode = mc.shadingNode('displacementShader',asShader = 1)
    mc.setAttr(disNode + '.scale',heightDepth)
    mc.connectAttr(heightFileNode.outAttr,disNode + '.displacement')

    if heightMap_8bit:
        mc.setAttr(heightFileNode.specificFileNode + '.alphaOffset',-zeroHeight)

    sgNode = basicOperater.createShadingGroup_connectDisplacement(targetMaterial, disNode)
    renderer = materialConverter.getRendererName(targetMaterialType)
    if renderer =='Redshift':
        basicOperater.convertMayaDisNodeToRsDisNode(sgNode)

def import_replaceMaterialsByName(*args):
    global materialName
    prepareGlobalVars()
    materialNames = materialName.split(';')
    if len(materialNames) >1:
        for material in materialNames:
            mc.hyperShade(o = material)
            objects = mc.ls(sl = 1)
            import_assignToSelectedObjects(material,objects)
    else:
        objects = mc.ls(sl = 1)
        import_assignToSelectedObjects(materialNames[0],objects)



def import_assignToSelectedObjects(thisMaterial,thisObjects,*args):
    sels = thisObjects
    objSelected = False
    if sels != []:
        for sel in sels:
            if mc.objectType(sel) == 'transform' or mc.objectType(sel) == 'mesh':
                objSelected = True
                break

    prepareGlobalVars()
    global textureTemplateUsing
    global userDefinedPath
    global targetMaterialType
    global usingMayaColorManagement
    global isUdim
    global openglNormal
    import_assignToSelectedObjectsNeedData = dataClass.Data(['textureTemplates','materialAttrs','bumpAttrs','subdiv_displacementAttrs'])
    dataDict = import_assignToSelectedObjectsNeedData.prepareData()
    materialDataClass = dataClass.Data(['materialAttrs'])
    materialAttrsDataDict = materialDataClass.prepareData()
    print dataDict
    textureTemplatesData = dataDict['textureTemplates']

    bumpData = dataDict['bumpAttrs']
    print bumpData
    materialAttrsData = materialAttrsDataDict

    print 'materialAttrsData'
    print materialAttrsData
    subdiv_displacementData = dataDict['subdiv_displacementAttrs']
    defaultAttr_specificAttr_dict =  textureTemplatesData[textureTemplateUsing]


    for key in defaultAttr_specificAttr_dict:
        if defaultAttr_specificAttr_dict[key] == '':
            defaultAttr_specificAttr_dict[key] = 'none'
    renderer = materialConverter.getRendererName(targetMaterialType)


    thisAbstractMaterial = Material('Default', materialAttrsData['Default'])
    thisAbstractMaterial.attrs['primaryReflectionBRDF'] = materialConverter.Attr('primaryReflectionBRDF',"{0:'default',1:'ggx'}")
    thisAbstractMaterial.attrs['primaryReflectionBRDF'].value = 1
    thisAbstractMaterial.attrs['primaryReflectionWeight'] = materialConverter.Attr('primaryReflectionWeight','default')
    thisAbstractMaterial.attrs['primaryReflectionWeight'].value = 1
    thisAbstractMaterial.attrs['primaryReflectionColor'] = materialConverter.Attr('primaryReflectionColor','default')
    thisAbstractMaterial.attrs['primaryReflectionColor'].value = [1,1,1]
    thisAbstractMaterial.attrs['diffuseWeight'] = materialConverter.Attr('diffuseWeight','default')
    thisAbstractMaterial.attrs['diffuseWeight'].value = 1
    thisAbstractMaterial.attrs['diffuseColor'] = materialConverter.Attr('diffuseColor','default')
    thisAbstractMaterial.attrs['diffuseColor'].value = [1,1,1]
    fileNodes = __setAbstractMaterial(thisAbstractMaterial,defaultAttr_specificAttr_dict, userDefinedPath, thisMaterial,materialAttrsData,textureTemplatesData,usingMayaColorManagement, isUdim)
    

    targetMaterial = Material(targetMaterialType, materialAttrsData[targetMaterialType])

    thisAbstractMaterial.convertTo(targetMaterial)
    targetMaterial = thisAbstractMaterial.createShader(name = thisMaterial)
    wastedBumpNode = None
    bumpFileNode = None
    #create and connect uv node
    uvNode = mc.shadingNode('place2dTexture',au = 1)
    for fileNode in fileNodes:
        if fileNode.bumpNode is not None:
            bumpFileNode = fileNode
            wastedBumpNode = fileNode.bumpNode
        basicOperater.connectUVNodeToTextureNode(uvNode, fileNode.specificFileNode)

    
    #create correct bump node for material
    if renderer == 'vray':
        inputBumpTextureNode = mc.listConnections(wastedBumpNode + '.bumpValue')[0]
        inputAttr = inputBumpTextureNode + '.outColor'
        outputAttr = mc.listConnections(wastedBumpNode + '.outNormal',p = 1)[0]
        mc.connectAttr(inputAttr , outputAttr,f = 1)

    bumpNode = materialConverter.convertConnect_BumpNode(bumpData, materialAttrsData, [targetMaterial], targetMaterialType)
    if bumpNode is not None:
        if openGLNormal:
            if renderer == 'Redshift':
                mc.setAttr(bumpNode + '.flipY', 0)
            if renderer == 'arnold':
                mc.setAttr(bumpNode + '.aiFlipR',0)
                mc.setAttr(bumpNode + '.aiFlipG',0)
            if renderer == 'vray':
                pass
        else:
            if renderer == 'Redshift':
                mc.setAttr(bumpNode + '.flipY', 1)
            if renderer == 'arnold':
                mc.setAttr(bumpNode + '.aiFlipR',0)
                mc.setAttr(bumpNode + '.aiFlipG',1)
            if renderer == 'vray':
                normalFileNode = mc.listConnections(bumpNode + '.bumpMap')[0]
                outNode = materialConverter.createVrayDirectXNormalConnect(normalFileNode)
                mc.connectAttr(outNode + '.outColor',bumpNode + '.bumpMap',f = 1)
                #outNode = materialConverter.createVrayDirectXNormalConnect(bumpFileNode.specificFileNode)

                #mc.connectAttr(outNode + '.outColor' ,bumpNode + '.bumpMap')

    #delete unused bump node 
    if wastedBumpNode is not None:
        mc.delete(wastedBumpNode)


    #create disNode
    global heightMap_8bit
    global heightDepth
    global heightMapAsDisplacement
    if heightMapAsDisplacement and thisAbstractMaterial.heightFileNode is not None:
        __createDisplacement_connect(thisAbstractMaterial.heightFileNode,targetMaterial,heightDepth,heightMap_8bit)
        
        
        #if something selected,set the selected objects' subdiv_dis attrs
        if objSelected:
            mc.select(sels)
            materialConverter.convertSet_SudivsDisplacementForSelected(subdiv_displacementData,'Default',renderer)
    if objSelected:
        
        mc.select(sels)
        mc.hyperShade(a = targetMaterial)


    mc.select(targetMaterial)

    #mc.nodeEditor('hyperShadePrimaryNodeEditor',e = 1, nodeViewMode = 'connected') 
    '''
    try:
        maya.mel.eval('hyperShadePanelGraphCommand("hyperShadePanel1", "rearrangeGraph")')
    except:
        pass
    '''