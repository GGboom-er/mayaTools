# python
import sys , os , subprocess , json
from functools import partial
from collections import OrderedDict

# maya
import pymel.core as pm
import maya.cmds as mc
import maya.mel as mel

# AM_MENU
import AM_MENU
from AM_MENU import relativePath
from AM_MENU.extensions import pyqt , six #, pickWalk
from AM_MENU.extensions.pickWalk import get_all_tag_children
from AM_MENU.core import ikfk_switch , spaceSwitch , mirror , utils
from AM_MENU.extensions.Qt  import QtWidgets , QtGui , QtCore
from AM_MENU.ui import hotkey_ui

# logging
import logging
LOG = logging.getLogger("Am Tools |")
LOG.level = logging.INFO


# from AM_MENU.core import spaceSwitch




BUILD_MENU_CMD_2 = """{importCmd}

try:
    import AM_MENU
    reload(AM_MENU)
    AM_MENU.markingMenu.buildMenus()
except Exception as e:
    raise e
    pass
"""
BUILD_MENU_CMD_3 = """{importCmd}

try:
    import importlib
    import AM_MENU
    importlib.reload(AM_MENU)
    AM_MENU.markingMenu.buildMenus()
except Exception as e:
    raise e
    pass
"""

DESTROY_MENU_CMD_2 = """{importCmd}

try:
    import AM_MENU
    reload(AM_MENU)
    wasInvoked = AM_MENU.markingMenu.destroyMenus()
except Exception as e:
    raise e
else:
    if not wasInvoked:
        pass
"""
DESTROY_MENU_CMD_3 = """{importCmd}

try:
    import importlib
    import AM_MENU
    importlib.reload(AM_MENU)
    wasInvoked = AM_MENU.markingMenu.destroyMenus()
except Exception as e:
    raise e
else:
    if not wasInvoked:
        pass
"""





menuName = 'Am_ToolsMMenu'
ACTIVE_MENUS = []



def Am_ikfk_switch_func( *args):
    key = args[0]
    ikfk_switch.switch_func(key)



def Am_mirror_flip_pose_func(*args):
    
    controls = [pm.PyNode(x) for x in args[0]]
    for ctl in controls:
        mirror.mirrorPose(flip=args[1], nodes=[ctl])





def getModifiers():
    mods = mc.getModifiers()
    isShiftPressed = (mods & 1) > 0
    isCtrlPressed = (mods & 4) > 0
    isAltPressed = (mods & 8) > 0
    return (isShiftPressed, isCtrlPressed, isAltPressed)






def getHotkeyKwargs(keyString):
    split = keyString.lower().split('+')
    kwargs = {}
    for s in split:
        if s == 'alt':
            kwargs['alt'] = True
        elif s == 'shift':
            kwargs['sht'] = True
        elif s == 'ctrl':
            kwargs['ctl'] = True
        elif s == 'command':
            kwargs['cmd'] = True
        else:
            if 'k' not in kwargs:
                kwargs['k'] = s
            else:
                raise ValueError('Invalid keyString: ' + keyString)
    return kwargs






def _switchToNonDefaultHotkeySet():
    if not hasattr(mc, 'hotkeySet'):
        return
    current = mc.hotkeySet(q=True, cu=True)
    if current == 'Maya_Default':
        existing = mc.hotkeySet(q=True, hotkeySetArray=True)
        if 'Maya_Default_Duplicate' in existing:
            mc.hotkeySet('Maya_Default_Duplicate', e=True, cu=True)
            LOG.info("Switched to hotkey set: Maya_Default_Duplicate")
        elif len(existing) > 1:
            for e in existing:
                if e != 'Maya_Default':
                    mc.hotkeySet(e, e=True, cu=True)
                    LOG.info("Switched to hotkey set: " + e)
                    break
        else:
            mc.hotkeySet('Maya_Default_Duplicate', src='Maya_Default', cu=True)
            LOG.info("Created duplicate hotkey set: Maya_Default_Duplicate")









