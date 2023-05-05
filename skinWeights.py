# _*_ coding:cp936 _*_
"""
Scripts :    python.plug_ins.skinWeights
Author  :    JesseChou
Date    :    2021/9/3
QQ      :    375714316
E-Mail  :    JesseChou0612@gmail.com or 375714316@qq.com
"""

import sys
import maya.api.OpenMaya as OpenMaya
from python.plug_ins import skinWeightsCmd

reload(skinWeightsCmd)

ExportCmd = skinWeightsCmd.ExportSkinWeights
ImportCmd = skinWeightsCmd.ImportSkinWeights
SmoothCmd = skinWeightsCmd.SmoothSkinWeights


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


def initializePlugin(plugin):
    pluginFn = OpenMaya.MFnPlugin(plugin)
    try:
        pluginFn.registerCommand(ExportCmd.pluginCmdName, ExportCmd.cmdCreator, ExportCmd.syntaxCreator)
    except:
        sys.stderr.write("Failed to register command: %s\n" % ExportCmd.pluginCmdName)
        raise
    try:
        pluginFn.registerCommand(ImportCmd.pluginCmdName, ImportCmd.cmdCreator, ImportCmd.syntaxCreator)
    except:
        sys.stderr.write("Failed to register command: %s\n" % ImportCmd.pluginCmdName)
        raise
    try:
        pluginFn.registerCommand(SmoothCmd.pluginCmdName, SmoothCmd.cmdCreator, SmoothCmd.syntaxCreator)
    except:
        sys.stderr.write("Failed to register command: %s\n" % SmoothCmd.pluginCmdName)
        raise


def uninitializePlugin(plugin):
    pluginFn = OpenMaya.MFnPlugin(plugin)
    try:
        pluginFn.deregisterCommand(ExportCmd.pluginCmdName)
    except:
        sys.stderr.write("Failed to unregister command: %s\n" % ExportCmd.pluginCmdName)
        raise
    try:
        pluginFn.deregisterCommand(ImportCmd.pluginCmdName)
    except:
        sys.stderr.write("Failed to unregister command: %s\n" % ImportCmd.pluginCmdName)
        raise
    try:
        pluginFn.deregisterCommand(SmoothCmd.pluginCmdName)
    except:
        sys.stderr.write("Failed to unregister command: %s\n" % SmoothCmd.pluginCmdName)
        raise
