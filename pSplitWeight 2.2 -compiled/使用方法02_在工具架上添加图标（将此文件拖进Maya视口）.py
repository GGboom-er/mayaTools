#coding=utf-8
import os,sys
import maya.cmds as cmds
import maya.mel as mel

def shelfButtonInstall():
    PATH = os.path.dirname(__file__) 
    PATH = os.path.abspath(PATH).replace('\\','/') 

    Label = "pSW"
    Script = '''#
try:  
    from importlib import reload
except:
    from imp import reload
finally:
    pass

import sys
if \"%s\" not in sys.path:
    sys.path.append(\"%s\")

import %s
reload (%s)
''' % (PATH,PATH,'pSplitWeight','pSplitWeight') 


    mel.eval('global string $gShelfTopLevel') 
    gShelfTopLevel = mel.eval('$tmp = $gShelfTopLevel') 

    currentShelf = cmds.tabLayout(gShelfTopLevel, query=True, selectTab=True)
    cmds.setParent(currentShelf)

    #
    iconExt="png"
    icon= "pythonFamily."+iconExt

    #
    cmds.shelfButton( 
        command = Script,
        annotation=Label,
        label=Label,
        imageOverlayLabel=Label,
        image=icon,
        image1=icon,
        sourceType="python"
        ) 

#
def onMayaDroppedPythonFile(param):
    shelfButtonInstall() 