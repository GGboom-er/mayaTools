import maya.cmds as mc
import maya.api.OpenMaya as om
import math
import maya.cmds as cmds

def static_compare( mesh, target ):
    mesh = get_shape(mesh)
    target = get_shape(target)
    if mesh and target:
        mesh_mesh = om.MFnMesh(mesh)
        target_mesh = om.MFnMesh(target)

        mesh_points = mesh_mesh.getPoints(om.MSpace.kWorld)
        target_points = target_mesh.getPoints(om.MSpace.kWorld)

        if len(mesh_points) != len(target_points):
            return True
        different_vtx_count = sum(
            1 for i, mpoint in enumerate(mesh_points) if mpoint.distanceTo(target_points[i]) > 0.0001)
        return float(different_vtx_count) / float(len(mesh_points))
    else:
        return 0.0

def get_shape( path ):
    nodes = cmds.ls(path, long=True)
    path = nodes[0]
    if cmds.objectType(path) != 'mesh':
        shapes = cmds.listRelatives(path, shapes=True, children=True, ni=1, type="mesh", fullPath=True)
        if not shapes:
            return False
        path = shapes[0]
    sel = om.MSelectionList()
    sel.add(path)
    return sel.getDagPath(0)





















