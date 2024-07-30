# -*- coding: utf-8 -*-


from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(384, 206)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.status_tag = QtWidgets.QLabel(Form)
        self.status_tag.setMinimumSize(QtCore.QSize(100, 0))
        self.status_tag.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.status_tag.setObjectName("status_tag")
        self.horizontalLayout_4.addWidget(self.status_tag)
        self.status_label = QtWidgets.QLabel(Form)
        self.status_label.setObjectName("status_label")
        self.horizontalLayout_4.addWidget(self.status_label)
        self.horizontalLayout_4.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.current_version_tag = QtWidgets.QLabel(Form)
        self.current_version_tag.setMinimumSize(QtCore.QSize(100, 0))
        self.current_version_tag.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.current_version_tag.setObjectName("current_version_tag")
        self.horizontalLayout_3.addWidget(self.current_version_tag)
        self.current_version_label = QtWidgets.QLabel(Form)
        self.current_version_label.setText("")
        self.current_version_label.setObjectName("current_version_label")
        self.horizontalLayout_3.addWidget(self.current_version_label)
        self.horizontalLayout_3.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.released_data_tag = QtWidgets.QLabel(Form)
        self.released_data_tag.setMinimumSize(QtCore.QSize(100, 0))
        self.released_data_tag.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.released_data_tag.setObjectName("released_data_tag")
        self.horizontalLayout_5.addWidget(self.released_data_tag)
        self.released_data_label = QtWidgets.QLabel(Form)
        self.released_data_label.setObjectName("released_data_label")
        self.horizontalLayout_5.addWidget(self.released_data_label)
        self.horizontalLayout_5.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.sep_line = QtWidgets.QFrame(Form)
        self.sep_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.sep_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.sep_line.setObjectName("sep_line")
        self.verticalLayout.addWidget(self.sep_line)
        self.gotoUpdatePage_btn = QtWidgets.QPushButton(Form)
        self.gotoUpdatePage_btn.setMinimumSize(QtCore.QSize(140, 23))
        self.gotoUpdatePage_btn.setObjectName("gotoUpdatePage_btn")
        self.verticalLayout.addWidget(self.gotoUpdatePage_btn)
        spacerItem = QtWidgets.QSpacerItem(20, 53, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.autoUpdate_chb = QtWidgets.QCheckBox(Form)
        self.autoUpdate_chb.setChecked(True)
        self.autoUpdate_chb.setObjectName("autoUpdate_chb")
        self.horizontalLayout_2.addWidget(self.autoUpdate_chb)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.close_btn = QtWidgets.QPushButton(Form)
        self.close_btn.setMinimumSize(QtCore.QSize(75, 23))
        self.close_btn.setObjectName("close_btn")
        self.horizontalLayout_2.addWidget(self.close_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.status_tag.setText(QtWidgets.QApplication.translate("Form", "Status :", None, -1))
        self.status_label.setText(QtWidgets.QApplication.translate("Form", "Update available", None, -1))
        self.current_version_tag.setText(QtWidgets.QApplication.translate("Form", "Current version :", None, -1))
        self.released_data_tag.setText(QtWidgets.QApplication.translate("Form", "Update available :", None, -1))
        self.released_data_label.setText(QtWidgets.QApplication.translate("Form", "2.0.34, released on 14 February, 2021", None, -1))
        self.gotoUpdatePage_btn.setText(QtWidgets.QApplication.translate("Form", "go to update page", None, -1))
        self.autoUpdate_chb.setText(QtWidgets.QApplication.translate("Form", "Automatically check for updates", None, -1))
        self.close_btn.setText(QtWidgets.QApplication.translate("Form", "Close", None, -1))

