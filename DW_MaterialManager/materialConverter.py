#encoding:utf-8
#material converter
import maya.cmds as mc
import pymel.core as pm
from collections import OrderedDict
import sys
import math
import json
import basicOperater
import UI
from nodeClass import *
from dataClass import *
reload(basicOperater)
#global var

unknownNodes = []
mayaVersion = int(mc.about(version = 1)[:4])

#around line 90 don't support udim types beside mari
class Attr(object):
    def __init__(self,attrName,operater):
        self.attrName = str(attrName)
        self.operater = operater
        self.value = None
        self.inputNode = None
        self.inputAttr = None
        self.superNode = None
        self.textureFileNode = None
    def __str__(self):
        return self.attrName
    def __add__(self,other):
        return self.attrName + other
    def __radd__ (self,other):
        return other+ self.attrName
    def getAttrFrom(self,superNode):
        self.superNode = superNode
        # if the attr is only for outpass data, this attr should not get data
        try:
            if self.attrName != 'outOnly':
                inputNode = mc.listConnections(superNode + '.' + self.attrName)
                inputAttr = mc.listConnections(superNode + '.' + self.attrName,p = 1)

                if inputNode is None:
                    self.value = pm.getAttr(superNode + '.' + self.attrName)
                else:
                    #maybe wrong here, one node can connect multi nodes
                    self.inputNode = inputNode[0]
                    self.inputAttr = inputAttr[0]
        except:
            pass

    def numberConvert(self,targetAttr):
        def __getVrayNormalType():
            upStreamNodes = mc.listHistory(self.superNode + '.bumpMap')
            textureFileNode = [node for node in upStreamNodes if mc.objectType(node) =='file'][0]
            connectToShaderNode = mc.listConnections(self.superNode,s = 1 ,d = 0)[0]
            #setting the normal maps'  normal type
            if connectToShaderNode != textureFileNode:
                self.value = True
        # to remap the value ,linear function
        def __linearLerp(origNumberString):
            numbers = origNumberString[5:].split(';')
            leftNumbers = numbers[0].strip('()')
            rightNumbers = numbers[1].strip('()')
            oldMin = float(leftNumbers.split('-')[0])
            oldMax = float(rightNumbers.split('-')[0])
            newMin = float(leftNumbers.split('-')[1])
            newMax = float(rightNumbers.split('-')[1])

            a = (newMax - newMin)/(oldMax - oldMin)
            b = (oldMin * newMax - oldMax * newMin)/(oldMin - oldMax)
            return[a,b]

        #if there are multi operaters, loop them
        '''
        selfOperaters = []
        targetAttrOperaters = []
        if '+' in self.operater:
            selfOperaters = self.operater.split(' + ')
        else:
            selfOperaters.append(self.operater)
        if '+' in targetAttr.operater:
            targetAttrOperaters = targetAttr.operater.split(' + ')
        else:
            targetAttrOperaters.append(targetAttr.operater)
        '''

        print self.value
        print 'before'
        print ''

        #this remap must happen before reverse
        if 'remap' in self.operater:
            a,b = __linearLerp(self.operater)
            self.value = self.value*a + b

        if (self.operater == 'reverse' and targetAttr.operater != 'reverse') or (self.operater != 'reverse' and targetAttr.operater == 'reverse'):
            self.value = 1 - self.value

        #this remap must happen after reverse
        if 'remap' in targetAttr.operater:
            a,b = __linearLerp(targetAttr.operater)
            self.value = (self.value - b)/a

        if self.operater == 'vector3ToScalar' and targetAttr.operater != 'vector3ToScalar':
            self.value = (self.value[0] + self.value[1] + self.value[2])/3.0
        

        if self.operater == 'vector3ToScalar + reverse' and targetAttr.operater != 'vector3ToScalar + reverse':
            print  self.value
            self.value = (self.value[0] + self.value[1] + self.value[2])/3.0
            self.value = 1 - self.value
        


        # boolize the value 0 to False,every other number to True
        if self.operater =='boolize' or self.operater =='ignoreTrueBoolize':
            if self.value != 0:
                self.value = 1
        if  'boolize_onlyTrue' in self.operater:
            trueValue = int(self.operater[-1])
            if self.value == trueValue:
                self.value = 1
            else:
                self.value = 0

        if self.operater[:7] =='outOnly':
            thisOutValue = self.operater[8:]
            self.value = int(thisOutValue)
        if 'boolize_default' in self.operater :
            defaultValue = int(self.operater[15:])

            if self.value != 0 and self.value != 1 and self.value != defaultValue:
                self.value = defaultValue

        if self.operater == 'getVrayNormalType':
            __getVrayNormalType()




        if targetAttr.operater == 'vector3ToScalar + reverse' and self.operater != 'vector3ToScalar + reverse':
            self.value = 1- self.value
            self.value = (self.value,self.value,self.value)

        if targetAttr.operater == 'vector3ToScalar' and self.operater != 'vector3ToScalar':
            self.value = (self.value,self.value,self.value)
        #for the arnold enableDisplacement and displacement scale both controlled by aiDispHeight
        if targetAttr.operater == 'F0_IOR':
            #keep divide zero safety
            if self.value == 1:
                self.value = 0.99
            self.value = (1 + math.sqrt(self.value))/ (1 - math.sqrt(self.value))
            #for vray ,the ior's max value is 100
            if self.value >100:
                self.value = 100
        if targetAttr.operater == 'IOR_F0':
            self.value = ((self.value -1)/(self.value + 1))**2
        if targetAttr.operater == 'Metal_F0':
            self.value = 0.96*self.value + 0.04
        if targetAttr.operater == 'DiffuseColor_ReflectionColor':

            [(1 - self.primaryMetalness) + colorChannel * self.primaryMetalness for colorChannel in self.value]
        # for some attr ,will be set two times,if false ,set to false 
        #if true don't touch it ,use the previous attr
        if targetAttr.operater == 'ignoreTrueBoolize':

            if self.value == 1:
                self.value = None
        if  'boolize_onlyTrue' in targetAttr.operater:
            trueValue = int(targetAttr.operater[-1])
            if self.value  == 1:
                self.value = trueValue
            else:
                self.value = 0
        if self.operater[0] == '{':
            thisDict = eval(self.operater)
            targetDict = eval(targetAttr.operater)
            targetDictReversed = {v:k for k,v in targetDict.items()}
            #if it is a translating attr, get the translated value
            if self.value in thisDict.keys():
                self.value = thisDict[self.value]
                self.value = targetDictReversed[self.value]
            #if it is not a translating attr, set the attr to default to translate
            else:
                thisDictReversed = {v:k for k,v in thisDict.items()}
                for key in thisDictReversed:
                    if 'default' in key:
                        self.value = thisDictReversed[key]
        
        if 'outOnly'in targetAttr.operater or 'none' == targetAttr.operater:
            'not using this ??????????????????????????'
            self.value = None
        if self.operater == 'none' :
            self.value = None

        if (self.operater == '1/x' and targetAttr.operater != '1/x') or (self.operater != '1/x' and targetAttr.operater == '1/x'):
            self.value = 1 / self.value
        




    def nodeConvert(self,targetAttr):
        #set all the file nodes color space right
        #for upStreamNode in upStreamNodes:
         #   if mc.objectType(upStreamNode) == 'file' and 'color' in origAttrs[i].lower():
         #       mc.setAttr(upStreamNode + '.colorSpace','gamma 2.2 Rec 709',type = 'string')
          #  if mc.objectType(upStreamNode) == 'file' and 'color' not in origAttrs[i].lower():
          #      mc.setAttr(upStreamNode + '.colorSpace','gamma 2.2 Rec 709',type = 'string')
        def __none():
            self.inputAttr = None
        def __reverseNode():
                #get all attrs connected to inputNode

                reverseNode = mc.shadingNode('reverse',au = 1)
                
                mc.connectAttr(self.inputAttr ,reverseNode + '.input.inputX')
                self.inputAttr = reverseNode + '.output.outputX'
        def __vecotr3ToScalar():
            luminanceNode = mc.shadingNode('luminance',au = 1)
            mc.connectAttr(self.inputAttr,luminanceNode + '.value')
            self.inputAttr = luminanceNode + '.outValue'
        def __scalarToVector3():
            remapHsvNode = mc.shadingNode('remapHsv',au = 1)
            mc.connectAttr(self.inputAttr,remapHsvNode + '.color.colorR')
            mc.connectAttr(self.inputAttr,remapHsvNode + '.color.colorG')
            mc.connectAttr(self.inputAttr,remapHsvNode + '.color.colorB')
            self.inputAttr = remapHsvNode + '.outColor'
        def __useOutColor():
            self.inputAttr = self.inputNode + '.outColor'
        def __useOutAlpha():
            self.inputAttr = self.inputNode + '.outAlpha'


        def __setFileTextureNameFromFileNode():
            def __setUVRepeat(rsNormalMapNode):
                #setUV
                place2dTextureNode = None
                fileNodeInputNodes = mc.listConnections(self.inputNode,s = 1,d = 0)
                for fileNodeInputNode in fileNodeInputNodes:
                    if mc.objectType(fileNodeInputNode)  == 'place2dTexture':
                        place2dTextureNode = fileNodeInputNode
                
                if place2dTextureNode is not None:
                    repeatU = mc.getAttr(place2dTextureNode + '.repeatU')
                    repeatV = mc.getAttr(place2dTextureNode + '.repeatV')
                    mc.setAttr(rsNormalMapNode + '.repeats0',repeatU)
                    mc.setAttr(rsNormalMapNode + '.repeats1',repeatV)


            upStreamNodes = mc.listHistory(self.inputNode)
            textureFileNode = [node for node in upStreamNodes if mc.objectType(node) =='file'][0]
            connectToShaderNode = mc.listConnections(self.inputNode,s = 1 ,d = 0)[0]
            fileTextureName = mc.getAttr(textureFileNode + '.fileTextureName')
            if mc.getAttr(textureFileNode + '.uvTilingMode') == 3:
                fileTextureName = fileTextureName.rpartition('.')[0][:-4] + '<UDIM>.' + fileTextureName.rpartition('.')[2]
            rsNormalMapNode = mc.shadingNode('RedshiftNormalMap',au = 1)
            mc.setAttr(rsNormalMapNode + '.tex0',fileTextureName,type = 'string')
            
            __setUVRepeat(rsNormalMapNode)

            self.value = fileTextureName
            self.inputNode = rsNormalMapNode
            self.inputAttr = rsNormalMapNode + '.' + self.attrName #'.outDisplacementVector'
        def __createFileNodeFromFileTextureName():
            def __setUVRepeat(thisFileNode):
                rsNormalMapNode = self.superNode
                if rsNormalMapNode is not None:
                    repeatU = mc.getAttr(rsNormalMapNode + '.repeats0')
                    repeatV = mc.getAttr(rsNormalMapNode + '.repeats1')
                    uvNode = mc.shadingNode('place2dTexture',au = 1)
                    basicOperater.connectUVNodeToTextureNode(uvNode,thisFileNode)
                    mc.setAttr(uvNode + '.repeatU',repeatU)
                    mc.setAttr(uvNode + '.repeatV',repeatV)
            global mayaVersion
            fileNode = basicOperater.FileNode()

            
            fileTextureName = self.value
            isUdim = False
            if fileTextureName is not None:
                if '<udim>' in fileTextureName.lower():
                    isUdim = True
            #set color space must be after the fileTexture name set!
            fileNode.fileTextureName = fileTextureName
            fileNode.asColor = True
            fileNode.colorSpace = 'Raw'
            fileNode.createFileNode(True, isUdim)
            #setUV
            __setUVRepeat(fileNode.specificFileNode)
            

            self.inputNode = fileNode.outNode
            self.inputAttr = fileNode.outAttr    

        def __F0_IOR():
            #keep from divide by zero
            try:
                mc.setAttr(self.inputNode + '.alphaGain',0.99)
            except:
                pass
            F0NodeAttr = NodeAttr(self.inputAttr)
            IOR  = (1 + F0NodeAttr**0.5)/(1 - F0NodeAttr**0.5)
            self.inputAttr = IOR.fullName
        def __IOR_F0():
            IORNodeAttr = NodeAttr(self.inputAttr)
            F0 = ((IORNodeAttr - 1)/(IORNodeAttr + 1))**2
            self.inputAttr = F0.fullName
        def __Metal_F0():
            metalnessAttrClass = NodeAttr(self.inputAttr)
            F0Class = metalnessAttrClass * 0.96 + 0.04
            self.inputAttr = F0Class.fullName

        if (self.operater == 'reverse' and targetAttr.operater != 'reverse') or (self.operater != 'reverse' and targetAttr.operater == 'reverse'):
            __reverseNode()
        if self.operater == 'scalarToVector3' and targetAttr.operater == 'scalarToVector3':
            pass
        if self.operater == 'vector3ToScalar' and targetAttr.operater != 'vector3ToScalar':
            __vecotr3ToScalar()
        if self.operater == 'createFile':
            __createFileNodeFromFileTextureName()
        if self.operater == 'scalarToVector3'and targetAttr.operater != 'scalarToVector3':
            __scalarToVector3()
        if self.operater == 'useOutColor':
            __useOutColor()
        
        if targetAttr.operater == 'useOutColor':
            __useOutAlpha()
        if targetAttr.operater == 'F0_IOR':
            __F0_IOR()
        if targetAttr.operater == 'IOR_F0':
            __IOR_F0()
        if targetAttr.operater == 'Metal_F0':
            __Metal_F0()
        if targetAttr.operater =='createFile':
            __setFileTextureNameFromFileNode()
        if targetAttr.operater == 'vector3ToScalar'and self.operater != 'vector3ToScalar':
            __scalarToVector3()
        if targetAttr.operater == 'scalarToVector3' and self.operater != 'scalarToVector3':
            __vecotr3ToScalar()

        if (targetAttr.operater) == 'none' or('outOnly'in targetAttr.operater):
            __none()
        if self.operater == 'none':
            __none()

        
        
    #def __customConvert(self):

    def convertTo(self,targetAttr):
        # if there is no texture connected to the attr ,just use the attr numb
        if self.operater == 'getVrayNormalType':
            self.numberConvert(targetAttr)
        if self.inputNode is None and self.value is not None and self.attrName != 'tex0':
            self.numberConvert(targetAttr)
            
        #for the rs normal node , its bumpType cant get from specific obj
        #give it a name called outOnly , and the operater is outOnly_ with a number
        if self.value is None and 'outOnly_' in self.operater:
            self.numberConvert(targetAttr)
        elif self.inputNode is not None or self.attrName == 'tex0':

            self.nodeConvert(targetAttr)
        self.attrName = targetAttr.attrName