class setHotkey_class(QtWidgets.QDialog , hotkey_ui.Ui_Dialog ):

    def __init__(self, parent = None ):
        super(setHotkey_class , self).__init__( parent )
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        self.setupUi(self)
        self.create_connections()
        self.create_window()
        self.create_layout()
        Hkey = AM_MENU.getPref_data("markingMenu_key")
        
        self.current_key_label.setText(Hkey)
        self.show()
        
        
    def create_window(self):

        self.setObjectName( "AmToolSetKotkeyMenu")
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Am_Tools | Set Hotkey ")
        self.resize(290, 225)

    def create_layout(self):

        self.gmc_layout = QtWidgets.QVBoxLayout()
        self.gmc_layout.addWidget(self)
        self.gmc_layout.setContentsMargins(3, 3, 3, 3)

        self.setLayout(self.gmc_layout)

    
    
    def create_connections(self):
        self.close_btn.clicked.connect(self.close)
        self.ok_btn.clicked.connect(self.set_hotkey)
        self.remove_btn.clicked.connect(self.remove_hotkey)
    
    
    
    
    
    def remove_hotkey(self):
        
        currentKey = AM_MENU.getPref_data("markingMenu_key")
        if currentKey:
            removeMenuHotkeys( currentKey )
            LOG.info("successful remove markingmenu hotkey ")
            self.current_key_label.setText("")
            AM_MENU.setPref_data("markingMenu_key" , "")
    
    
    
    
    def set_hotkey( self ):
        
        if not self.hotKey_lineEdit.text():
            LOG.warning("Enter atless one key letter for Am Tools menu")
            return
            
        command = ""
        if self.alt_chb.isChecked(): command += "alt+"
        if self.ctrl_chb.isChecked(): command += "ctrl+"
        if self.shift_chb.isChecked(): command += "shift+"
        command += self.hotKey_lineEdit.text()
        registerMenuHotkeys(command)
        
        AM_MENU.setPref_data("markingMenu_key" , "{}".format(command))
        
        
        LOG.info("markingmenu hotkey set with %s" %command)
        self.close()
    
    




def registerMenuHotkeys( hotkey ):
    
    global menuName
    
    rtCmdIdFmt = "AM_MENU_{0}_{1}"
    namedCmdIdFmt = "AM_MENU_{0}_{1}_nameCmd"
    
    keyKwargs = getHotkeyKwargs(hotkey)
    annotation = "A collection of useful tools at working Am_Rig "
    
    runTimeKwargs = {
        "annotation": annotation,
        "category": "Custom Scripts.AM_MENU",
        "cl":"python",
    }

    # clean prebuild and secondary commands
    importCmd = ""
    
    # create run time commands
    if six.PY2:
        buildCmd = BUILD_MENU_CMD_2.format(menuName=menuName, importCmd=importCmd)
        destroyCmd = DESTROY_MENU_CMD_2.format(menuName=menuName, importCmd=importCmd)
    else:
        buildCmd = BUILD_MENU_CMD_3.format(menuName=menuName, importCmd=importCmd)
        destroyCmd = DESTROY_MENU_CMD_3.format(menuName=menuName, importCmd=importCmd)
        

    buildRtCmdId = rtCmdIdFmt.format("build", menuName)
    if mc.runTimeCommand(buildRtCmdId, q=True, ex=True):
        mc.runTimeCommand(buildRtCmdId, e=True, delete=True)
    mc.runTimeCommand(buildRtCmdId, c=buildCmd, **runTimeKwargs)

    buildNameCmdId = namedCmdIdFmt.format("build", menuName)
    mc.nameCommand(buildNameCmdId, c=buildRtCmdId, ann=buildRtCmdId + " Named Command")

    destroyRtCmdId = rtCmdIdFmt.format("destroy", menuName)
    if mc.runTimeCommand(destroyRtCmdId, q=True, ex=True):
        mc.runTimeCommand(destroyRtCmdId, e=True, delete=True)
    mc.runTimeCommand(destroyRtCmdId, c=destroyCmd, **runTimeKwargs)

    destroyNameCmdId = namedCmdIdFmt.format("destroy", menuName)
    mc.nameCommand(destroyNameCmdId, c=destroyRtCmdId, ann=destroyRtCmdId + " Named Command")
    
    _switchToNonDefaultHotkeySet()
    mc.hotkey(name=buildNameCmdId, **keyKwargs)
    mc.hotkey(releaseName=destroyNameCmdId, **keyKwargs)


