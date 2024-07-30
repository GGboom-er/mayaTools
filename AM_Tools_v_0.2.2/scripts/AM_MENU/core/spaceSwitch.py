# python
import  os , subprocess


# maya
import pymel.core as pm
import maya.cmds as mc
import maya.api.OpenMaya as OpenMaya


# AM_Tools 
# import AM_MENU
from AM_MENU.core import utils
from AM_MENU.extensions import pyqt
from AM_MENU.extensions.Qt import QtWidgets ,QtGui , QtCore
from AM_MENU.ui import space_initializer_ui
from AM_MENU.ui import space_renamer_ui
# reload(srUI)

# logging
import logging
LOG = logging.getLogger("Am Tools |")


maya_ver = int(utils.getMayaVer2())




class space_initializer(QtWidgets.QDialog, space_initializer_ui.Ui_Dialog):

    def __init__(self, parent=None):
        self.toolName = "space_initializer"
        super(space_initializer, self).__init__(parent=parent)
        self.setupUi(self)

        self.use_translate = True
        self.use_rotate = True
        self.cons_mode = "constraint"
        
        self.create_connections()
        self.setWindowTitle("Space Initializer")

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

    def create_connections(self):
        self.buttonBox.accepted.connect(self.ok)
        self.buttonBox.rejected.connect(self.cancel)

    def ok(self):
        self.use_translate = self.useTrans_chb.isChecked()
        self.use_rotate = self.useRotate_chb.isChecked()
        if self.by_blnd_rb.isChecked():
            self.cons_mode = "blnd"
        
    def cancel(self):
        LOG.warning("add new space Cancelled")


def exec_space_initializer(*args):

    windw = space_initializer()
    if windw.exec_():
        return windw





class space_renamer(QtWidgets.QDialog, space_renamer_ui.Ui_Dialog):

    def __init__(self, parent= None ):
        self.toolName = "space_renamer"
        super(space_renamer, self).__init__(parent=parent)
        self.setupUi(self)
        self.ctrl = None
        
        self.create_connections()
        self.setWindowTitle("Space Renamer")

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.get_space_item()
    
    
    def get_space_item(self):
        
        sel = pm.selected()
        if sel:
            if sel[0].hasAttr('space'):
                self.ctrl = sel[0]
                attr = self.ctrl.attr("space")
                enum_string = pm.attributeQuery('space', node= self.ctrl , listEnum=True)[0]
                enum_options = enum_string.split(":")
                
                self.renamerTable.setRowCount(len(enum_options))
                for i , item in enumerate(enum_options):
                    self.renamerTable.setItem( i , 0 , QtWidgets.QTableWidgetItem(item) )
                        
                
    def create_connections(self):
        self.buttonBox.accepted.connect(self.ok)
        self.buttonBox.rejected.connect(self.cancel)

    def ok(self):
        if self.ctrl:
            names_list = [(self.renamerTable.item(i , 0).text()).strip() for i in range(self.renamerTable.rowCount())]
            enum = ":".join(names_list)
            pm.addAttr(self.ctrl.attr("space") , e =True , enumName = enum)
            
    def cancel(self):
        LOG.warning("space rename Cancelled")



def exec_space_renamer(*args):

    windw = space_renamer(pyqt.maya_main_window())
    windw.show()