class Converter(object):
    def __init__(self,converterType,converterAttrs):
        self.attrs = {}
        self.specificObjectName = ''
        self.converterType = converterType
        for key in converterAttrs:
            # if there is no such attr ,ignore!!!!
            if str(converterAttrs[key][0]) != 'none':
                self.attrs[key] = Attr(converterAttrs[key][0],converterAttrs[key][1])
    def __str__(self):
        return self.converterType
    __repr__ = __str__
    
    def __getattr__(self,attr):
        for self.attr in self.attrs:
            if attr == self.attr:
                return self.attrs[self.attr]
    def getAttrsFrom(self,specificObject):
        
        self.specificObjectName = specificObject
        for key in self.attrs:
            self.attrs[key].getAttrFrom(specificObject)
    def __customConvert(self):
        pass

    def convertTo(self,targetConverter):
        #convert all the attrs of this material to target material's attr
        self.converterType = targetConverter.converterType
        deleteAttrs = []
        for origAttr in self.attrs:
            if origAttr in targetConverter.attrs.keys():
                self.attrs[origAttr].convertTo(targetConverter.attrs[origAttr])
            else:
                deleteAttrs.append(origAttr)
        #delete the attrs that the converted material will not have
        for deleteAttr in deleteAttrs:
            self.attrs.pop(deleteAttr)

        self.__customConvert()

        return self