def removeMenuHotkeys( hotkey ):
    global menuName
    
    rtCmdIdFmt = "AM_MENU_{0}_{1}"
    namedCmdIdFmt = "AM_MENU_{0}_{1}_nameCmd"
    keyKwargs = getHotkeyKwargs(hotkey)
    
    buildRtCmdId = rtCmdIdFmt.format("build", menuName)
    if mc.runTimeCommand(buildRtCmdId, q=True, ex=True):
        mc.runTimeCommand(buildRtCmdId, e=True, delete=True)

    destroyRtCmdId = rtCmdIdFmt.format("destroy", menuName)
    if mc.runTimeCommand(destroyRtCmdId, q=True, ex=True):
        mc.runTimeCommand(destroyRtCmdId, e=True, delete=True)
    
    # clear hotkeys if set
    buildNameCmdId = namedCmdIdFmt.format("build", menuName)
    destroyNameCmdId = namedCmdIdFmt.format("destroy", menuName)
    keyQueryKwargs = keyKwargs.copy()
    key = keyQueryKwargs.pop('k')
    if mc.hotkey(key, query=True, name=True, **keyQueryKwargs) == buildNameCmdId:
        mc.hotkey(name="", **keyKwargs)
    if mc.hotkey(key, query=True, releaseName=True, **keyQueryKwargs) == destroyNameCmdId:
        mc.hotkey(releaseName="", **keyKwargs)






def buildMenus():
    
    global ACTIVE_MENUS
    
    destroyMenus()
    inst = Am_viewportMenu()
    if inst.shouldBuild():
        ACTIVE_MENUS.append(inst)
        inst.build()
            




def destroyMenus():
    
    global ACTIVE_MENUS
    
    wasAnyInvoked = False
    for m in ACTIVE_MENUS:
        wasAnyInvoked = wasAnyInvoked or m.wasInvoked
        LOG.debug('Destroying menu: {0}'.format(m))
        m.destroy()
    ACTIVE_MENUS = []
    
    return wasAnyInvoked





