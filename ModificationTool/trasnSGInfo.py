#!/usr/bin/env python
# _*_ coding:cp936 _*_

"""
@author: GGboom
@license: MIT
@contact: https://github.com/GGboom-er
@file: trasnSGInfo.py
@date: 2024/5/24 15:16
@desc: 
"""
import maya.cmds as cmds
def get_shape_node( transform ):
    """
    ��ȡ����transform�ڵ�ĵ�һ��shape�ڵ㡣
    """
    shapes = cmds.listRelatives(transform, shapes=True, ni=1)
    if len(shapes) == 1:
        return shapes[0]
    else:
        cmds.warning("No shape nodes found for {}.".format(transform))
        return None


def get_components_from_sg( shading_group ):
    """
    ��ȡָ��Shading Group�ڵ������ģ�������Ϣ��

    :param shading_group: Shading Group�ڵ�����
    :return: ����������б�
    """
    components = cmds.sets(shading_group, query=True)
    return components


def copy_sg_components( source_transform, target_transform ):
    """
    ��Դģ�͵������Ϣ��ӵ�Ŀ��ģ�ͣ�����Ŀ��ģ�͵������ӵ����е�Shading Group�ڵ㡣
    :param source_transform: Դģ�͵�transform�ڵ�����
    :param target_transform: Ŀ��ģ�͵�transform�ڵ�����
    # ʾ��ʹ��
    source_transform = "xiaoyueqinwild_head1"
    target_transform = "xiaoyueqinwild_head2"
    copy_sg_components(source_transform, target_transform)
    """
    source_shape = get_shape_node(source_transform)
    target_shape = get_shape_node(target_transform)

    if not source_shape or not target_shape:
        cmds.warning("Source or target shape node not found.")
        return

    # ��ȡԴģ�͵�SG�ڵ�
    shading_groups = cmds.listConnections(source_shape, type='shadingEngine')
    if not shading_groups:
        cmds.warning("No shading groups found for {}.".format(source_shape))
        return

    for shading_group in shading_groups:
        # ��ȡ���ӵ�SG�ڵ�������Ϣ
        components = get_components_from_sg(shading_group)
        if not components:
            cmds.warning("No components found for shading group {}.".format(shading_group))
            continue
        # ��Ŀ��ģ�͵���Ӧ�����ӵ����е�SG�ڵ�
        new_components = []
        for comp in components:
            if comp.startswith(source_transform):
                comp_index = comp[len(source_transform):]
                new_components.append(target_transform + comp_index)

        if new_components:
            cmds.sets(new_components, edit=True, forceElement=shading_group)
            print("Added components to {}: {}".format(shading_group, new_components))
