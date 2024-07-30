import json , os
import datetime
import webbrowser
import pymel.core as pm
from functools import partial

# relativePath
relativePath = os.path.dirname(os.path.abspath(__file__))



# AM_MENU
import AM_MENU
from AM_MENU import version , markingMenu
from AM_MENU.ui import update_ui
from AM_MENU.extensions import pyqt
from AM_MENU.extensions.Qt  import QtWidgets , QtGui , QtCore
from AM_MENU.core.python_utils import  PY2 , Object
from AM_MENU.core import utils




maya_ver = int(utils.getMayaVer2())




# add AM_MENU :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def AM_toolsMenuLoader():
    main_window = pm.language.melGlobals['gMainWindow']
    menu_obj = 'AMToolsMenu'
    menu_label = 'AM Tools'
    
    AM_custom_tools_menu = pm.menu(menu_obj , label=menu_label , parent=main_window, tearOff=True )
    
    pm.menuItem(label = 'Set Hotkey' , command = partial( setHotkey ) , i = "Am_menu_Hotkey_32.png")
    
    if maya_ver >= 2018:
        from AM_MENU.extensions  import  anim_picker , aboutAnimPicker
        
        pm.menuItem(label = 'Anim Picker' , subMenu=True , parent=AM_custom_tools_menu , tearOff=True , i = "Am_select_32.png")
        pm.menuItem(label = 'Anim Picker' , command = partial(anim_picker.load , False) )
        pm.menuItem(label = 'Edit Anim Picker' , command = partial(anim_picker.load , True))
        pm.menuItem( label = 'Help' , divider=True)
        pm.menuItem(label = 'About Anim Picker' , command = partial( aboutAnimPicker ))
        pm.setParent('..' , menu=True)
        
    pm.menuItem( label = 'Help' , divider=True)
    pm.menuItem(label = 'Contact Us' , command = partial(webbrowser.open , 'https://movahhedi.com/contact/') , i = "Am_contact1_32.png")
    pm.menuItem(label = 'Check for Updates' , command = partial( AM_MENU.checkForUpdate ))
    pm.menuItem(label = 'About' , command = partial( AM_MENU.about_AM_Tools ))

    

def setHotkey(*args):
    markingMenu.setHotkey_class(pyqt.maya_main_window())
    











class UpdateWin(QtWidgets.QDialog , update_ui.Ui_Form ):

    def __init__(self, parent=None):
        super(UpdateWin , self).__init__(parent)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setupUi(self)
        
        
        # window
        self.setObjectName( "AmToolVersionUpdate")
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Am_Tools | version update ")
        self.setMinimumSize(QtCore.QSize(420, 215))
        self.resize(420 , 215)
        
        
        # layout 
        self.gmc_layout = QtWidgets.QVBoxLayout()
        self.gmc_layout.addWidget(self)
        self.gmc_layout.setContentsMargins(3, 3, 3, 3)
        self.setLayout(self.gmc_layout)
        
        # connect signal
        self.create_connections()
        
        
        
        self.status_label.setText("<strong>Checking for update...</strong>")
        self.current_version_label.setText("<strong>{0}</strong>".format(version.version))
        
        checkUpdate = getPref_data("AutoCheckUpdate")
        self.autoUpdate_chb.setChecked(checkUpdate)
        
        self.visibleItems = [self.current_version_tag , self.current_version_label , self.released_data_tag , self.released_data_label, self.sep_line , self.gotoUpdatePage_btn]
        for item in self.visibleItems:
            item.setVisible(False)
        
    def create_connections(self):
        self.close_btn.clicked.connect(self.close)
        self.autoUpdate_chb.toggled.connect(self.changeAutoUpdate)
        
        
        
    def success_dwn(self , info):

        self.status_label.setText("<strong>{0}</strong>".format('Update available!' if info.update_available else "AM_Tools is up to date"))
        
        if info.update_available:
            
            for item in self.visibleItems:
                item.setVisible(True)
            
            self.released_data_label.setText(
                "Update available: <strong>{0}</strong>, released on {1}".format(info.latest_version, info.update_date.strftime("%d %B, %Y"))
            )
            self.gotoUpdatePage_btn.setText("Download AM_Tools v" + info.latest_version)

            @pyqt.on(self.gotoUpdatePage_btn.clicked)
            def open_link():
                webbrowser.open_new(info.download_url)

    
    
    def changeAutoUpdate(self):
        
        if self.autoUpdate_chb.isChecked():
            setPref_data("AutoCheckUpdate" , True)
        else:
            setPref_data("AutoCheckUpdate" , False)
        
    
    
    


