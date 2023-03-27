import sys
import maya.cmds as cmds
import pymel.core as pm
print('...' * 30)
#sys.path.append(r'P:\pipeline\ppas')
sys.path.append(r'C:\Python27\Lib\site-packages')
sys.path.append(r'C:\workspace\ppas')

def auto_menu():
    from launcher.fitment.maya import fitment
    reload(fitment)
    fitment.fitment()

pm.scriptJob(event=('SceneOpened', auto_menu))

cmds.lockNode(cmds.ls(type = 'shadingEngine'),lu =0,ln =1,ic =1,l =0)