class Am_viewportMenu(object):
    
    def __init__(self):
        
        isShiftPressed, isCtrlPressed, isAltPressed = getModifiers()
        self.popupKeyKwargs = {
            'mm': True,
            'aob': True,
            'parent':'viewPanes',
            'sh':isShiftPressed,
            'ctl':isCtrlPressed,
            'alt':isAltPressed,
        }
        
        self.wasInvoked = False
        self.panel = mc.getPanel(up=True)
        self.panelType = mc.getPanel(typeOf=self.panel)
        self.popupMenuId = 'Am_VMenu'
        self.mouseButton = 1
        self.buildItemsOnShow = True

    def shouldBuild(self):
        return True


    def build(self):
        
        self.destroy()
        self.menu = mc.popupMenu(self.popupMenuId, b=self.mouseButton, postMenuCommand = self.onMenuWillShow , **self.popupKeyKwargs)
        if not self.buildItemsOnShow:
            mc.setParent(self.menu , m=True)
            self.buildMenuItems()
    
    
    
    def destroy(self):
        
        if mc.popupMenu(self.popupMenuId, q=True, ex=True):
            mc.deleteUI(self.popupMenuId)
    
    
    
    def onMenuWillShow(self , menu, parent):
        self.wasInvoked = True
        if self.buildItemsOnShow:
            self.sel = mc.ls(sl=True , l=True)
            mc.popupMenu(self.menu , e=True ,  deleteAllItems=True)
            mc.setParent(self.menu, m=True)
            self.buildMenuItems()
    
    
    
    def buildMenuItems(self):
        query = lambda x : mc.modelEditor(self.panel, q=True, **{x:True})
        selected = self.sel
        current_control = selected[0] if selected else None
        userAttr = mc.listAttr(current_control , userDefined=True, keyable=False) if current_control else []
        
        
        is_AmRig = True if current_control and mc.attributeQuery( 'AmCtrl', node=current_control , exists=True ) else False
        for ctl in selected:
            if not utils.uniqueName(ctl):
                LOG.warning("More than one object matches name: {}. Am Tools is available by limited options".format(ctl.split("|")[-1]))
                # is_AmRig = False
                break
        
        
        child_controls = []
        if is_AmRig:
            
            for ctl in selected:
                try:
                    # [child_controls.append(x) for x in pickWalk.get_all_tag_children(mc.ls(mc.listConnections(ctl), type="controller"))if x not in child_controls]
                    [child_controls.append(x) for x in get_all_tag_children(ctl) if x not in child_controls]
                except:
                    pass
            
            if child_controls:
                child_controls.append(current_control)
        
        
        
        display_subMenu = mc.menuItem(p= self.menu , rp='N' ,   l='Toggle Display' , subMenu=1 , i='Am_visibility_32.png')
        mc.menuItem(p=display_subMenu , rp='N', ecr=False,      l='Polys',      cb=query('polymeshes'),     c=partial( self.__class__.setDisplay , self.panel , not(query('polymeshes')) , ['polymeshes'] ))
        mc.menuItem(p=display_subMenu , rp='NW', ecr=False,     l='Curves',     cb=query('nurbsCurves'),    c=partial( self.__class__.setDisplay , self.panel , not(query('nurbsCurves')) , ['nurbsCurves'] ))
        mc.menuItem(p=display_subMenu , rp='NE', ecr=False,     l='Surfaces',   cb=query('nurbsSurfaces'),  c=partial( self.__class__.setDisplay , self.panel , not(query('nurbsSurfaces')) , ['nurbsSurfaces', 'subdivSurfaces'] ))
        mc.menuItem(p=display_subMenu , rp='E', ecr=False,      l='joints',     cb=query('joints'),         c=partial( self.__class__.setDisplay , self.panel , not(query('joints')) , ['joints'] ))
        mc.menuItem(p=display_subMenu , rp='W', ecr=False,      l='locators',   cb=query('locators'),       c=partial( self.__class__.setDisplay , self.panel , not(query('locators')) , ['locators'] ))
        mc.menuItem(p=display_subMenu , rp='SE', ecr=False,     l='deformers',  cb=query('deformers'),      c=partial( self.__class__.setDisplay , self.panel , not(query('deformers')) , ['deformers'] ))
        mc.menuItem(p=display_subMenu , rp='SW', ecr=False,     l='ikHandles',  cb=query('ikHandles'),      c=partial( self.__class__.setDisplay , self.panel , not(query('ikHandles')) , ['ikHandles'] ))
        mc.menuItem(p=display_subMenu , rp='S', ecr=False,      l='Cameras',    cb=query('cameras'),        c=partial( self.__class__.setDisplay , self.panel , not(query('cameras')) , ['cameras'] ))
        
        mc.menuItem(p=self.menu , rp='NE',ecr=False , l='Reset Translate' , c= partial( self.__class__.resetValue , selected , ['t'] )  , i = "Am_resetTranslate_32.png")
        Reset_subMenu = mc.menuItem(p= self.menu , rp='E' , l='Reset' , subMenu=1 , i='Am_reset_32.png')
        mc.menuItem(p= Reset_subMenu ,  rp='NE',    l='Reset channelBox' ,          c= partial( self.__class__.reset_channelBox , selected ) , i='Am_resetChannelBox_32.png')
        mc.menuItem(p= Reset_subMenu ,  rp='E',     l='Reset Rotate' ,              c= partial( self.__class__.resetValue , selected , ["r"] ) , i='Am_resetRotate_32.png')
        mc.menuItem(p= Reset_subMenu ,  rp='SE',    l='Reset_SRT' ,                 c= partial( self.__class__.resetValue , selected , ["t","r","s"] ) , i='Am_reset_32.png')
        mc.menuItem(p= Reset_subMenu ,  rp='NW',     l='Reset selected Attribute' ,  c= partial( self.__class__.resetValue , selected , ["channelBox"] ) , i='Am_resetSelectedAttr_32.png')
        if is_AmRig and child_controls:
            mc.menuItem(p= Reset_subMenu ,  rp='SW',     l='Reset all bellow' ,          c= partial( self.__class__.reset_channelBox , child_controls ) , i='Am_resetBellow_32.png')
        
        mc.menuItem(p=self.menu , rp='SE',ecr=False , l='Reset Scale' , c= partial( self.__class__.resetValue , selected , ['s'] )  , i = "Am_resetScale_32.png")
        
        if is_AmRig and child_controls:
            mc.menuItem(p=self.menu , rp='S',ecr=False , l='Select child controls' , c= partial( self.__class__.select_nodes , child_controls )  , i = "Am_select_child.png")
        
        
        
        # select all rig controls
        if is_AmRig:
            selection_set = mc.ls(mc.listConnections(current_control),type="objectSet")
            if selection_set:
                for item in selection_set:
                    if mc.attributeQuery( 'is_controllers_set', node=item , exists=True ):
                        all_rig_controls = mc.sets(item , query=True)
                        mc.menuItem(p=self.menu , rp='SW',ecr=False , l='Select all controls' , c= partial( self.__class__.select_nodes , all_rig_controls )  , i = "Am_select_32.png")
                        
        
        xRay_subMenu = mc.menuItem(p= self.menu , rp='W' , l='X_ray' , subMenu=1 , i='Am_XRay_32.png')
        mc.menuItem(p= xRay_subMenu ,rp='W', l='X_Ray' , ecr=True , c = pm.Callback(self.toggle_mode , 'xray') , i = 'Am_XRay_32.png')
        mc.menuItem(p= xRay_subMenu ,rp='S', l='joint X_ray' , ecr=True , c = pm.Callback(self.toggle_mode , 'joint') , i = 'Am_XRayJoint_32.png')
        
        
        mc.menuItem(p= self.menu ,rp='NW', l='Isolate' , ecr=True , c = self.switch_isolate , i = 'Am_isolate_32.png')
        
        

            
        _p_switch_menu = mc.menuItem(p= self.menu , l='Space' , subMenu=True , tearOff=False , i='Am_space_32.png')
            
        if userAttr and 'space' in userAttr :
            mc.radioMenuItemCollection(parent=_p_switch_menu)
            k_values = mc.addAttr("{}.space".format(current_control), query=True, enumName=True).split(":")
            current_state = mc.getAttr("{}.space".format(current_control) )
            
            for idx , k_val in enumerate(k_values):
                if idx == current_state:
                    state = True
                else:
                    state = False
                mc.menuItem(parent=_p_switch_menu, label= k_val, radioButton=state , c = partial( spaceSwitch.switch_space_func , current_control , idx))
                
            mc.menuItem(p=_p_switch_menu, divider=True)
            
        mc.menuItem(p= _p_switch_menu , l='Add New Space' , ecr=True , c = partial ( spaceSwitch.add_new_space , selected ) , i = "Am_space_32.png")
        mc.menuItem(p= _p_switch_menu , l='Space Renamer' , ecr=True , c = partial ( spaceSwitch.exec_space_renamer ) , i= "Am_addGroup_32.png" )
        mc.menuItem(p= _p_switch_menu , l='Add Space Group' , ecr=True , c = partial ( spaceSwitch.add_space_group , current_control ) , i= "Am_addGroup_32.png" )
        
        
        
        
        if is_AmRig and userAttr and 'match_nodes' in userAttr :
            mc.menuItem(p= self.menu , divider=True)
            mc.menuItem(p= self.menu , l='Switch Ik/Fk' , ecr=True , c = partial( Am_ikfk_switch_func , False ) , i = "Am_IkFkSwitch_32.png")
            mc.menuItem(p= self.menu , l='Switch Ik/Fk + Key' , ecr=True , c = partial( Am_ikfk_switch_func , True ) , i = "Am_IkFkSwitch_key_32.png")
                
        if is_AmRig:
            # add mirror
            mc.menuItem(p= self.menu , divider=True)
            mc.menuItem(p= self.menu, label="Mirror" , ecr=True, c = partial(Am_mirror_flip_pose_func , selected , False) , i= "Am_mirror_32.png")
            if child_controls:
                mc.menuItem(p= self.menu, label="Mirror all bellow", ecr=True , c =partial(Am_mirror_flip_pose_func , child_controls , False) , i= "Am_mirror_32.png")
            
            # add flips
            mc.menuItem(p= self.menu, label="Flip" , ecr=True , c =partial(Am_mirror_flip_pose_func, selected, True) , i= "Am_flip_32.png")
            if child_controls:
                mc.menuItem(p= self.menu, label="Flip all bellow" , ecr=True , c =partial(Am_mirror_flip_pose_func, child_controls, True) , i= "Am_flip_32.png")
            mc.menuItem(p= self.menu , divider=True)
            
        
        if is_AmRig:
            _Settings_menu = mc.menuItem(p= self.menu , l='Settings' , subMenu=True , tearOff=False , i = "Am_settings_32.png")
            mc.menuItem(p= _Settings_menu , label="component setting" , ecr=True , c = self.__class__.get_CompSetting , i= "Am_compSettings_32.png" )
            mc.menuItem(p= _Settings_menu , label="switch pose" , ecr=True , c = self.__class__.switchPose , i = "Am_switch_32.png") 
            
    
    
    
    
    @staticmethod
    def get_CompSetting(*args):
        
        sel = pm.selected()
        
        if sel and sel[0].hasAttr("AmCtrl"):
                
            item = sel[0]
            setting_node = None
            while True:
                parent = item.getParent()
                if parent and parent.hasAttr("componentType"):
                    setting_node = parent
                    break
                elif parent:
                    item = parent
                else:
                    break
            
            pm.select(setting_node)
            
    
    
    
    
    
    @staticmethod
    def get_option_var_state( ov_name ):
        if not mc.optionVar(exists = ov_name):
            mc.optionVar(intValue = (ov_name, 0))
        
        return mc.optionVar(query = ov_name)
        
        
    @classmethod
    def switchPose(cls , *args):
        
        sel = mc.ls(sl=True)
        if not sel:
            return
        
        if mc.attributeQuery( 'AmCtrl', node=sel[0] , exists=True ):
            cls.goto_rigPose(cls.get_option_var_state('goto_rigPose__ov'))
            mc.optionVar(intValue=("goto_rigPose__ov", not cls.get_option_var_state('goto_rigPose__ov')))
    
    
    @classmethod
    def goto_rigPose(cls , idx = 0):
        
        current_control = mc.ls(sl=True)
        if not current_control:
            return

        selection_set = mc.ls(mc.listConnections(current_control[0]),type="objectSet")
        if selection_set:
            for item in selection_set:
                if mc.attributeQuery( 'is_controllers_set', node=item , exists=True ):
                    all_rig_controls = mc.sets(item , query=True)
                    cls.toPoseAttr(all_rig_controls , idx)
    
    
    @staticmethod
    def toPoseAttr( controls, poseAttr=0):
        if not isinstance(controls, list):
            controls = [controls]

        for ctrl in controls:
            ctrlPoseAttr = "{}.Am_pose_{}".format(ctrl,poseAttr)
            poseAttrName = ctrlPoseAttr.split(".")[-1]

            if not poseAttrName in mc.listAttr(ctrl):
                continue
            
            ctrlAttrDict = eval(mc.getAttr(ctrlPoseAttr))
            for attr in ctrlAttrDict:
                try:
                    mc.setAttr("{}.{}".format(ctrl,attr), ctrlAttrDict[attr])
                except:
                    pass

        
        
        
        
        
    @classmethod
    def switch_isolate(cls , *args):
        currentPanel = mc.getPanel(wf=True)
        state = mc.isolateSelect(currentPanel, query=True, state=True)
        mel.eval('enableIsolateSelect %s %d' % (currentPanel,not state) )




        
    @classmethod
    def select_nodes (cls , *args):
        try:
            mc.select(args[0] , add=True)
        except:
            pass
            
    
    def toggle_mode(self , mode = 'xray'):
        
        if mode == 'xray':
            newState = not mc.modelEditor( self.panel, query=True, xray=True )
            mc.modelEditor( self.panel, edit=True, xray= newState)
        
        elif mode == 'wire':
            newState = not mc.modelEditor( self.panel, query=True, wos=True )
            mc.modelEditor( self.panel, edit=True, wos= newState)

        elif mode == 'joint':
            newState = not mc.modelEditor( self.panel, query=True, jx=True )
            mc.modelEditor( self.panel, edit=True, jx= newState)

        

    @classmethod
    def setDisplay(cls , *args ):
        
        panel = args[0]
        enabled = args[1]
        keys = args[2]
        
        kwargs = {}
        for k in keys:
            kwargs[k] = enabled
        mc.modelEditor(panel, e=True, **kwargs)
    
    
    
    
    @classmethod
    def resetValue (cls , *args ):
        
        selection = args[0]
        operation = args[1]
        
        for op in operation: 
            if op in ['t' , 'r' , 's']:
                cls.set_default_value(selection , [op + axis for axis in ['x', 'y' , 'z']] )
                
        if "channelBox" in operation:
            sel_attr = cls.getchannelBox_selected()
            if sel_attr:
                cls.set_default_value(selection , sel_attr )
        
        
    
    @classmethod
    def set_default_value(cls , objs , attribute=  [ "tx", "ty", "tz","rx", "ry", "rz","sx", "sy", "sz"]):
        
        if not objs:
            return
            
        if not isinstance(objs, list):
            objs = [objs]
        
        for item in objs:
            for atr in attribute:
                try:
                    dv = mc.attributeQuery(atr , node= item , listDefault=True)[0]
                    mc.setAttr("%s.%s" % (item, atr ), dv )
                except:
                    pass
    
    
    
    
    @classmethod
    def reset_channelBox(cls , *args):
        for obj in args[0] :
            keyable_attrs = mc.listAttr(obj , keyable=True)
            cls.set_default_value(obj , keyable_attrs )

    
    
    
    @classmethod
    def getchannelBox_selected(cls ):
        
        ch_Box = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')
        attr_selected = mc.channelBox(ch_Box, q=True, sma=True)
        
        return attr_selected