class Material(Converter):
    def __init__(self,converterType,converterAttrs):
        super(Material,self).__init__(converterType,converterAttrs)

        self.primaryFresnelType = None   
        self.primaryF0Attr = None
        self.primaryIORAttr = None
        self.primaryMetalnessAttr = None

        self.secondaryFresnelType = None
        self.secondaryF0Attr = None
        self.secondaryMetalnessAttr = None
        self.secondaryMetalnessInputNodeAttr = None

        self.heightFileNode = None
    def __getMetalness(self,specificObject,primaryMetalnessAttrName,secondaryMetalnessAttrName):
        primaryMetalnessInputs = mc.listConnections(specificObject + '.' + primaryMetalnessAttrName)
        self.primaryMetalnessAttr = Attr(primaryMetalnessAttrName, 'default')
        self.primaryMetalnessAttr.getAttrFrom(specificObject)
        if secondaryMetalnessAttrName is not None:
            self.secondaryMetalnessAttr = Attr(secondaryMetalnessAttrName, 'default')
            self.secondaryMetalnessAttr.getAttrFrom(specificObject)
        
    def getFresnelTypeFrom(self,specificObject):
        if self.converterType == 'RedshiftArchitectural':
            primaryTempType = mc.getAttr(specificObject + '.brdf_fresnel')
            if primaryTempType == 1:
                self.primaryFresnelType = 'IOR'
                self.primaryIORAttr = Attr('brdf_fresnel_ior', 'default')
                self.primaryIORAttr.getAttrFrom(specificObject)
            elif primaryTempType == 0:
                self.primaryFresnelType = 'F0'
                self.primaryF0Attr = Attr('brdf_0_degree_refl','default')
                self.primaryF0Attr.getAttrFrom(specificObject)
            
            secondaryTempType = mc.getAttr(specificObject + '.brdf_base_fresnel')
            if secondaryTempType == 1:
                self.secondaryFresnelType = 'IOR'
                self.secondaryIORAttr = Attr('brdf_base_fresnel_ior', 'default')
                self.secondaryIORAttr.getAttrFrom(specificObject)
            elif secondaryTempType == 0:
                self.secondaryFresnelType = 'F0'
                self.secondaryF0Attr = Attr('brdf_base_0_degree_refl','default')
                self.secondaryF0Attr.getAttrFrom(specificObject)
        
        elif self.converterType  == 'RedshiftMaterial':
            primaryTempType = mc.getAttr(specificObject + '.refl_fresnel_mode')
            if primaryTempType == 1:
                self.primaryFresnelType = 'F0'
                self.primaryF0Attr = Attr('refl_reflectivity','vector3ToScalar')
                self.primaryF0Attr.getAttrFrom(specificObject)
            elif primaryTempType == 3:
                self.primaryFresnelType = 'IOR'
                self.primaryIORAttr = Attr('refl_ior', 'default')
                self.primaryIORAttr.getAttrFrom(specificObject)
            elif primaryTempType == 2:
                self.primaryFresnelType = 'Metal'
                self.__getMetalness(specificObject,'refl_metalness',None)
            
            secondaryTempType = mc.getAttr(specificObject + '.refl_fresnel_mode')
            if secondaryTempType == 1:
                self.secondaryFresnelType = 'F0'
                self.secondaryF0Attr = Attr('coat_reflectivity','vector3ToScalar')
                self.secondaryF0Attr.getAttrFrom(specificObject)
            elif secondaryTempType == 3:
                self.secondaryFresnelType = 'IOR'
                self.secondaryIORAttr = Attr('coat_ior','default')
                self.secondaryIORAttr.getAttrFrom(specificObject)

        elif self.converterType  == 'aiStandard':
            tempType = mc.getAttr(specificObject + '.specularFresnel')
            if tempType == 0:
                self.primaryFresnelType  = 'noFresnel'
            elif tempType == 1:
                self.primaryFresnelType  = 'F0'
                self.primaryF0Attr = Attr('Ksn','default')
                self.primaryF0Attr.getAttrFrom(specificObject)

        
        elif self.converterType  == 'aiStandardSurface':
            primaryMetalnessInputs = mc.listConnections(specificObject + '.metalness')
            

            if primaryMetalnessInputs is None:
                primaryTempType = mc.getAttr(specificObject + '.metalness')
                if primaryTempType != 0:
                    self.primaryFresnelType = 'Metal'
                    self.primaryMetalnessAttr = Attr('metalness', 'default')
                    self.primaryMetalnessAttr.getAttrFrom(specificObject)
                else:
                    self.primaryFresnelType = 'IOR'
                    self.primaryIORAttr = Attr('specularIOR', 'default')
                    self.primaryIORAttr.getAttrFrom(specificObject)
            else:
                self.primaryFresnelType = 'Metal'

            self.__getMetalness(specificObject,'metalness',None)
            # secondary fresnel type only have ior mode
            secondaryFresnelType = 'IOR'

        elif self.converterType  == 'alSurface':
            primaryMetalnessInputs = mc.listConnections(specificObject + '.specular1FresnelMode')
            primaryTempType = mc.getAttr(specificObject + '.specular1FresnelMode')

            if primaryTempType == 0:
                self.primaryFresnelType = 'IOR'
                self.primaryIORAttr = Attr('specular1Ior', 'default')
                self.primaryIORAttr.getAttrFrom(specificObject)
            elif primaryTempType == 1:
                self.primaryFresnelType = 'F0'
                self.primaryF0Attr = Attr('specular1Reflectivity','vector3ToScalar')
                self.primaryF0Attr.getAttrFrom(specificObject)
            
            secondaryTempType = mc.getAttr(specificObject + '.specular2FresnelMode')
            if secondaryTempType == 0:
                self.secondaryFresnelType = 'IOR'
                self.secondaryIORAttr = Attr('specular2Ior', 'default')
                self.secondaryIORAttr.getAttrFrom(specificObject)
            elif secondaryTempType == 1:
                self.secondaryFresnelType = 'F0'
                self.secondaryF0Attr = Attr('specular2Reflectivity','vector3ToScalar')
                self.secondaryF0Attr.getAttrFrom(specificObject)
            
        elif self.converterType == 'VRayMtl':
            self.primaryFresnelType = 'IOR'
            self.primaryIORAttr = Attr('fresnelIOR', 'default')
            self.primaryIORAttr.getAttrFrom(specificObject)
    def __setFresnelType(self,specificObject):
        def __diffuseColor_reflectionColor(specificObject, diffuseColorName,metalnessAttr,reflectionColorName):
            if metalnessAttr is not None and diffuseColorName is not None:
                diffuseColorAttr = Attr(diffuseColorName, 'default')
                diffuseColorAttr.getAttrFrom(specificObject)
                if diffuseColorAttr.inputNode is None and metalnessAttr.inputNode is None:
                    reflectionColor = [(1 - metalnessAttr.value) + colorChannel * metalnessAttr.value for colorChannel in diffuseColorAttr.value]
                    pm.setAttr(specificObject + '.' + reflectionColorName, reflectionColor)
                elif diffuseColorAttr.inputNode is not None and metalnessAttr.inputNode is None:
                    diffuseColorNodeAttrClass = NodeAttr(diffuseColorAttr.inputAttr)
                    reflectionColor = [(1- metalnessAttr.value),(1- metalnessAttr.value),(1- metalnessAttr.value)] + diffuseColorNodeAttrClass * metalnessAttr.value
                    mc.connectAttr(reflectionColor.fullName, specificObject + '.' + reflectionColorName,f = 1)
                elif diffuseColorAttr.inputNode is None and metalnessAttr.inputNode is not None:
                    metalnessNodeAttrClass = NodeAttr(metalnessAttr.inputAttr)
                    reflectionColor = (1 - metalnessNodeAttrClass) + diffuseColorAttr.value * metalnessNodeAttrClass
                    mc.connectAttr(reflectionColor.fullName, specificObject + '.' + reflectionColorName,f = 1)
                elif diffuseColorAttr.inputNode is not None and metalnessAttr.inputNode is not None:
                    diffuseColorNodeAttrClass = NodeAttr(diffuseColorAttr.inputAttr)
                    metalnessNodeAttrClass = NodeAttr(metalnessAttr.inputAttr)
                    reflectionColorAttr =  (1 -metalnessNodeAttrClass) + diffuseColorNodeAttrClass * metalnessNodeAttrClass
                    mc.connectAttr(reflectionColorAttr , specificObject + '.'+reflectionColorName,f = 1)
        def __metalnessControlDiffuseColor(specificObject,diffuseColorName,metalnessAttr):
            reverseNode = mc.shadingNode('reverse',au = 1)
            multiplyDivideNode = mc.shadingNode('multiplyDivide',au = 1)
            if metalnessAttr is not None and diffuseColorName is not None:
                diffuseColorAttr = Attr(diffuseColorName, 'default')
                diffuseColorAttr.getAttrFrom(specificObject)
                if diffuseColorAttr.inputNode is None and metalnessAttr.inputNode is None:
                    realDiffuseColor =  [(1 -metalnessAttr.value) *colorChannel  for colorChannel in diffuseColorAttr.value]
                    pm.setAttr(specificObject + '.' + diffuseColorName, realDiffuseColor)
                elif diffuseColorAttr.inputNode is not None and metalnessAttr.inputNode is None:
                    diffuseColorNodeAttrClass = NodeAttr(diffuseColorAttr.inputAttr)
                    realDiffuseColor = [(1- metalnessAttr.value),(1- metalnessAttr.value),(1- metalnessAttr.value)] * diffuseColorNodeAttrClass 
                    mc.connectAttr(realDiffuseColor.fullName, specificObject + '.' + diffuseColorName,f = 1)
                elif diffuseColorAttr.inputNode is None and metalnessAttr.inputNode is not None:
                    metalnessNodeAttrClass = NodeAttr(metalnessAttr.inputAttr)
                    realDiffuseColor = (1 - metalnessNodeAttrClass) * diffuseColorAttr.value
                    mc.connectAttr(realDiffuseColor.fullName, specificObject + '.' + diffuseColorName,f = 1)
                elif diffuseColorAttr.inputNode is not None and metalnessAttr.inputNode is not None:
                    diffuseColorNodeAttrClass = NodeAttr(diffuseColorAttr.inputAttr)
                    metalnessNodeAttrClass = NodeAttr(metalnessAttr.inputAttr)
                    realDiffuseColorAttr =  (1 -metalnessNodeAttrClass) * diffuseColorNodeAttrClass 
                    mc.connectAttr(realDiffuseColorAttr , specificObject + '.'+ diffuseColorName,f = 1)
        def __Metal_F0(specificObject,diffuseColorName,metalnessAttrClass,reflectionName,f0Name,vecotr3ToScalar):
            __diffuseColor_reflectionColor(specificObject, diffuseColorName, metalnessAttrClass,reflectionName)
            __metalnessControlDiffuseColor(specificObject, diffuseColorName, metalnessAttrClass)
            F0Attr = Attr('F0', 'Metal_F0')
            if self.primaryMetalnessAttr is not None:
                self.primaryMetalnessAttr.convertTo(F0Attr)
                if self.primaryMetalnessAttr.inputNode is None:
                    F0 = self.primaryMetalnessAttr.value
                    mc.setAttr(specificObject + '.' + f0Name,F0)
                else:
                    F0 = self.primaryMetalnessAttr.inputAttr

                    # the brdf_0_degree_refl only get scalar, should only plug one channel into it
                    if vecotr3ToScalar:
                        luminanceNode = mc.shadingNode('luminance',au = 1)
                        mc.connectAttr(F0,luminanceNode + '.value',f = 1)
                        resultAttr = luminanceNode + '.outValue'
                    else:
                        resultAttr = F0 +'.output3Dx'

                mc.connectAttr(resultAttr,specificObject + '.' +f0Name,f = 1)
        def __Metal_IOR(specificObject,diffuseName,metalnessAttrClass,reflectionName,IORName,vecotr3ToScalar):
            __diffuseColor_reflectionColor(specificObject, diffuseName, metalnessAttrClass,reflectionName)
            __metalnessControlDiffuseColor(specificObject, diffuseName, metalnessAttrClass)
            F0Attr = Attr('F0', 'Metal_F0')
            IORAttr = Attr('IOR','F0_IOR')
            metalnessTextureFileNode = metalnessAttrClass.inputNode
            #prevent divide zero, when converting into ior
            mc.setAttr(metalnessTextureFileNode + '.alphaGain',0.99)
            if self.primaryMetalnessAttr is not None:
                self.primaryMetalnessAttr.convertTo(F0Attr)
                self.primaryMetalnessAttr.convertTo(IORAttr)
                if self.primaryMetalnessAttr.inputNode is None:
                    IOR = self.primaryMetalnessAttr.value
                    mc.setAttr(specificObject + '.' + IORName,IOR)
                else:
                    IOR = self.primaryMetalnessAttr.inputAttr

                    if vecotr3ToScalar:
                        luminanceNode = mc.shadingNode('luminance',au = 1)
                        mc.connectAttr(F0,luminanceNode + '.value',f = 1)
                        resultAttr = luminanceNode + '.outValue'
                    else:
                        resultAttr = IOR +'.outputX'
                    mc.connectAttr(resultAttr,specificObject + '.' +IORName,f = 1)

        if self.converterType == 'RedshiftArchitectural':
            if self.primaryFresnelType == 'noFresnel':
                mc.setAttr(specificObject + '.brdf_fresnel',0)
                mc.setAttr(specificObject + '.brdf_0_degree_refl',1)
                mc.setAttr(specificObject + '.brdf_90_degree_refl',1)

            if self.primaryFresnelType == 'IOR':
                mc.setAttr(specificObject + '.brdf_fresnel',1)
                mc.setAttr(specificObject + '.brdf_fresnel_lockIOR',0)
            if self.secondaryFresnelType == 'IOR':
                mc.setAttr(specificObject + '.brdf_base_fresnel',1)
                mc.setAttr(specificObject + '.brdf_base_fresnel_lockIOR',0)

            if self.primaryFresnelType == 'F0':
                mc.setAttr(specificObject + '.brdf_fresnel',0)
            if self.secondaryFresnelType == 'F0':
                mc.setAttr(specificObject + '.brdf_base_fresnel',0)  

            if self.primaryFresnelType == 'Metal':
                mc.setAttr(specificObject + '.brdf_fresnel',1)
                mc.setAttr(specificObject + '.brdf_90_degree_refl',0)
                __Metal_IOR(specificObject, 'diffuse', self.primaryMetalnessAttr, 'refl_color', 'brdf_fresnel_ior', False)


            if self.secondaryFresnelType == 'Metal':
                mc.setAttr(specificObject + '.brdf_base_fresnel',1)
                mc.setAttr(specificObject + '.brdf_base_fresnel_lockIOR',0)
                __Metal_IOR(specificObject, 'diffuse', self.secondaryMetalnessAttr, 'refl_base_color', 'brdf_base_fresnel_ior', False)

        elif self.converterType == 'RedshiftMaterial':
            if self.primaryFresnelType == 'noFresnel':
                mc.setAttr(specificObject + '.refl_fresnel_mode',1)
                pm.setAttr(specificObject + '.refl_reflectivity',(1,1,1))

            if self.primaryFresnelType == 'IOR':
                mc.setAttr(specificObject + '.refl_fresnel_mode',3)
            if self.secondaryFresnelType == 'IOR':
                mc.setAttr(specificObject + '.coat_fresnel_mode',3)

            if self.primaryFresnelType == 'F0':
                mc.setAttr(specificObject + '.refl_fresnel_mode',1)
            if self.secondaryFresnelType == 'F0':
                mc.setAttr(specificObject + '.coat_fresnel_mode',1)

            if self.primaryFresnelType == 'Metal':
                mc.setAttr(specificObject + '.refl_fresnel_mode',2)
            if self.secondaryFresnelType == 'Metal':
                mc.setAttr(specificObject + '.coat_fresnel_mode',1)
                __Metal_F0(specificObject, 'diffuse_color', self.secondaryMetalnessAttr, 'coat_color','coat_reflectivity', True)



        elif self.converterType == 'aiStandard':
            if self.primaryFresnelType == 'noFresnel':
                mc.setAttr(specificObject + '.specularFresnel',0)

            if self.primaryFresnelType == 'IOR':
                mc.setAttr(specificObject + '.specularFresnel',1)
                self.primaryIORAttr.convertTo(Attr('specularFresnel','IOR_F0'))
                if self.primaryIORAttr.inputNode is None:
                    
                    F0 = self.primaryIORAttr.value
                    mc.setAttr(specificObject + '.Ksn',F0)
                else:
                    #self.primaryIORAttr.convertTo(Attr('specularFresnel','IOR_F0'))
                    F0 = self.primaryIORAttr.inputAttr
                    mc.connectAttr(F0 + '.outputX',specificObject + '.Ksn',f = 1)
            if self.primaryFresnelType == 'F0':
                mc.setAttr(specificObject + '.specularFresnel',1)

            if self.primaryFresnelType == 'Metal':
                mc.setAttr(specificObject + '.specularFresnel',1)
                __Metal_F0(specificObject, 'color', self.primaryMetalnessAttr, 'KsColor','Ksn', False)






        elif self.converterType == 'aiStandardSurface':
            if self.primaryFresnelType == 'noFresnel':
                mc.setAttr(specificObject + '.specularIOR',1000)
            #this material have IOR attr, so don't need any translate
            if self.primaryFresnelType == 'IOR':
                pass
            if self.secondaryFresnelType  == 'IOR':
                pass
            if self.primaryFresnelType == 'F0':
                self.primaryF0Attr.convertTo(Attr('specularFresnel','F0_IOR'))
                if self.primaryF0Attr.inputNode is None:
                    
                    IOR = self.primaryF0Attr.value
                    mc.setAttr(specificObject + '.specularIOR',IOR)
                else:

                    IOR = self.primaryF0Attr.inputAttr
                    mc.connectAttr(IOR + '.outputX',specificObject + '.specularIOR',f = 1)
            if self.secondaryFresnelType == 'F0':
                self.secondaryF0Attr.convertTo(Attr('coatIOR','F0_IOR'))
                if self.secondaryF0Attr.inputNode is None:
                    
                    IOR = self.secondaryF0Attr.value
                    mc.setAttr(specificObject + '.coatIOR',IOR)
                else:

                    IOR = self.secondaryF0Attr.inputAttr
                    mc.connectAttr(IOR + '.outputX',specificObject + '.coatIOR',f = 1)
            #this material have metal attr, so don't need any translate
            if self.primaryFresnelType == 'Metal':
                pass
            if self.secondaryFresnelType == 'Metal':
                # convert metal to f0
                # convert f0 to IOR
                __Metal_IOR(specificObject, 'baseColor', self.secondaryMetalnessAttr, 'coatColor','coatIOR', False)

        elif self.converterType == 'alSurface':
            if self.primaryFresnelType == 'noFresnel':
                mc.setAttr(specificObject + '.specular1FresnelMode', 1 )
                mc.setAttr(specificObject + '.specular1Reflectivity', [1,1,1] )
            #this material have IOR attr, so don't need any translate
            if self.primaryFresnelType == 'IOR':
                mc.setAttr(specificObject + '.specular1FresnelMode', 0 )
            #this material have F0 attr, so don't need any translate
            if self.primaryFresnelType == 'F0':
                mc.setAttr(specificObject + '.specular1FresnelMode', 1 )

            if self.primaryFresnelType == 'Metal':
                mc.setAttr(specificObject + '.specular1FresnelMode', 0)
                __Metal_IOR(specificObject, 'diffuseColor', self.primaryMetalnessAttr, 'specular1Color','specular1Ior', False)

            if self.secondaryFresnelType == 'IOR':
                mc.setAttr(specificObject + '.specular2FresnelMode', 0 )
            #this material have F0 attr, so don't need any translate
            if self.secondaryFresnelType == 'F0':
                mc.setAttr(specificObject + '.specular2FresnelMode', 1 )

            if self.secondaryFresnelType == 'Metal':
                mc.setAttr(specificObject + '.specular2FresnelMode', 0)
                __Metal_IOR(specificObject, 'diffuseColor', self.primaryMetalnessAttr, 'specular2Color','specular2Ior', False)  

        elif self.converterType == 'VRayMtl':
            if self.primaryFresnelType == 'noFresnel':
                mc.setAttr(specificObject + '.useFresnel', 0 )
                
            #this material have IOR attr, so don't need any translate
            if self.primaryFresnelType == 'IOR':
                mc.setAttr(specificObject + '.useFresnel', 1)
                mc.setAttr(specificObject + '.lockFresnelIORToRefractionIOR', 0)

            if self.primaryFresnelType == 'F0':
                mc.setAttr(specificObject + '.useFresnel', 1)
                mc.setAttr(specificObject + '.lockFresnelIORToRefractionIOR', 0)
                self.primaryF0Attr.convertTo(Attr('fresnelIOR','F0_IOR'))
                if self.primaryF0Attr.inputNode is None:
                    IOR = self.primaryF0Attr.value
                    mc.setAttr(specificObject + '.fresnelIOR',IOR)
                else:
                    IOR = self.primaryF0Attr.inputAttr
                    mc.connectAttr(IOR + '.outputX',specificObject + '.fresnelIOR',f = 1)
           
            if self.primaryFresnelType == 'Metal':
                mc.setAttr(specificObject + '.useFresnel', 1)
                mc.setAttr(specificObject + '.lockFresnelIORToRefractionIOR', 0)
                __Metal_IOR(specificObject, 'color', self.primaryMetalnessAttr, 'reflectionColor','fresnelIOR', False)
            
    def getMaterialAttrsFrom(self,specificObject):
        self.getAttrsFrom(specificObject)
        self.getFresnelTypeFrom(specificObject)

    def createShader(self,name = ''):
        if self.specificObjectName == '':
            rename = 'M_' + name
        else:
            rename = self.specificObjectName + '_converted_' +self.converterType
        shader = mc.shadingNode(self.converterType,asShader = 1 , n =  rename )
        
        for origAttr in self.attrs:
            tempAttr = self.attrs[origAttr]


            if tempAttr.inputNode is None and tempAttr.value is not None:

                if tempAttr.attrName in ['brdf_fresnel_ior','brdf_base_fresnel_ior']:

                    if tempAttr.value > 20:
                        tempAttr.value = 20
                pm.setAttr(shader + '.' + tempAttr,tempAttr.value)
            elif tempAttr.inputNode is not None:
                mc.connectAttr(tempAttr.inputAttr,shader + '.' + tempAttr,f = 1)  
        self.__setFresnelType(shader)        
        return shader
