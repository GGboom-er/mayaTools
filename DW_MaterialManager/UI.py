#encoding:utf-8
#global var
#DW_MaterialManager_v2.02 author masterdai
import maya.cmds as mc
import sys,json,os
import webbrowser
import basicOperater
from functools import partial
from collections import OrderedDict
import dataClass
reload (dataClass)
import materialConverter
reload(materialConverter)
import materialImporter
reload (materialImporter)


mayaVersion = int(mc.about(version = 1)[:4])
supportedTemplates = ['Arnold4(aistandard)','Arnold4(alSurface)','Arnold5(aistandard)','Redshift','Vray','PBR_MetalRough','SubstanceDesigner_MetalRough','Custom']
convertFrom = 'RedshiftArchitectural'
convertTo = 'RedshiftArchitectural'
affectColorSwatch = False
origColorSpace = 'target_use_maya_colorSpace'
targetColorSpace = 'target_use_maya_colorSpace'



#the json files in the materialAttrs folder determins which renderer is supported
supportedMaterials = []
materialAttrsData = dataClass.Data(['materialAttrs'])
materialsDataDict = materialAttrsData.prepareData()
for supportedMaterial in materialsDataDict:
	if supportedMaterial != 'Default':
		supportedMaterials.append(supportedMaterial)
supportedMaterials.sort()
print supportedMaterials

#trueReflection bool used to define whether to use the trueReflection system

def changeConvertFrom(*args):
	savePreset()
	global convertFrom
	convertFrom = mc.optionMenuGrp('convertFromOptionMenu',q = 1, v = 1)
	convertTo = mc.optionMenuGrp('convertToOptionMenu',q = 1, v = 1)

	itemsShort = mc.optionMenuGrp('convertToOptionMenu',q = 1, ils = 1)
	itemsLong = mc.optionMenuGrp('convertToOptionMenu',q = 1, ill = 1)
	itemsDict = {}
	for i in range(len(itemsLong)):
		itemsDict[itemsShort[i]] = itemsLong[i]
	for i,item in enumerate(itemsShort):
		mc.menuItem(itemsDict[item],e = 1,en = 1)
		if item == convertFrom:
			mc.menuItem(itemsDict[item],e = 1,en = 0)
			if item == convertTo:
				changeTo = itemsShort[(i + 1)%len(itemsShort)]
				mc.optionMenuGrp('convertToOptionMenu',e = 1, v = changeTo)


	
	if convertFrom == 'RedshiftArchitectural' or convertFrom == 'aiStandardSurface':
		mc.radioCollection('origRadioCollection',e = 1,sl = 'orig_use_maya_colorSpace')
	elif convertFrom == 'aiStandard':
		mc.radioCollection('origRadioCollection',e = 1,sl = 'orig_classic_gamma_2point2')
	changeConvertTo()
	#
def changeConvertTo(*args):
	global convertTo
	convertTo = mc.optionMenuGrp('convertToOptionMenu',q = 1, v = 1)
	if convertTo == 'RedshiftArchitectural' or convertFrom == 'aiStandardSurface':
		mc.radioCollection('targetRadioCollection',e = 1,sl = 'target_use_maya_colorSpace')
	elif convertTo == 'aiStandard':
		mc.radioCollection('targetRadioCollection',e = 1,sl = 'target_classic_gamma_2point2')
	savePreset()

def changeOrigColorSpace(*args):
	global origColorSpace
	origColorSpace = mc.radioCollection('origRadioCollection',q = 1,sl = 1)
	if origColorSpace == 'orig_use_maya_colorSpace':
		mc.radioButton('target_use_maya_colorSpace',e = 1,m = 1)
		mc.radioButton('target_classic_gamma_2point2',e = 1,m = 1)
		mc.radioButton('target_classic_Raw',e = 1,m =1 )
	elif origColorSpace == 'orig_classic_gamma_2point2':
		mc.radioButton('target_use_maya_colorSpace',e = 1,m = 1,sl = 1)
		mc.radioButton('target_classic_gamma_2point2',e = 1,m = 1)
		mc.radioButton('target_classic_Raw',e = 1,m = 0)
	elif origColorSpace == 'orig_classic_Raw':
		mc.radioButton('target_use_maya_colorSpace',e = 1,m = 1,sl = 1)
		mc.radioButton('target_classic_gamma_2point2',e = 1,m = 0)
		mc.radioButton('target_classic_Raw',e = 1,m = 1)
	savePreset()