def add_new_space( *args ):
    
    cons_items = args[0]
    
    cons_nodes = [utils.getNode(item) for item in cons_items if cons_items]
    ctrl = cons_nodes[-1]
    drivers = cons_nodes[:-1]
    
    cons_grp = get_space_cons_grp(ctrl)
    if not cons_grp:
        LOG.warning("cannot find Space group , first add Space group then try again")
        return
    
    if not cons_grp.hasAttr("consNode"):
        LOG.warning("not find consNode attribute ")
        return
        
    
    for item in ['tx','ty','tz','rx','ry','rz']:
        cons_grp.attr(item).unlock()
        
    
    
    space_atr = get_space_attr(ctrl)
    space_Options = [opt for opt in space_atr[1] if opt != "None"]
    space_idx = len(space_Options) 
    

    
    blend , cons_mode = get_constraint_node( cons_grp )
    
    if not blend :
        init_space = exec_space_initializer()
        if not init_space:
            return
        
        
        if init_space.cons_mode == "blnd":
            if int(maya_ver) < 2020 :
                cons_mode = "constraint"
                LOG.warning("Driver Node changed to Parent Constraint. blend matrix just available for mara 2020 and higher")
            else:
                cons_mode = init_space.cons_mode
        else:
            cons_mode = init_space.cons_mode
            
        
    
    if cons_mode == "blnd":
        
        if not blend :
            use_translate = init_space.use_translate
            use_rotate = init_space.use_rotate
            
            
            blend = pm.createNode("blendMatrix")
            m = cons_grp.offsetParentMatrix.get()
            blend.inputMatrix.set(m)
            pm.connectAttr( blend.attr('message') , cons_grp.attr("consNode") , f=True )
            
            
        if not ctrl.hasAttr("spaceUseTranslate"):
            pm.addAttr(ctrl, ln="spaceUseTranslate", at="bool", defaultValue = use_translate, k=False)
        enable_translate_attr = ctrl.attr("spaceUseTranslate")
            

        if not ctrl.hasAttr("spaceUseRotate"):
            pm.addAttr(ctrl , ln = "spaceUseRotate" , at="bool" , defaultValue = use_rotate , k = False )
        enable_rotate_attr = ctrl.attr("spaceUseRotate")
        
        
        parent = cons_grp.getParent()
        curent_blnd_index = get_next_available_index(blend.attr("target"))
        Enums_dic = space_atr[0].getEnums()
        currentEnumNames    = [Enums_dic[i] for i in range( len(Enums_dic)) ] 
        newEnumNames        = currentEnumNames + [item.name().split("|")[-1] for item in drivers]
        enum = ":".join(newEnumNames )
        pm.addAttr(space_atr[0] , e =True , enumName = enum)
        
        
        
        for i , driver in enumerate(drivers):
            
            enum_idx = len(Enums_dic) + i
            blnd_idx = curent_blnd_index + i
            
            connect_matrix_driver(blend, cons_grp , driver , blnd_idx , parent )
            target_attr = blend.attr( "target[{}]".format(blnd_idx) )
            
            node_name = pm.createNode("condition")
            pm.connectAttr(space_atr[0] , node_name + ".firstTerm")
            pm.setAttr(node_name + ".secondTerm", enum_idx )
            pm.setAttr(node_name + ".operation", 0 )
            pm.setAttr(node_name + ".colorIfTrueR", 1)
            pm.setAttr(node_name + ".colorIfFalseR", 0)
            pm.connectAttr(node_name + ".outColorR", target_attr.attr("weight") )
    
            pm.connectAttr(enable_translate_attr , target_attr.attr("useTranslate"))
            pm.connectAttr(enable_rotate_attr , target_attr.attr("useRotate"))
            
        if not cons_grp.attr("offsetParentMatrix").isConnected():
            pm.connectAttr( blend.attr("outputMatrix") , cons_grp.attr("offsetParentMatrix") )

        
        
        
    elif cons_mode == "constraint":
        
        customOpt = {"maintainOffset":True}
        connection = {}
        cons_t = cons_grp.getMatrix(worldSpace = True)
        if blend:
            for item in ["t", "r"]:
                for x in ["x", "y", "z"]:
                    con = cons_grp.attr("{}{}".format(item , x)).listConnections(p=True , s=True , d=False)
                    connection["{}{}".format(item , x)] = con
                    
                    if item == "t":
                        cons_grp.attr("t{}".format(x)).disconnect()
                        pm.connectAttr(blend.attr("constraintTranslate{}".format(x.capitalize())) , cons_grp.attr("t{}".format(x)) , f=True)
                    
                    if item == "r":
                        cons_grp.attr("r{}".format(x)).disconnect()
                        pm.connectAttr(blend.attr("constraintRotate{}".format(x.capitalize())) , cons_grp.attr("r{}".format(x)) , f=True)
                    
        else:
            if not init_space.use_translate:
                customOpt["skipTranslate"] = ["x", "y", "z"]
            if not init_space.use_rotate:
                customOpt["skipRotate"] = ["x", "y", "z"]
            
        
        
        cons_list = drivers + [cons_grp]
        cns_node = pm.parentConstraint(*cons_list , **customOpt )
        cns_attr = pm.parentConstraint(cns_node, query=True, weightAliasList=True)
        add_new_indx = len(cns_attr) - space_idx
        pm.connectAttr( cns_node.attr('message') , cons_grp.attr("consNode") , f=True )
        
        
        alias_list = [att.longName().split(att.attrName().replace('w' , 'W'))[0] for att in cns_attr[add_new_indx*-1:] ]
        enum = ":".join(space_atr[1] + alias_list)
        pm.addAttr(space_atr[0] , e =True , enumName = enum)
        
        
        
        if connection:
            for item , conct in connection.items():
                cons_grp.attr(item).disconnect()
                if conct:
                    pm.connectAttr(conct[0] , cons_grp.attr(item) , f=True)
            
            cons_grp.setMatrix(cons_t , worldSpace = True)
        
        
        
        i = len(space_atr[1])
        for att in cns_attr[add_new_indx*-1:]:
            node_name = pm.createNode("condition")
            pm.connectAttr(space_atr[0] , node_name + ".firstTerm")
            pm.setAttr(node_name + ".secondTerm", i)
            pm.setAttr(node_name + ".operation", 0)
            pm.setAttr(node_name + ".colorIfTrueR", 1)
            pm.setAttr(node_name + ".colorIfFalseR", 0)
            pm.connectAttr(node_name + ".outColorR", att )
            
            i +=1
        
        pm.select(ctrl)
            






