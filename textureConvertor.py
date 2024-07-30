# _*_ coding:cp936 _*_
"""
Scripts :    python.tools.rigging.textureConvertor
Author  :    JesseChou
Date    :    2022/6/28
QQ      :    375714316
E-Mail  :    JesseChou0612@gmail.com or 375714316@qq.com
"""
import re
import math
import os
import maya.cmds as mc
from maya import cmds
import python.tools.ywmTools.meshTools.senceInfoFn as ss
import pymel.core as pm


def get_uv_main_section_fn(mesh):
    """
    # 通过所给的mesh api 节点，获取其所属uv象限
    :param apiNode: mesh api 节点，MObject类型
    :return: [u,v]
    """
    uvs = []
    us, vs = mesh.getUVs()
    u_m = int(math.floor(min(us)))
    v_m = int(math.floor(min(vs)))
    for i in range(len(us)):
        u = max(u_m, int(math.floor(us[i] - 0.001)))
        v = max(v_m, int(math.floor(vs[i] - 0.001)))
        if [u, v] not in uvs:
            uvs.append([u, v])
    return uvs


def get_cache_uv_infos(cache='cache'):
    mesh_list = pm.ls([i for i in mc.listRelatives(cache, ad=1, type='mesh') if mc.ls(i, type='mesh', ni=1)])
    infos = {}
    for mesh in mesh_list:
        infos[mesh.name()] = get_uv_main_section_fn(mesh)
    return infos


def get_uv_section_infos(mesh):
    # 获取uv每块详细信息
    us, vs = mesh.getUVs()
    infos = {}
    for i in range(len(us)):
        u = us[i]
        v = vs[i]
        s_u = max(0, int(math.floor(u - 0.001)))
        s_v = max(0, int(math.floor(v - 0.001)))
        key = '%d_%d' % (s_u, s_v)
        if key not in infos.keys():
            infos[key] = []
        infos[key].append([u, v])
    return infos


def get_section_face(mesh, u, v):
    """
    获取指定mesh的位于指定uv区域的面
    :param mesh: 模型节点
    :param u: 起始u区域
    :param v: 起始v区域
    :return:
    """
    infos = []
    uv_num = pm.polyEvaluate(mesh, uvcoord=True)
    for i in range(uv_num):
        u_, v_ = pm.polyEditUV(mesh.map[i], q=1, u=1, v=1)
        if u <= u_ <= u + 1 and v <= v_ < v + 1:
            infos.append(mesh.map[i])
    face_list = pm.polyListComponentConversion(infos, fuv=1, tf=1, internal=1)
    return face_list


def duplicateShaderNet(node, u, v):
    """
    复制材质链接树
    :param node: 起始节点名称
    :param u: 贴图所属u象限
    :param v: 贴图所属v象限
    :return: 复制出来的新节点
    """
    noExitPath = list()
    if cmds.nodeType(node) not in ['transform', 'mesh', 'colorManagementGlobals', 'place2dTexture']:
        newNode = '%s_u%d_v%d_' % (node, u, v)
        if not cmds.objExists(newNode):
            try:
                newNode = cmds.duplicate(node, n=newNode)[0]
            except Exception as e:
                print(e)
        if cmds.objExists(newNode):
            if cmds.nodeType(newNode) == 'file':
                print newNode
                value = cmds.getAttr('%s.uvTilingMode' % node)

                if value == 3:
                    num = 1001 + v * 10 + u
                    path = cmds.getAttr('%s.fileTextureName' % node)
                    newPath = path.replace('<UDIM>', str(num))
                    search = re.search(r'\d{4}\.tif', path)
                    if search:
                        newPath = path.replace(search.group(), '%04d.tif' % num)

                    cmds.setAttr('%s.uvTilingMode' % newNode, 0)
                    if os.path.exists(newPath):
                        cmds.setAttr('%s.fileTextureName' % newNode, newPath, type='string')
                    else:
                        noExitPath.append((newNode, newPath))
                else:
                    mc.delete(newNode)
                    return node, noExitPath

            cons = cmds.listConnections(node, s=True, d=False, p=True) or []
            sourceNodes = []

            for con in cons:
                temps = con.split('.')
                if temps[0] not in sourceNodes:
                    sourceNodes.append(temps[0])
            for temp in sourceNodes:
                nod = duplicateShaderNet(temp, u, v)[0]

                if nod:
                    for con in cons:
                        if con.startswith('%s.' % temp):

                            attrs = cmds.listConnections(con, s=False, d=True, p=True) or []
                            for attr in attrs:
                                if attr.startswith('%s.' % node):

                                    connectList = mc.listConnections(con.replace(temp, nod), s=1, p=1) or []
                                    if attr.replace(node, newNode) not in connectList:

                                        if attr.replace(node, newNode).split('.')[1] == 'colorGain':
                                            pass

                                        else:
                                            cmds.connectAttr(con.replace(temp, nod), attr.replace(node, newNode),
                                                             f=True)
                                            if mc.nodeType(nod) == 'RedshiftRaySwitch':
                                                preNode = mc.listConnections(nod + '.cameraColorBack', s=1)[-1]
                                                nexNode = mc.listConnections(nod + '.outColor', type='RedshiftMaterial')
                                                if preNode and nexNode:
                                                    mc.connectAttr(preNode + '.outColor',
                                                                   nexNode[-1] + '.diffuse_color', f=1)

            return newNode, noExitPath
        else:
            return node, noExitPath
    return node, noExitPath


