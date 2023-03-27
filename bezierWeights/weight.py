# coding:utf-8

import os
import json
import re
from functools import partial

import pymel.core as pm

ROOT = os.path.abspath(os.path.join(__file__+"../.."))


def bezier_v(p, t):
    return p[0]*(1-t)**3 + 3*p[1]*t*(1-t)**2 + 3*p[2]*t**2*(1-t) + p[3]*t**3


def bezier_t(p, v):
    min_t = 0.0
    max_t = 1.0
    while True:
        t = (min_t+max_t)/2
        error_range = bezier_v(p, t) - v
        if error_range > 0.0001:
            max_t = t
        elif error_range < -0.0001:
            min_t = t
        else:
            return t


def get_widget(x, xs=(0, 0.2, 0.8, 1), ys=(0, 0, 1, 1)):
    if x <= 0:
        return ys[0]
    elif x >= 1:
        return ys[3]
    t = bezier_t(xs, x)
    return bezier_v(ys, t)


def assert_geometry(geometry=None, shape_type="mesh"):
    u"""
    :param geometry: 几何体
    :param shape_type: 形节点类型
    :return:
    判断物体是否为集合体
    """
    if geometry is None:
        selected = pm.selected(o=1)
        if len(selected) == 0:
            return pm.warning("please select a " + shape_type)
        geometry = selected[0]
    if geometry.type() == shape_type:
        return geometry.getParent()
    if geometry.type() != "transform":
        return pm.warning("please select a " + shape_type)
    shape = geometry.getShape()
    if not shape:
        return pm.warning("please select a " + shape_type)
    if shape.type() != shape_type:
        return pm.warning("please select a " + shape_type)
    return geometry


def get_skin_cluster(polygon=None):
    if polygon is None:
        polygon = assert_geometry(shape_type="mesh")
    if polygon is None:
        return
    for history in polygon.history(type="skinCluster"):
        return history
    pm.warning("\ncan not find skinCluster")


def upload_weight(n=None):
    skin_cluster = get_skin_cluster()
    if n is None:
        n = skin_cluster.getGeometry()[0].getParent().name()
    wts = [list(skin_cluster.getWeights(skin_cluster.getGeometry()[0], i))
           for i in range(len(skin_cluster.influenceObjects()))]
    wts = sum([list(i) for i in zip(*wts)], [])
    path = os.path.join(ROOT, "weights", n+".json")
    with open(path, "w") as fp:
        json.dump(wts, fp, indent=4)


def load_weight(skin_cluster=None, n=None):
    if skin_cluster is None:
        skin_cluster = get_skin_cluster()
    if skin_cluster is None:
        return
    if n is None:
        n = skin_cluster.getGeometry()[0].getParent().name()
    path = os.path.join(ROOT, "weights", n+".json")
    with open(path, "r") as fp:
        wts = json.load(fp)
    skin_cluster.setWeights(skin_cluster.getGeometry()[0], range(len(skin_cluster.influenceObjects())),  wts)


def split_key(d, joint):
    return joint.getTranslation(space="world")[d]


def split_radius(joint1, joint2):
    return max((joint1.getTranslation(space="world") - joint2.getTranslation(space="world")).length(), 0.0001)


def spine_radius(*args):
    return pm.softSelect(q=1, ssd=1) * 2


def up_inverse(joint1, joint2):
    temp = pm.group(em=1, n="temp")
    pm.delete(pm.pointConstraint(joint1, joint2, temp))
    up = pm.group(em=1, n="up")
    up.t.set(temp.t.get())
    up.ty.set(temp.ty.get()+1)
    pm.delete(pm.aimConstraint(up, temp, aimVector=[0, 1, 0], u=[1, 0, 0], wut="object", wuo=joint2))
    inverse = temp.getMatrix(ws=1).inverse()
    pm.delete(temp, up)
    return inverse