def switch_space_func(*args):
    
    auto_clav = None
    switch_control = args[0].split("|")[-1]
    switch_idx = args[1]
    
    autokey = mc.listConnections("{}.space".format(switch_control), type="animCurve")
    if autokey:
        mc.setKeyframe(switch_control , time=(mc.currentTime(query=True) - 1.0))
        
        if mc.attributeQuery( 'hasAutoClav', node=switch_control , exists=True ) :
            try:
                clav_ctrl = mc.listConnections(switch_control+'.hasAutoClav')[0]
                if clav_ctrl+".autoClav" != 0:
                    mc.setKeyframe(clav_ctrl , time=(mc.currentTime(query=True) - 1.0))
                    auto_clav = clav_ctrl
            except:
                pass
        
        
    
    changeSpace(switch_control ,  switch_idx )
    
    if autokey:
        mc.setKeyframe(switch_control ,time=(mc.currentTime(query=True)))
        if auto_clav:
            mc.setKeyframe(auto_clav ,time=(mc.currentTime(query=True)))
            




def changeSpace( ctl_name , cnsIndex ):
    
    namespace = utils.getNamespace(ctl_name)
    
    if namespace:
        ctl = utils.getNode(namespace + ":" + stripNamespace(ctl_name))
    else:
        ctl = utils.getNode(ctl_name)
    
    
    if ctl.hasAttr("hasAutoClav"):
        try:
            clav = ctl.attr("hasAutoClav").listConnections()[0]
            clavWM = clav.getMatrix(worldSpace=True)
            sWM = ctl.getMatrix(worldSpace=True)
            oAttr = ctl.attr('space')
            oAttr.set(cnsIndex)
            
            if clav.attr("autoClav").get() == 0 :
                ctl.setMatrix(sWM, worldSpace=True)
            else:
                for i in xrange(5):
                    clav.setMatrix(clavWM, worldSpace=True)
                    ctl.setMatrix(sWM, worldSpace=True)
        
        except :
            pass
    else:
        sWM = ctl.getMatrix(worldSpace=True)
        oAttr = ctl.attr('space')
        oAttr.set(cnsIndex)
        ctl.setMatrix(sWM, worldSpace=True)
        







def get_constraint_node( cons_grp ):
    cons_mode = ""
    blend = None
    consNodeList = cons_grp.attr("consNode").listConnections(p=True , s=True , d=False)
    if not consNodeList:
        if cons_grp.hasAttr("offsetParentMatrix") and cons_grp.attr("offsetParentMatrix").isConnected() :
            blnd_node = cons_grp.attr("offsetParentMatrix").listConnections(p=True , s=True , d=False)
            if blnd_node and blnd_node[0].node().type() == "blendMatrix" :
                blend = blnd_node[0].plugNode()
                pm.connectAttr( blend.attr('message') , cons_grp.attr("consNode") , f=True )
                cons_mode = "blnd"
        else:
            for item in ["tx","ty","tz","rx","ry","rz"]:
                const = cons_grp.attr(item).listConnections(p=True , s=True , d=False)
                if const and const[0].node().type() == "parentConstraint" :
                    blend = const[0].plugNode()
                    pm.connectAttr( blend.attr('message') , cons_grp.attr("consNode") , f=True )
                    cons_mode = "constraint"
                    break
    else:
        blend = cons_grp.attr("consNode").listConnections(p=True , s=True , d=False)[0].plugNode()
        if blend.type() == "parentConstraint":
            cons_mode = "constraint"
        elif blend.type() == "blendMatrix":
            cons_mode = "blnd"
            
    return blend , cons_mode