def changeHeightMapAsDisplacement(*args):
	useHeight = mc.checkBox('heightMapAsDisplacement', q = 1 , v = 1)
	if useHeight:
		mc.textFieldGrp('heightDepth',e = 1,m = 1)
		mc.checkBox('heightMap_8bit',e = 1,m = 1)
		mc.textFieldGrp('zeroHeight',e = 1,m = 1)
		mc.checkBox('enableSubdiv_dis',e = 1, v = 1 )
	else:
		mc.textFieldGrp('heightDepth',e = 1,m = 0)
		mc.checkBox('heightMap_8bit',e = 1,m = 0)
		mc.textFieldGrp('zeroHeight',e = 1,m = 0)
		mc.checkBox('enableSubdiv_dis',e = 1, v = 0 )
	savePreset()
def changeTargetColorSpace(*args):
	global targetColorSpace
	targetColorSpace = mc.radioCollection('targetRadioCollection',q = 1,sl = 1)
	savePreset()

def heightMap_8bit(*args):
	mc.textFieldGrp('heightDepth',e = 1, tx = 0.05)
def heightMap_32bit(*args):
	mc.textFieldGrp('heightDepth',e = 1, tx = 1)

def changeUseTemplate(*args):
	template = mc.optionMenuGrp('useTemplate',q = 1,v = 1)
	if template == 'Custom':
		mc.textFieldGrp('diffuseColor', e = 1,m = 1)
		mc.textFieldGrp('metalness',e = 1,m = 1)
		mc.textFieldGrp('reflectionColor',e = 1,m = 1)
		mc.textFieldGrp('glossiness',e = 1,m = 1)
		mc.textFieldGrp('f0',e = 1,m = 1)
		mc.textFieldGrp('ior',e = 1,m = 1)
		mc.textFieldGrp('emissive',e = 1,m = 1)
		mc.textFieldGrp('normal',e = 1,m = 1)
		mc.textFieldGrp('height',e = 1,m = 1)
		mc.separator('customTemplateStart',e = 1, m = 1)
		mc.separator('customTemplateEnd',e = 1, m = 1)
		saveCustomTemplate()
		#mc.button('saveCustom',e = 1,m = 1)
	else:
		mc.textFieldGrp('diffuseColor', e = 1,m = 0)
		mc.textFieldGrp('metalness',e = 1,m = 0)
		mc.textFieldGrp('reflectionColor',e = 1,m = 0)
		mc.textFieldGrp('glossiness',e = 1,m = 0)
		mc.textFieldGrp('f0',e = 1,m = 0)
		mc.textFieldGrp('ior',e = 1,m = 0)
		mc.textFieldGrp('emissive',e = 1,m = 0)
		mc.textFieldGrp('normal',e = 1,m = 0)
		mc.textFieldGrp('height',e = 1,m = 0)
		mc.separator('customTemplateStart',e = 1, m = 0)
		mc.separator('customTemplateEnd',e = 1, m = 0)
		#mc.button('saveCustom',e = 1,m = 0)
	if 'SubstanceDesigner' in template:
		mc.checkBox('heightMapAsDisplacement',e = 1 , v = 1)
		changeHeightMapAsDisplacement()
	elif template != 'Custom':
		mc.checkBox('heightMapAsDisplacement',e = 1, v = 0)
		changeHeightMapAsDisplacement()
	savePreset()
def savePreset_changeUseTemplate(*args):
	savePreset()
	changeUseTemplate()
