import mayaTools.SSDR_local_sp as slsl
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import random, math
import maya.mel as mel
import maya.cmds as cmds

qtVersion = cmds.about(qtVersion=True)

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtUiTools
import shiboken2

uifile_path = slsl.__path__[0].replace('\\','/')  + '/ui/window.ui'

def loadui(uifile_path):
    uifile = QtCore.QFile(uifile_path)
    uifile.open(QtCore.QFile.ReadOnly)
    uiWindow = QtUiTools.QUiLoader().load(uifile, parentWidget = QtWidgets.QWidget(maya_main_window()))
    uifile.close()
    return uiWindow
    
def maya_main_window():
    try:
        main_window = QtWidgets.QApplication.allWidgets()[0]
        while True:
            last_win = main_window.parent()
            if last_win:
                main_window = last_win
            else:
                break
        return main_window
    except Exception as e:
        print (e)
    
class MainWindow():
    def __init__(self):
        self.ui = loadui(uifile_path)
        self.ui.setWindowFlags(QtCore.Qt.Dialog)
        Currentpoint = QtGui.QCursor.pos()
        self.ui.move(Currentpoint.x(),Currentpoint.y())
        
        int_Validator = QtGui.QIntValidator()    
        self.ui.startFrame_LE.setValidator(int_Validator)
        self.ui.endFrame_LE.setValidator(int_Validator)
        
        
        #edit widget behaiver
        self.ui.selectedJoints_CB.stateChanged.connect(self.selectedJoints_changed)
        self.ui.convert_PB.clicked.connect(self.run_ssdr_convert)
        
        self.ui.translate_chk.stateChanged.connect(self.translate_mask)
        self.ui.rotate_chk.stateChanged.connect(self.translate_mask)
        self.ui.scale_chk.stateChanged.connect(self.translate_mask)
        self.ui.customAttr.stateChanged.connect(self.translate_mask)
        
        self.ui.blendshape_chk.stateChanged.connect(self.translate_mask)
        self.ui.bake_fbx_btn.clicked.connect(self.BakeFbxFunction)
        self.ui.run_btn.clicked.connect(self.autoTranslateAnim)
        self.ui.deleteanim.clicked.connect(self.deleteAnimation)
        self.ui.loadBlendshape_btn.clicked.connect(self.getBsname)
        
        self.ui.mirror_btn.clicked.connect(self.mirrorjointFunction)
        self.ui.rivet_getmesh_btn.clicked.connect(self.rivetGetmesh)
        self.ui.rivet_getjnt_btn.clicked.connect(self.rivetGetJnt)
        self.ui.rivet_generate_btn.clicked.connect(self.rivetFunctions)
        self.ui.attr_limit_btn.clicked.connect(self.setAttr_limit)
        
        self.ui.control_parent_get_btn.clicked.connect(self.get_parentControl)
        self.ui.del_kpc_btn.clicked.connect(self.del_kpc_func)
        
        self.ui.get_ex_jnt_btn.clicked.connect(self.get_exist_joint_list)
        self.ui.del_ex_jnt_btn.clicked.connect(self.del_exist_sel_joint)
        
        self.ui.ex_jnt_list.setSelectionMode(self.ui.ex_jnt_list.ExtendedSelection)
        
        self.ui.aj_generate_btn.clicked.connect(self.generating_func)
        self.ui.get_parent_btn.clicked.connect(self.get_reparentname)
        
        self.ui.reparent_btn.clicked.connect(self.reparent_func)
        
    def getMesh(self):
        sel = cmds.ls(sl=True)
        if sel:
            for ii in sel:
                shapes = cmds.listRelatives(ii,s=True)
                if shapes:
                    for hh in shapes:
                        if cmds.objectType(hh) == 'mesh':
                            return ii
                    
    def getjointList(self):
        sel = cmds.ls(sl=True)
        if sel:
            joints = [ii for ii in sel if cmds.objectType(ii) == 'joint']
            if joints:
                return joints
                
    def LockAttr(self,jnt,app = True):
        for ii in jnt:
            cmds.setAttr(ii + '.tx',l=app)
            cmds.setAttr(ii + '.ty',l=app)
            cmds.setAttr(ii + '.tz',l=app)
            cmds.setAttr(ii + '.rx',l=app)
            cmds.setAttr(ii + '.ry',l=app)
            cmds.setAttr(ii + '.rz',l=app)
        
    def selectedJoints_changed(self):
        state = self.ui.selectedJoints_CB.isChecked()
        if state == True:
            self.ui.numJoint_SB.setEnabled(False)
            self.ui.num_jnt_label.setEnabled(False)
        else:
            self.ui.numJoint_SB.setEnabled(True)
            self.ui.num_jnt_label.setEnabled(True)
            
    def translate_mask(self):
        state1 = self.ui.translate_chk.isChecked()
        state2 = self.ui.rotate_chk.isChecked()
        state3 = self.ui.scale_chk.isChecked()
        stateAttr = self.ui.customAttr.isChecked()
        state4 = self.ui.blendshape_chk.isChecked()
        if state1 == False and state2 == False and state3 == False and stateAttr == False:
            self.ui.blendshapeOptions_frame.setEnabled(True)
        else:
            self.ui.blendshapeOptions_frame.setEnabled(False)
            
        if state4 == True:
            self.ui.transformOptions_frame.setEnabled(False)
        else :
            self.ui.transformOptions_frame.setEnabled(True)
            
    def run_ssdr_convert(self):
        start = self.ui.startFrame_LE.text()
        end = self.ui.endFrame_LE.text()
        maxinf = self.ui.maxInf_SB.value()
        boneNum = self.ui.numJoint_SB.value()
        mesh = self.getMesh()
        if self.ui.iter_box.isChecked():
            pass
        if self.ui.selectedJoints_CB.isChecked():
            jnt = self.getjointList()
            if jnt != None and mesh != None:
                self.LockAttr(jnt)
                cmds.demBones(mesh,eb=jnt,sf=int(start),ef=int(end),mi=maxinf)
                self.LockAttr(jnt,app=False)
            else:
                om.MGlobal.displayError('Please select animBone and animMesh')
        else:
            if mesh != None:
                cmds.demBones(mesh,b=boneNum,sf=int(start),ef=int(end),mi=maxinf)
            
    def showUI(self):
        self.ui.show()
        SSDCheckLoad()
        
    def closeUI(self):
        self.ui.close()
        self.ui.deleteLater()
        
    def get_parentControl(self):
        sel = cmds.ls(sl=True)
        if sel:
            self.ui.control_parent_name_input.setText(sel[0])
            
    def del_kpc_func(self):
        sel = cmds.ls('*kamiParentConstrain*')
        if sel:
            num = str(len(sel))
            cmds.delete(sel)
            self.ui.del_kpc_btn.setText(num+' Node Clean')
        
    def get_errorPercentBreak(self):
        state = self.ui.stopAt_CB.isChecked()
        if state == True:
            return self.ui.errorPercentBreak_DSB.value()
        else:
            return -1.0
            
    def are_animated(self, meshes):
        for item in meshes:
            if not is_animated_mesh(item):
                return False
        return True
        
    def set_matching(self, err, iterDone):
        matching = get_matching_percent(err)
        self.ui.error_LE.setText('%.3f' % matching)
        self.ui.iterDone_LE.setText(str(iterDone))
        
    def autoTranslateAnim(self):
        sels = cmds.ls(sl=True)
        if len(sels) != 0 :
            if len(self.ui.blendshape_edit.text()) != 0 and self.ui.blendshape_chk.isChecked() == True:
                bsname = self.ui.blendshape_edit.text()
                if cmds.objExists(bsname) and cmds.objectType(bsname) == 'blendShape':
                    bslist = cmds.listAttr(bsname+'.w',m=True)
                    cmds.setKeyframe(bsname)
                    alreadyset = []
                    for ii in bslist:
                        targetName = bsname+'.'+ii
                        origValue = cmds.getAttr(targetName)
                        if cmds.listAttr(targetName,k=True) != None and cmds.listAttr(targetName,u=True) != None:
                            moveTime(1)
                            if alreadyset:
                                for qq in alreadyset:
                                    cmds.setAttr(bsname+'.'+qq,0)
                            cmds.setAttr(targetName,1)
                            alreadyset.append(ii)
                            cmds.setKeyframe(bsname)
    
                        #tranningAnimation(bsname,bsname+'.'+ii,False,1)
                
            elif self.ui.translate_chk.isChecked() == True or self.ui.rotate_chk.isChecked() == True or self.ui.scale_chk.isChecked() == True:
                cmds.setKeyframe(sels)
                for ii in sels :
                    #translate animation
                    if self.ui.translate_chk.isChecked() == True:
                        tranningAnimation(sels,ii+'.translateX',float(self.ui.translateMin_edit.text()),float(self.ui.translateMax_edit.text()))
                        tranningAnimation(sels,ii+'.translateY',float(self.ui.translateMin_edit.text()),float(self.ui.translateMax_edit.text()))
                        tranningAnimation(sels,ii+'.translateZ',float(self.ui.translateMin_edit.text()),float(self.ui.translateMax_edit.text()))
                    if self.ui.rotate_chk.isChecked() == True:
                        tranningAnimation(sels,ii+'.rotateX',float(self.ui.rotateMin_edit.text()),float(self.ui.rotateMax_edit.text()))
                        tranningAnimation(sels,ii+'.rotateY',float(self.ui.rotateMin_edit.text()),float(self.ui.rotateMax_edit.text()))
                        tranningAnimation(sels,ii+'.rotateZ',float(self.ui.rotateMin_edit.text()),float(self.ui.rotateMax_edit.text()))
                    if self.ui.scale_chk.isChecked() == True:
                        tranningAnimation(sels,ii+'.scaleX',float(self.ui.scaleMin_edit.text()),float(self.ui.scaleMax_edit.text()))
                        tranningAnimation(sels,ii+'.scaleY',float(self.ui.scaleMin_edit.text()),float(self.ui.scaleMax_edit.text()))
                        tranningAnimation(sels,ii+'.scaleZ',float(self.ui.scaleMin_edit.text()),float(self.ui.scaleMax_edit.text()))
        else:
            cmds.warning('not select!')
            
    def deleteAnimation(self):
        sels = cmds.ls(sl=True)
        if len(sels) != 0:
            for hh in sels:
                inputs = cmds.listConnections(hh,s=True)
                if inputs:
                    for ii in inputs:
                        if cmds.objectType(ii) == 'animCurveTL' or cmds.objectType(ii) == 'animCurveTU' or cmds.objectType(ii) == 'animCurveTA':
                            cmds.delete(ii)
                            
    def deleteAnimation_inner(self,sels):
        if len(sels) != 0:
            for hh in sels:
                inputs = cmds.listConnections(hh,s=True)
                if inputs:
                    for ii in inputs:
                        if cmds.objectType(ii) == 'animCurveTL' or cmds.objectType(ii) == 'animCurveTU' or cmds.objectType(ii) == 'animCurveTA':
                            cmds.delete(ii)
                            
    def getBsname(self):
        sels = cmds.ls(sl=True)
        if cmds.objectType(sels[0]) == 'blendShape' and self.ui.blendshape_chk.isChecked() == True:
            self.ui.blendshape_edit.setText(sels[0])
            
    def mirrorjointFunction(self):
        sel = cmds.ls(sl=True)
        if sel:
            joint = []
            for ii in sel:
                if cmds.objectType(ii) == 'joint':
                    joint.append(ii)
            if joint:
                keyword1 = self.ui.keywords_L.text()
                keyword2 = self.ui.keywords_R.text()
                for ii in joint:
                    if self.ui.mirror_order_1.isChecked():
                        cmds.mirrorJoint(ii,mxy=True,mb=True,sr=(str(keyword1),str(keyword2)))
                    elif self.ui.mirror_order_2.isChecked():
                        cmds.mirrorJoint(ii,myz=True,mb=True,sr=(str(keyword1),str(keyword2)))
                    elif self.ui.mirror_order_3.isChecked():
                        cmds.mirrorJoint(ii,mxz=True,mb=True,sr=(str(keyword1),str(keyword2)))
        else:
            cmds.warning('not selected')
            
    def rivetGetmesh(self):
        sel = cmds.ls(sl=True)
        if sel:
            shape = cmds.pickWalk(sel[0],d='down')[0]
            if cmds.objectType(shape) == 'mesh':
                self.ui.rivetmesh_tex_line.setText(sel[0])
            cmds.select(cl=True)
                
    def rivetGetJnt(self):
        sel = cmds.ls(sl=True)
        if sel:
            joint = []
            for ii in sel:
                if cmds.objectType(ii) == 'joint':
                    joint.append(ii)
            self.ui.rivetjoint_tex_line.setText(','.join(joint))
            cmds.select(cl=True)
            
    def rivetFunctions(self):
        mesh = self.ui.rivetmesh_tex_line.text()
        jnts = self.ui.rivetjoint_tex_line.text()
        if mesh and jnts:
            jntsList = jnts.split(',')
            getNewCPOM = cmds.createNode("closestPointOnMesh")
            getTheMeshShape = cmds.listRelatives(mesh,s=True)
            cmds.connectAttr (getTheMeshShape[0]+".outMesh",getNewCPOM+".inMesh",f=1)
            
            #create parent attr
            if self.ui.controler_check.isChecked():
                if cmds.objExists(str(self.ui.control_parent_name_input.text())):
                    parent_con = str(self.ui.control_parent_name_input.text())
                    if cmds.objExists(parent_con +'.sdp') == False:
                        cmds.addAttr(parent_con,shortName='sdp', longName='SecondDisplay', at='bool',dv=True)
                        cmds.setAttr(parent_con + '.sdp',k=True)
            
            for ii in range(len(jntsList)):
                getNewFolShape = cmds.createNode("follicle")
                cmds.setAttr(getNewFolShape+".simulationMethod",0)
                cmds.setAttr(getNewFolShape+".degree",1)
                cmds.setAttr(getNewFolShape+".sampleDensity",0)
                cmds.setAttr(getNewFolShape+".template",1)
                getTheFolold = cmds.listRelatives(getNewFolShape,p=True)
                
                getrename = cmds.rename(getTheFolold[0],'fol_rivet')
                getNewFolShape_new=cmds.listRelatives(getrename,s=True)
                
                cmds.connectAttr(getTheMeshShape[0]+".outMesh",getNewFolShape_new[0]+".inputMesh",f=1)
                cmds.connectAttr(getTheMeshShape[0]+".worldMatrix[0]",getNewFolShape_new[0]+".inputWorldMatrix",f=1)
                cmds.connectAttr(getNewFolShape_new[0]+".outTranslate",getrename+".translate",f=1)
                cmds.connectAttr(getNewFolShape_new[0]+".outRotate",getrename+".rotate",f=1)
                
                getPos_loc = cmds.xform(jntsList[ii],q=True,t=True,ws=True)
                cmds.setAttr(getNewCPOM+".inPosition",getPos_loc[0] ,getPos_loc[1] ,getPos_loc[2])
                getU = cmds.getAttr(getNewCPOM+".parameterU")
                getV = cmds.getAttr(getNewCPOM+".parameterV")
                cmds.setAttr(getNewFolShape_new[0]+".parameterU",getU)
                cmds.setAttr(getNewFolShape_new[0]+".parameterV",getV)
                cmds.select(cl=True)    
                
                #controler logic
                if self.ui.controler_check.isChecked():
                    if cmds.objExists(str(self.ui.control_parent_name_input.text())):
                        attach_grp = cmds.group(em=True,n=jntsList[ii]+'_Attach_Grp')
                        offset_grp = cmds.group(em=True,n=jntsList[ii]+'_offset_Grp')
                        control = cmds.circle(n=jntsList[ii]+'_Con',ch=False)[0]
                        cmds.parent(control,offset_grp)
                        cmds.parent(offset_grp,attach_grp)
                        cmds.matchTransform(attach_grp,jntsList[ii],pos=True)
                        parentConstrain_kami(getrename,attach_grp,maintain=1)
                        #cmds.parentConstraint(getrename,attach_grp,mo=True)
                        if '_R' in jntsList[ii]:
                            if self.ui.reverse_check.isChecked():
                                cmds.setAttr(offset_grp+'.scaleX',-1)
                            else:
                                pass
                        if self.ui.second_check.isChecked():
                            jntsListOffset = cmds.group(em=True,w=True,n=jntsList[ii]+'_offset_grp')
                            cmds.matchTransform(jntsListOffset,jntsList[ii])
                            cmds.parent(jntsList[ii],jntsListOffset)
                            # newii = cmdx.encode(jntsList[ii])
                            # newii['rotate'] = (0,0,0)
                            # newii['jointOrient'] = (0,0,0)
                            # controlNew = cmdx.encode(control)
                            # controlNew['translate'] >> newii['translate']
                            # controlNew['rotate'] >> newii['rotate']
                            # controlNew['scale'] >> newii['scale']
                            cmds.setAttr(jntsList[ii]+'.rotateX',0)
                            cmds.setAttr(jntsList[ii]+'.rotateY',0)
                            cmds.setAttr(jntsList[ii]+'.rotateZ',0)
                            cmds.setAttr(jntsList[ii]+'.jointOrientX',0)
                            cmds.setAttr(jntsList[ii]+'.jointOrientY',0)
                            cmds.setAttr(jntsList[ii]+'.jointOrientZ',0)
                            
                            cmds.connectAttr(control+'.translate',jntsList[ii]+'.translate')
                            cmds.connectAttr(control+'.rotate',jntsList[ii]+'.rotate')
                            cmds.connectAttr(control+'.scale',jntsList[ii]+'.scale')
                            
                        else:
                            parentConstrain_kami(control,jntsList[ii],maintain=1)
                            #cmds.parentConstraint(control,jntsList[ii],mo=False)
                        cmds.connectAttr(parent_con+'.sdp',control+'.visibility')
                        
                    else:
                        cmds.warning('please get parentControlName!')
                else:
                    cmds.parentConstraint(getrename,jntsList[ii],mo=False)
            cmds.delete(getNewCPOM)
            
    def setAttr_limit(self):
        sels = cmds.ls(sl=True)
        if sels:
            for ii in sels :
                if self.ui.translate_chk.isChecked() == True:
                    tmin = float(self.ui.translateMin_edit.text())
                    tmax = float(self.ui.translateMax_edit.text())
                    cmds.transformLimits(ii,tx=(tmin,tmax),ty=(tmin,tmax),tz=(tmin,tmax),etx=(1,1),ety=(1,1),etz=(1,1))
                if self.ui.rotate_chk.isChecked() == True:
                    rmin = float(self.ui.rotateMin_edit.text())
                    rmax = float(self.ui.rotateMax_edit.text())
                    cmds.transformLimits(ii,rx=(rmin,rmax),ry=(rmin,rmax),rz=(rmin,rmax),erx=(1,1),ery=(1,1),erz=(1,1))
                if self.ui.scale_chk.isChecked() == True:
                    smin = float(self.ui.scaleMin_edit.text())
                    smax = float(self.ui.scaleMax_edit.text())
                    cmds.transformLimits(ii,sx=(smin,smax),sy=(smin,smax),sz=(smin,smax),esx=(1,1),esy=(1,1),esz=(1,1))
                    
    def exportSelectItemToFbx(self,filePath,filename,mintime,maxtime):
        sel = cmds.ls(sl=True)
        if sel:
            name = filename + '.fbx'
            mel.eval('FBXExportInputConnections -v false;')
            mel.eval('FBXExportGenerateLog -v false;')
            mel.eval('FBXExportBakeComplexAnimation -v true;')
            mel.eval('FBXExportBakeComplexEnd -v {};'.format(maxtime))
            mel.eval('FBXExportBakeComplexStart -v {};'.format(mintime))
            mel.eval('FBXExport -f "{0}/{1}" -s;'.format(filePath,name))
            
        else:
            cmds.warning('!!!!!')
            
    def BakeFbxFunction(self):
        if len(self.ui.blendshape_edit.text()) != 0 and self.ui.blendshape_chk.isChecked() == True:
            fileName = cmds.fileDialog2(fileFilter='selectdir',dialogStyle=2,fm=2,okc='selectDir')
            if fileName:
                fileName = fileName[0].encode('gbk')
                bsname = self.ui.blendshape_edit.text()
                sel = cmds.ls(sl=True)
                if sel:
                    if cmds.objExists(bsname) and cmds.objectType(bsname) == 'blendShape':
                        bslist = cmds.listAttr(bsname + '.w',m=True)
                        for ii in bslist:
                            cmds.currentTime(0)
                            cmds.setAttr(bsname+'.'+ii,0)
                            cmds.setKeyframe(bsname+'.'+ii)
                            cmds.currentTime(1)
                            cmds.setAttr(bsname+'.'+ii,1)
                            cmds.setKeyframe(bsname+'.'+ii)
                            self.exportSelectItemToFbx(fileName,ii,0,1)
                            cmds.currentTime(0)
                            cmds.setAttr(bsname+'.'+ii,0)
                            cmds.cutKey(bsname+'.'+ii)
                    else:
                        cmds.warning('BsNode illegal!')
                else:
                    cmds.warning('Non selected!')
        else:
            cmds.warning('blendshape Node Non existent')
            
    def get_exist_joint_list(self):
        sel = cmds.ls(sl=True)
        if sel:
            joint = []
            for ii in sel:
                if cmds.objectType(ii) == 'joint':
                    joint.append(ii)
            if joint:
                self.ui.ex_jnt_list.clear()
                for ii in joint:
                    self.ui.ex_jnt_list.addItem(ii)
                    
    def del_exist_sel_joint(self):
        items = self.ui.ex_jnt_list.selectedItems()
        if items:
            for ii in items:
                row = self.ui.ex_jnt_list.row(ii)
                self.ui.ex_jnt_list.takeItem(row)
                
    def generating_func(self):
        itemsNum = self.ui.ex_jnt_list.count()
        sftime = int(self.ui.aj_sr_input.text())
        eftime = int(self.ui.aj_er_input.text())
        numjnt = self.ui.aj_num_box.value()
        sel = cmds.ls(sl=True)
        if len(sel) == 1:
            shape = cmds.listRelatives(sel[0],s=True)[0]
            if cmds.objectType(shape) == 'mesh':
                if itemsNum != 0 :
                    exjnt = [self.ui.ex_jnt_list.item(hh).text() for hh in range(itemsNum)]
                    cmds.demBones(b=numjnt,sf=sftime,ef=eftime,eb=exjnt)
                else:
                    cmds.demBones(b=numjnt,sf=sftime,ef=eftime)
        else:
            cmds.warning('please select one mesh!')
            
    def get_reparentname(self):
        sel = cmds.ls(sl=True)
        if sel:
            if cmds.objectType(sel[0]) == 'joint':
                self.ui.parent_name_in.setText(sel[0])
                
    def reparent_func(self):
        Pname = self.ui.parent_name_in.text()
        sftime = int(self.ui.aj_sr_input.text())
        eftime = int(self.ui.aj_er_input.text())
        if Pname:
            sels = cmds.ls(sl=True)
            if sels:
                jnts = [ii for ii in sels if cmds.objectType(ii) == 'joint']
                if jnts:
                    locs = []
                    constrain = []
                    for ii in jnts:
                        loc = cmds.spaceLocator(n=ii+'_bake_loc')[0]
                        cons = cmds.parentConstraint(ii,loc,mo=False)[0]
                        constrain.append(cons)
                        locs.append(loc)
                    cmds.bakeResults(locs,t=(sftime,eftime))
                    cmds.delete(constrain)
                    
                    constrain = []
                    self.deleteAnimation_inner(jnts)
                    for ii in jnts:
                        cmds.parent(ii,Pname)
                        cons = cmds.parentConstraint(ii+'_bake_loc',ii,mo=False)[0]
                        constrain.append(cons)
                    cmds.bakeResults(jnts,t=(sftime,eftime))
                    cmds.delete(constrain,locs)
                    
                        