class UpdateChecker(Object):
    
    def __init__(self , manually = False ):
        
        self.win = UpdateWin(pyqt.maya_main_window())
        showUi = self.win.autoUpdate_chb.isChecked()
        
        if showUi:
            res = self.download_info()
            if res[0] and res[1]:
                if res[1].update_available:
                    self.win.success_dwn(res[1])
                    self.win.show()
        elif not manually:
            self.win.close()
    
    
    
    def download_info(self):
        
        if PY2:
            from urllib2 import urlopen, Request
        else:
            from urllib.request import urlopen, Request
        
        
        url = "https://movahhedi.com/Am_Tools_versionChecker.php"
        
        result = False
        try:
            result = urlopen(url , timeout=5).read()
        except Exception as e:
            print (e)
            
        info = None
        if result:
            response = json.loads(result)
            info = UpdateInfo()
            info.update_date = datetime.datetime.strptime(response['dateReleased'],"%Y-%m-%d")
            info.latest_version =  '.'.join(str(e) for e in response['latestVersion'])
            info.download_url = response['downloadUrl']
            info.update_available = version.compareVer([int(i)for i in response["latestVersion"]] )
            
            
        return result , info




class UpdateInfo(Object):
    def __init__(self):
        self.update_available = False
        self.update_date = ''
        self.latest_version = ''
        self.download_url = ''



def checkForUpdate(*args):
    
    checker = UpdateChecker(manually = True)
    checker.win.show()
    res = checker.download_info()
    
    if not res[0]:
        checker.win.status_label.setText("<strong>Error connection</strong>")
    
    elif res[0] and res[1]:
        checker.win.success_dwn(res[1])
        







# load data perf :::::::::::::::::::::::::::::::::::::::::::::::::::::

def getPref_data(key):
    
    pref_file   = os.path.normpath(os.path.join(relativePath , 'pref.json'))
    
    if not os.path.isfile( pref_file ):
        return ""
    
    _file   = open(pref_file)
    data    = json.load(_file)
    _file.close()
    
    current_hotHey = data.get(key)
    
    return current_hotHey





# set data perf :::::::::::::::::::::::::::::::::::::::::::::::::::::

def setPref_data(key , value):  
    
    pref_file   = os.path.normpath(os.path.join(relativePath , 'pref.json'))
    
    _file   = open(pref_file)
    data    = json.load(_file)
    _file.close()
    
    data[key] = value
    
    json_data       = json.dumps(data , sort_keys=True , ensure_ascii = True , indent = True)
    
    f = open(pref_file , 'w')
    f.write(json_data)
    f.close()
    





# about AM_Tools Win :::::::::::::::::::::::::::::::::::::::::::::::::::::

def about_AM_Tools(*args):
    """About AM_Tools"""
    AM_Tools_ver = version.version
    
    note = """

    AM_Tools version: {}

    AM_Tools is under the terms of the MIT License
    
    Copyright (c) 2021 Seyed Abolfazl Movahhedi
    
    AM_Tools is a small and free tool for all characters that has developed 
    by AM_Rig Tool.
    AM_Tools is also available for other Rigging by limited options.
    for further information and download tutorials please check out below link.
    
    https://movahhedi.com

    """.format(AM_Tools_ver)
    pm.confirmDialog(title='About AM_Tools', message=note, button=["OK"],
                     defaultButton='OK', cancelButton='OK', dismissString='OK')