def changeAffectColorSwitch(*args):
	global affectColorSwatch
	affectColorSwatch = mc.checkBox('affectColorSwatch',q = 1 ,v = 1)
def savePreset_changeAffectColorSwitch(*args):
	changeAffectColorSwitch()
	savePreset()

def saveCustomTemplate(*args):
	scriptPath = mc.internalVar(usd = 1)
	DW_MaterialManagerPath = scriptPath + r'DW_MaterialManager'
	templateFilePath = os.path.join(DW_MaterialManagerPath,'data/textureTemplates.json')
	templateFilePath = templateFilePath.replace('/','\\')
	contentDict = {}
	contentDict['diffuseColor'] = mc.textFieldGrp('diffuseColor', q = 1,tx = 1)
	contentDict['primaryMetalness'] = mc.textFieldGrp('metalness', q = 1,tx = 1)
	contentDict['primaryReflectionColor'] = mc.textFieldGrp('reflectionColor', q = 1,tx = 1)
	contentDict['primaryReflectionGlossiness'] = mc.textFieldGrp('glossiness', q = 1,tx = 1)
	contentDict['primaryReflectionF0'] = mc.textFieldGrp('f0', q = 1,tx = 1)
	contentDict['primaryReflectionIOR'] = mc.textFieldGrp('ior', q = 1,tx = 1)
	contentDict['pureColor'] = mc.textFieldGrp('emissive', q = 1,tx = 1)
	contentDict['bump'] = mc.textFieldGrp('normal', q = 1,tx = 1)
	contentDict['height'] = mc.textFieldGrp('height', q = 1,tx = 1)
	with open(templateFilePath, "r") as fp:
		templates = json.load(fp) 

	templates['Custom'] = contentDict
	

	with open(templateFilePath, "w") as fp:
		json.dump(templates, fp,indent = 2) 
def savePreset_saveCustomTemplate(*args):
	savePreset()
	saveCustomTemplate()
def getMaterialFromSelectedAndStore(*args):
	materials = basicOperater.getMaterialFromSelected()
	materialsStr = ''
	for i,material in enumerate(materials):
		if i == 0:
			materialsStr = material
		else:
			materialsStr += ',' + material
	
	mc.text('tempMaterial',e = 1,l = materialsStr)
def assignMaterialToSelected(*args):
	materials = mc.text('tempMaterial',q = 1,l = 1)
	material = materials.partition(',')[0]
	curSels = mc.ls(sl = 1)
	basicOperater.assignMaterialWithDisplacement(material, material,sels = curSels)
	enableSubdiv_dis = mc.checkBox('enableSubdiv_dis',q = 1, v = 1)
	if enableSubdiv_dis:
		targetMaterialType = mc.optionMenuGrp('createMaterial',q = 1 ,v = 1)
		renderer = materialConverter.getRendererName(targetMaterialType)
		subdiv_displacementAttrsData = dataClass.Data(['subdiv_displacementAttrs'])
		subdiv_displacementAttrsDataDict = subdiv_displacementAttrsData.prepareData()
		subdiv_displacementData = subdiv_displacementAttrsDataDict['subdiv_displacementAttrs']

		materialConverter.convertSet_SudivsDisplacementForSelected(subdiv_displacementData,'Default',renderer)


def materialConvert(*args):
	global convertFrom
	global convertTo
	global origColorSpace
	global targetColorSpace
	global affectColorSwatch
	materialConverter.materialConvert(convertFrom,convertTo,origColorSpace,targetColorSpace,affectColorSwatch)	
def openDirectory(*argus):
	returnDirectory = mc.fileDialog2(fm = 3,ff = None,ds = 1)
	if returnDirectory != None:
		returnDirectory = returnDirectory[0]
	else:
		returnDirectory = ''

	mc.textFieldGrp('userDefinedPathTextField',e = 1, tx = returnDirectory)	

def openWeb(webPath,*args):
	webbrowser.open(webPath, new=0, autoraise=True)


