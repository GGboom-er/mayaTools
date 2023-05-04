# _*_ coding:cp936 _*_
"""
Scripts :    python.tools.rigging.riggingCorrection
Author  :    JesseChou
Date    :    2021/4/27
QQ      :    375714316
E-Mail  :    JesseChou0612@gmail.com or 375714316@qq.com
"""
import attrToolsPK.attrTools as aa
import python.tools.rigging.controllerManager as cm
from python.core import config, setting
from python.meta import parent, selection
# from python.tools.rigging import controllerManager, utils
import controllerManager
import utils
from maya import cmds

reload(aa)
def check_node(name, node):
    """
    # 检查指定类型指定名称的节点是否存在
    :param name: 节点名称
    :param node: 节点类型
    :return: 节点名称
    """
    judge = False
    if cmds.objExists(name):
        if cmds.nodeType(name) == node:
            judge = True
    if not judge:
        name = cmds.createNode(node, n=name)
    return name


def get_controller_size(controller):
    """
    # 获取控制器真实大小
    :param controller: 控制器名称
    :return: 控制器的尺寸
             [x,y,z]
    """
    try:
        bbx = cmds.xform('%s.cv[*]' % controller, q=1, bb=1)
    except Exception as e:
        print(e)
        bbx = cmds.xform(controller, q=1, bb=1)
    x = abs(bbx[3] - bbx[0])
    y = abs(bbx[4] - bbx[1])
    z = abs(bbx[5] - bbx[2])
    return [x, y, z]


def match_controller_size(controller, size):
    """
    # 匹配控制器大小
    :param controller: 控制器名称
    :param size: 指定大小
    :return:
    """
    radius = max(*get_controller_size(controller))
    num = size * 1.0 / radius
    cmds.select('%s.cv[*]' % controller, r=1)
    cmds.scale(num, num, num, r=True, ocp=True)


def match_transform(base, target):
    """
    # 匹配物体位置
    :param base: 要匹配位置的基础物体
    :param target: 要匹配位置的的目标物体
    :return:
    """
    position = cmds.xform(target, q=True, ws=True, t=True)
    rotation = cmds.xform(target, q=True, ws=True, ro=True)
    scale = cmds.xform(target, q=True, ws=True, s=True)
    cmds.xform(base, ws=True, t=position, ro=rotation, s=scale)


def check_sub_group(name, parentObj):
    """
    # 检查附加组别
    :param name:组别名称
    :param parentObj: 父物体
    :return:组别名称
    """
    if not cmds.objExists(name):
        cmds.createNode('transform', n=name)
    cmds.setAttr('%s.inheritsTransform' % name, 0)
    parent.fitParent(name, parentObj)
    for attr in setting.CHANNEL_BASE_ATTRS:
        if attr != 'v':
            cmds.setAttr('%s.%s' % (name, attr), e=1, l=1, k=0)
        else:
            cmds.setAttr('%s.%s' % (name, attr), e=1, l=0, k=0)
    return name


def lock_channel_attrs(transform, attrs):
    for attr in attrs:
        cmds.setAttr('%s.%s' % (transform, attr), e=True, l=True, k=False)


class Controller(object):
    def __init__(self, name, index, color, parentObj=None):
        self.name = name
        self.color = color
        self.index = index
        self.parent = parentObj

    @property
    def controller(self):
        if not cmds.objExists(self.name):
            control = controllerManager.Controller(self.name, post='', color=self.color)
            control.create(self.index)
        return self.name

    @property
    def extra(self):
        ext = '%sExt' % self.controller
        if not cmds.objExists(ext):
            cmds.createNode('transform', n=ext)
            match_transform(ext, self.controller)
        parent.fitParent(self.controller, ext)
        return ext

    @property
    def offset(self):
        oft = '%sOft' % self.controller
        if not cmds.objExists(oft):
            cmds.createNode('transform', n=oft)
            match_transform(oft, self.extra)
        parent.fitParent(self.extra, oft)
        # print ('<>' * 50, oft, '\r\n', self.parent, '<>' * 50)
        parent.fitParent(oft, self.parent)
        return oft

    def __repr__(self):
        return self.controller

    def create(self):
        return self.offset


class Rigging(object):
    def __init__(self, **kwargs):
        """
        :param kwargs:  main_group_name/mgn         主组别的名称(字符串)
                        geometry_group_name/ggn     模型组别名称(字符串)
                        rigging_group_name/rgn      绑定组别名称(字符串)
                        deform_group_name/dgn       影响物组别名称(字符串)
                        other_group_name/ogn        其他杂项组别名称(字符串)

                        main_controller_name/mcn    主控制器名称(字符串)
                        main_controller_index/mci   主控制器创建编号(整数)
                        main_controller_color/mcc   主控制器颜色(3位0-1小数列表)

                        second_controller_name/scn  次级控制器名称(字符串)
                        second_controller_index/sci 次级控制器创建编号(整数)
                        second_controller_color/scc 次级控制器颜色(3位0-1小数列表)
        """
        self.__main_group = None
        self.__main_group_name = kwargs.get('main_group_name', kwargs.get('mgn', 'Group'))
        self.__geometry_group = None
        self.__geometry_group_name = kwargs.get('geometry_group_name', kwargs.get('ggn', 'Geometry'))
        self.__rigging_group = None
        self.__rigging_group_name = kwargs.get('rigging_group_name', kwargs.get('rgn', 'Rigging'))
        self.__deform_group = None
        self.__deform_group_name = kwargs.get('deform_group_name', kwargs.get('dgn', 'Deformation'))
        self.__other_group = None
        self.__other_group_name = kwargs.get('other_group_name', kwargs.get('ogn', 'Reference'))

        self.__main_controller = None
        self.__main_controller_name = kwargs.get('main_controller_name', kwargs.get('mcn', 'Rig'))
        self.__main_controller_index = kwargs.get('main_controller_index', kwargs.get('mci', 41))
        self.__main_controller_color = kwargs.get('main_controller_color', kwargs.get('mcc', [0, 1, 0]))

        self.__second_controller = None
        self.__second_controller_name = kwargs.get('second_controller_name', kwargs.get('scn', 'Ctr'))
        self.__second_controller_index = kwargs.get('second_controller_index', kwargs.get('sci', 28))
        self.__second_controller_color = kwargs.get('second_controller_color', kwargs.get('scc', [1, 1, 0]))

        self.__group_infos = config.RIG_GROUP_CONFIG

    @property
    def main_group_name(self):
        return self.__main_group_name

    @property
    def main_group(self):
        return self.__main_group

    @property
    def geometry_group_name(self):
        return self.__geometry_group_name

    @property
    def geometry_group(self):
        return self.__geometry_group

    @property
    def other_group_name(self):
        return self.__other_group_name

    @property
    def other_group(self):
        return self.__other_group

    @property
    def rigging_group_name(self):
        return self.__rigging_group_name

    @property
    def rigging_group(self):
        return self.__rigging_group

    @property
    def deform_group_name(self):
        return self.__deform_group_name

    @property
    def deform_group(self):
        return self.__deform_group

    @property
    def main_controller_name(self):
        return self.__main_controller_name

    @property
    def main_controller_index(self):
        return self.__main_controller_index

    @property
    def main_controller_color(self):
        return self.__main_controller_color

    @property
    def main_controller(self):
        return self.__main_controller

    @property
    def second_controller_name(self):
        return self.__second_controller_name

    @property
    def second_controller_index(self):
        return self.__second_controller_index

    @property
    def second_controller_color(self):
        return self.__second_controller_color

    @property
    def second_controller(self):
        return self.__second_controller

    def check_groups(self):
        if not self.main_group:
            self.__main_group = check_node(self.main_group_name, 'transform')
            lock_channel_attrs(self.main_group, setting.CHANNEL_BASE_ATTRS)
        if not self.geometry_group:
            self.__geometry_group = check_node(self.geometry_group_name, 'transform')
            lock_channel_attrs(self.geometry_group, setting.CHANNEL_BASE_ATTRS)
            parent.fitParent(self.geometry_group, self.main_group)
            cmds.setAttr('%s.overrideDisplayType' % self.geometry_group, 2)
            for node in ['cache', 'data']:
                if cmds.objExists(node):
                    parent.fitParent(node, self.geometry_group)
        if not self.rigging_group:
            self.__rigging_group = check_node(self.rigging_group_name, 'transform')
            lock_channel_attrs(self.rigging_group, setting.CHANNEL_BASE_ATTRS)
            parent.fitParent(self.rigging_group, self.main_group)
        if not self.deform_group:
            self.__deform_group = check_node(self.deform_group_name, 'transform')
            lock_channel_attrs(self.deform_group, setting.CHANNEL_BASE_ATTRS)
            parent.fitParent(self.deform_group, self.main_group)
        if not self.other_group:
            self.__other_group = check_node(self.other_group_name, 'transform')
            lock_channel_attrs(self.other_group_name, setting.CHANNEL_BASE_ATTRS)
            parent.fitParent(self.other_group_name, self.main_group)
            cmds.setAttr('%s.overrideDisplayType' % self.other_group_name, 2)

    def fit_controller_size(self, size=1.0):
        """
        适配控制器大小
        :param size: 物体大小
        :return:
        """
        select = selection.Selection()
        match_controller_size(self.main_controller, size * 2.2)
        match_controller_size(self.second_controller, size * 1.1)
        select.reselect()

    def check_controllers(self):
        # 创建控制器
        if self.rigging_group:
            if not self.main_controller:
                self.__main_controller = Controller(self.main_controller_name, self.main_controller_index,
                                                    self.main_controller_color, self.rigging_group)
                self.main_controller.create()
            if not self.second_controller:
                self.__second_controller = Controller(self.second_controller_name, self.second_controller_index,
                                                      self.second_controller_color, self.main_controller.controller)
                self.second_controller.create()
        else:
            print (u'请先创建基础组别，再来执行创建控制器命令！')


