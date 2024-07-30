import maya.cmds as cmds


def get_shape_node( transform ):
    """
    获取给定transform节点的第一个shape节点。
    """
    shapes = cmds.listRelatives(transform, shapes=True)
    if shapes:
        return shapes[0]
    else:
        cmds.warning("No shape nodes found for {}.".format(transform))
        return None


def copy_texture_connections( source_transform, target_transform ):
    """
    将源模型的材质连接复制到目标模型。
    """
    source_shape = get_shape_node(source_transform)
    target_shape = get_shape_node(target_transform)

    if not source_shape or not target_shape:
        cmds.warning("Source or target shape node not found.")
        return

    # 获取源模型的材质
    shading_groups = cmds.listConnections(source_shape, type='shadingEngine')
    if not shading_groups:
        cmds.warning("No shading groups found for {}.".format(source_shape))
        return

    shading_group = shading_groups[0]

    # 获取材质
    materials = cmds.ls(cmds.listConnections(shading_group + ".surfaceShader"), materials=True)
    if not materials:
        cmds.warning("No materials found for shading group {}.".format(shading_group))
        return

    material = materials[0]

    # 获取连接到材质的贴图文件节点
    texture_files = cmds.listConnections(material, type='file')
    if not texture_files:
        cmds.warning("No texture files found connected to material {}.".format(material))
        return

    texture_file = texture_files[0]

    # 获取目标模型的材质
    target_shading_groups = cmds.listConnections(target_shape, type='shadingEngine')
    if not target_shading_groups:
        # 如果目标模型没有材质，创建一个新的材质并分配给目标模型
        target_material = cmds.shadingNode('lambert', asShader=True, name=target_transform + '_mat')
        target_shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=target_material + 'SG')
        cmds.connectAttr(target_material + '.outColor', target_shading_group + '.surfaceShader')
        cmds.sets(target_transform, edit=True, forceElement=target_shading_group)
    else:
        target_shading_group = target_shading_groups[0]
        target_materials = cmds.ls(cmds.listConnections(target_shading_group + ".surfaceShader"), materials=True)
        if not target_materials:
            cmds.warning("No materials found for shading group {}.".format(target_shading_group))
            return
        target_material = target_materials[0]

    # 连接贴图文件节点到目标材质
    cmds.connectAttr(texture_file + ".outColor", target_material + ".color", force=True)
    print("Connected {}.outColor to {}.color".format(texture_file, target_material))


# 示例使用
source_transform = "pSphere2"
target_transform = "pSphere1"
copy_texture_connections(source_transform, target_transform)



selected_objects = cmds.ls(selection=True)

# 获取当前选择的对象的第一个
selected_object = selected_objects[0]

selected_attributes = cmds.channelBox('mainChannelBox', query=True, selectedHistoryAttributes=True)