def savePreset(*args):
	contentDict = {}
	mc.frameLayout('MaterialImport',q= 1,cl = 1)
	contentDict['MaterialImport'] = mc.frameLayout('MaterialImport',q= 1,cl = 1)
	contentDict['createMaterial'] = mc.optionMenuGrp('createMaterial',q= 1,v = 1)
	contentDict['useTemplate'] = mc.optionMenuGrp('useTemplate',q= 1,v = 1)
	contentDict['udim'] = mc.checkBox('udim',q= 1,v = 1)
	contentDict['usingMayaColorManagement'] = mc.checkBox('usingMayaColorManagement',q= 1,v = 1)
	contentDict['openGLNormal'] = mc.checkBox('openGLNormal',q= 1,v = 1)
	contentDict['zeroHeight'] = mc.textFieldGrp('zeroHeight',q= 1,tx = 1)
	contentDict['heightDepth'] = mc.textFieldGrp('heightDepth',q= 1,tx = 1)
	contentDict['heightMap_8bit'] = mc.checkBox('heightMap_8bit',q= 1,v = 1)
	contentDict['heightMapAsDisplacement'] = mc.checkBox('heightMapAsDisplacement',q= 1,v = 1)
	contentDict['userDefinedPathTextField'] = mc.textFieldGrp('userDefinedPathTextField',q= 1,tx = 1)
	contentDict['materialNameInput'] = mc.textFieldGrp('materialNameInput',q= 1,tx = 1)
	contentDict['MaterialConverter'] = mc.frameLayout('MaterialConverter',q= 1,cl = 1)
	contentDict['convertFromOptionMenu'] = mc.optionMenuGrp('convertFromOptionMenu',q= 1,v = 1)
	contentDict['convertToOptionMenu'] = mc.optionMenuGrp('convertToOptionMenu',q= 1,v = 1)
	contentDict['LinearWorkFlow'] = mc.frameLayout('LinearWorkFlow',q= 1,cl = 1)
	contentDict['affectColorSwatch'] = mc.checkBox('affectColorSwatch',q = 1,v = 1)
	contentDict['origRadioCollection'] = mc.radioCollection('origRadioCollection',q= 1,sl = 1)
	contentDict['targetRadioCollection'] = mc.radioCollection('targetRadioCollection',q= 1,sl = 1)

	contentDict['diffuseColor'] = mc.textFieldGrp('diffuseColor', q = 1,tx = 1)
	contentDict['metalness'] = mc.textFieldGrp('metalness', q = 1,tx = 1)
	contentDict['reflectionColor'] = mc.textFieldGrp('reflectionColor', q = 1,tx = 1)
	contentDict['glossiness'] = mc.textFieldGrp('glossiness', q = 1,tx = 1)
	contentDict['f0'] = mc.textFieldGrp('f0', q = 1,tx = 1)
	contentDict['ior'] = mc.textFieldGrp('ior', q = 1,tx = 1)
	contentDict['emissive'] = mc.textFieldGrp('emissive', q = 1,tx = 1)
	contentDict['normal'] = mc.textFieldGrp('normal', q = 1,tx = 1)
	contentDict['height'] = mc.textFieldGrp('height', q = 1,tx = 1)


	contentDict['MaterialAssign']  = mc.frameLayout('MaterialAssign',q = 1,cl = 1)
	contentDict['enableSubdiv_dis'] = mc.checkBox('enableSubdiv_dis',q = 1,v =1)

	scriptPath = mc.internalVar(usd = 1)
	DW_MaterialManagerPath = scriptPath + r'DW_MaterialManager'
	presetFilePath = os.path.join(DW_MaterialManagerPath,'presets','UI_lastPreset.json')
	presetFilePath = presetFilePath.replace( '\\','/')

	with open(presetFilePath, "w") as fp:
		json.dump(contentDict, fp,indent = 2)