def convert_shader(uv_infos):
    sg_infos = get_mesh_sg_infos(uv_infos.keys())
    for sg_node, mesh_list in sg_infos.items():
        for mesh in mesh_list:
            cons = cmds.listConnections('%s.instObjGroups[*]' % mesh, s=False, d=True, p=True) or []
            for con in cons:
                s_cons = cmds.listConnections(con, s=True, d=False, p=True) or []
                for s_con in s_cons:
                    cmds.disconnectAttr(s_con, con)
            uvs = uv_infos.get(mesh)
            mesh_node = pm.PyNode(mesh)
            for uv in uvs:
                new_sg = '%s__u%d_v%d__' % (sg_node, uv[0], uv[1])
                if not cmds.objExists(new_sg):
                    cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=new_sg)
                    cons = cmds.listConnections('%s.surfaceShader' % sg_node, s=True, d=False, p=True)
                    if cons:
                        node = cons[0].split('.')[0]
                        new_shader = duplicateShaderNet(node, uv[0], uv[1])[0]
                        cmds.connectAttr(cons[0].replace(node, new_shader), '%s.surfaceShader' % new_sg, f=True)
                if len(uvs) == 1:
                    cmds.sets(mesh, e=True, fe=new_sg)
                else:
                    face_list = get_section_face(mesh_node, uv[0], uv[1])
                    cmds.sets(face_list, e=True, fe=new_sg)


def get_mesh_sg_infos(meshes):
    """
    # 获取指定模型匹配的shadingGroup节点
    :param meshes: 指定的mesh节点列表
    :return: 匹配信息 {shadingGroup:[mesh1,mesh2...]}
    """
    infos = {}
    for mesh in meshes:
        cons = cmds.listConnections(mesh, s=False, d=True, type='shadingEngine')
        if cons:
            if cons[0] not in infos.keys():
                infos[cons[0]] = []
            infos[cons[0]].append(mesh)
    return infos


def create_surface_shader():
    # 创建surface材质可视化效果
    for controller in ['VisibilityCtr', 'Prop']:
        if cmds.objExists(controller):
            break
    control_attr = ''
    if cmds.objExists(controller):
        control_attr = '%s.shader_switch' % controller
        if not cmds.objExists(control_attr):
            cmds.addAttr(controller, ln='shader_switch', at='enum', en='default:surface:')
        cmds.setAttr(control_attr, e=True, l=False, cb=True)
    if control_attr:
        sg_nodes = cmds.ls(typ='shadingEngine')
        for node in sg_nodes:
            switch_bc = '%s__BC__' % node
            if not cmds.objExists(switch_bc):
                cmds.shadingNode('blendColors', asUtility=True, n=switch_bc)
            if control_attr:
                cmds.connectAttr(control_attr, '%s.blender' % switch_bc, f=True)
            s_attr = '%s.surfaceShader' % node
            s_cons = cmds.listConnections(s_attr, s=True, d=False, p=True)
            if not s_cons:
                s_attr = '%s.rsSurfaceShader' % node
                s_cons = cmds.listConnections(s_attr, s=True, d=False, p=True)
            if s_cons:
                value = None
                s_s = None
                temps = s_cons[0].split('.')
                if temps[0] != switch_bc:
                    cmds.connectAttr(s_cons[0], '%s.color2' % switch_bc, f=True)
                    cmds.connectAttr('%s.output' % switch_bc, '%s.surfaceShader' % node, f=True)
                surface_node = '%s__SS__' % node
                if not cmds.objExists(surface_node):
                    cmds.shadingNode('surfaceShader', asShader=True, n=surface_node)
                cmds.connectAttr('%s.outColor' % surface_node, '%s.color1' % switch_bc, f=True)
                if cmds.objExists('%s.color' % temps[0]):
                    s_s = cmds.listConnections('%s.color' % temps[0], s=True, d=False, p=True)
                    if not s_s:
                        value = cmds.getAttr('%s.color' % temps[0])[0]
                elif cmds.objExists('%s.diffuse_color' % temps[0]):
                    s_s = cmds.listConnections('%s.diffuse_color' % temps[0], s=True, d=False, p=True)
                    if not s_s:
                        value = cmds.getAttr('%s.diffuse_color' % temps[0])[0]
                if value:
                    cmds.setAttr('%s.outColor' % surface_node, *value, type='double3')
                if s_s:
                    cmds.connectAttr(s_s[0], '%s.outColor' % surface_node, f=True)


def convert_texture(cache):
    delSmoothNode = ss.deleteSmoothNode(ss.getMesh())
    delRsColorCorrectionNode = ss.delRsColorCorrectionNode()
    uv_infos = get_cache_uv_infos()
    convert_shader(uv_infos)


def convertor(force=0):
    judge = 1
    if force == 0:
        text = cmds.confirmDialog(m=u'执行此命令前，请先保存文件，以防数据丢失，造成不可恢复的损失！',
                                  b=[u'确认已存储', u'取消'])
        if text == u'取消':
            judge = 0
    if judge:
        convert_texture('cache')
        sur = 1
        if force == 0:
            text = cmds.confirmDialog(m=u'是否要添加材质 平图化 效果？', b=[u'确认', u'取消'])
            if text == u'取消':
                sur = 0
        if sur:
            create_surface_shader()
