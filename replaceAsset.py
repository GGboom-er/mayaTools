# _*_ coding:cp936 _*_
"""
Scripts :    python.tools.rigging.replaceAsset
Author  :    JesseChou
Date    :    2022/12/20 
QQ      :    375714316
E-Mail  :    JesseChou0612@gmail.com or 375714316@qq.com
"""

from maya import cmds
from python.tools.rigging import skinToolkit, utils
import os
import attrToolsPK.texture_rig.textureRig as att
class ReplaceAsset(object):
    def __init__(self, **kwargs):
        self.namespace = kwargs.get('namespace', kwargs.get('ns', ''))
        self.remove_base = kwargs.get('removeBase', kwargs.get('rb', False))
        self.log = kwargs.get('log', False)
        self.mesh_list = []
        self.transform_list = []
        self.__result = {}

    @property
    def result(self):
        return self.__result

    def log_out(self, text):
        if self.log:
            print (text)

    def analyse_asset(self):
        if self.namespace:
            self.mesh_list = cmds.listRelatives(cmds.ls('%s*' % self.namespace, type='mesh'), p=True)
            self.transform_list = cmds.ls('%s*' % self.namespace, type='transform')

    def close_smooth(self):
        utils.close_poly_smooth(self.namespace, True)

    def replace_skin_weight(self):
        # �滻�ʲ���Ƥ
        self.__result['skin'] = skinToolkit.batchSkinAndCopy(self.namespace, self.mesh_list)

    def replace_blend_shape(self):
        # �滻�ʲ�bs
        base_mesh_list = []
        for mesh in self.mesh_list:
            base_transform = mesh.replace(self.namespace, '')
            if cmds.objExists(base_transform):
                base_mesh_list.append(base_transform)
        bs_infos = utils.get_blend_shape_infos(base_mesh_list)
        replace_infos = {}
        for key in bs_infos.keys():
            replace_infos[key] = utils.transfer_blend_shape(key, '%s%s' % (self.namespace, key))
        self.__result['replace_blend_shape'] = replace_infos

    def replace_visibility(self):
        # �滻�ʲ�������Ϣ����
        base_obj = 'visData'
        target_obj = '%s%s' % (self.namespace, base_obj)
        attr_list = cmds.listAttr(base_obj, ud=True)
        infos = utils.replace_attributes(base_obj, target_obj, attr_list)
        self.__result['replace_visibility'] = infos
        return infos

    def replace_lod_visibility(self):
        infos = {}
        for transform in self.transform_list:
            base_obj = transform.replace(self.namespace, '')
            if cmds.objExists(base_obj):
                infos[base_obj] = utils.replace_attributes(base_obj, transform, ['lodVisibility'])
        self.__result['replace_lod_visibility'] = infos

    def replace_sub_attributes(self):
        # �滻�ʲ��Զ�����������
        infos = {'success': {}, 'failed': {}}
        sub_trans = []
        data = 'data'
        if cmds.objExists(data):
            sub_trans = cmds.listRelatives(data, ad=True)
            if 'visData' in sub_trans:
                sub_trans.remove('visData')
        sub_trans.insert(0, data)
        for tran in sub_trans:
            target_tran = '%s%s' % (self.namespace, tran)
            if cmds.objExists(target_tran):
                attrs = cmds.listAttr(tran, ud=True)
                if attrs:
                    temp = utils.replace_attributes(tran, target_tran, attrs)
                    if not temp.get('base_none') and not temp.get('target_none') and not temp.get('different'):
                        infos['success'][tran] = temp
                    else:
                        infos['failed'][tran] = temp
        self.__result['replace_sub_attributes'] = infos
        return infos

    def remove_base_objects(self):
        if self.remove_base:
            for obj in ['cache', 'data']:
                cmds.delete(obj, ch=True)
                cmds.delete(obj)

    def optimize_file(self):
        # ���ο��������ļ����ŵ� Geometry ����
        for obj in ['cache', 'data']:
            if cmds.objExists('%s%s' % (self.namespace, obj)):
                cmds.parent('%s%s' % (self.namespace, obj), 'Geometry')
        # ɾ���ο�����������
        if cmds.objExists('%sGroup' % self.namespace):
            cmds.delete('%sGroup' % self.namespace)
        if self.remove_base:
            # �Ƴ��ο��������ʲ��Ŀռ���
            cmds.namespace(mnr=1, rm=self.namespace)

    def do_replace(self):
        if self.namespace:
            self.log_out(u'%s��ʼ�����ļ���Ϣ%s' % ('<' * 25, '>' * 25))
            self.analyse_asset()
            self.log_out(u'%s��ʼ�Ƴ�ģ�͵�smooth�ڵ�%s' % ('<' * 25, '>' * 25))
            self.close_smooth()
            # �滻�ʲ�bs��Ϣ
            self.log_out(u'%s��ʼ����Blend Shape ��Ϣ%s' % ('<' * 25, '>' * 25))
            self.replace_blend_shape()
            # �滻�ʲ���Ƥ��Ϣ
            self.log_out(u'%s��ʼ������ƤȨ��%s' % ('<' * 25, '>' * 25))
            self.replace_skin_weight()
            # �滻�ʲ�������Ϣ����
            self.log_out(u'%s��ʼ�滻�ʲ�����������Ϣ%s' % ('<' * 25, '>' * 25))
            self.replace_visibility()
            # �滻lod visibility ��������
            self.log_out(u'%s��ʼ�滻���� Lod Visibility����%s' % ('<' * 25, '>' * 25))
            self.replace_lod_visibility()
            # �滻�ʲ��Զ�����������
            self.log_out(u'%s��ʼ�滻�ʲ��Զ�����������%s' % ('<' * 25, '>' * 25))
            self.replace_sub_attributes()
            # �Ƴ�ԭʼ����
            self.log_out(u'%s��ʼ�Ƴ�ԭʼ����%s' % ('<' * 25, '>' * 25))
            self.remove_base_objects()
            # �����ļ�
            self.log_out(u'%s��ʼ�����Ż��ļ�%s' % ('<' * 25, '>' * 25))
            self.optimize_file()

