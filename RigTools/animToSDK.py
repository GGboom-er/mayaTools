#!/usr/bin/env python
# _*_ coding:cp936 _*_

"""
@author: GGboom
@license: MIT
@contact: https://github.com/GGboom-er
@file: animToSDK.py
@date: 2024/3/25 14:45
@desc: 
"""
import maya.cmds as cmds

# �������߽ڵ������
animCurveNode = cmds.ls(sl=1)[0]

# ��ȡ�ؼ�֡ʱ���ֵ
keyTimes = [i - 100 for i in cmds.keyframe(animCurveNode, query=True, timeChange=True)]
keyValues = cmds.keyframe(animCurveNode, query=True, valueChange=True)

# �����ߺͱ������ߵ�����
driverAttr = 'walk_Main_Ctr.walk'
drivenAttr = 'PoleExtraArm1_R' + '.' + animCurveNode.split('_')[-1]

# ������е�SDK��������Ҫ�����Ƿ�ִ���ⲽ��
# cmds.delete(drivenAttr, inputConnections=True)

# Ϊÿ���ؼ�֡����SDK
for time, value in zip(keyTimes, keyValues):
    # ���������ߵ�ֵ
    cmds.setAttr(driverAttr, time)

    # ���������SDK
    cmds.setDrivenKeyframe(drivenAttr, currentDriver=driverAttr, driverValue=time, value=value)

cmds.delete(animCurveNode)