def loadPreset(reset = False,*args):
	scriptPath = mc.internalVar(usd = 1)
	DW_MaterialManagerPath = scriptPath + r'DW_MaterialManager'
	if not reset:
		presetFilePath = os.path.join(DW_MaterialManagerPath,'presets','UI_lastPreset.json')
	else:
		presetFilePath = os.path.join(DW_MaterialManagerPath,'presets','UI_defaultPreset.json')
	presetFilePath = presetFilePath.replace( '/','\\')

	with open(presetFilePath, "r") as fp:
		contentDict = json.load(fp)

	mc.frameLayout('MaterialImport',e= 1,cl = contentDict['MaterialImport'])
	mc.optionMenuGrp('createMaterial',e= 1,v = contentDict['createMaterial'])
	mc.optionMenuGrp('useTemplate',e= 1,v = contentDict['useTemplate'])
	mc.checkBox('udim',e= 1,v = contentDict['udim'])
	mc.checkBox('usingMayaColorManagement',e= 1,v = contentDict['usingMayaColorManagement'])
	mc.checkBox('openGLNormal',e= 1,v = contentDict['openGLNormal'])
	mc.textFieldGrp('zeroHeight',e= 1,tx = contentDict['zeroHeight'])
	mc.textFieldGrp('heightDepth',e= 1,tx = contentDict['heightDepth'])
	mc.checkBox('heightMap_8bit',e= 1,v = contentDict['heightMap_8bit'])
	mc.checkBox('heightMapAsDisplacement',e= 1,v = contentDict['heightMapAsDisplacement'])
	mc.textFieldGrp('userDefinedPathTextField',e= 1,tx = contentDict['userDefinedPathTextField'])
	mc.textFieldGrp('materialNameInput',e= 1,tx = contentDict['materialNameInput'])
	mc.frameLayout('MaterialConverter',e= 1,cl = contentDict['MaterialConverter'])
	mc.optionMenuGrp('convertFromOptionMenu',e= 1,v = contentDict['convertFromOptionMenu'])
	mc.optionMenuGrp('convertToOptionMenu',e= 1,v = contentDict['convertToOptionMenu'])
	mc.frameLayout('LinearWorkFlow',e= 1,cl = contentDict['LinearWorkFlow'])
	mc.checkBox('affectColorSwatch',e = 1,v = contentDict['affectColorSwatch'])
	mc.radioCollection('origRadioCollection',e= 1,sl = contentDict['origRadioCollection'])
	mc.radioCollection('targetRadioCollection',e= 1,sl = contentDict['targetRadioCollection'])

	mc.textFieldGrp('diffuseColor', e = 1,tx = contentDict['diffuseColor'])
	mc.textFieldGrp('metalness',e = 1,tx = contentDict['metalness'])
	mc.textFieldGrp('reflectionColor',e = 1,tx = contentDict['reflectionColor'])
	mc.textFieldGrp('glossiness',e = 1,tx = contentDict['glossiness'])
	mc.textFieldGrp('f0',e = 1,tx = contentDict['f0'])
	mc.textFieldGrp('ior',e = 1,tx = contentDict['ior'])
	mc.textFieldGrp('emissive',e = 1,tx = contentDict['emissive'])
	mc.textFieldGrp('normal',e = 1,tx = contentDict['normal'])
	mc.textFieldGrp('height',e = 1,tx = contentDict['height'])

	mc.frameLayout('MaterialAssign',e = 1,cl = contentDict['MaterialAssign'])
	mc.checkBox('enableSubdiv_dis',e = 1,v = contentDict['enableSubdiv_dis'])

	changeUseTemplate()