class Shape(Converter):
    def __customConvert(self):
        pass

    #for vray renderer if the subdiv parameter not exist,using 0
    def getAttrsFrom(self,specificObject):
        self.specificObjectName = specificObject
        for key in self.attrs:
            if  mc.objExists(specificObject + '.' + self.attrs[key]):
                self.attrs[key].getAttrFrom(specificObject)
            else:
                self.attrs[key].value = 0


    def __addVrayAttrs(self,shape):
        mc.vray("addAttributesFromGroup",shape,'vray_subdivision',1)
        mc.vray("addAttributesFromGroup",shape,'vray_subquality',1)
        mc.vray("addAttributesFromGroup",shape,'vray_displacement',1)
    def setSpecificShapeAttrs(self,shape):
        for key in self.attrs:
            tempAttr = self.attrs[key]
            if 'vray' in tempAttr.attrName:
                self.__addVrayAttrs(shape)
            if self.attrs[key].value is not None:
                mc.setAttr(shape + '.' + self.attrs[key].attrName,self.attrs[key].value)


class BumpNode(Converter):
    def createConnectBumpNodeTo(self,shader,materialData):
        shaderBumpInputAttr = materialData[mc.objectType(shader)]['bump'][0]
        #print shaderBumpInputAttr,'shaderBumpInputAttr'
        #for gerneral not vray type 
        if 'vray' not in self.converterType.lower():
            # if converted type is not rsNormal,create bumpNode
            #otherwise the bumpNode has already created in attr class
            if 'RedshiftNormalMap' != self.converterType:
                bumpNode = mc.shadingNode(self.converterType,au = 1)
            else:
                bumpNode = self.attrs['bumpTextureConnect'].inputNode
            try:
                if mc.objectType(bumpNode) == 'bump2d':
                    mc.setAttr(bumpNode + '.aiFlipR',0)
                    mc.setAttr(bumpNode + '.aiFlipG',0)
            except:
                mc.warning('arnold attribute FlipR channel not found !')

            #bump2d or rsBumpMap
            for origAttr in self.attrs:
                tempAttr = self.attrs[origAttr]
                #no texture connected   the attr exist    the attr is not outOnly
                if tempAttr.inputNode is None and tempAttr.attrName != 'tex0' and tempAttr.value is not None:

                    pm.setAttr(bumpNode + '.' + tempAttr,tempAttr.value)
                elif tempAttr.inputAttr is not None:
                    upStreamNodes = mc.listHistory(tempAttr.inputNode)
                    textureFileNodes = [node for node in upStreamNodes if mc.objectType(node) =='file']
                    # if target renderer is rs and using normal map ,there will be no texture file
                    if textureFileNodes is not None and len(textureFileNodes) > 0:
                        textureFileNode = textureFileNodes[0]
                    else:
                        textureFileNode = None
                    connectToShaderNode = mc.listConnections(tempAttr.superNode,s = 1 ,d = 0)[0]

                    #mc.connectAttr(textureFileNode + '.outAlpha',bumpNode + '.' + tempAttr)
                    if textureFileNode is not None:
                        try:
                            mc.connectAttr(textureFileNode + '.outAlpha',bumpNode + '.' + tempAttr)
                        except:
                            mc.connectAttr(textureFileNode + '.outColor',bumpNode + '.' + tempAttr)
                    
                    mc.connectAttr(bumpNode + '.' + self.attrs['outAttr']  ,shader + '.'+shaderBumpInputAttr,f = 1)
            return bumpNode     
        #this converted type == vray
        if 'vray' in self.converterType.lower():
            for origAttr in self.attrs:
                tempAttr = self.attrs[origAttr]
                if tempAttr.inputNode is None and tempAttr.attrName != 'tex0' and tempAttr.value is not None and tempAttr.attrName != 'outOnly':
                    pm.setAttr(shader + '.' + tempAttr,tempAttr.value)
                elif tempAttr.inputAttr is not None and tempAttr.attrName != 'outColor' and tempAttr.attrName != 'outOnly':
                    #if converted from other renderers
                    if not self.attrs['directX'].value:
                        upStreamNodes = mc.listHistory(tempAttr.inputNode)
                        textureFileNode = [node for node in upStreamNodes if mc.objectType(node) =='file'][0]
                        nodeForConnect = textureFileNode
                    else:
                        nodeForConnect = createVrayDirectXNormalConnect(tempAttr.inputNode)

                    try:
                        mc.connectAttr(nodeForConnect + '.' + self.attrs['outAttr']  ,shader + '.' +shaderBumpInputAttr,f = 1)
                    except:
                        pass 
            return shader
        #????
        '''
        elif 'RedshiftNormalMap' == self.converterType:
            for origAttr in self.attrs:
                tempAttr = self.attrs[origAttr]
                if tempAttr.inputNode is None:
                    pm.setAttr(shader + '.' + tempAttr,tempAttr.value)
        '''



