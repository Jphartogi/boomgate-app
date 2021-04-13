# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form.ui'
#
# Created by: PyQt5 UI code generator 5.15.3
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(640, 132)
        Form.setMinimumSize(QtCore.QSize(640, 132))
        Form.setStyleSheet("QLabel{\n"
"    font: bold 10pt \"Open Sans\";\n"
"    color: #353942;\n"
"}\n"
"\n"
"QPushButton{\n"
"    font: 8pt \"Open Sans\";\n"
"    color: #353942;\n"
"}\n"
"\n"
"QComboBox{\n"
"    font: 8pt \"Open Sans\";\n"
"    color: #353942;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(Form)
        self.centralwidget.setObjectName("centralwidget")
        self.formLayout_2 = QtWidgets.QFormLayout(self.centralwidget)
        self.formLayout_2.setObjectName("formLayout_2")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_camera = QtWidgets.QLabel(self.centralwidget)
        self.label_camera.setObjectName("label_camera")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_camera)
        self.line_camera = QtWidgets.QLineEdit(self.centralwidget)
        self.line_camera.setObjectName("line_camera")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.line_camera)
        self.label_gate = QtWidgets.QLabel(self.centralwidget)
        self.label_gate.setObjectName("label_gate")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_gate)
        self.line_gate = QtWidgets.QLineEdit(self.centralwidget)
        self.line_gate.setObjectName("line_gate")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.line_gate)
        self.label_port = QtWidgets.QLabel(self.centralwidget)
        self.label_port.setObjectName("label_port")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_port)
        self.line_port = QtWidgets.QLineEdit(self.centralwidget)
        self.line_port.setObjectName("line_port")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.line_port)
        self.formLayout_2.setLayout(0, QtWidgets.QFormLayout.SpanningRole, self.formLayout)
        self.button_enter = QtWidgets.QPushButton(self.centralwidget)
        self.button_enter.setMinimumSize(QtCore.QSize(0, 30))
        self.button_enter.setObjectName("button_enter")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.button_enter)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setMinimumSize(QtCore.QSize(209, 30))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.comboBox)
        Form.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(Form)


# class Form(QForm):
#     def __init__(self):
#         super().__init__()

#         self.ui = Ui_Form()
#         self.ui.setupUi(self)
#         self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

#         self.data = json.load(f)
        
#         self.ui.line_camera.setText(self.data["camera_address"])
#         self.ui.line_gate.setText(self.data["gate_address"])
#         self.ui.line_port.setText(self.data["port_address"])

#         self.ui.button_enter.clicked.connect(self.close)

# if __name__ == "__main__":
#     application = QApplication(sys.argv)
#     Form = Form()
#     Form.show()
#     sys.exit(application.exec_())