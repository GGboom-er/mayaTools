# -*- coding: utf-8 -*-
#!/usr/bin/env python
__author__ = 'yangzhuo'
import sys,os
import time


def checkModulePath():
    MODULE_PATHS = [r'C:\Python27\Lib\site-packages','P:\pipeline\ppas',
                    r'P:\Maya\Modules\Modules_Public\pipeline\scripts',
                    r'P:\Maya\Modules\Modules_Public\pipeline\scripts\ppas_layout_tool',
                    r'P:\Maya\Modules\Modules_Public\pipeline\scripts\ppas_layout_tool\ppstools\cgtw_',
                    r'P:\Maya\Modules\Modules_Public\pipeline\scripts\ppas_layout_tool\ppstools']
    for path in MODULE_PATHS:
        if path not in sys.path:
            sys.path.append(path)

checkModulePath()
from functools import partial
from dayu_widgets.qt import *
from dayu_widgets.label import MLabel
from dayu_widgets.combo_box import MComboBox
from dayu_widgets.progress_bar import MProgressBar
from dayu_widgets import dayu_theme, MItemViewFullSet, MPushButton, MMenu
from dayu_widgets.item_view import MTableView
from dayu_widgets.item_model import MTableModel, MSortFilterModel
from dayu_path import DayuPath

ani_root = r'X:\Project\{project}\pub\lgt_comp'



class SuccessMessageBox(QMessageBox):
    def __init__(self, msg, parent=None):
        super(SuccessMessageBox, self).__init__(parent)
        self.setWindowTitle(self.tr('Success'))
        self.setText('<span style="font-size:18px;color:#ddd">' + self.tr('Congratulations') + '</span>')
        self.setInformativeText('<span style="font-size:16px;color:#888">' + msg + '</span>')
        self.setStandardButtons(QMessageBox.Ok)


