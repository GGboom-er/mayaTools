#!/usr/bin/env python
# _*_ coding:cp936 _*_

"""
@author: GGboom
@license: MIT
@contact: https://github.com/GGboom-er
@file: match_mod_Pnt.py
@date: 2024/4/15 14:28
@desc: 
"""
import maya.cmds as cmds


def apply_vertex_positions( source_model, prefix ):
    """
    ��һ��ģ�͵Ķ���λ��Ӧ�õ���һ�������ض�ǰ׺��ģ���ϡ�

    :param source_model: Դģ�͵����ơ�
    :param prefix: Ŀ��ģ��ǰ׺��
    """
    target_model = '{}{}'.format(prefix, source_model)  # ʹ�þ�ʽ���ַ�����ʽ��

    # ���Դģ�ͺ�Ŀ��ģ���Ƿ����
    if not cmds.objExists(source_model) or not cmds.objExists(target_model):
        print("One of the models does not exist.")
        return

    # ��ȡԴģ�ͺ�Ŀ��ģ�͵Ķ�����
    source_vertices = cmds.polyEvaluate(source_model, vertex=True)
    target_vertices = cmds.polyEvaluate(target_model, vertex=True)

    # ��鶥�����Ƿ�ƥ��
    if source_vertices != target_vertices:
        print("The number of vertices does not match between models.")
        return

    # ��һ���ö���λ��
    for i in range(source_vertices):
        # ����Դ�����Ŀ�궥�����������
        source_vertex = '{}.vtx[{}]'.format(source_model, i)
        target_vertex = '{}.vtx[{}]'.format(target_model, i)

        # ��ȡԴ����λ��
        vertex_position = cmds.pointPosition(source_vertex, world=True)

        # ��λ��Ӧ�õ�Ŀ�궥��
        cmds.xform(target_vertex, worldSpace=True, translation=vertex_position)

