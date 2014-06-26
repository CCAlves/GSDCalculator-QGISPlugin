# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_terraindatamanipulator.ui'
#
# Created: Thu Apr 03 10:49:21 2014
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_TerrainDataManipulator(object):
    def setupUi(self, TerrainDataManipulator):
        TerrainDataManipulator.setObjectName(_fromUtf8("TerrainDataManipulator"))
        TerrainDataManipulator.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(TerrainDataManipulator)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(TerrainDataManipulator)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TerrainDataManipulator.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TerrainDataManipulator.reject)
        QtCore.QMetaObject.connectSlotsByName(TerrainDataManipulator)

    def retranslateUi(self, TerrainDataManipulator):
        TerrainDataManipulator.setWindowTitle(_translate("TerrainDataManipulator", "TerrainDataManipulator", None))

