# _*_ coding:cp936 _*_
"""
Scripts :    python.tools.rigging.utils
Author  :    JesseChou
Date    :    2022/12/20 
QQ      :    375714316
E-Mail  :    JesseChou0612@gmail.com or 375714316@qq.com
"""
import os.path

from maya import cmds


def close_poly_smooth(namespace='', remove_nodes=False):
    if namespace:
        if not namespace.endswith(':'):
            namespace = '%s:' % namespace
    nodes = cmds.ls('%s*' % namespace, type='polySmoothFace')
    for node in nodes:
        try:
            cmds.setAttr('%s.divisions' % node, 0)
        except Exception as e:
            print (e)
        if remove_nodes:
            try:
                cmds.delete(node)
            except Exception as e:
                print(e)


def replace_attributes(base_obj, target_obj, attr_list, break_base_connection=True):
    """
    # �滻��������
    :param base_obj: ��������
    :param target_obj: Ŀ������
    :param attr_list: �����б�
    :param break_base_connection: �Ƿ�ϵ��������������
    :return: �滻��� {'success': [...],
                      'base_none': [...],
                      'target_none': [...],
                      'different': [...]}
    """
    infos = {'success': [], 'base_none': [], 'target_none': [], 'different': []}
    node_locked = cmds.lockNode(target_obj, q=True)[0]
    if node_locked:
        cmds.lockNode(target_obj, l=False)
    for attr in attr_list:
        if not cmds.objExists('%s.%s' % (base_obj, attr)):
            infos['base_none'].append(attr)
        elif not cmds.objExists('%s.%s' % (target_obj, attr)):
            infos['target_none'].append(attr)
        else:
            attr_locked = cmds.getAttr('%s.%s' % (target_obj, attr), l=True)
            attr_type = cmds.getAttr('%s.%s' % (base_obj, attr), type=True)
            attr_value = cmds.getAttr('%s.%s' % (base_obj, attr))
            if attr_locked:
                cmds.setAttr('%s.%s' % (target_obj, attr), e=True, l=False)
            # ��ȡ��������
            source_cons = cmds.listConnections('%s.%s' % (base_obj, attr), s=True, d=False, p=True)
            if source_cons:
                for source in source_cons:
                    cmds.connectAttr(source, '%s.%s' % (target_obj, attr), f=True)
                    if break_base_connection:
                        cmds.disconnectAttr(source, '%s.%s' % (base_obj, attr))
            else:
                if attr_type == 'string':
                    cmds.setAttr('%s.%s' % (target_obj, attr), attr_value, type='string')
                else:
                    cmds.setAttr('%s.%s' % (target_obj, attr), attr_value)
            # ��ȡ�������
            destination_cons = cmds.listConnections('%s.%s' % (base_obj, attr), s=False, d=True, p=True)
            if destination_cons:
                for destination in destination_cons:
                    cmds.connectAttr('%s.%s' % (target_obj, attr), destination, f=True)
            if attr_locked:
                cmds.setAttr('%s.%s' % (target_obj, attr), e=True, l=True)
            infos['success'].append(attr)
    if node_locked:
        cmds.lockNode(target_obj, l=True)
    return infos


def replace_blend_shape(base_obj, target_obj):
    """
    # �滻blendeShape
    :param base_obj:ԭʼ����
    :param target_obj: Ŀ������
    :return: �Ƿ��滻�ɹ�
    """
    judge = False
    if base_obj != target_obj:
        judge = True
    return judge


def get_blend_shape_infos(mesh_list):
    # ��ȡָ��ģ���б��blendshape��Ϣ
    import python.tools.ywmTools.ReBlendShapeTool.blendShapeV2 as bv2
    reload(bv2)
    infos = {}
    deform_infos = bv2.transferBs.getDeformInfo2(mesh_list)
    for key, value in deform_infos.items():
        bs_nodes = value.get('bsNodeList')
        if bs_nodes:
            infos[key] = bs_nodes
    return infos


def transfer_blend_shape(base_obj, target_obj):
    """
    ����bs������Ϣ
    :param base_obj:��������
    :param target_obj: Ŀ������
    :return: �Ƿ񴫵ݳɹ�
    """
    judge = False
    if cmds.objExists(base_obj) and cmds.objExists(target_obj):
        # import python.tools.ywmTools.ReBlendShapeTool.blendShapeV2 as bv2
        # reload(bv2)
        # self = bv2.transferBs()
        import mayaTools.ReBlendShapeTool.blendShapeV2 as mr
        reload(mr)
        aa = mr.transferBs()
        return aa.transferBsFn(base_obj, target_obj)


def reset_meshes_render_attrs():
    # ����cache��������ģ�͵Ŀ���Ⱦ����
    attrs = {'castsShadows': True,
             'receiveShadows': True,
             'holdOut': False,
             'motionBlur': True,
             'primaryVisibility': True,
             'smoothShading': True,
             'visibleInReflections': True,
             'visibleInRefractions': True,
             'doubleSided': True}
    cache = 'cache'
    if cmds.objExists(cache):
        meshes = cmds.listRelatives(cache, ad=True, type='mesh', ni=True)
        for mesh in meshes:
            for attr, value in attrs.items():
                cmds.setAttr('%s.%s' % (mesh, attr), value)


def transfer_connect_attrs(base, target, attrs):
    """
    ��Ⲣ��������������������
    :param base: ��������
    :param target: Ŀ������
    :param attrs: �����б�
    :return:
    """
    infos = {'success': [], 'failed': []}
    for attr in attrs:
        if cmds.objExists('%s.%s' % (base, attr)):
            default_value = cmds.getAttr('%s.%s' % (base, attr))
            attr_args = {'ln': attr,
                         'at': cmds.attributeQuery(attr, node=base, at=True)
                         }
            if cmds.attributeQuery(attr, node=base, mxe=True):
                attr_args['max'] = cmds.attributeQuery(attr, node=base, max=True)[0]
            elif cmds.attributeQuery(attr, node=base, sxe=True):
                attr_args['max'] = cmds.attributeQuery(attr, node=base, smx=True)[0]
            if cmds.attributeQuery(attr, node=base, mne=True):
                attr_args['min'] = cmds.attributeQuery(attr, node=base, min=True)[0]
            elif cmds.attributeQuery(attr, node=base, sme=True):
                attr_args['min'] = cmds.attributeQuery(attr, node=base, smn=True)[0]
            if not cmds.objExists('%s.%s' % (target, attr)):
                cmds.addAttr(target, **attr_args)
            cmds.setAttr('%s.%s' % (target, attr), e=True, l=False, k=True)
            cmds.setAttr('%s.%s' % (target, attr), default_value)
            cmds.connectAttr('%s.%s' % (target, attr), '%s.%s' % (base, attr), f=True)
            infos['success'].append(attr)
        else:
            infos['failed'].append(attr)
    return infos


def get_task_info():
    # ��ȡ��ǰ�ļ����ʲ������Ϣ
    import pymel.core as pm
    node = pm.PyNode('defaultObjectSet')
    attr = 'task_info'
    if pm.attributeQuery(attr, node=node, exists=True):
        return eval(node.attr(attr).get())


def get_standardization_file(project, asset_type, asset_name):
    file_path = ''
    folder = 'X:/Project/%s/pub/lgt_comp/standardization/%s/%s' % (project, asset_type, asset_name)
    if os.path.isdir(folder):
        file_list = [x for x in os.listdir(folder) if x.endswith('.ma')]
        if file_list:
            file_list.sort()
            file_path = '%s/%s' % (folder, file_list[-1])
    return file_path