class ChrRigging(Rigging):
    def __init__(self, **kwargs):
        """
        :param kwargs:  main_group_name/mgn             主组别的名称(字符串)
                        geometry_group_name/ggn         模型组别名称(字符串)
                        rigging_group_name/rgn          绑定组别名称(字符串)
                        deform_group_name/dgn           影响物组别名称(字符串)
                        other_group_name/ogn            其他杂项组别名称(字符串)

                        main_controller_name/mcn        主控制器名称(字符串)
                        main_controller_index/mci       主控制器创建编号(整数)
                        main_controller_color/mcc       主控制器颜色(3位0-1小数列表)

                        second_controller_name/scn      次级控制器名称(字符串)
                        second_controller_index/sci     次级控制器创建编号(整数)
                        second_controller_color/scc     次级控制器颜色(3位0-1小数列表)

                        third_controller_name/tcn       三级控制器名称(字符串)
                        third_controller_index/tci      三级控制器创建编号(整数)
                        third_controller_color/tcc      三级控制器颜色(3位0-1小数列表)

                        visibility_controller_name/vcn  显隐控制器名称(字符串)
                        visibility_controller_index/vci 显隐控制器创建编号(整数)
                        visibility_controller_color/vcc 显隐控制器颜色(3位0-1小数列表)

                        extra_group_name/egn            附加绑定组别名称(字符串)
                        facial_group_name/fgn           表情绑定组别名称(字符串)
        """
        super(ChrRigging, self).__init__(**kwargs)
        self.__second_controller_name = kwargs.get('second_controller_name', kwargs.get('scn', 'Chr'))
        self.__second_controller_index = kwargs.get('second_controller_index', kwargs.get('sci', 112))
        self.__second_controller_color = kwargs.get('second_controller_color', kwargs.get('scc', [.45, .25, 0.05]))

        self.__third_controller = None
        self.__third_controller_name = kwargs.get('third_controller_name', kwargs.get('tcn', 'Main'))
        self.__third_controller_index = kwargs.get('third_controller_index', kwargs.get('tci', 56))
        self.__third_controller_color = kwargs.get('third_controller_color', kwargs.get('tcc', [0.22, 0.02, 0.54]))
        self.__visibility_controller = None
        self.__visibility_controller_name = kwargs.get('visibility_controller_name', kwargs.get('vcn', 'VisibilityCtr'))
        self.__visibility_controller_index = kwargs.get('visibility_controller_index', kwargs.get('vci', 117))
        self.__visibility_controller_color = kwargs.get('visibility_controller_color', kwargs.get('vcc', [1, 0, 0]))

        self.__extra_group = None
        self.__extra_group_name = kwargs.get('extra_group_name', kwargs.get('egn', 'ExtraSystem'))
        self.__facial_group = None
        self.__facial_group_name = kwargs.get('facial_group_name', kwargs.get('fgn', 'FacialSystem'))

    @property
    def visibility_Attributes(self):
        attrs = [{'name': 'deform_sys_vis', 'type': 'bool', 'value': True, 'keyable': False},
                 {'name': 'extra_sys_vis', 'type': 'bool', 'value': False, 'keyable': False},
                 {'name': 'facial_sys_vis', 'type': 'bool', 'value': False, 'keyable': False},
                 {'name': 'sub_facial_sys_vis', 'type': 'bool', 'value': False, 'keyable': False},
                 {'name': 'geometry_select_able', 'type': 'bool', 'value': False, 'keyable': False},
                 {'name': 'RigSpeed', 'type': 'enum', 'value': 'normal(SLOW):proxy(FAST)', 'keyable': False},
                 {'name': 'cache_vis', 'type': 'bool', 'value': True, 'keyable': True}]
        return attrs

    @property
    def extra_group_name(self):
        return self.__extra_group_name

    @property
    def extra_group(self):
        return self.__extra_group

    @property
    def facial_group_name(self):
        return self.__facial_group_name

    @property
    def facial_group(self):
        return self.__facial_group

    @property
    def second_controller_name(self):
        return self.__second_controller_name

    @property
    def second_controller_index(self):
        return self.__second_controller_index

    @property
    def second_controller_color(self):
        return self.__second_controller_color

    @property
    def third_controller_name(self):
        return self.__third_controller_name

    @property
    def third_controller_index(self):
        return self.__third_controller_index

    @property
    def third_controller_color(self):
        return self.__third_controller_color

    @property
    def third_controller(self):
        return self.__third_controller

    @property
    def visibility_controller_name(self):
        return self.__visibility_controller_name

    @property
    def visibility_controller_index(self):
        return self.__visibility_controller_index

    @property
    def visibility_controller_color(self):
        return self.__visibility_controller_color

    @property
    def visibility_controller(self):
        return self.__visibility_controller

    def check_visibility_attrs(self, controller):
        """
        检查显示控制器控制属性
        :return:
        """
        for attr in self.visibility_Attributes:
            name = attr.get('name')
            if name:
                if not cmds.objExists('%s.%s' % (controller, name)):
                    if attr.get('type' != 'enum'):
                        cmds.addAttr(controller, ln=name, at=attr.get('type'), dv=attr.get('value'))
                    else:
                        cmds.addAttr(controller, ln=name, at=attr.get('type'), en=attr.get('value'))
                # cmds.setAttr('%s.%s' % (controller, name), attr.get('value'))
                keyable = attr.get('keyable')
                if keyable:
                    cmds.setAttr('%s.%s' % (controller, name), e=1, l=0, k=1)
                else:
                    cmds.setAttr('%s.%s' % (controller, name), e=1, l=0, cb=1)

        for attr in setting.CHANNEL_BASE_ATTRS:
            cmds.setAttr('%s.%s' % (controller, attr), e=1, l=1, k=0)

    def check_chr_controllers(self):
        # 检查角色绑定控制器
        # 检测基础控制器
        self.check_controllers()
        if self.rigging_group:
            # 检测第三级控制器
            if not self.third_controller:
                self.__third_controller = Controller(self.third_controller_name, self.third_controller_index,
                                                     self.third_controller_color, self.second_controller.controller)
                self.third_controller.create()

            # 检测显隐控制器
            if not self.visibility_controller:
                self.__visibility_controller = Controller(self.visibility_controller_name,
                                                          self.visibility_controller_index,
                                                          self.visibility_controller_color,
                                                          self.third_controller.controller)
                self.visibility_controller.create()
            # 检测显隐控制器控制属性
            self.check_visibility_attrs(self.visibility_controller)

    def fit_visibility_controller(self, position, size):
        """
        适配显示控制器位置和大小
        :param position: 控制器位置
        :param size: 控制器大小
        :return:
        """
        visOft = self.visibility_controller.offset
        cmds.xform(visOft, ws=1, t=position)
        cmds.setAttr('%s.rx' % visOft, 90)
        match_controller_size(self.visibility_controller.controller, size)

    def fit_chr_controller_size(self, size=1.0):
        """
        匹配角色绑定特有控制器尺寸
        :param size: 控制器尺寸
        :return:
        """
        self.fit_controller_size(size)
        match_controller_size(self.third_controller.controller, size)

    def check_chr_sub_groups(self):
        # 检测所需附加组别
        if not self.extra_group:
            self.__extra_group = check_sub_group(self.extra_group_name, self.third_controller.controller)
        if not self.facial_group:
            self.__facial_group = check_sub_group(self.facial_group_name, self.third_controller.controller)

    def connect_sub_groups_attrs(self):
        # 连接组别间的属性控制连接
        controller = self.visibility_controller.controller
        # 检测可选性反转节点
        geoRev = check_node('GeometrySelectAbleRV', 'reverse')
        # 连接控制器的模型可选性到反转节点
        cmds.connectAttr('%s.%s' % (controller, self.visibility_Attributes[4].get('name')),
                         '%s.ix' % geoRev, f=1)
        # 将反转后的属性，连接到 geometry 和 other 组别的控制属性上
        for group in [self.geometry_group, self.other_group]:
            cmds.connectAttr('%s.ox' % geoRev, '%s.overrideEnabled' % group, f=1)
        # 连接deform组别的显隐
        cmds.connectAttr('%s.%s' % (controller, self.visibility_Attributes[0].get('name')),
                         '%s.lodVisibility' % self.deform_group, f=True)
        # 连接extra组别的显隐属性
        cmds.connectAttr('%s.%s' % (controller, self.visibility_Attributes[1].get('name')),
                         '%s.lodVisibility' % self.extra_group, f=True)
        # 连接facial组别的显隐属性
        cmds.connectAttr('%s.%s' % (controller, self.visibility_Attributes[2].get('name')),
                         '%s.lodVisibility' % self.facial_group, f=True)
        # 锁定extra和facial组别的显隐属性
        '''for grp in [self.extra_group, self.facial_group]:
            cmds.setAttr('%s.v' % grp, e=True, l=True, k=False)'''
        # 连接 cache 组的显隐
        if cmds.objExists('cache'):
            if cmds.objExists('visData.cache__vis__'):
                cmds.connectAttr('%s.%s' % (controller, self.visibility_Attributes[6].get('name')),
                                 'visData.cache__vis__', f=True)
            else:
                cmds.connectAttr('%s.%s' % (controller, self.visibility_Attributes[6].get('name')),
                                 'cache.visibility', f=True)

    def chr_correct(self):
        # 检测并创建基础组别
        self.check_groups()
        # 检测并创建角色绑定特有控制器
        self.check_chr_controllers()
        # 检测并创建角色绑定特有附加组别
        self.check_chr_sub_groups()
        # 连接组别间的属性控制连接
        self.connect_sub_groups_attrs()