#
#
# Utilities
#
#


def moveTime(num):
    time = cmds.currentTime(q=True) + num
    cmds.currentTime(time,e=True)
    
def tranningAnimation(sels,name,min,max):
    if cmds.objExists(name):
        orig = cmds.getAttr(name)
        if cmds.listAttr(name,k=True) != None and cmds.listAttr(name,u=True) != None:
            moveTime(1)
            cmds.setAttr(name,max)
            cmds.setKeyframe(sels)
            
            if min != False:
                moveTime(1)
                cmds.setAttr(name,min)
                cmds.setKeyframe(sels)
            
            moveTime(1)
            cmds.setAttr(name,orig)
            cmds.setKeyframe(sels)
    else:
        cmds.warning('the Attr not exists!!!!')
        
def getDagPath(node=None):
    sel = om.MSelectionList()
    sel.add(node)
    d = om.MDagPath()
    sel.getDagPath(0, d)
    return d

def getLocalOffset(parent, child):
    parentWorldMatrix = getDagPath(parent).inclusiveMatrix()
    childWorldMatrix = getDagPath(child).inclusiveMatrix()
    return childWorldMatrix * parentWorldMatrix.inverse()
        
def parentConstrain_kami(aa,bb,maintain=0,scale=0):
    
    ccmatrix = cmds.createNode('multMatrix',n=bb+'_kamiParentConstrain_multM')
    ddmatrix = cmds.createNode('decomposeMatrix',n=bb+'_kamiParentConstrain_deCom')
    
    if maintain == 0 :
        cmds.connectAttr(aa+'.worldMatrix[0]',ccmatrix+'.matrixIn[0]')
        cmds.connectAttr(bb+'.parentInverseMatrix[0]',ccmatrix+'.matrixIn[1]')
        cmds.connectAttr(ccmatrix+'.matrixSum',ddmatrix+'.inputMatrix')
        
    elif maintain == 1:
        #aa bb local offset
        localOffset = getLocalOffset(aa,bb)
        cmds.setAttr(ccmatrix+".matrixIn[0]", [localOffset(i, j) for i in range(4) for j in range(4)], type="matrix")
        
        #mul aa offset
        cmds.connectAttr(aa+'.worldMatrix[0]',ccmatrix+'.matrixIn[1]')
        
        #preserve parent effect
        cmds.connectAttr(bb+'.parentInverseMatrix[0]',ccmatrix+'.matrixIn[2]')
        
        cmds.connectAttr(ccmatrix+'.matrixSum',ddmatrix+'.inputMatrix')
        
    cmds.connectAttr(ddmatrix+'.outputTranslate',bb+'.translate')
    cmds.connectAttr(ddmatrix+'.outputRotate',bb+'.rotate')
    cmds.connectAttr(ddmatrix+'.outputScale',bb+'.scale')
    
    if scale == 1:
        cmds.connectAttr(ddmatrix+'.outputScale',bb+'.scale')
        
    if cmds.objectType(bb) == 'joint':
        multyNode = cmds.createNode('multiplyDivide',n=bb+'_kamiParentConstrain_zero_MD')
        cmds.connectAttr(multyNode+'.output',bb+'.jointOrient')        


def SSDCheckLoad():
    if cmds.pluginInfo('dembone', q=True, l=True):
        pass
    else:
        version = int(cmds.about(v=True)[:4])
        if version > 2017:
            local_file = slsl.__path__[0].replace('\\','/') + '/plug-ins/' + str(version) + '/dembone.mll'
            cmds.loadPlugin(local_file)
        else:
            cmds.error('The plug-in only supports versions larger than 2017')
        