def createVrayDirectXNormalConnect(normalFileNode):
    reverseNode = mc.shadingNode('reverse',au = 1)
    remapHsvNode = mc.shadingNode('remapHsv',au = 1)
    mc.connectAttr(normalFileNode + '.outColor',reverseNode + '.input')
    mc.connectAttr(reverseNode + '.output.outputY',remapHsvNode + '.color.colorG')
    mc.connectAttr(normalFileNode + '.outColor.outColorR',remapHsvNode + '.color.colorR')
    mc.connectAttr(normalFileNode + '.outColor.outColorB',remapHsvNode + '.color.colorB')
    return remapHsvNode

def getRendererName(materialType):
    if 'RS' in materialType or 'Redshift' in materialType:
        rendererName = 'Redshift'
    elif 'ai' in materialType or 'alSurface' in materialType:
        rendererName = 'arnold'
    elif 'VRay' in materialType:
        rendererName = 'vray'
    elif 'Default' in materialType:
        rendererName = 'Default'
    else:
        rendererName = 'legacy'
    return rendererName

def getBumpNodeTypeName(targetMaterialType,origBumpType):
    if 'ai' in targetMaterialType or 'alSurface' in targetMaterialType:
        bumpNodeType = 'bump2d'
    elif 'VRay' in targetMaterialType:
        bumpNodeType = 'VRayMtl'
    elif 'Redshift' in targetMaterialType and origBumpType == 0:
        bumpNodeType = 'RedshiftBumpMap'
    elif 'Redshift' in targetMaterialType and origBumpType == 1:
        bumpNodeType = 'RedshiftNormalMap'
    else:
        bumpNodeType = ''
    return bumpNodeType