class AdvRigging59(ChrRigging):
    def __init__(self, **kwargs):
        super(AdvRigging59, self).__init__(**kwargs)
        self._mainSize_ = 1
        self.__deform_group_name = kwargs.get('deform_group_name', kwargs.get('dgn', 'DeformationSystem'))

    @property
    def deform_group_name(self):
        return self.__deform_group_name

    @property
    def main_system_name(self):
        return 'MainSystem'

    @property
    def main_system(self):
        if cmds.objExists(self.main_system_name):
            return self.main_system_name

    @property
    def main_extra_name(self):
        return 'MainExt'

    @property
    def main_extra(self):
        if cmds.objExists(self.main_extra_name):
            return self.main_extra_name

    def rename_adv_group(self):
        # 重命名 adv 主控制器的组别
        if self.main_system and not self.main_extra:
            cmds.rename(self.main_system, self.main_extra_name)
            if cmds.objExists('MainOft'):
                parent.fitParent(self.main_extra, 'MainOft')

    def get_adv_rig_size(self):
        # 获取绑定控制器基础大小
        if cmds.objExists(self.third_controller):
            self._mainSize_ = max(*get_controller_size(self.third_controller))

    def match_other_adv_groups(self):
        # 匹配adv其他组别
        if cmds.objExists('MotionSystem'):
            parent.fitParent('MotionSystem', self.third_controller)

        if cmds.objExists('FitSkeleton'):
            parent.fitParent('FitSkeleton', self.other_group)

    def fit_adv_visibility_controller(self):
        if cmds.objExists('HeadEnd_M'):
            point = cmds.xform('HeadEnd_M', q=True, ws=True, t=True)
            new_point = [point[0], point[1] * 1.15, point[2]]
            self.fit_visibility_controller(new_point, self._mainSize_ * 0.25)

    def adv_chr_correct(self):
        self.rename_adv_group()
        self.chr_correct()
        self.match_other_adv_groups()
        self.get_adv_rig_size()
        self.fit_chr_controller_size(self._mainSize_)
        self.fit_adv_visibility_controller()

        print (self, u'Advance Skeleton 绑定修正')

    def adv_system_reset(self):
        if cmds.objExists('FitSkeleton') and cmds.objExists(self.main_group_name):
            parent.fitParent('FitSkeleton', self.main_group_name)
        if cmds.objExists('MotionSystem') and cmds.objExists(self.main_group_name):
            parent.fitParent('MotionSystem', self.main_group_name)
            if cmds.objExists(self.third_controller_name):
                if self.main_extra:
                    cmds.rename(self.main_extra, self.main_system_name)
                parent.fitParent(self.main_system, 'MotionSystem')
        if cmds.objExists(self.deform_group_name):
            cmds.setAttr('%s.v' % self.deform_group_name, e=True, l=False)


