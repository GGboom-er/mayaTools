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
    将一个模型的顶点位置应用到另一个具有特定前缀的模型上。

    :param source_model: 源模型的名称。
    :param prefix: 目标模型前缀。
    """
    target_model = '{}{}'.format(prefix, source_model)  # 使用旧式的字符串格式化

    # 检查源模型和目标模型是否存在
    if not cmds.objExists(source_model) or not cmds.objExists(target_model):
        print("One of the models does not exist.")
        return

    # 获取源模型和目标模型的顶点数
    source_vertices = cmds.polyEvaluate(source_model, vertex=True)
    target_vertices = cmds.polyEvaluate(target_model, vertex=True)

    # 检查顶点数是否匹配
    if source_vertices != target_vertices:
        print("The number of vertices does not match between models.")
        return

    # 逐一设置顶点位置
    for i in range(source_vertices):
        # 构建源顶点和目标顶点的完整名称
        source_vertex = '{}.vtx[{}]'.format(source_model, i)
        target_vertex = '{}.vtx[{}]'.format(target_model, i)

        # 获取源顶点位置
        vertex_position = cmds.pointPosition(source_vertex, world=True)

        # 将位置应用到目标顶点
        cmds.xform(target_vertex, worldSpace=True, translation=vertex_position)