def convertSet_SudivsDisplacementForSelected(subdiv_displacementData,sourceRenderer,targetRenderer):
    selected = mc.ls(sl = 1)
    shapes = mc.ls(selected,dag = 1, s = 1)
    if selected != [] and shapes == []:
        mc.warning('no objectes selected')
    else:
        for shape in shapes:
            if mc.objectType(shape) == 'mesh':
                if sourceRenderer != 'Default' and sourceRenderer != 'legacy' and targetRenderer != 'legacy':
                    origShape = Shape(sourceRenderer, subdiv_displacementData[sourceRenderer])
                    origShape.getAttrsFrom(shape)

                    targetShape = Shape(targetRenderer, subdiv_displacementData[targetRenderer])


                    convertedShape = origShape.convertTo(targetShape)
                else:
                    origShape = Shape('Default', subdiv_displacementData['Default'])
                    origShape.attrs['enableSubdivision'].value = 1
                    origShape.attrs['enableDisplacement'].value = 1
                    origShape.attrs['subdivisions'].value = 6
                    targetShape = Shape(targetRenderer, subdiv_displacementData[targetRenderer])

                    convertedShape = origShape.convertTo(targetShape)


                convertedShape.setSpecificShapeAttrs(shape)
def convertAssign_materialForSelected(materialData,shadersConverting,targetMaterialType):
    convertedShaders = []
    #convert shader to target and assign
    for shader in shadersConverting:
        thisMaterialType = mc.objectType(shader)
        thisMaterial = Material(thisMaterialType, materialData[thisMaterialType])
        thisMaterial.getMaterialAttrsFrom(shader)

        targetMaterial = Material(targetMaterialType, materialData[targetMaterialType])
        convertedMaterial = thisMaterial.convertTo(targetMaterial)
        print 'start create shader===================='
        convertedShader = convertedMaterial.createShader()
        print 'create shader over ===================='
        convertedShaders.append(convertedShader)
        #get objects assigned the shader
        newSgNode = basicOperater.assignMaterialWithDisplacement(shader, convertedShader)
        renderer = getRendererName(targetMaterialType)
        if renderer == 'Redshift':
            basicOperater.convertMayaDisNodeToRsDisNode(newSgNode)

    return convertedShaders

