# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt6 UI code generator 6.7.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 700)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.connectBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.connectBtn.setGeometry(QtCore.QRect(630, 10, 76, 30))
        self.connectBtn.setObjectName("connectBtn")
        # self.dataTable = QtWidgets.QTableView(parent=self.centralwidget)
        # self.dataTable.setGeometry(QtCore.QRect(20, 50, 850, 550))
        # self.dataTable.setObjectName("dataTable")
        self.textBrowser = QtWidgets.QTextBrowser(parent=self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(720, 10, 150, 30))
        self.textBrowser.setObjectName("textBrowser")
        self.splitter = QtWidgets.QSplitter(parent=self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(21, 10, 230, 30))
        self.splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter.setObjectName("splitter")
        self.label = QtWidgets.QLabel(parent=self.splitter)
        self.label.setObjectName("label")
        self.ipaddInput = QtWidgets.QTextEdit(parent=self.splitter)
        self.ipaddInput.setObjectName("ipaddInput")
        self.splitter_2 = QtWidgets.QSplitter(parent=self.centralwidget)
        self.splitter_2.setGeometry(QtCore.QRect(267, 10, 90, 30))
        self.splitter_2.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.label_2 = QtWidgets.QLabel(parent=self.splitter_2)
        self.label_2.setObjectName("label_2")
        self.portInput = QtWidgets.QTextEdit(parent=self.splitter_2)
        self.portInput.setObjectName("portInput")
        self.splitter_3 = QtWidgets.QSplitter(parent=self.centralwidget)
        self.splitter_3.setGeometry(QtCore.QRect(390, 10, 170, 30))
        self.splitter_3.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter_3.setObjectName("splitter_3")
        self.label_3 = QtWidgets.QLabel(parent=self.splitter_3)
        self.label_3.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.label_3.setObjectName("label_3")
        self.rateInput = QtWidgets.QTextEdit(parent=self.splitter_3)
        self.rateInput.setObjectName("rateInput")
        self.addBtn = QtWidgets.QToolButton(parent=self.centralwidget)
        self.addBtn.setGeometry(QtCore.QRect(760, 620, 26, 25))
        icon = QtGui.QIcon.fromTheme("list-add")
        self.addBtn.setIcon(icon)
        self.addBtn.setObjectName("addBtn")
        self.removeBtn = QtWidgets.QToolButton(parent=self.centralwidget)
        self.removeBtn.setGeometry(QtCore.QRect(800, 620, 26, 25))
        icon = QtGui.QIcon.fromTheme("list-remove")
        self.removeBtn.setIcon(icon)
        self.removeBtn.setObjectName("removeBtn")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.connectBtn.setText(_translate("MainWindow", "Connect"))
        self.label.setText(_translate("MainWindow", "IP Address"))
        self.label_2.setText(_translate("MainWindow", "Port"))
        self.label_3.setText(_translate("MainWindow", "Sampling [s]"))
        self.addBtn.setText(_translate("MainWindow", "..."))
        self.removeBtn.setText(_translate("MainWindow", "..."))