#UI part
def UI():
	offsetFromLeft = 80

	if mc.dockControl('DW_MaterialManager_dockControl',ex = 1):
		mc.deleteUI('DW_MaterialManager_dockControl')
	mc.window('DW_MaterialManager',t = 'DW_MaterialManager',menuBar = 1 )

	mc.showWindow()

	mainRCL = mc.rowColumnLayout(w = 450,numberOfColumns = 1)
	mc.dockControl('DW_MaterialManager_dockControl',area = 'left',content = 'DW_MaterialManager',fl = 1,l = 'DW_MaterialManager' )
	#mc.separator(style = 'none',h = 20)
	mc.menu(label = 'UI',tearOff = 0)
	mc.menuItem(label = 'save preset',c = savePreset)
	mc.menuItem( label='reset to default',c = partial(loadPreset,True))
	#mc.rowColumnLayout(co = (1,'left',300))
	mc.menu( label='Help', tearOff=0 ,hm = 1)
	mc.menuItem( label='how to use',c = partial(openWeb,r'https://zhuanlan.zhihu.com/p/27649330'))
	mc.menuItem( label='checkNewVersion',c = partial(openWeb,r'https://trello.com/b/Zphjhcpo'))
	mc.menuItem( label='aboutAuthor',c = partial(openWeb,r'http://weibo.com/david376 '))

##################################################################################################################################################
	
	#the UI used to choose renderer
	tabLayout = mc.tabLayout()
	frame01 = mc.frameLayout('MaterialImport',l = 'Material Importer',cll = 1, cl = 0,w =400,cc = savePreset,ec = savePreset_changeUseTemplate,p = tabLayout)

	mc.separator(style = 'none',h = 1)
	createMaterial = mc.optionMenuGrp('createMaterial', l = 'CreateMaterial',cc = savePreset,cw2 = [offsetFromLeft,100])
	for supportedMaterial in supportedMaterials:
		mc.menuItem(supportedMaterial)


	useTemplate = mc.optionMenuGrp('useTemplate', l = 'UseTemplate',cc = changeUseTemplate,cw2 = [offsetFromLeft,100])
	for template in supportedTemplates:
		mc.menuItem(template)

	mc.separator('customTemplateStart')
	mc.textFieldGrp('diffuseColor',l = 'diffuseColor',cl2 = ['right','left'],cw2 = [offsetFromLeft,100],cc = savePreset_saveCustomTemplate)
	mc.textFieldGrp('metalness',l = 'metalness',cl2 = ['right','left'],cw2 = [offsetFromLeft,100],cc = savePreset_saveCustomTemplate)
	mc.textFieldGrp('reflectionColor',l = 'reflectionColor',cl2 = ['right','left'],cw2 = [offsetFromLeft,100],cc = savePreset_saveCustomTemplate)
	mc.textFieldGrp('glossiness',l = 'glossiness',cl2 = ['right','left'],cw2 = [offsetFromLeft,100],cc = savePreset_saveCustomTemplate)
	mc.textFieldGrp('f0',l = 'f0',cl2 = ['right','left'],cw2 = [offsetFromLeft,100],cc = savePreset_saveCustomTemplate)
	mc.textFieldGrp('ior',l = 'ior',cl2 = ['right','left'],cw2 = [offsetFromLeft,100],cc = savePreset_saveCustomTemplate)
	mc.textFieldGrp('emissive',l = 'emissive',cl2 = ['right','left'],cw2 = [offsetFromLeft,100],cc = savePreset_saveCustomTemplate)
	mc.textFieldGrp('normal',l = 'normal',cl2 = ['right','left'],cw2 = [offsetFromLeft,100],cc = savePreset_saveCustomTemplate)
	mc.textFieldGrp('height',l = 'height',cl2 = ['right','left'],cw2 = [offsetFromLeft,100],cc = savePreset_saveCustomTemplate)
	#buttonRCL00 = mc.rowColumnLayout(co = (1,'left',offsetFromLeft + 2))
	#mc.button('saveCustom',l = 'saveCustom',w = 100,h = 30,c = saveCustomTemplate)
	mc.separator('customTemplateEnd',p = frame01)

	mc.rowColumnLayout(co = (1,'left',offsetFromLeft + 4),p = frame01)




	mc.separator(h = 20) 
	mc.separator(style = 'out') 

	mc.checkBox('udim',l = 'udim textures',align = 'right',cc = savePreset)  

	#mc.checkBox(l = 'true reflection',onc = trueReflection_on,ofc = trueReflection_off,align = 'right') 

	# if 2016 and above version maya, usingMayaColorManagement as default.
	# if 2015 and lower version maya, don't use mayaColorManagement
	if mayaVersion >2015:
		usingMayaColorManagement = True
	else:
		usingMayaColorManagement = False
	mc.checkBox('usingMayaColorManagement',l = 'usingMayaColorManagement',align = 'right',v = usingMayaColorManagement,cc = savePreset)
	mc.checkBox('openGLNormal',l = 'openGLNormal   (uncheck means directX normal)',align = 'right',v = 1,cc = savePreset)
	
	mc.separator(h = 1,p = frame01)
	#mc.rowColumnLayout(co = (1,'left',offsetFromLeft + 4))
	#heightMapText = mc.text('heightMap:',al = 'left')

	mc.rowColumnLayout(p = frame01,h = 45)

	mc.textFieldGrp('zeroHeight',l = 'zeroHeight',cl2 = ['right','left'],cw2 = [80,100],tx = 0.5,cc = savePreset)
	mc.textFieldGrp('heightDepth',l = 'heightDepth',cl2 = ['right','left'],cw2 = [80,100],tx = 0.05,cc = savePreset)
	
	mc.rowColumnLayout(co = (1,'left',offsetFromLeft + 4),p = frame01,h = 40)
	mc.checkBox('heightMap_8bit',l = 'heightMap_8bit',align = 'right',v = 1,ofc = heightMap_32bit,onc = heightMap_8bit ,cc = savePreset) 

	mc.checkBox('heightMapAsDisplacement',l = 'heightMapAsDisplacement',align = 'right',v = 1,cc = changeHeightMapAsDisplacement) 
	
	mc.separator(h = 1,p = frame01) 





	inputRCL = mc.rowColumnLayout(p = mainRCL,w = 430)
	userDefinedPathTextField = mc.textFieldGrp('userDefinedPathTextField',l = 'TexturesPath',cw2 = [offsetFromLeft,320],p = frame01,cc = savePreset)
	mc.iconTextButton(style = 'iconOnly',image = 'xgBrowse.png', p = userDefinedPathTextField,c = openDirectory)
	materialNameInput = mc.textFieldGrp('materialNameInput',l = 'MaterialName',cw2 = [offsetFromLeft,320],p = frame01,\
	tx = '',cc = savePreset)

	buttonRCL01 = mc.rowColumnLayout(co = (1,'left',offsetFromLeft + 2),p  = frame01)
	convertButton = mc.button('import',l = 'import / assign',w = 320,h = 50,c = materialImporter.import_replaceMaterialsByName,p = buttonRCL01)
	#convertButton = mc.button('replace',l = 'import / replaceByName',w = 320,h = 50,c = materialImporter.main,p = buttonRCL01)
	mc.separator(style = 'none',h = 5,p = frame01)