def setColorSpaceForShader(shaders,sourceColorSpace, targetColorSpace,materialData,affectColorSwitch):
    def __getListWithout(thisList,*args):
        for arg in args:
            for element in thisList:
                if arg in element:
                    thisList.remove(element)
        return thisList
        
    def __setColorSpace(fileNode,colorSpace):
        mc.setAttr(fileNode + '.colorSpace',colorSpace,type = 'string')
    def __createGammaNode_connectTo(fileNode,gammaValue):
        fileNodeOutputNodes = mc.listConnections(fileNode,s = 0,d = 1)
        outputNodeInputAttrs = mc.listConnections(fileNode,s = 0,d = 1,p = 1)
         
        __getListWithout(fileNodeOutputNodes,*['defaultTextureList','materialInfo'])
        __getListWithout(outputNodeInputAttrs,*['defaultTextureList','materialInfo'])
        fileNodeOutputAttrs = [mc.listConnections(attr,s = 1,d = 0,p = 1)[0] for attr in outputNodeInputAttrs]

        for i in range(len(fileNodeOutputNodes)):
            gammaCorrectNode = mc.shadingNode('gammaCorrect',au = 1)
            mc.setAttr(gammaCorrectNode + '.gammaX',gammaValue)
            mc.setAttr(gammaCorrectNode + '.gammaY',gammaValue)
            mc.setAttr(gammaCorrectNode + '.gammaZ',gammaValue)
            if fileNodeOutputAttrs[i].rpartition('.')[-1] == 'outColor':
                mc.connectAttr(fileNodeOutputAttrs[i] , gammaCorrectNode + '.value',f = 1)
                mc.connectAttr(gammaCorrectNode + '.outValue',outputNodeInputAttrs[i],f = 1)
            elif fileNodeOutputAttrs[i].rpartition('.')[-1] == 'outAlpha':
                mc.connectAttr(fileNodeOutputAttrs[i],gammaCorrectNode + '.value.valueX',f = 1)
                mc.connectAttr(gammaCorrectNode + '.outValue.outValueX',outputNodeInputAttrs[i],f = 1)
   
    def __changeColorByGamma(shader,attrName,gammaValue):
        inputNode = mc.listConnections(shader + '.' + attrName)
        if inputNode is None:
            origColor = pm.getAttr(shader + '.' + attrName)
            changedColor = [channel**gammaValue for channel in origColor]
            pm.setAttr(shader + '.' +attrName ,changedColor)

    for shader in shaders:
        #change every color attr
        if affectColorSwitch:
            shaderType = mc.objectType(shader)
            attrs = materialData[shaderType]
            for attr in attrs.keys():
                colorAttrs = ['diffuseColor','primaryReflectionColor','secondaryReflectionColor','refractionColor','endColor','translucencyColor','pureColor']
                if attr in colorAttrs:
                    specificAttr = materialData[shaderType][attr][0]
                    #some attrs maybe none, ignore it 
                    if specificAttr != 'none':
                        if sourceColorSpace == 'orig_use_maya_colorSpace' and targetColorSpace == 'target_classic_gamma_2point2':
                            __changeColorByGamma(shader, specificAttr, 0.454)

                        
                        elif sourceColorSpace == 'orig_use_maya_colorSpace' and targetColorSpace == 'target_classic_Raw':
                            __changeColorByGamma(shader, specificAttr, 1)
                        elif sourceColorSpace == 'orig_classic_gamma_2point2' and targetColorSpace == 'target_use_maya_colorSpace':
                            __changeColorByGamma(shader, specificAttr, 2.2)
                            
                        elif sourceColorSpace == 'orig_classic_Raw' and targetColorSpace == 'target_use_maya_colorSpace':
                            __changeColorByGamma(shader, specificAttr, 1)
            
        # change file node's gamma
        shaderOutputNodes = mc.listConnections(shader,s = 0,d = 1)
        sgNodes = [outputNode for outputNode in shaderOutputNodes if mc.objectType(outputNode) == 'shadingEngine']
        if sgNodes != []:
            upStreamNodes = mc.listHistory(sgNodes[0])
        else:
            upStreamNodes = mc.listHistory(shader)
        fileNodes = [node for node in upStreamNodes if mc.objectType(node) == 'file']

        
        for fileNode in fileNodes:
            if sourceColorSpace == 'orig_use_maya_colorSpace' and targetColorSpace == 'target_classic_gamma_2point2':
                __createGammaNode_connectTo(fileNode, 0.454)
            
            elif sourceColorSpace == 'orig_use_maya_colorSpace' and targetColorSpace == 'target_classic_Raw':
                __createGammaNode_connectTo(fileNode, 1)
            elif sourceColorSpace == 'orig_classic_gamma_2point2' and targetColorSpace == 'target_use_maya_colorSpace':
                __setColorSpace(fileNode, 'gamma 2.2 Rec 709')
                
            elif sourceColorSpace == 'orig_classic_Raw' and targetColorSpace == 'target_use_maya_colorSpace':
                __setColorSpace(fileNode, 'Raw')
                
                