class AdvRigging(ChrRigging):
    def __init__(self, **kwargs):
        super(AdvRigging, self).__init__(**kwargs)
        self._mainSize_ = 1
        self.__deform_group_name = kwargs.get('deform_group_name', kwargs.get('dgn', 'DeformationSystem'))
        self.__adv_version = kwargs.get('adv_version', kwargs.get('av', '5.74'))
        self.__adv_face_group = 'FaceGroup'
        self.__adv_facial_rig = None

    @property
    def adv_version(self):
        return self.__adv_version

    @property
    def deform_group_name(self):
        return self.__deform_group_name

    @property
    def adv_face_group(self):
        return self.__adv_face_group

    @property
    def adv_facial_rig(self):
        if cmds.objExists(self.adv_face_group):
            if not self.__adv_facial_rig:
                self.__adv_facial_rig = AdvFacialRigging(av=self.adv_version, afg=self.adv_face_group)
        return self.__adv_facial_rig

    @property
    def adv_sides(self):
        return ['_L', '_R']

    def get_adv_rig_size(self):
        # 获取绑定控制器基础大小
        if cmds.objExists(self.third_controller):
            self._mainSize_ = max(*get_controller_size(self.third_controller))

    def match_other_adv_groups(self):
        # 匹配adv其他组别
        if cmds.objExists('MotionSystem'):
            parent.fitParent('MotionSystem', self.third_controller.controller)

        if cmds.objExists('FitSkeleton'):
            parent.fitParent('FitSkeleton', self.other_group)

        if cmds.objExists(self.adv_face_group):
            parent.fitParent(self.adv_face_group, self.facial_group)

    def fit_adv_visibility_controller(self):
        if cmds.objExists('HeadEnd_M'):
            point = cmds.xform('HeadEnd_M', q=True, ws=True, t=True)
            new_point = [point[0], point[1] * 1.10, point[2]]
            self.fit_visibility_controller(new_point, self._mainSize_ * 0.25)

    def match_adv_vis_attrs(self):
        # 匹配adv控制器的显隐控制属性到vis控制器上
        if self.third_controller and self.visibility_controller:
            attr_infos = {}
            # 将原始大环上的显隐控制属性，转移到头顶的vis控制器上，由于是新想到的需求，之前任务中并未安排，暂时停止，后续安排时间处理

    def main_scale_correct(self):
        judge = True
        for ctrl in [self.main_controller_name, self.second_controller_name, self.third_controller_name]:
            if not cmds.objExists(ctrl):
                judge = False
                break
        if judge:
            rig_offset_scale_md = check_node('riggingOffsetScaleMD', 'multiplyDivide')
            rig_extra_scale_md = check_node('riggingExtraScaleMD', 'multiplyDivide')
            rig_ctrl_scale_md = check_node('riggingControllerScaleMD', 'multiplyDivide')
            chr_offset_scale_md = check_node('characterOffsetScaleMD', 'multiplyDivide')
            chr_extra_scale_md = check_node('characterExtraScaleMD', 'multiplyDivide')
            chr_ctrl_scale_md = check_node('characterControllerScaleMD', 'multiplyDivide')
            main_offset_scale_md = check_node('mainOffsetScaleMD', 'multiplyDivide')
            main_extra_scale_md = check_node('mainExtraScaleMD', 'multiplyDivide')
            main_ctrl_scale_md = check_node('mainControllerScaleMD', 'multiplyDivide')

            cmds.setAttr('%s.i1' % rig_offset_scale_md, 1, 1, 1, type='double3')
            cmds.connectAttr('%sOft.s' % self.main_controller_name, '%s.i2' % rig_offset_scale_md, f=True)
            cmds.connectAttr('%s.o' % rig_offset_scale_md, '%s.i1' % rig_extra_scale_md, f=True)
            cmds.connectAttr('%sExt.s' % self.main_controller_name, '%s.i2' % rig_extra_scale_md, f=True)
            cmds.connectAttr('%s.o' % rig_extra_scale_md, '%s.i1' % rig_ctrl_scale_md, f=True)
            cmds.connectAttr('%s.s' % self.main_controller_name, '%s.i2' % rig_ctrl_scale_md, f=True)

            cmds.connectAttr('%s.o' % rig_ctrl_scale_md, '%s.i1' % chr_offset_scale_md, f=True)
            cmds.connectAttr('%sOft.s' % self.second_controller_name, '%s.i2' % chr_offset_scale_md, f=True)
            cmds.connectAttr('%s.o' % chr_offset_scale_md, '%s.i1' % chr_extra_scale_md, f=True)
            cmds.connectAttr('%sExt.s' % self.second_controller_name, '%s.i2' % chr_extra_scale_md, f=True)
            cmds.connectAttr('%s.o' % chr_extra_scale_md, '%s.i1' % chr_ctrl_scale_md, f=True)
            cmds.connectAttr('%s.s' % self.second_controller_name, '%s.i2' % chr_ctrl_scale_md, f=True)

            cmds.connectAttr('%s.o' % rig_ctrl_scale_md, '%s.i1' % main_offset_scale_md, f=True)
            cmds.connectAttr('%sOft.s' % self.third_controller_name, '%s.i2' % main_offset_scale_md, f=True)
            cmds.connectAttr('%s.o' % main_offset_scale_md, '%s.i1' % main_extra_scale_md, f=True)
            cmds.connectAttr('%sExt.s' % self.third_controller_name, '%s.i2' % main_extra_scale_md, f=True)
            cmds.connectAttr('%s.o' % main_extra_scale_md, '%s.i1' % main_ctrl_scale_md, f=True)
            cmds.connectAttr('%s.s' % self.third_controller_name, '%s.i2' % main_ctrl_scale_md, f=True)

            cmds.connectAttr('%s.o' % main_ctrl_scale_md, 'MainScaleMultiplyDivide.i1', f=True)
        if cmds.objExists(self.deform_group_name):
            judge = True
            for attr in ['s', 'sx', 'sy', 'sz']:
                cmds.setAttr('%s.%s' % (self.deform_group_name, attr), e=True, l=False)
                cons = cmds.listConnections('%s.%s' % (self.deform_group_name, attr), s=True, d=False)
                if cons:
                    if cmds.nodeType(cons[0]) == 'scaleConstraint':
                        judge = False
            if judge:
                cmds.scaleConstraint(self.main_controller_name, self.deform_group_name, mo=True)
            cmds.setAttr('%s.s' % self.deform_group_name, e=True, l=True)

    def main_scale_correctFn(self):
        judge = True
        for ctrl in [self.main_controller_name, self.second_controller_name, self.third_controller_name]:
            if not cmds.objExists(ctrl):
                judge = False
                break
        if judge:
            main_ctrl_scale_DeMatrix = check_node('mainControllerScaleDeMAtrix', 'decomposeMatrix')
            cmds.connectAttr(self.third_controller_name+'.worldMatrix[0]',main_ctrl_scale_DeMatrix+'.inputMatrix',f =1)
            con = cmds.listConnections('MainScaleMultiplyDivide.i1',p =1,d =0,s =1)
            if con == ['Main.scale']:
                cmds.disconnectAttr(con[0],'MainScaleMultiplyDivide.i1')
            cmds.connectAttr(main_ctrl_scale_DeMatrix+'.outputScale','MainScaleMultiplyDivide.i1', f=True)
            self.addSet(obj = main_ctrl_scale_DeMatrix,set = 'AllSet')
            if cmds.objExists(self.deform_group_name):
                deform_scale_DeMatrix = check_node('deform_scale_DeMatrix', 'decomposeMatrix')
                cmds.setAttr('%s.s' % self.deform_group_name, e=True, l=False)
                cmds.connectAttr(self.third_controller_name + '.worldMatrix[0]', deform_scale_DeMatrix + '.inputMatrix',
                                 f=1)
                cmds.connectAttr(deform_scale_DeMatrix + '.outputScale', self.deform_group_name+'.s', f=True)
                cmds.setAttr('%s.s' % self.deform_group_name, e=True, l=True)
                cmds.setAttr('%s.v' % self.deform_group_name, e=True, l=False)
                self.addSet(obj=deform_scale_DeMatrix, set='AllSet')

    def lock_fk_translate(self):
        # 锁定并隐藏fk控制器的translate 和 visibility 属性
        body_parts = [u'Shoulder', u'Elbow', u'Wrist', u'Hip', u'Knee', u'Ankle', u'Toes']
        for side in self.adv_sides:
            for part in body_parts:
                fk_ctr = 'FK%s%s' % (part, side)
                if cmds.objExists(fk_ctr):
                    attrs = ['v'] + ['t%s' % x for x in 'xyz']
                    for attr in attrs:
                        cmds.setAttr('%s.%s' % (fk_ctr, attr), e=True, l=True, k=False, cb=False)
    def lock_ikSec_scale( self ):
        body_parts = [u'Neck',u'Shoulder',u'Elbow',u'Hip',u'Knee']
        for side in self.adv_sides:
            for part in body_parts:
                for i in range(1,3):
                    iksec_ctr = 'Bend%s%s%s' % (part,i,side)
                    if cmds.objExists(iksec_ctr):
                        attrs = ['v'] + ['s%s' % x for x in 'yz']
                        for attr in attrs:
                            cmds.setAttr('%s.%s' % (iksec_ctr, attr), e=True, l=True, k=False, cb=False)
    def correct_hand_cup(self):
        # 修正手掌无名指和小拇指缩放问题
        for side in self.adv_sides:
            ctrl_grp = 'FKParentConstraintToCup%s' % side
            if cmds.objExists(ctrl_grp):
                cons = cmds.listConnections('%s.s' % ctrl_grp, s=True, d=False, p=True) or []
                if cons:
                    if cmds.nodeType(cons[0]) == 'joint':
                        cmds.disconnectAttr(cons[0], '%s.s' % ctrl_grp)
                        cmds.scaleConstraint(cons[0].split('.')[0], ctrl_grp, mo=True)
    def editFootIKCtrlShape( self ):
        for side in self.adv_sides:
            if side == '_L':
                sacleValue = -1
            elif side == '_R':
                sacleValue = 1
            try:
                frontCtrl = cmds.xform('RollToesEnd' + side, q=1, ws=1, t=1)
                backCtrl = cmds.xform('RollHeel' + side, q=1, ws=1, t=1)
                insidePnt = cmds.xform('IKLegFootRockInnerPivot' + side, q=1, ws=1, t=1)
                outsidePnt = cmds.xform('IKLegFootRockOuterPivot' + side, q=1, ws=1, t=1)
                ctrlShape = cmds.listRelatives('IKLeg' + side, s=1, type='nurbsCurve')
            except Exception as e:
                print (e)
            if frontCtrl and backCtrl and insidePnt and outsidePnt and ctrlShape:
                ctrlShape = ctrlShape[0]
                # ctrlWIMatrix = pm.dt.Matrix(cmds.xform('IKLeg' + side, q=1, ws=1, m=1)).inverse()
                # Apnt = pm.dt.Point(frontCtrl) * ctrlWIMatrix
                # Bpnt = pm.dt.Point(backCtrl)
                # Bpnt = pm.dt.Point(backCtrl) * ctrlWIMatrix
                # Cpnt = pm.dt.Point([insidePnt[0],insidePnt[1],insidePnt[2]+1*sacleValue*0.02*self._mainSize_]) * ctrlWIMatrix
                # Dpnt = pm.dt.Point([outsidePnt[0],outsidePnt[1],outsidePnt[2]-1*sacleValue*0.02*self._mainSize_]) * ctrlWIMatrix
                #
                # setApnt = [cmds.setAttr(ctrlShape + '.cv[%s]' % (pnt), Bpnt[0], Apnt[1], Cpnt[2]) for pnt in
                #            ['3', '6', '10', '11']]
                # setBpnt = [cmds.setAttr(ctrlShape + '.cv[%s]' % (pnt), Bpnt[0], Bpnt[1], Cpnt[2]) for pnt in
                #            ['2', '7', '14', '15']]
                # setCpnt = [cmds.setAttr(ctrlShape + '.cv[%s]' % (pnt), Bpnt[0], Apnt[1], Dpnt[2]) for pnt in
                #            ['4', '5', '9', '12']]
                # setDpnt = [cmds.setAttr(ctrlShape + '.cv[%s]' % (pnt), Bpnt[0], Bpnt[1], Dpnt[2]) for pnt in
                #            ['0', '1', '8', '13']]


                setApnt = [cmds.xform(ctrlShape + '.cv[%s]' % (pnt),
                                      t=[insidePnt[0] + 1 * sacleValue * 0.02 * self._mainSize_, backCtrl[1],
                                         frontCtrl[2]], ws=1) for pnt in ['3', '6', '10', '11']]
                setBpnt = [cmds.xform(ctrlShape + '.cv[%s]' % (pnt),
                                      t=[outsidePnt[0] - 1 * sacleValue * 0.02 * self._mainSize_, backCtrl[1],
                                         frontCtrl[2]], ws=1) for pnt in
                           ['2', '7', '14', '15']]
                setCpnt = [cmds.xform(ctrlShape + '.cv[%s]' % (pnt),
                                      t=[insidePnt[0] + 1 * sacleValue * 0.02 * self._mainSize_, backCtrl[1],
                                         backCtrl[2]], ws=1) for pnt in
                           ['4', '5', '9', '12']]
                setDpnt = [cmds.xform(ctrlShape + '.cv[%s]' % (pnt),
                                      t=[outsidePnt[0] - 1 * sacleValue * 0.02 * self._mainSize_, backCtrl[1],
                                         backCtrl[2]], ws=1) for pnt in
                           ['0', '1', '8', '13']]




    def adv_rig_preset(self):
        # 针对于adv绑定的参数预设
        if cmds.objExists('%s.jointVis' % self.third_controller.controller):
            cmds.setAttr('%s.jointVis' % self.third_controller.controller, True)
            cmds.setAttr('%s.jointVis' % self.third_controller.controller, e=True, cb=False)
    def adv_hiden_dirveJnt( self ):
        if cmds.objExists('MotionSystem'):
            [cmds.setAttr(i+'.drawStyle',2) for i in cmds.ls('MotionSystem',dag =1,type ='joint')]

    def createfingerCtrl(self):

        for side in self.adv_sides:
            if cmds.objExists('Fingers' + side):
                sideValue = 1
                ctrlName = 'FKIKFingersMain' + side
                if not cmds.objExists(ctrlName):
                    ctr = cm.Controller(ctrlName, size=self._mainSize_*0.1, postfix='')
                    ctr.create(9)
                    cmds.setAttr(ctrlName + '.lineWidth', 1.5)
                    cmds.setAttr(ctrlName + '.overrideEnabled', 1)
                    cmds.setAttr(ctrlName + '.overrideColor', 17)
                    self.addSet(obj = ctrlName,set = 'AllSet')
                    self.addSet(obj=ctrlName, set='ControlSet')

                    newNameShape = cmds.listRelatives(ctrlName, type='nurbsCurve', ni=1) or []
                    if newNameShape:
                        self.addSet(obj=newNameShape[0], set='AllSet')
                ctrlGrpName = ctrlName + '_Grp'
                if not cmds.objExists(ctrlGrpName):
                    cmds.group(n=ctrlGrpName, empty=1)
                    self.addSet(obj = ctrlGrpName,set = 'AllSet')
                    self.addSet(obj=ctrlGrpName, set='ControlSet')
                ctrlGrpChilden = cmds.listRelatives(ctrlGrpName, c=1) or []
                if ctrlName not in ctrlGrpChilden:
                    cmds.parent(ctrlName, ctrlGrpName)
                    cmds.parentConstraint('Wrist' + side, ctrlGrpName, mo=0)
                    if side == '_L':
                        sideValue = -1
                    elif side == '_R':
                        sideValue = 1
                    cmds.setAttr(ctrlName + '.r', 90 * sideValue, 0, -90 * sideValue)
                    cmds.setAttr(ctrlName + '.t', 0, 0, self._mainSize_ * 0.15 * sideValue)
                    cmds.makeIdentity(ctrlName, apply=1, r=1)
                if cmds.objExists('Wrist' + side):
                    m = cmds.xform('Wrist' + side, q=1, ws=1, m=1)
                    cmds.xform(ctrlGrpName, ws=1, m=m)
                DrivingSystem = 'DrivingSystem'
                DrivingSystemChilden = cmds.listRelatives(DrivingSystem, c=1) or []
                if cmds.objExists(DrivingSystem) and ctrlGrpName not in DrivingSystemChilden:
                    cmds.parent(ctrlGrpName, DrivingSystem)
                lock_channel_attrs(ctrlName, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                FKIKSystemGrp = 'FKIKSystem'
                if cmds.objExists(FKIKSystemGrp):
                    FKIKSystemGrp = cmds.ls('FKIKSystem', dag=1, type='parentConstraint')
                    fingerIKFKswitchCtrlList = list()
                    for part in ['Wrist', 'Cup']:
                        wristConstraint = [ctrl for ctrl in FKIKSystemGrp if
                                           part + side in cmds.listConnections(ctrl, d=0, s=1, type='transform')]
                        fingerIKFKswitchCtrlList += [cmds.listRelatives(
                            cmds.ls(
                                cmds.listConnections(constraint + '.constraintRotateY', d=1, s=0, type='transform', et=1)[
                                    0], s=1,
                                dag=1)[0], p=1)[0] for constraint in wristConstraint]
                    fingerIKFKswitchCtrlList.sort()
                    FingersCtrl = 'Fingers' + side
                    if cmds.objExists(FingersCtrl):
                        cmds.setAttr('Fingers' + side + '.lodVisibility', 0)
                        attrInfo = aa.AttrToolsClass.getAttrInfo(FingersCtrl,
                                                                 cmds.listAttr(FingersCtrl, ud=1, k=1, l=0))
                    else:
                        attrInfo = {'None':[]}
                    attrInfo.values()[0].insert(0, {
                        '___FK___': {'lock': True, 'cb': True, 'type': 'enum', 'enum': '__________', 'longName': '___FK___',
                                     'key': False, 'niceName': '___FK___'}})
                    attrInfo.values()[0].append({'___FK_IK_FKIKBlend___': {'lock': True, 'cb': True, 'type': 'enum',
                                                                           'enum': '__________',
                                                                           'longName': '___FK_IK_FKIKBlend___',
                                                                           'key': False,
                                                                           'niceName': '___FK_IK_FKIKBlend___'}})
                    [attrInfo.values()[0].append({ctrl: {'max': 10, 'min': 0, 'lock': False, 'defaultValue': 0.0,
                                                         'longName': ctrl, 'niceName': ctrl, 'key': True, 'cb': False,
                                                         'type': u'float'}})
                     for ctrl in fingerIKFKswitchCtrlList]

                    attrList = aa.AttrToolsClass.createAttrFn(ctrlName, attrInfo.values())
                    for attr in attrList:
                        ctrlAttr = ctrlName + '.' + attr
                        if cmds.objExists(ctrlAttr):

                            cmds.addAttr(ctrlAttr, e=1, max=10)
                            if cmds.objExists(FingersCtrl+ '.' + attr):
                                self.updateBuildPose(ctrlAttr, value=0)
                                if attr == 'spread':
                                    cmds.addAttr(ctrlAttr, e=1, min=-5)
                                    cmds.setDrivenKeyframe(FingersCtrl+'.'+attr, cd=ctrlAttr, dv=-5,
                                                           v=-5)
                                    cmds.setDrivenKeyframe(FingersCtrl+'.'+attr, cd=ctrlAttr,
                                                           dv=10, v=10)
                                elif attr == 'cup':
                                    cmds.addAttr(ctrlAttr, e=1, min=0)
                                    cmds.setDrivenKeyframe(FingersCtrl+'.'+attr, cd=ctrlAttr, dv=0,
                                                           v=0)
                                    cmds.setDrivenKeyframe(FingersCtrl+'.'+attr, cd=ctrlAttr,
                                                           dv=10, v=10)
                                elif attr in ['indexCurl', 'middleCurl', 'ringCurl', 'pinkyCurl', 'thumbCurl']:
                                    cmds.addAttr(ctrlAttr, e=1, min=-2)
                                    cmds.setDrivenKeyframe(FingersCtrl+'.'+attr, cd=ctrlAttr, dv=-2,
                                                           v=-2)
                                    cmds.setDrivenKeyframe(FingersCtrl+'.'+attr, cd=ctrlAttr,
                                                           dv=10, v=10)
                                cmds.setDrivenKeyframe(FingersCtrl + '.' + attr, cd=ctrlAttr, dv=0,
                                                       v=0)
                            if cmds.objExists(attr + '.FKIKBlend'):
                                self.updateBuildPose(ctrlAttr, value=0)
                                cmds.setDrivenKeyframe(attr + '.FKIKBlend', cd=ctrlAttr, dv=0,
                                                       v=0)
                                cmds.setDrivenKeyframe(attr + '.FKIKBlend', cd=ctrlAttr,
                                                       dv=10, v=10)
                                cmds.setAttr(attr + '.lodVisibility', 0)

    def addSet( self,obj = '',set = '' ):
        if not cmds.sets(obj,im=set):
            cmds.sets(obj, addElement=set)
    def updateBuildPose(self, attr='',type = 'value' ,value=0, buildPose='buildPose' ):
        if cmds.objExists(buildPose + '.udAttr'):
            oldAttrStr = str(cmds.getAttr(buildPose + '.udAttr'))
            if attr not in oldAttrStr:
                if type == 'value':
                    cmds.setAttr(buildPose+'.udAttr',oldAttrStr+';setAttr %s %s;'%(attr,value),type = 'string')
                elif type == 'ctrl':
                    cmds.setAttr(buildPose + '.udAttr', oldAttrStr + ';xform -os -t 0 0 0 -ro 0 0 0 -s 1 1 1 %s;' % attr,type = 'string')
    def updateBuildPoseAndSetFn( self,name):
        newname = cmds.listRelatives(name[0], p=1) or []
        newNameShape = cmds.listRelatives(newname,type = 'nurbsCurve',ni =1) or []
        if newNameShape:
            self.addSet(obj=newNameShape[0], set='AllSet')
        self.addSet(obj=newname, set='AllSet')
        self.addSet(obj=newname, set='ControlSet')
        self.updateBuildPose(newname[0], type='ctrl')
        if newname == [] or newname == ['Group']:
            return 0
        else:
            return (self.updateBuildPoseAndSetFn(newname))

    def fixUpdateBuildPoseAndSetFn( self ):

        self.addSet(obj=self.extra_group_name, set='AllSet')
        self.addSet(obj=self.extra_group_name, set='ControlSet')

        self.addSet(obj=self.facial_group_name, set='AllSet')
        self.addSet(obj=self.facial_group_name, set='ControlSet')

        self.addSet(obj=self.other_group_name, set='AllSet')
        self.addSet(obj=self.other_group_name, set='ControlSet')

        self.addSet(obj=self.geometry_group_name, set='AllSet')
        self.addSet(obj=self.geometry_group_name, set='ControlSet')

        self.addSet(obj=self.visibility_controller_name, set='AllSet')
        self.addSet(obj=self.visibility_controller_name, set='ControlSet')

        self.addSet(obj='VisibilityCtrOft', set='AllSet')
        self.addSet(obj='VisibilityCtrOft', set='ControlSet')

        self.addSet(obj='VisibilityCtrExt', set='AllSet')

        self.addSet(obj='VisibilityCtrShape', set='AllSet')

        self.addSet(obj='VisibilityCtr', set='AllSet')
        self.addSet(obj='VisibilityCtr', set='ControlSet')
    def adv_chr_correct(self):
        self.chr_correct()
        self.match_other_adv_groups()
        self.get_adv_rig_size()
        self.fit_chr_controller_size(self._mainSize_)
        self.fit_adv_visibility_controller()
        self.match_adv_vis_attrs()
        if self.adv_facial_rig:
            self.adv_facial_rig.do_facial_correct()
        #self.main_scale_correct()
        self.main_scale_correctFn()
        self.lock_fk_translate()
        self.lock_ikSec_scale()
        self.adv_hiden_dirveJnt()
        self.correct_hand_cup()
        self.editFootIKCtrlShape()
        self.createfingerCtrl()
        self.adv_rig_preset()
        self.updateBuildPoseAndSetFn(['Main'])
        self.fixUpdateBuildPoseAndSetFn()
    def adv_system_reset(self):
        if cmds.objExists('FitSkeleton') and cmds.objExists(self.third_controller_name):
            parent.fitParent('FitSkeleton', self.third_controller_name)
        if cmds.objExists(self.deform_group_name):
            parent.fitParent(self.deform_group_name, self.third_controller_name)
            cmds.setAttr('%s.v' % self.deform_group_name, e=True, l=False)
        if cmds.objExists(self.adv_face_group) and cmds.objExists(self.main_group_name):
            parent.fitParent(self.adv_face_group, self.main_group_name)

    def correct(self):
        self.adv_chr_correct()


class AdvFacialRigging(object):
    def __init__(self, **kwargs):
        self.__adv_version = kwargs.get('adv_version', kwargs.get('av', '5.74'))
        self.__adv_face_group = kwargs.get('adv_face_group', kwargs.get('afg', 'FaceGroup'))

    @property
    def adv_versio(self):
        return self.__adv_version

    @property
    def adv_face_group(self):
        return self.__adv_face_group

    @property
    def adv_sides(self):
        return ['_L', '_R']

    def eye_brow_inner_correct(self):
        # 修正眉毛内测控制
        # 第一步，锁定无用控制器属性
        lock_attr_list = ['v', 'influence', 'EyeBrowMid1Joint', 'EyeBrowMiddleJoint']
        for side in self.adv_sides:
            for attr in lock_attr_list:
                obj_attr = 'EyeBrowInner%s.%s' % (side, attr)
                if cmds.objExists(obj_attr):
                    cmds.setAttr(obj_attr, e=True, l=False, k=False, cb=False)
        # 第二步，转移控制面板属性到面部控制器上
        for side in self.adv_sides:
            ctrl_box = 'ctrlBrow%s' % side
            brow_ctrl = 'EyeBrowInner%s' % side
            transfer_attr_list = ['squeeze', 'outerUpDown']
            utils.transfer_connect_attrs(ctrl_box, brow_ctrl, transfer_attr_list)

    def eye_region_correct(self):
        # 眼睛控制器修正
        #transfer_attr_list = ['pupil', 'iris', 'blink', 'blinkCenter', 'upperLid', 'lowerLid', 'squint']
        transfer_attr_list = ['upperLid', 'lowerLid','blink', 'blinkCenter',  'squint', 'iris','pupil']
        for side in self.adv_sides:
            ctrl_box = 'ctrlEye%s' % side
            eye_ctrl = 'EyeRegion%s' % side
            utils.transfer_connect_attrs(ctrl_box, eye_ctrl, transfer_attr_list)
            # for attr in transfer_attr_list:
            #     if attr in ['blink', 'blinkCenter', 'squint']:
            #         cmds.addAttr('%s.%s' % (eye_ctrl, attr), e=True, maxValue=10, minValue=0)
            #     else:
            #         cmds.addAttr('%s.%s' % (eye_ctrl, attr), e=True, maxValue=10, minValue=-10)

    def lip_region_correct(self):
        # 嘴唇控制器修正
        # 骨骼位移修正，增加转嘴功能
        lip_region_joint = 'LipRegionJoint_M'
        lip_region_oft = 'LipRegionJointOffset_M'
        lip_region_ext = '%sExt' % lip_region_joint
        lip_region_tra = '%sTra' % lip_region_joint

        lip_region_ext = check_node(lip_region_ext, 'transform')
        lip_region_tra = check_node(lip_region_tra, 'transform')
        parent.fitParent(lip_region_ext, lip_region_tra)
        parent.fitParent(lip_region_tra, lip_region_oft)

        # 求出牙齿到嘴唇的距离，来确定转嘴的中心点位置
        lip_joint_position = cmds.xform(lip_region_joint, q=True, ws=True, t=True)
        teeth_joint_position = cmds.xform('upperTeethJoint_M', q=True, ws=True, t=True)
        lip_length = abs(lip_joint_position[2] - teeth_joint_position[2])
        cmds.setAttr('%s.t' % lip_region_tra, 0, 0, -lip_length, typ='double3')
        cmds.setAttr('%s.r' % lip_region_tra, 0, 0, 0, typ='double3')
        cmds.setAttr('%s.s' % lip_region_tra, 1, 1, 1, typ='double3')
        connections = cmds.listConnections(lip_region_joint, s=True, d=False, p=True) or []
        for connection in connections:
            sub_connections = cmds.listConnections(connection, s=False, d=True, p=True) or []
            for sub_connection in sub_connections:
                replace_attr = sub_connection.replace(lip_region_joint, lip_region_ext)
                if cmds.objExists(replace_attr):
                    cmds.connectAttr(connection, replace_attr, f=True)
                    cmds.disconnectAttr(connection, sub_connection)
        parent.fitParent(lip_region_joint, lip_region_ext)
        cmds.setAttr('%s.t' % lip_region_joint, 0, 0, lip_length, type='double3')
        cmds.setAttr('%s.r' % lip_region_joint, 0, 0, 0, typ='double3')
        cmds.setAttr('%s.s' % lip_region_joint, 1, 1, 1, typ='double3')

        # 隐藏 SmileBulge 控制器
        for side in self.adv_sides:
            ctrl = 'SmileBulge%s' % side
            if cmds.objExists(ctrl):
                cmds.setAttr('%s.lodVisibility' % ctrl, 0)
        # lower,upper lip 属性修正
        for part in ['lower', 'upper']:
            lip_ctrl = '%sLip_M' % part
            # press 属性连接修正
            press_rv = '%s_press_RV' % lip_ctrl
            check_node(press_rv, 'remapValue')
            cmds.setAttr('%s.inputMin' % press_rv, 2)
            cmds.setAttr('%s.inputMax' % press_rv, 0)
            cmds.setAttr('%s.outputMin' % press_rv, -10)
            cmds.setAttr('%s.outputMax' % press_rv, 10)
            cmds.connectAttr('%s.sz' % lip_ctrl, '%s.inputValue' % press_rv, f=True)
            cmds.connectAttr('%s.outColorR' % press_rv, 'ctrlMouth_M.%sPress' % part, f=True)

            # squeeze 属性连接修正
            squeeze_rv = '%s_squeeze_RV' % lip_ctrl
            check_node(squeeze_rv, 'remapValue')
            cmds.setAttr('%s.inputMin' % squeeze_rv, 1)
            cmds.setAttr('%s.inputMax' % squeeze_rv, 0)
            cmds.setAttr('%s.outputMin' % squeeze_rv, 0)
            cmds.setAttr('%s.outputMax' % squeeze_rv, 10)
            cmds.connectAttr('%s.sy' % lip_ctrl, '%s.inputValue' % squeeze_rv, f=True)
            cmds.connectAttr('%s.outColorR' % squeeze_rv, 'ctrlMouth_M.%sSqueeze' % part, f=True)

            # lower roll 属性修正
            roll_rv = '%s_roll_RV' % lip_ctrl
            check_node(roll_rv, 'remapValue')
            multi = -1 if part == 'upper' else 1
            cmds.setAttr('%s.inputMin' % roll_rv, 40 * multi)
            cmds.setAttr('%s.inputMax' % roll_rv, -40 * multi)
            cmds.setAttr('%s.outputMin' % roll_rv, 10)
            cmds.setAttr('%s.outputMax' % roll_rv, -10)
            cmds.connectAttr('%s.rx' % lip_ctrl, '%s.inputValue' % roll_rv, f=True)
            cmds.connectAttr('%s.outColorR' % roll_rv, 'ctrlMouth_M.%sRoll' % part, f=True)

            cmds.setAttr('%s.ry' % lip_ctrl, e=True, l=True, k=False)
            cmds.setAttr('%s.rz' % lip_ctrl, e=True, l=True, k=False)
            cmds.setAttr('%s.sx' % lip_ctrl, e=True, l=True, k=False)

    def smile_pull_correct(self):
        # 限制位移幅度并传递 zip 属性
        for side in self.adv_sides:
            smile_ctr = 'SmilePull%s' % side
            cmds.transformLimits(smile_ctr, tx=[-0.5, 1], etx=[1, 1], ty=[-0.5, 1], ety=[1, 1])
            if cmds.objExists('ctrlMouth_M.zipLips%s' % side):
                if not cmds.objExists(smile_ctr + '.' + 'zipLips'):
                    info = utils.transfer_connect_attrs('ctrlMouth_M', smile_ctr, ['zipLips%s' % side])
                    if 'zipLips%s' % side in info['success']:
                            cmds.renameAttr(smile_ctr + '.' + 'zipLips%s' % side, 'zipLips')
    def add_teeth_ctrls(self):
        # 增加牙齿控制器
        def add_single_ctr(part,key, position):
            # 创建骨骼和所需组别
            name = '%sTeeth_%s' % (part, key)
            joint_name = '%sJoint' % name
            joint_oft = '%sJoint_oft' % name
            check_node(joint_name, 'joint')
            check_node(joint_oft, 'transform')

            cmds.xform(joint_name, ws=1, t=position)
            cmds.xform(joint_oft, ws=1, t=position)
            parent.fitParent(joint_name, joint_oft)
            # 创建控制器
            controller_name = '%sCtr' % name
            if not cmds.objExists(controller_name):

                if part == 'upper':
                    colorList = [0.7, 0.2, 0.2]
                if part == 'lower':
                    colorList = [0.2, 0.7, 0.7]
                control = controllerManager.Controller(controller_name, post='', color=colorList, ge=True,
                                                       g=['Ext', 'Tra', 'Oft'], d='z')
                control.create(99)
                cmds.xform(control.groups[-1], ws=True, t=position)
                # cmds.parentConstraint(control.curve, joint_name, w=True, mo=True)
                # cmds.scaleConstraint(control.curve, joint_name, w=True)
                cmds.connectAttr('%s.t'%control.curve,'%s.t'%joint_name,f =1)
                cmds.connectAttr('%s.r' % control.curve, '%s.r' % joint_name,f =1)
                cmds.connectAttr('%s.s' % control.curve, '%s.s' % joint_name,f =1)
                return [joint_oft, control.groups[-1]]
            return [joint_oft, controller_name+'Oft']

        left_position = cmds.xform('SmilePull_L', q=True, ws=True, t=True)
        right_position = cmds.xform('SmilePull_R', q=True, ws=True, t=True)
        for part in ['upper', 'lower']:
            positions = {}
            center_position = cmds.xform('%sTeethJoint_M' % part, q=True, ws=True, t=True)
            positions['left_side1'] = [left_position[0], center_position[1], center_position[2]]
            positions['left_side2'] = [center_position[0] + (left_position[0] - center_position[0]) * 0.5,
                                       center_position[1],
                                       center_position[2] + (left_position[2] - center_position[2]) * 0.4]
            positions['center'] = [center_position[0], center_position[1],
                                   center_position[2] + (left_position[2] - center_position[2]) * 0.5]
            positions['right_side1'] = [right_position[0], center_position[1], center_position[2]]
            positions['right_side2'] = [center_position[0] + (right_position[0] - center_position[0]) * 0.5,
                                        center_position[1],
                                        center_position[2] + (right_position[2] - center_position[2]) * 0.4]

            for key, position in positions.items():
                joint_grp, ctrl_grp = add_single_ctr(part, key, position)
                if part == 'upper':
                    pntCtrl = 'ctrlMouth_M'
                if part == 'lower':
                    pntCtrl = 'ctrlPhonemes_M'

                parent.fitParent(joint_grp, '%sTeethJoint_M' % part)
                parent.fitParent(ctrl_grp, '%sTeeth_M' % part)

            parentConstraints = cmds.listRelatives('%sTeethJoint_M' % part, type='parentConstraint')
            if parentConstraints:
                for constraint in parentConstraints:
                    parentList = cmds.parentConstraint(constraint, query=True, targetList=True)
                    for parentNode in parentList:
                        if parentNode == '%sTeeth_M'%part:
                            jntGrp = '%sTeethJoint_M_TraGrp'% part
                            if not cmds.objExists(jntGrp):
                                cmds.createNode('transform', n=jntGrp)
                                cmds.delete(cmds.parentConstraint('%sTeethJoint_M' % part, jntGrp))
                                cmds.parent(jntGrp, cmds.listRelatives('%sTeethJoint_M' % part, p=1)[0])
                                cmds.parent('%sTeethJoint_M' % part, jntGrp)

                                cmds.delete(constraint)
                                ctrlMouth_MPnt = cmds.xform(pntCtrl, q=1, ws=1, t=1)
                                cmds.xform('%sTeethOffset_M'%part, ws=1, t=[ctrlMouth_MPnt[0],ctrlMouth_MPnt[1],ctrlMouth_MPnt[2]])

                                cmds.parentConstraint('%sTeeth_M' % part,jntGrp,mo =1)


        #移出舌头控制器
        for v in [0,1,2,3]:
            jnt = 'Tongue%sJoint_M'%v
            parentConstraints = cmds.listRelatives(jnt, type=['parentConstraint','pointConstraint','orientConstraint'])
            if parentConstraints:
                for constraint in parentConstraints:
                    parentList = cmds.parentConstraint(constraint, query=True, targetList=True)
                    for parentNode in parentList:
                        if parentNode == 'Tongue%s_M'%v:
                            cmds.delete(constraint)
        ctrlMouth_MPnt = cmds.xform('ctrlMouth_M', q=1, ws=1, t=1)
        ctrlPhonemes_M_MPnt = cmds.xform('ctrlPhonemes_M', q=1, ws=1, t=1)
        TonguePnt = [ctrlMouth_MPnt[0], (ctrlMouth_MPnt[1] + ctrlPhonemes_M_MPnt[1]) * 0.5, ctrlMouth_MPnt[2]]
        cmds.xform('Tongue0Offset_M', ws=1, t=TonguePnt)
        for v in [0, 1, 2, 3]:
            ctrl = 'Tongue%s_M'%v
            jnt= 'Tongue%sJoint_M'%v
            jntGrp = cmds.listRelatives(jnt,p =1)[0]
            cmds.xform(jntGrp,ws =1,t = cmds.xform(jnt,ws =1,t =1,q =1))
            cmds.xform(jntGrp, ws=1, ro=cmds.xform(jnt, ws=1, ro=1, q=1))
            cmds.xform(jntGrp,  s=cmds.xform(jnt, s=1, q=1))
            try:
                cmds.setAttr(jnt+'.t',0,0,0)
                cmds.setAttr(jnt + '.r', 0, 0, 0)
                cmds.setAttr(jnt + '.s', 1, 1, 1)
            except:
                pass
            if v != 0:
                cmds.connectAttr('%s.t' % ctrl, '%s.t' % jnt, f=1)
                cmds.connectAttr('%s.r' % ctrl, '%s.r' % jnt, f=1)
            else:
                cmds.parentConstraint(ctrl, jnt, mo=1)
                #cmds.orientConstraint(ctrl, jnt, mo=1)
            cmds.scaleConstraint(ctrl,jnt,mo =1)
            # cmds.orientConstraint(ctrl,jnt,mo =1)



    def eye_iris_correct(self):
        # 当前版本暂时未发现问题
        pass

    def do_facial_correct(self):
        self.eye_brow_inner_correct()
        self.eye_region_correct()
        self.lip_region_correct()
        self.smile_pull_correct()
        self.add_teeth_ctrls()
        if cmds.objExists('ctrlBoxOffset'):
            cmds.setAttr('ctrlBoxOffset.v', False)
        self.eye_iris_correct()

def chr_correct(**kwargs):
    rig = None
    '''if cmds.objExists('TSM3_root'):
        rig = TSM3Rigging(**kwargs)'''
    if cmds.objExists('FitSkeleton') and cmds.objExists('Main'):
        rig = AdvRigging(**kwargs)
    if rig:
        rig.correct()
    return rig


def correct(**kwargs):
    """
    根据场景信息，判断资产类型和修正方案，并执行修正
    :param kwargs: 修正参数
    :return:
    """
    chr_correct(**kwargs)































