class AssembleWidget(QDialog):
    def __init__(self, parent=None):
        super(AssembleWidget, self).__init__(parent=parent)

        self.setObjectName('AssembleWidget')
        self.project_box = MComboBox()
        self.project_box.setMaximumWidth(134)
        project_list = getProjectList()
        self.project_box.addItems(project_list)
        self.project_box.currentIndexChanged.connect(self.slot_get_shot)

        self.assetType_box = MComboBox()
        self.assetType_box.setMaximumWidth(134)
        self.assetType_box.addItems(['chr', 'prp'])
        self.assetType_box.currentIndexChanged.connect(self.slot_get_shot)


        choose_lay = QHBoxLayout()
        choose_lay.addWidget(MLabel('Choose Project: ').strong().secondary())
        choose_lay.addWidget(self.project_box)
        choose_lay.addSpacing(10)

        choose_lay.addWidget(MLabel('Choose assetType: ').strong().secondary())
        choose_lay.addWidget(self.assetType_box)
        choose_lay.addSpacing(10)
        choose_lay.addStretch()

        select_all_btn = MPushButton('Select All')
        select_all_btn.setMaximumWidth(180)
        select_all_btn.clicked.connect(partial(self.select_data, 'all'))

        invert_select_btn = MPushButton('Invert Select')
        invert_select_btn.setMaximumWidth(180)
        invert_select_btn.clicked.connect(partial(self.select_data, 'invert'))

        select_none_btn = MPushButton('Select None')
        select_none_btn.setMaximumWidth(180)
        select_none_btn.clicked.connect(partial(self.select_data, 'none'))

        btn_lay = QHBoxLayout()
        btn_lay.addWidget(select_all_btn)
        btn_lay.addWidget(invert_select_btn)
        btn_lay.addWidget(select_none_btn)

        header_list = [
            {"key": "shot1", "label": "", 'checkable': True, 'searchable': True, 'color': dayu_theme.warning_color},
            {"key": "shot2", "label": "", 'checkable': True, 'searchable': True, 'color': dayu_theme.warning_color},
            {"key": "shot3", "label": "", 'checkable': True, 'searchable': True, 'color': dayu_theme.warning_color},
            {"key": "shot4", "label": "", 'checkable': True, 'searchable': True, 'color': dayu_theme.warning_color},
            {"key": "shot5", "label": "", 'checkable': True, 'searchable': True, 'color': dayu_theme.warning_color},
            {"key": "shot6", "label": "", 'checkable': True, 'searchable': True, 'color': dayu_theme.warning_color},
            {"key": "shot7", "label": "", 'checkable': True, 'searchable': True, 'color': dayu_theme.warning_color}
        ]
        self.source_model = MTableModel()
        self.source_model.set_header_list(header_list)
        self.model_sort = MSortFilterModel()
        self.model_sort.set_header_list(header_list)
        self.model_sort.setSourceModel(self.source_model)

        self.item_view = MTableView()
        self.item_view.setModel(self.model_sort)
        self.item_view.enable_context_menu(True)
        self.item_view.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.item_view.sig_context_menu.connect(self.slot_context_menu)
        self.item_view.set_header_list(header_list)

        open_btn = MPushButton(u'Open File')
        run_btn = MPushButton(u'Run')

        #open_btn.clicked.connect(self.slot_open)
        run_btn.clicked.connect(self.slot_run)

        run_lay = QHBoxLayout()
        run_lay.addWidget(open_btn)
        run_lay.addWidget(run_btn)

        self.progress = MProgressBar()
        self.progress.setValue(0)
        progress_lay = QHBoxLayout()
        progress_lay.addWidget(MLabel('Pack File Progress: ').warning().strong())
        progress_lay.addWidget(self.progress)

        main_lay = QVBoxLayout()
        main_lay.addLayout(choose_lay)
        main_lay.addLayout(btn_lay)
        main_lay.addWidget(self.item_view)
        main_lay.addLayout(progress_lay)
        main_lay.addLayout(run_lay)
        self.resize(999, 888)
        self.setLayout(main_lay)
        dayu_theme.apply(self)
        self.slot_get_shot()
        self.project_box.setCurrentIndex(self.project_box.findText('cat11'))

    def slot_context_menu(self, event):
        if event.selection:
            context_menu = MMenu(parent=self)
            view_action = context_menu.addAction('Select')
            view_action.setIcon(MIcon('success_line.svg'))
            view_action.triggered.connect(partial(self.slot_select_shot, event))
            context_menu.exec_( QCursor.pos() )


    def slot_get_shot(self):
        project = self.project_box.currentText()
        assetType = self.assetType_box.currentText()
        if project and assetType:

            assertList = getAssetList(project, assetType)
            new_shot_list = self.split_list_by_len(list(sorted(set(assertList))), 7)
            result = []
            for x in sorted(new_shot_list):
                temp_dict = {}
                for index, shot in enumerate(x):
                    temp_dict.setdefault('shot{}'.format(index + 1), shot)
                result.append(temp_dict)
            self.source_model.set_data_list(result)
        # self.source_model.get_data_list()
        # self.item_view.set(result)
        self.item_view.header_view.resizeSections(QHeaderView.ResizeToContents)

    @staticmethod
    def split_list_by_len(list_collection, len_):
        """
        将集合均分，每份n个元素
        :param list_collection:
        :param len_:
        :return:返回的结果为评分后的每份可迭代对象
        """
        for x in range(0, len(list_collection), len_):
            yield list_collection[x: x + len_]


    def select_data(self, type_):
        """
        选择模式 全选 反选  不选
        :return:
        """
        result = self.source_model.get_data_list()
        if type_ == 'all':
            for x in result:
                new_x = {'{}'.format(shot).split('_checked')[0]+'_checked': 2 for shot, state in x.items() if 'shot' in shot}
                x.update(new_x)
        elif type_ == 'none':
            for x in result:
                new_x = {'{}'.format(shot).split('_checked')[0]+'_checked': 0 for shot, state in x.items() if 'shot' in shot}
                x.update(new_x)
        elif type_ == 'invert':
            for x in result:
                temp_dict = {}
                for shot, state in x.items():
                    if ('shot' in shot and 'checked' in shot) or 'shot' not in shot:
                        continue
                    now = x.get('{}_checked'.format(shot))
                    new = 2 if not now else 0
                    temp_dict.setdefault('{}_checked'.format(shot), new)
                x.update(temp_dict)

    def get_shot_list(self):
        # 进行数据处理 将用户选中的镜头
        shot_list = []
        for x in self.source_model.get_data_list():
            for shot, state in x.items():
                if 'shot' in shot and 'checked' in shot:
                    if state == 2:
                        shot_list.append(x.get(shot.split('_')[0]))
        return list(sorted(shot_list))

    def slot_run(self, action=None):
        """
        预留的接口  对应 Run 按钮
        :return:
        """

        project = self.project_box.currentText()
        assetType = self.assetType_box.currentText()
        assetList = self.get_shot_list()
        if project and assetType and assetList:
            create_BAT_test(project,assetType,assetList)
        SuccessMessageBox('Success!', parent=self).exec_()
def getProjectList():
    """
    # 获取所有项目列表
    :return: cgtw中所有的项目列表
    """
    try:
        #result = [p.get('project.entity') for p in util.get_project()]
        result = [p.name for p in DayuPath(r'X:\Project').listdir() if os.path.exists(ani_root.format(project=p.name))]
    except Exception as e:
        print(e)
        result = []

    return result

def getAssetList(project, assetType):
    """
    # 根据项目，资产类型获取所有对应的资产列表
    :param project: 项目
    :param assetType: 资产类型
    :return: 对应的资产列表
    """
    try:
        result = os.listdir(r'X:\Project\%s\pub\rig\rig_asset\%s'%(project,assetType))
        return result
    except Exception as e:
        print(e)
    return []
def create_BAT_test(project,assetType,assetList):
    selfPath = os.getcwd()
    mayaPyPath = r'C:\Program Files\Autodesk\Maya2018\bin\mayapy.exe'
    cmdPath = selfPath+'/testCacheFn.py'
    cmdName = '/testCacheCmd.bat'
    command = '"%s" %s %s %s %s' % (mayaPyPath, cmdPath, project, assetType, ' '.join(assetList))
    with open(selfPath + cmdName, 'w') as f:
        f.write(command)
    os.system("cmd.exe /c" + selfPath + cmdName)
    return command

def run():
    import sys
    try:
        QApplication(sys.argv)
    except:
        pass
    from dayu_widgets import dayu_theme
    win = AssembleWidget()
    dayu_theme.apply(win)
    win.show()
    win.exec_()
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    test = AssembleWidget()
    dayu_theme.apply(test)
    test.show()
    sys.exit(app.exec_())
