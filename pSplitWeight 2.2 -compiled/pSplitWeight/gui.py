#coding=utf-8

try:
    from importlib import reload 
except:
    from imp import reload 
finally:
    pass

import os,sys 

import maya.cmds as cmds 
import maya.mel as mel 

try:
    from . import lib as LIB 
except:
    import lib as LIB 
reload (LIB) 

try:
    from . import api as API
except:
    import api as API
reload (API) 

maya_version = cmds.about(q=True,version=True) 
maya_version = int(maya_version) 
if maya_version <=2022:
    from .maya2018 import utils as UTI 
else:
    from .maya2022 import utils as UTI 
reload (UTI) 



DEBUG = API.Debug.debug 

class UI: 

    def __init__(self):
        pass

        self.name = u'pSplitWeight v2.2 (兼容 maya2022+ )'
        self.ui = u'pSplitWeight_Window'

        self.buildUI() 
        self.updateUI() 
        self.showUI() 
        self.refreshUI() 

    def showUI(self): 
        cmds.showWindow(self.ui) 

    def refreshUI(self): 
        cmds.window(self.ui,e=1,h=1,w=350)

    def buildUI(self): 

        try:
            cmds.deleteUI(self.ui)
        except:
            pass

        cmds.window(self.ui,t=self.name,w=400) 

        #
        column_main = cmds.columnLayout(adj=1) 
        cmds.separator(style='none')

        #
        cmds.setParent(column_main)
        quickly_select_frame = cmds.frameLayout(label=u'Load',mw=10,hlc=[0.3,0.3,0.3],bgc=[0.35,0.35,0.35],
                                    collapseCommand=lambda *args:self.refreshUI(),
                                    cll=1,cl=0) 
        
        cmds.separator( style='none',h=5) 

        
        cmds.rowLayout(numberOfColumns=3,cw=([1,150],[2,200],[3,52]),ct3=['right','both','both'])
        cmds.text(l=u'* 权重源(关节): ',align='left') 
        self.srcInf_field = cmds.textField(tx='',w=125,en=0) 
        cmds.iconTextButton(style='textOnly',label=u'加载',font='fixedWidthFont',w=50,bgc=[0.75,0.75,0.75],c=lambda*args:self.ui_load_or_update_srcInf(1),en=True) 
        cmds.setParent('..') 


        cmds.rowLayout(numberOfColumns=4,cw=([1,150],[2,200],[3,25],[4,25]),ct4=['right','both','both','both']) 
        cmds.text(l=u'目标影响(关节): ',align='left') 
        self.dstInf_option = cmds.optionMenu(label='',changeCommand=lambda*args: self.ui_load_or_update_dstInf(0)) 
        cmds.iconTextButton(style=u'textOnly',label='+',font='fixedWidthFont',bgc=[0.75,0.75,0.75],w=25,h=20,c= lambda *args:self.ui_load_or_update_dstInf(1),en=True) 
        cmds.iconTextButton(style=u'textOnly',label='-',font='fixedWidthFont',bgc=[0.75,0.75,0.75],w=25,h=20,c= lambda *args:self.ui_load_or_update_dstInf(-1),en=True) 
        cmds.setParent('..') 

        cmds.rowLayout(numberOfColumns=4,cw=([1,150],[2,200],[3,25],[4,25]),ct4=['right','both','both','both']) 
        cmds.text(l=u'* 权重计算依赖(曲线/曲面): ',align='left') 
        self.surCrv_option = cmds.optionMenu(label='',changeCommand=lambda*args: self.ui_load_or_update_surCrv(0)) 
        cmds.iconTextButton(style='textOnly',label='+',font='fixedWidthFont',bgc=[0.75,0.75,0.75],w=25,h=20,c= lambda *args:self.ui_load_or_update_surCrv(1),en=True) 
        cmds.iconTextButton(style='textOnly',label='-',font='fixedWidthFont',bgc=[0.75,0.75,0.75],w=25,h=20,c= lambda *args:self.ui_load_or_update_surCrv(-1),en=True) 
        cmds.setParent('..') 


        quickly_select_frame = cmds.frameLayout(label=u'Advanced Option',mw=10,hlc=[0.3,0.3,0.3],bgc=[0.35,0.35,0.35],
                                    collapseCommand=lambda *args:self.refreshUI(),
                                    cll=1,cl=0) 

        cmds.separator( style='none',h=5) 


        cmds.rowLayout(numberOfColumns=4,cw=([1,140],[2,200],[3,25],[4,25]),ct4=['right','both','both','left']) 
        cmds.text( label=u' 权重衰减曲线 : ',align='left') 

        self.weight_curve_option = cmds.optionMenu(label='',w=149,changeCommand=lambda*args: self.edit_fractal_node_c(0)) 
        self.set_optionMenu(self.weight_curve_option,
                            [u'预设01', 
                             u'预设02', 
                             u'预设03', 
                             u'预设04'], 
                             u'预设01') 
        cmds.iconTextButton(style='textOnly',w=50,label=u'编辑',font='fixedWidthFont',bgc=[0.75,0.75,0.75],h=25,
                            c=lambda *args:self.edit_fractal_node_c(1), 
                            en=True) 
        cmds.setParent('..') 

        cmds.rowLayout(numberOfColumns=5,ct5=['right','left','both','both','left']) 
        self.weightType_radioButtonGrp = cmds.radioButtonGrp( label=u'权重计算类型 : ', labelArray2=[u'线性', u'循环'], numberOfRadioButtons=2,select=1) 
        cmds.setParent('..') 

        cmds.rowLayout(numberOfColumns=5,ct5=['right','left','both','both','left']) 
        self.offset_type_radioButtonGrp = cmds.radioButtonGrp( label=u'权重类型 : ', labelArray2=[u'次级', u'关节'], numberOfRadioButtons=2,select=1) 
        cmds.setParent('..') 
        cmds.separator( style='none',h=10) 

        cmds.setParent(column_main) 
        quickly_select_frame = cmds.frameLayout(label=u'Select',mw=10,hlc=[0.3,0.3,0.3],bgc=[0.35,0.35,0.35],
                                    collapseCommand=lambda *args:self.refreshUI(),
                                    cll=1,cl=0) 
        cmds.separator( style='none',h=5) 

        cmds.rowLayout(numberOfColumns=5,cw=([1,150],[2,125],[3,25],[4,25],[5,75]),ct5=['right','both','both','both','both']) 
        cmds.text(l=u'编辑边界(选择点/线): ',align='left') 
        self.quickSel_option = cmds.optionMenu(label='',changeCommand=lambda*args: self.ui_load_or_update_quickSelSet(0),en=True) 
        cmds.iconTextButton(style='textOnly',label='+',font='fixedWidthFont',bgc=[0.75,0.75,0.75],w=25,h=20,c= lambda *args:self.ui_load_or_update_quickSelSet(1),en=True) 
        cmds.iconTextButton(style='textOnly',label='-',font='fixedWidthFont',bgc=[0.75,0.75,0.75],w=25,h=20,c= lambda *args:self.ui_load_or_update_quickSelSet(-1),en=True) 
        cmds.setParent('..') 

        cmds.rowLayout(numberOfColumns=2,ct2=['right','left']) 
        cmds.iconTextButton(style='textOnly',w=200,label=u'查看边界',font='fixedWidthFont',
                            bgc=[0.75,0.75,0.75],c=lambda *args:UTI.QuickSelectVtx().select_quick_select_set(),en=True) 
        cmds.iconTextButton(style='textOnly',w=200,label=u'快速选择顶点',font='fixedWidthFont',
                            bgc=[0.75,0.75,0.75],c=lambda *args:UTI.QuickSelectVtx().multi_loop_sel_vtxs(),en=True) 
        cmds.setParent('..') 

        cmds.rowLayout(numberOfColumns=2,ct2=['right','left']) 
        cmds.iconTextButton(style='textOnly',w=200,label=u'暂存当前选择',font='fixedWidthFont',
                            bgc=[0.75,0.75,0.75],c=lambda *args:UTI.QuickSelectVtx().record_selected_vtx(),en=True) 
        cmds.iconTextButton(style='textOnly',w=200,label=u'回到最后一次选择',font='fixedWidthFont',
                            bgc=[1.0,0.5,0.0],c=lambda *args:self.last_vtx_selected_c(),en=True) 
        cmds.setParent('..') 

        cmds.separator( style='none',h=5) 

        cmds.setParent(column_main) 
        cmds.separator( style='double') 
        cmds.iconTextButton(style='textOnly',label=u'分解权重',font='fixedWidthFont',bgc=[0.0,0.4,0.25],w=300,h=50,c= lambda *args:self.calculate_weight_c(),en=True) 
        cmds.text(l=' @Pan ',h=15,align='right',bgc=[0.1,0.1,0.1]) 

    #
    def updateUI(self):
        self.ui_load_or_update_surCrv(0) 
        self.ui_load_or_update_dstInf(0) 
        self.ui_load_or_update_srcInf(0) 
        self.ui_load_or_update_quickSelSet(0) 
        cmds.select(cl=True) 
    
    #
    def ui_load_or_update_srcInf(self,Edit=False):
        UTI.initMasterSet() 
        if Edit==True:
            UTI.updateSrcInfSet() 
        if cmds.objExists(LIB.SrcInf_Set):
            cmds.select(LIB.SrcInf_Set,r=True) 
        List = cmds.ls(sl=True) 
        if List:
            Value = List[0]
        else:
            Value = ''
        cmds.textField(self.srcInf_field,e=True,text=Value) 
    
    #
    def ui_load_or_update_surCrv(self,Edit=0):
        UTI.initMasterSet() 
        menuList,activate = self.get_optionMenu(self.surCrv_option) 

        if Edit == -1: 
            if activate: 
                cmds.sets(activate, e=True, remove=LIB.SurCrv_Set) 
                menuList.remove(activate) 
                activate = None 

        if Edit == 1: 
            uv_curve = UTI.updateSurCrvSet() 
            if uv_curve in menuList: 
                activate = uv_curve

        # 根据Set重新设定Option 
        List = ['None'] 
        if cmds.objExists(LIB.SurCrv_Set):
            listSetMember = cmds.sets(LIB.SurCrv_Set,q=True) 
            if listSetMember:
                List = List + listSetMember 

        self.set_optionMenu(self.surCrv_option,List,activate) 

        if Edit == 0:
            pass

        if activate:
            try:
                cmds.select(activate,r=True) 
            except:
                pass

    #
    def ui_load_or_update_dstInf(self,Edit=0):
        UTI.initMasterSet() 
        menuList,activate = self.get_optionMenu(self.dstInf_option) 
        if Edit == -1:
            if activate: 
                cmds.delete(activate) 
                menuList.remove(activate) 
                activate = None

        if Edit == 1:
            UTI.AddSubInfSet() 

        # 根据Set重新设定Option 
        List = None 
        if cmds.objExists(LIB.SubInf_Set): 
            List = cmds.listConnections(LIB.SubInf_Set,source=True,destination=False,type='objectSet') 
        if List is not None: 
            for item in List: 
                if item not in menuList: 
                    activate = item 
        self.set_optionMenu(self.dstInf_option,List,activate) 
        if Edit == 0:
            cmds.select(activate,r=True) 
            '''cmds.select(cmds.listConnections(activate,source=True,destination=False),r=True)'''

    #
    def ui_load_or_update_quickSelSet(self,Edit=0):
        UTI.QuickSelectVtx().init_quick_select_set() 
        menuList,activate = self.get_optionMenu(self.quickSel_option) 
        if Edit == -1:
            if activate:
                cmds.delete(activate) 
                menuList.remove(activate) 
                activate = None
        elif Edit == 1:
            UTI.QuickSelectVtx().create_quick_select_set() 
        # 根据Set重新设定Option 
        List = None 
        if cmds.objExists(LIB.QuickSel_Set):
            List = cmds.listConnections(LIB.QuickSel_Set,source=True,destination=False,type='objectSet') 
        if List is not None:
            for item in List:
                if item not in menuList: 
                    activate = item 
        self.set_optionMenu(self.quickSel_option,List,activate) 
        if Edit == 0:
            cmds.select(activate,r=True) 


    # 获取optionMenu的信息
    def get_optionMenu(self,OptionMenu): 
        menuItemList = [] 
        activate = None 
        #
        menuItems = cmds.optionMenu(OptionMenu,q=True,ill=True) 
        if menuItems:
            activate = cmds.optionMenu(OptionMenu,v=True,q=True) 
            for item in menuItems:
                label = cmds.menuItem(item,label=True,q=True) 
                menuItemList.append(label) 
        return (menuItemList,activate) 


    # 设置optionMenu的信息
    def set_optionMenu(self,OptionMenu,MenuItemList=[],ActivateMenuItem=None):
    
        try:
            cmds.deleteUI(cmds.optionMenu(OptionMenu,q=True,ill=True)) 
        except:
            pass

        if MenuItemList:
            for item in MenuItemList:
                cmds.setParent(OptionMenu,menu=True) 
                cmds.menuItem(label=item,p=OptionMenu) 
        if ActivateMenuItem is not None: 
            if ActivateMenuItem in MenuItemList: 
                cmds.optionMenu(OptionMenu,v=ActivateMenuItem,e=True) 


    def last_vtx_selected_c(self): 
        if not cmds.objExists(LIB.LastSel_Set): 
            cmds.warning(u'还没有保存过之前的选择.') 
            return 
        cmds.select(LIB.LastSel_Set,r=True) 





    # 获取绑定数据
    def getSettingInfos(self):
        _dstJoints_set = self.get_optionMenu(self.dstInf_option)[1]
        _dstJoints = API.get_set_member(_dstJoints_set) 

        #
        _nurbsObject = self.get_optionMenu(self.surCrv_option)[1] 
        if _nurbsObject == 'None':_nurbsObject = None 
        #
        _srcJoint = cmds.textField(self.srcInf_field,q=True,tx=True) 
        #
        _weight_falloff_type = cmds.optionMenu(self.weight_curve_option,sl=True,q=True) 
        #
        _weight_type = None 
        if ( cmds.radioButtonGrp(self.weightType_radioButtonGrp, q=True, select=True ) == 1 ): 
            _weight_type = 'Linear' 
        elif ( cmds.radioButtonGrp(self.weightType_radioButtonGrp, q=True, select=True ) == 2 ): 
            _weight_type = 'Circle' 
        #
        _weight_offset_type = cmds.radioButtonGrp(self.offset_type_radioButtonGrp, q=True, select=True ) == 1
        if ( cmds.radioButtonGrp(self.offset_type_radioButtonGrp, q=True, select=True ) == 1 ): 
            _weight_offset_type = 'Secondary' 
        elif ( cmds.radioButtonGrp(self.offset_type_radioButtonGrp, q=True, select=True ) == 2 ): 
            _weight_offset_type = 'Chain' 

        self.settingInfos = {'dstJoints': _dstJoints, 
                             'nurbsObject': _nurbsObject, 
                             'srcJoint': _srcJoint, 
                             'weight_falloff_type': _weight_falloff_type,
                             'weight_type': _weight_type, 
                             'weight_offset_type': _weight_offset_type 
                            } 
        return self.settingInfos 








    def calculate_weight_c(self):
        
        inf = self.getSettingInfos() 
        #
        CW = UTI.pSplitWeight_CLS( 
            srcJoint = inf.get('srcJoint', None), 
            dstJoints = inf.get('dstJoints', None), 
            nurbsObject = inf.get('nurbsObject', None), 
            weight_type = inf.get('weight_type', None), 
            weight_falloff_type = inf.get('weight_falloff_type', None), 
            weight_offset_type = inf.get('weight_offset_type', None) 
            ) 
        CW.set() 

    def create_fit_curve_c(self,do=True):
        inf = self.getSettingInfos() 
        #
        CW = UTI.pSplitWeight_CLS( 
            srcJoint = inf.get('srcJoint', None), 
            dstJoints = inf.get('dstJoints', None), 
            nurbsObject = inf.get('nurbsObject', None), 
            weight_type = inf.get('weight_type', None), 
            weight_falloff_type = inf.get('weight_falloff_type', None), 
            weight_offset_type = inf.get('weight_offset_type', None) 
            ) 
        #
        CW.init_fit_curve() 

    def edit_fractal_node_c(self,do=1): 
        inf = self.getSettingInfos() 
        #
        CW = UTI.pSplitWeight_CLS( 
            srcJoint = inf.get('srcJoint', None), 
            dstJoints = inf.get('dstJoints', None), 
            nurbsObject = inf.get('nurbsObject', None), 
            weight_type = inf.get('weight_type', None), 
            weight_falloff_type = inf.get('weight_falloff_type', None), 
            weight_offset_type = inf.get('weight_offset_type', None) 
            ) 
        
        if do == 0: 
            try:
                cmds.delete(LIB.Fractal_Node)
            except:
                pass
        fractal_node = CW.create_fractal_node() 
        if do == 1: 
            cmds.select(LIB.Fractal_Node,r=True) 
            mel.eval('GraphEditor') 
        

