import maya.OpenMaya    as OpenMaya
import maya.cmds    as  mc
from AM_MENU.core.python_utils import  Object


class AmRig_channelBox(Object):
    
    def __init__( self ):
        
        self.id = self.registerCallback()
        self.update()
        
    # ------------------------------------------------------------------------
    
    def registerCallback(self):
        
        return OpenMaya.MModelMessage.addCallback(
            OpenMaya.MModelMessage.kActiveListModified, 
            self.update
        )
        
    def removeCallback(self):
        """
        Remove the callback that updates the ui every time the selection
        list is modified.
        """
        OpenMaya.MMessage.removeCallback(self.id)
        
        
    # ------------------------------------------------------------------------
    
    def update(self, *args): 
        nodes = mc.ls(sl=True, l=True) or []
        self.updateColour(nodes)

    # ------------------------------------------------------------------------
    
    def updateColour(self, nodes):
        for node in nodes:
            attrs = mc.listAttr(node, userDefined=True) or []
            for attr in attrs:
                if attr.startswith("AM___SEP_"):
                    mc.channelBox(
                        'mainChannelBox', 
                        edit=True, 
                        attrRegex=attr, 
                        attrColor=(1.0 , 0.4 , 0.4) ,
                        attrBgColor= [0.22 , 0.22, 0.22]
                    )


AmRig_channelBox()