def convertConnect_BumpNode(bumpData,materialData,convertedShaders,targetMaterialType):
    targetRenderer = getRendererName(targetMaterialType)
    for shader in convertedShaders:
        bumpAttrInputNodes = mc.listConnections(shader +'.' + materialData[targetMaterialType]['bump'][0])
        
        if bumpAttrInputNodes is not None:
            origBumpNode = bumpAttrInputNodes[0]
            origBumpNodeType = mc.objectType(origBumpNode)

            #if orig mtl is vray, use vray mtl as bumpNode
            bumpNodeTypes = ['RedshiftBumpMap','RedshiftNormalMap','bump2d']
            if origBumpNodeType not in  bumpNodeTypes: # means this is vray bump type
                origBumpNodeType = 'VRayMtl'
                if mc.objExists(origBumpNode + '.outColor'):
                    connectedShaders = mc.listConnections(origBumpNode + '.outColor')
                elif mc.objExists(origBumpNode  + '.output'):
                    connectedShaders = mc.listConnections(origBumpNode + '.output')
                elif mc.objExists(origBumpNode  + '.outValue'):
                    connectedShaders = mc.listConnections(origBumpNode + '.outValue')
                for connectedShader in connectedShaders:
                    if mc.objectType(connectedShader) == 'VRayMtl':
                        origBumpNode = connectedShader
            origBumpClass = BumpNode(origBumpNodeType,bumpData[origBumpNodeType])

            if targetRenderer != 'vray':
                specificBumpNode = origBumpNode
            else:
                specificBumpNode = shader
            specificBumpNodeType = mc.objectType(specificBumpNode)
            origBumpClass.getAttrsFrom(origBumpNode)
            targetBumpNodeType = getBumpNodeTypeName(targetMaterialType,origBumpClass.bumpType.value)
            targetBumpClass = BumpNode(targetBumpNodeType,bumpData[targetBumpNodeType])

            convertedBumpClass = origBumpClass.convertTo(targetBumpClass)
            bumpNode = convertedBumpClass.createConnectBumpNodeTo(shader,materialData)
            return bumpNode

def materialConvert(sourceMaterialType,targetMaterialType,sourceColorSpace,targetColorSpace,affectColorSwitch,*args):
    sels = mc.ls(sl = 1)
    data = Data(['materialAttrs','subdiv_displacementAttrs','bumpAttrs'])
    dataDict = data.prepareData()
    materialDataClass = Data(['materialAttrs']) 
    materialData = materialDataClass.prepareData()
    subdiv_displacementData = dataDict['subdiv_displacementAttrs']
    bumpData = dataDict['bumpAttrs']

    #vars
    #get shaders from selected objects or from selected materials
    
    shadersConverting = basicOperater.getMaterialFromSelected()
    shadersConverting = [shader for shader in shadersConverting if mc.objectType(shader) == sourceMaterialType]
    if shadersConverting == []:
        mc.warning('no %s material found,nothing converted!'%sourceMaterialType)



    sourceRenderer = getRendererName(sourceMaterialType)
    targetRenderer = getRendererName(targetMaterialType)

    print 'begin subdiv_displacement '
    convertSet_SudivsDisplacementForSelected(subdiv_displacementData,sourceRenderer,targetRenderer)
    print 'end subdiv_displacement'
    print '======================================================'
    print 'begin material convert'
    convertedShaders = convertAssign_materialForSelected(materialData,shadersConverting,targetMaterialType)
    print 'end material convert'
    print '======================================================'
    print 'begin bump convert'
    convertConnect_BumpNode(bumpData,materialData,convertedShaders,targetMaterialType)
    print 'end bump convert'
    setColorSpaceForShader(convertedShaders, sourceColorSpace, targetColorSpace,materialData,affectColorSwitch)
    
    return convertedShaders



#if __name__ == '__main__':
#    main()