##################################################################################################################################################

	frame02 = mc.frameLayout('MaterialAssign',l = 'Material Assign',cll = 1, cl = 0,w =430,p = tabLayout,cc = savePreset,ec = savePreset)
	
	mc.separator(h = 5,style = 'none')
	mc.rowColumnLayout(nc = 2,cs = [2,10])
	mc.text('tempMaterial:')
	mc.text('tempMaterial',l = '' )
	mc.separator(h = 3,p = frame02)
	buttonRCL02 = mc.rowColumnLayout(co = (1,'left',offsetFromLeft + 2),nc = 2,cs = [2,10], p = frame02)
	mc.checkBox('enableSubdiv_dis',l = 'enableSubdiv_dis',v =1,cc = savePreset)
	mc.separator(h = 1,style = 'none')
	mc.button('getMaterial',l = 'getMaterial',w = 150,h = 50,c = getMaterialFromSelectedAndStore)

	mc.button('assignTempMaterial',l = 'assignTempMaterial',w = 150,h = 50,c = assignMaterialToSelected)
	mc.separator(h = 20)	

####################################################################################################################################################################
	frame03 = mc.frameLayout('MaterialConverter',l = 'Material Converter',cll = 1, cl = 0,w =230,cc = savePreset,ec = savePreset,p = tabLayout)
	mc.separator(style = 'none',h = 1)
	convertFromOptionMenu = mc.optionMenuGrp('convertFromOptionMenu', l = 'from: ',cc = changeConvertFrom,cw2 = [30,165],cal = [1,'left'],cl2 = ['left','left'])
	for supportedMaterial in supportedMaterials:
		mc.menuItem(supportedMaterial)
	
	convertToOptionMenu = mc.optionMenuGrp('convertToOptionMenu', l = 'to :',p = convertFromOptionMenu ,cal = [(1,'left')],cw2 = [20,165],cc= changeConvertTo)
	for supportedMaterial in supportedMaterials:
		mc.menuItem(supportedMaterial)
	
	def __switchMaterial():
		global convertFrom
		global convertTo
		temp = ''
		temp = convertTo
		convertTo = convertFrom
		convertFrom = temp
		convertFromOptionMenu
		mc.optionMenuGrp('convertFromOptionMenu',e = 1, v = convertFrom)
		mc.optionMenuGrp('convertToOptionMenu',e = 1, v = convertTo)

	mc.iconTextButton(style = 'iconOnly',image = 'iGroom_reset.png', p = convertToOptionMenu ,c = __switchMaterial)	

	buttonRCL03 = mc.rowColumnLayout(co = (1,'left',30 + 4))

	def __LWF_frameLayout():
		frame04 = mc.frameLayout('LinearWorkFlow',l = 'LinearWorkFlow',cll = 1, cl = 0,w =340,cc = savePreset,ec = savePreset)
		
		mc.rowColumnLayout(numberOfRows = 3,co = (2,'left',60))

		origRadioCollection = mc.radioCollection('origRadioCollection')
		mc.radioButton('orig_use_maya_colorSpace',l = 'use maya colorSpace',sl = 1,ofc = changeOrigColorSpace)
		mc.radioButton('orig_classic_gamma_2point2',l = 'classic gamma 2.2',ofc = changeOrigColorSpace)
		mc.radioButton('orig_classic_Raw',l = 'classic Raw',ofc = changeOrigColorSpace)

		targetRadioCollection = mc.radioCollection('targetRadioCollection')
		mc.radioButton('target_use_maya_colorSpace',l = 'use maya colorSpace',sl = 1,ofc = changeTargetColorSpace)
		mc.radioButton('target_classic_gamma_2point2',l = 'classic gamma 2.2',ofc = changeTargetColorSpace)
		mc.radioButton('target_classic_Raw',l = 'classic Raw',ofc = changeTargetColorSpace)

		mc.separator(h = 1,p = frame04)
		mc.checkBox('affectColorSwatch',l = 'affect color swatch',cc = savePreset_changeAffectColorSwitch,p = frame04)
		mc.separator(h = 5,p = frame04)


	__LWF_frameLayout()
	#for changeConvertFrom function will change UI settings ,we should loadPreset before it
	loadPreset()
	changeConvertFrom()
	changeConvertTo()
	changeUseTemplate()
	changeAffectColorSwitch()
	changeHeightMapAsDisplacement()

	mc.separator(style = 'none',h = 20)
	convertButton = mc.button('convert',l = 'convert',w = 340,h = 50,c = materialConvert,p = buttonRCL03)

	#mc.columnLayout(p = mainRCL,w = 300)
	mc.rowColumnLayout(co = (1,'left',250),p = mainRCL,w = 300)
	mc.text(l = 'DW_MaterialManager_v2.03b',w =160,al = 'right',hyperlink = 1,ww = 1,ann = 'the version of the script')
	mc.separator(h = 10)

	


if __name__ =='__main__':
	UI()