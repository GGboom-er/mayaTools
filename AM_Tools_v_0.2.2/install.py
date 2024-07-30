import os
import sys
import shutil

try:
    from maya.app.startup import basic
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
    import maya.OpenMayaUI as OpenMayaUI
    from maya import cmds , mel
    import pymel.core as pm
    import maya.api.OpenMaya as om
    maya_app = True
    
except ImportError():
    maya_app = False







def _install():

    # -- current folder where the installer resides 
    current_folder = os.path.dirname(__file__)
    
    install_path = current_folder
    cmds.flushUndo()
    
    
    if not os.path.join(install_path, "scripts") in sys.path:
        sys.path.append(os.path.join(install_path, "scripts"))
        
    
    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # -- install plugins --
    
    plugin_dir = "plug-ins"
    install_plugins = False
    maya_version    = cmds.about(version=True)
    
    if install_plugins:
        
        try:
            cmds.unloadPlugin("weightDriver.mll", force=True)
        except:
            pass
        
        platform        = 'windows'
        if cmds.about(win64=1):
            platform    = 'windows' # 'mll'
            
        elif cmds.about(macOSx86=1):
            platform    = 'osx' # 'lib'
            
        elif cmds.about(linux64=1):
            platform    = 'linux' # 'os'
            
        plugin_dir      = os.path.join("platforms" , maya_version , platform , "x64" , "plug-ins" )
        plugin_folder   = os.path.join(install_path , plugin_dir )
        
        
        # # Add plugin folder to Maya Plugins
        mel.eval('putenv "MAYA_PLUG_IN_PATH" (`getenv "MAYA_PLUG_IN_PATH"`+";{0}")'.format(plugin_folder))
        
        # # Try autoload AM_Tools plugins
        files_path = [plugin_folder + os.sep + x for x in os.listdir(plugin_folder)]
        for plug in files_path:
            try:
                cmds.loadPlugin(plug, qt=True)
                if cmds.pluginInfo(plug , q=True, loaded=True):
                    cmds.pluginInfo(plug, edit=1, autoload=True)
            except:
                pass
        
        # -- allows for not having to restart maya
        cmds.loadModule(scan=True)
        cmds.loadModule(allModules=True)
        
        # -- force load the plugins just incase it does not happen
        try:
            cmds.loadPlugin("weightDriver.mll")
        except:
            pass
            
    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    
    
    maya_modules = os.path.normpath(os.path.join(os.environ["MAYA_APP_DIR"], cmds.about(version=True), "modules"))
    
    if not os.path.isdir(maya_modules):
        os.makedirs(maya_modules)
        
    menu_mod   = os.path.join(maya_modules , "AM_Tools.mod" )
    if os.path.isfile(menu_mod):
        os.remove(menu_mod)

    mod_discrib = """+ AM_Tools 1.0 {}
plug-ins: {}
icons: icons
scripts: scripts
""".format(install_path , plugin_dir )
    
    
    f_dst = open( menu_mod , 'w')
    f_dst.write (mod_discrib)
    f_dst.close ( )
    
    
    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    
    
    # -- reload user setup files
    basic.executeUserSetup()
    
    
    # -- installation message
    message = ("Installation Complete!\nPlease Reset Maya")
    # -- installation dialog window
    input = cmds.confirmDialog(title="Installation",
                             message=message,
                             icon="information",
                             button=["OK"])
    
    pm.displayInfo("Installation Complete. Please Reset Maya")
    


if maya_app:
    _install()