def connect_matrix_driver(blend, cons_grp, driver, blnd_idx, parent):
    mult = pm.createNode("multMatrix")
    offset = cons_grp.worldMatrix.get() * cons_grp.matrix.get().inverse() * driver.worldInverseMatrix.get()
    mult.matrixIn[0].set(offset)
    pm.connectAttr(driver.worldMatrix[0] , mult.matrixIn[1] )
    
    if parent:
        pm.connectAttr( parent.attr("worldInverseMatrix[0]") , mult.attr("matrixIn[2]") , f = True)
    
    pm.connectAttr( mult.matrixSum , blend.attr("target[{}].targetMatrix".format(blnd_idx)) )
    



def get_next_available_index(attr):
    ne = attr.getNumElements()
    if ne == attr.numConnectedElements():
        return ne
    else:
        for e in range(ne):
            if not attr.attr(attr.elements()[e]).listConnections():
                return e








def get_space_attr(ctrl):
    
    if ctrl.hasAttr('space'):
        attr = ctrl.attr("space")
        enum_string = pm.attributeQuery('space', node= ctrl , listEnum=True)[0]
        enum_options = enum_string.split(":")
    else:
        enum = "None"
        attr = pm.addAttr(ctrl , ln = 'space' , at="enum" ,en =enum , k=True)
        enum_options = ["None"]
    
    return ctrl.attr("space") , enum_options
    









def get_space_cons_grp(ctrl_name):
    
    ctrl = utils.getNode(ctrl_name)
    cons_grp = None
    i = 1
    while i < 10:
        parent = ctrl.getParent(i)
        if not parent:
            break
        # if parent.name().split("|")[-1] == ctrl.name().split("|")[-1] +'_space_cons':
        if ctrl.name().split("|")[-1] +'_space_cons' in parent.name().split("|")[-1] :
            cons_grp = parent
            break
        i += 1
    
    
    if cons_grp:
        if not cons_grp.hasAttr("consNode"):
            cons_grp.addAttr("consNode", at='message' , hidden = True)
    
    
    return cons_grp

    
    

def add_space_group( *args ):
    
    ctl_name = args[0]
    deep = 1
    if not mc.referenceQuery( ctl_name , inr=True):
        ctrl = utils.getNode(ctl_name)
        parent = ctrl.getParent(deep)
        child = ctrl.getParent(deep-1)
        name = '%s_space_cons'%ctrl.name()
        sub_trans = pm.PyNode(pm.createNode("transform", n=name))
        sub_trans.setTransformation(child.getMatrix(worldSpace=True))
        if parent:
            parent.addChild(sub_trans)
        sub_trans.addChild(child)
    else:
        file_path   = (mc.referenceQuery( ctl_name ,filename=True,unresolvedName=True).replace('//' , '/'))
        refNode     = mc.referenceQuery(ctl_name ,referenceNode=True)
        _ctl_name   = ctl_name.split(':')[-1]
        add_subprocess_trans(file_path , _ctl_name, str(deep) )
        mc.file(referenceNode=refNode,loadReference=True)
        

    
def add_subprocess_trans(file_path , ctl_name, deep):
    
    scriptPath   = os.path.normpath(os.path.join(relativePath , "core" , "addSub_transform.py"))
    mayapy   = os.path.normpath(os.path.join(os.getcwd() , "mayapy.exe")).replace('\\' , '/')
    
    maya = subprocess.Popen(mayapy +' '+scriptPath +' '+ file_path +' '+ ctl_name+' '+deep ,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out,err = maya.communicate()
    exitcode = maya.returncode
    if str(exitcode) != '0':
        LOG.error(err)
        LOG.error('error opening file: {}'.format(file_path))
    else:
        LOG.info('Successful create data for {}'.format(file_path))
        
       
       
       
       






