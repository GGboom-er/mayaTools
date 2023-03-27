#encoding:utf-8
#material converter
import maya.cmds as mc
import pymel.core as pm
import sys
import json
mc.about(windows = 1)
scriptPath = mc.internalVar(usd = 1)
DW_MaterialManagerPath = scriptPath + r'DW_MaterialManager'

# if the systerm is windows,then use \\ replace /
if mc.about(windows = 1):
	DW_MaterialManagerPath = DW_MaterialManagerPath.replace(r'/','\\')
else:
	pass
	
if DW_MaterialManagerPath not in sys.path:
    sys.path.insert(0,DW_MaterialManagerPath)

try:
    import UI
    
except:
    mc.error('the DW_MaterialManager folder is placed wrong,the right path is : {0}'.format(scriptPath))
    
reload(UI)
UI.UI()