def get_rigPublish_file(project ='', rigType = 'asset_lib',asset_type = '', asset_name = '',selfPath = ''):
    file_path = ''
    folder = 'X:/Project/%s/pub/%s/%s/%s/%s' % (project, rigType,asset_type, asset_name,selfPath)
    if os.path.isdir(folder):
        file_list = [x for x in os.listdir(folder) if x.endswith('.ma')]
        if file_list:
            file_list.sort()
            file_path = '%s/%s' % (folder, file_list[-1])
    return file_path
def checkFileTime(fileA,fileB):
    timeA = os.stat(fileA).st_mtime
    timeB = os.stat(fileB).st_mtime
    if timeA > timeB:
        return fileA
    else:
        return fileB

def replaceAsset(log=False):
    judge = 0
    task_infos = utils.get_task_info()
    if task_infos:
        judge = 1
        project = task_infos.get('project_db', '').replace('proj_', '')
        assetType = task_infos.get('sequence', '')
        asset = task_infos.get('shot', '')
        if project and assetType and asset:
            judge = 2
            atpFilePath = utils.get_standardization_file(project, assetType, asset)
            assetLibFilePath = get_rigPublish_file(project,'asset_lib' ,assetType, asset,r'rig\task_master')
            print atpFilePath
            print assetLibFilePath
            if atpFilePath and assetLibFilePath:
                assetLibFileTime = os.stat(assetLibFilePath).st_mtime
                atpFileTime = os.stat(atpFilePath).st_mtime
                if assetLibFileTime < atpFileTime:
                    returninfo = 'Yes'
                else:
                    judge = 3
                    returninfo = cmds.confirmDialog(title='Confirm', message=u'atp ���ڰ�����ļ����Ƿ��滻�ʲ���', button=['Yes', 'No'],
                                       defaultButton='Yes', cancelButton='No', dismissString='No')
                if returninfo == 'Yes':
                    judge = 4
                    namespace = 'replace_asset'
                    try:
                        cmds.file(atpFilePath, i=1, ns=namespace, type="mayaAscii", options='v=0;', ignoreVersion=1,
                                  mergeNamespacesOnClash=0, ra=True, pr=True)
                    except Exception as e:
                        print (e)
                    if cmds.objExists('%s:cache' % namespace):
                        rc = ReplaceAsset(ns='%s:' % namespace)
                        rc.do_replace()
                        addPrefix = ['cache','data']
                        for i in addPrefix:
                            addPrefix = [cmds.rename(j,'prefix_'+j) for j in cmds.listRelatives(i,pa =1,ad =1)]
                        att.convertTexture('replace_asset:cache')
                        judge = 5

    if log:
        if judge in [0, 1]:
            cmds.confirmDialog(t=u'��ʾ��Ϣ', m=u'δ��ȡ�����������Ϣ��������Ϣ��ȫ!!!')
        if judge == 2:
            cmds.confirmDialog(t=u'��ʾ��Ϣ', m=u'δ�ҵ���Ӧ��ATP�ύ�ļ�!!!')
        if judge == 3:
            cmds.confirmDialog(t=u'��ʾ��Ϣ', m=u'atp�ļ�����assetLib!!!')
        if judge == 4:
            cmds.confirmDialog(t=u'��ʾ��Ϣ', m=u'�ļ�����ʧ��!!!')
        if judge == 5:
            cmds.confirmDialog(t=u'��ʾ��Ϣ', m=u'���ʲ��滻�ɹ�!!!')
    return judge


if __name__ == '__main__':
    namespace = 'tbx_chr_xman_atp_atp_v030:'
    self = ReplaceAsset(ns=namespace, rb=True, log=True)
    self.do_replace()