def split_inverse(joint1, joint2):
    temp = pm.group(em=1)
    pm.delete(pm.pointConstraint(joint1, joint2, temp))
    pm.delete(pm.aimConstraint(joint2, temp, wut="none", wuo=joint2))
    inverse = temp.getMatrix(ws=1).inverse()
    pm.delete(temp)
    return inverse


def spine_inverse(joint1, joint2):
    temp = pm.group(em=1)
    pm.delete(pm.pointConstraint(joint2, temp))
    pm.delete(pm.orientConstraint(joint1, joint2, temp))
    local_tx = (pm.datatypes.Point(joint1.getTranslation(space="world")) * joint2.getMatrix(ws=1).inverse())[0]
    if local_tx > 0:
        temp.sx.set(-1)
    inverse = temp.getMatrix(ws=1).inverse()
    pm.delete(temp)
    return inverse


def base_kwargs(inverse, radius, d, *args):
    polygon = assert_geometry(shape_type="mesh")
    if polygon is None:
        return
    mesh = polygon.getShape()
    sk = get_skin_cluster(polygon)
    influences = sk.getInfluence()
    joints = [joint for joint in influences if not joint.liw.get()]
    if d != 3:
        joints.sort(key=partial(split_key, d))
    joint_ids = [influences.index(joint) for joint in joints]
    old_weight_matrix = [list(sk.getWeights(mesh, i)) for i in joint_ids]
    max_weights = [sum(ws) for ws in zip(*old_weight_matrix)]
    points = mesh.getPoints(space="world")
    wx_matrix = []
    for i, joint in enumerate(joints[1:]):
        matrix = inverse(joints[i], joint)
        wx_matrix.append([(p * matrix)[0]/radius(joints[i], joint) for p in points])
    pm.select(polygon)
    return locals()


def split_solve(r, xs, ys, wx_matrix, max_weights, joint_ids, mesh, sk, joints, **kwargs):
    weight_matrix = [[1 for _ in wx_matrix[0]]]
    for wxs in wx_matrix:
        weights =[get_widget(wx/r+0.5, xs, ys) for wx in wxs]
        weights = [min(w1, w2) for w1, w2 in zip(weight_matrix[-1], weights)]
        weight_matrix.append(weights)
        weight_matrix[-2] = [w2 - w1 for w1, w2 in zip(weight_matrix[-1], weight_matrix[-2])]
    weight_matrix = [[w*m for w, m in zip(ws, max_weights)]for ws in weight_matrix]
    weights = sum([list(ws) for ws in zip(*weight_matrix)], [])
    sk.setWeights(mesh, joint_ids, weights)
    paint_joints = [joint for joint in sk.paintTrans.inputs() if joint.type() == "joint"]
    if len(paint_joints) == 1:
        sk.paintWeights.set(weight_matrix[joints.index(paint_joints[0])])


up_kwargs = partial(base_kwargs, up_inverse, split_radius)
split_kwargs = partial(base_kwargs, split_inverse, split_radius)
spine_kwargs = partial(base_kwargs, spine_inverse, spine_radius)


def soft_kwargs(*args):
    polygon = assert_geometry(shape_type="mesh")
    mesh = polygon.getShape()
    pm.softSelect(sse=1)
    pm.softSelect(ssc="0,1,1,1,0,1")
    radius = pm.softSelect(q=1, ssd=1)
    pm.softSelect(ssd=radius * 2)
    old_points = mesh.getPoints(space="world")
    pm.move([0, 1, 0], r=1)
    new_points = mesh.getPoints(space="world")
    pm.move([0, -1, 0], r=1)
    pm.softSelect(ssd=radius)
    wxs = [(new[1] - old[1]) for old, new in zip(old_points, new_points)]
    return locals()


def soft_solve(xs, ys, r, sk, wxs, **kwargs):
    ys = [1 - y for y in ys]
    wxs = [(1-wx)*2/r for wx in wxs]
    weights = [get_widget(x, xs, ys) for x in wxs]
    sk.paintWeights.set(weights)


