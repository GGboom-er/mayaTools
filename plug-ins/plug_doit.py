import maya.OpenMaya as OpenMaya
import maya.cmds as mc
import maya.OpenMayaMPx as OpenMayaMPx
import sys

commandName = 'pluginCommand'

class pluginCommand(OpenMayaMPx.MPxCommand):
    
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        
    def doIt(self,argList):
        loc_name = mc.createNode('locator')
        return loc_name




def cmdCreator():
    return OpenMayaMPx.asMPxPtr(pluginCommand())
    
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand(commandName,cmdCreator)
    except:
        sys.stderr.write('failed to register command:'+commandName)
        


def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    
    try:
        mplugin.deregisterCommand(commandName)
        
    except:
        sys.stderr.write('failed to de-register command:'+commandName)