def ik_kwargs(*args):
    polygon = assert_geometry(shape_type="mesh")
    mesh = polygon.getShape()
    sk = get_skin_cluster(polygon)
    joint1 = [joint for joint in sk.getInfluence() if joint.type() == "joint" and not joint.liw.get()]
    if len(joint1) != 1:
        return pm.mel.warning("\nyou need a unlock joint")
    joint1 = joint1[0]

    joint2 = [joint for joint in sk.paintTrans.inputs() if joint.type() == "joint"]
    if len(joint2) != 1:
        return pm.mel.warning("\nyou need a paint joint")
    joint2 = joint2[0]

    matrix = spine_inverse(joint1, joint2)
    radius = pm.softSelect(q=1, ssd=1) * 2
    wxs = [(p * matrix)[0] / radius for p in mesh.getPoints(space="world")]
    pm.select(polygon)
    return locals()


def ik_solve(xs, ys, r, sk, wxs, **kwargs):
    weights = [get_widget(x/r+0.5, xs, ys) for x in wxs]
    sk.paintWeights.set(weights)


def loop_solve(**kwargs):
    polygon = assert_geometry(shape_type="mesh")
    mesh = polygon.getShape()
    sk = get_skin_cluster(polygon)
    joint_vtx_ids = {}
    for i, joint in enumerate(sk.getInfluence()):
        if not joint.liw.get():
            point = joint.getTranslation(space="world")
            _, face_id = mesh.getClosestPoint(point, space="world")
            face = mesh.f[face_id]
            length_map = {(mesh.vtx[vId].getPosition(space="world") - point).length(): mesh.vtx[vId] for vId in
                          face.getVertices()}
            joint_vtx_ids[i] = set([length_map[min(length_map.keys())].index()])
    old_weight_matrix = [list(sk.getWeights(mesh, i)) for i in joint_vtx_ids.keys()]
    max_weights = [sum(ws) for ws in zip(*old_weight_matrix)]
    weight_ids = set([i for i, w in enumerate(max_weights) if w > 0.0001])
    id_edges = {}
    pattern = re.compile("[0-9]+")
    ve = {i: [int(s) for s in pattern.findall(line)[1:]] for i, line in enumerate(pm.polyInfo(mesh, ve=1))}
    ev = {i: [int(s) for s in pattern.findall(line)[1:]] for i, line in enumerate(pm.polyInfo(mesh, ev=1))}
    vv = {v: [v for e in es for v in ev[e]] for v, es in ve.items()}
    while weight_ids:
        for joint_id, vtx_ids in joint_vtx_ids.items():
            edge_ids = weight_ids & vtx_ids
            if edge_ids:
                id_edges.setdefault(joint_id, set()).update(edge_ids)
                weight_ids -= edge_ids
            joint_vtx_ids[joint_id] = set([i for vtx_id in vtx_ids for i in vv.get(vtx_id, [])])
    weights = []
    for i, w in enumerate(max_weights):
        for joint_id in sorted(joint_vtx_ids.keys()):
            if i in id_edges.get(joint_id, set()):
                weights.append(w)
            else:
                weights.append(0)
    sk.setWeights(mesh, sorted(joint_vtx_ids.keys()), weights)
    return id_edges


def loop_kwargs(*args):
    return {}

kwargs_list = [soft_kwargs, ik_kwargs, up_kwargs, split_kwargs, spine_kwargs, loop_kwargs]
solve_list = [soft_solve, ik_solve, split_solve, split_solve, split_solve, loop_solve]


def solve_kwargs(i, d):
    skin_cluster = get_skin_cluster()
    if not skin_cluster:
        return skin_cluster
    kwargs = dict(sk=skin_cluster)
    kwargs.update(kwargs_list[i](d))
    return kwargs


def solve(i, xs, ys, r, d, **kwargs):
    kwargs.update(**locals())
    solve_list[i](**kwargs)
