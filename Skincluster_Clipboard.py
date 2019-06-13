# -*- coding: utf-8 -*-

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from maya.app.general import mayaMixin
from maya import OpenMayaUI as omui
import maya.cmds as mc
import shiboken2

class SkinclusterClipboard(mayaMixin.MayaQWidgetBaseMixin, QMainWindow):
    def __init__(self, parent=None):
        super(SkinclusterClipboard, self).__init__(parent)
        self.setWindowTitle("Skincluster_Clipboard")
        self.resize(150, 100)

        self.window = QWidget()
        self.setCentralWidget(self.window)

        self.layout = QVBoxLayout(self.window)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.window.setLayout(self.layout)

        self._selectvtx()
        self._buttonGp()
        self._dividePercentage()
        self._modeButton()

    def _selectvtx(self):
        self.selItem = QWidget()
        self.srcLay = QHBoxLayout(self.selItem)
        self.srcLay.setContentsMargins(5, 0, 5, 0)
        self.selItem.setLayout(self.srcLay)
        self.layout.addWidget(self.selItem)

        self.srctxt = QLabel('source:')
        self.srcFld = QSpinBox(self.selItem)
        self.srcFld.setEnabled(False)
        self.srcFld.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.srcLay.addWidget(self.srctxt)
        self.srcLay.addWidget(self.srcFld)

    def _buttonGp(self):
        self.butItem = QWidget()
        self.butLay = QVBoxLayout(self.butItem)
        self.butLay.setContentsMargins(5, 0, 5, 0)
        self.butItem.setLayout(self.butLay)
        self.layout.addWidget(self.butItem)

        self.copyBut = QPushButton('Copy')
        self.pasteBut = QPushButton('Paste')
        self.blendBut = QPushButton('Blend')

        self.copyBut.clicked.connect(self._copy)
        self.pasteBut.clicked.connect(self._paste)
        self.blendBut.clicked.connect(self._blend)

        self.butLay.addWidget(self.copyBut)
        self.butLay.addWidget(self.pasteBut)
        self.butLay.addWidget(self.blendBut)

    def _dividePercentage(self):
        self.divItem = QWidget()
        self.divLay = QHBoxLayout(self.divItem)
        self.divLay.setContentsMargins(5, 0, 5, 0)
        self.divItem.setLayout(self.divLay)
        self.layout.addWidget(self.divItem)

        self.divFld = QSpinBox(self.divItem)
        self.divFld.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.divFld.setRange(0, 100)
        self.divLay.addWidget(self.divFld)

    def _modeButton(self):
        self.modeItem = QWidget()
        self.modeLay = QHBoxLayout(self.modeItem)
        self.modeLay.setContentsMargins(5, 0, 5, 0)
        self.modeItem.setLayout(self.modeLay)
        self.layout.addWidget(self.modeItem)

        self.recBut = QRadioButton('Rec')
        self.FirstBut = QRadioButton('1st')
        self.FirstBut.toggle()

        self.radGp = QButtonGroup()
        self.radGp.addButton(self.recBut, 1)
        self.radGp.addButton(self.FirstBut, 2)

        self.modeLay.addWidget(self.recBut)
        self.modeLay.addWidget(self.FirstBut)
        self.modeItem.setLayout(self.modeLay)

    def _copy(self):
        self.inf = []
        self.src_lst = mc.ls(os=True, fl=True)
        self.srcFld.setValue(len(self.src_lst))

    def _paste(self):
        self.mode = True
        self.chk = self.recBut.isChecked()
        self._targetSelect()
        self._modeCheck()
        self._skinpaint()

    def _blend(self):
        self.chk = self.recBut.isChecked()
        self.div = self.divFld.value() * 0.01

        self.mode = False
        self._targetSelect()
        self._modeCheck()
        self._skinpaint()

    def _targetSelect(self):
        self.tgt_lst = mc.ls(os=True, fl=True)

    def _skinpaint(self):
        for i in range(len(self.tgt_lst)):
            mc.skinPercent(self.src_skn[0], self.tgt_lst[i], tv=self.inf[i][self.tgt_lst[i]])
        self.inf = []

    def _modeCheck(self):
        if self.chk is True:
            self._infRecList()
        else:
            self._infFstList()

    def _infFstList(self):
        tmpd = {}
        for i in range(len(self.tgt_lst)):
            self.val = []
            src = self.src_lst[0]
            src_obj = src.split('.')
            temp = mc.connectionInfo('{}.inMesh'.format(src_obj[0]), sfd=True)
            self.src_skn = temp.split('.')
            self.src_jnt = mc.skinCluster(self.src_lst[0], q=True, inf=True)
            self.src_wgt = mc.skinPercent(self.src_skn[0], self.src_lst[0], q=True, v=True)

            if self.mode is True:
                for j in range(len(self.src_jnt)):
                    temp = ('{}'.format(self.src_jnt[j]), self.src_wgt[j])
                    self.val.append(temp)

            else :
                self.div_jnt = []
                self.div_wgt = []
                tgt = self.tgt_lst[i]
                tgt_obj = tgt.split('.')
                temp = mc.connectionInfo('{}.inMesh'.format(tgt_obj[0]), sfd=True)
                self.tgt_skn = temp.split('.')
                self.tgt_jnt = mc.skinCluster(self.tgt_lst[i], q=True, inf=True)
                self.tgt_wgt = mc.skinPercent(self.tgt_skn[0], self.tgt_lst[i], q=True, v=True)
                self.div_jnt.append(self.src_jnt[0])

                if self.src_jnt[0] in self.tgt_jnt:
                    idx = self.tgt_jnt.index(self.src_jnt[0])
                    self.div_wgt.append(self.src_wgt[0] * self.div + self.tgt_wgt[idx] * (1.00 - self.div))
                else:
                    self.div_wgt.append(self.src_wgt[0] * self.div)

                for f in range(len(self.tgt_jnt)):
                    if self.tgt_jnt[f] not in self.div_jnt:
                        self.div_jnt.append(self.tgt_jnt[f])
                        self.div_wgt.append(self.tgt_wgt[f] * (1.00 - self.div))

                for f in range(len(self.div_jnt)):
                    temp = ('{}'.format(self.div_jnt[f]), self.div_wgt[f])
                    self.val.append(temp)
            
            tmpd[self.tgt_lst[i]] = self.val
            self.inf.append(tmpd)

    def _infRecList(self):
        tmpd = {}
        for i in range(len(self.tgt_lst)):
            self.val = []
            src = self.src_lst[i]
            src_obj = src.split('.')
            temp = mc.connectionInfo('{}.inMesh'.format(src_obj[0]), sfd=True)
            self.src_skn = temp.split('.')
            self.src_jnt = mc.skinCluster(self.src_lst[i], q=True, inf=True)
            self.src_wgt = mc.skinPercent(self.src_skn[0], self.src_lst[i], q=True, v=True)

            if self.mode is True:
                for j in range(len(self.src_jnt)):
                    temp = ('{}'.format(self.src_jnt[j]), self.src_wgt[j])
                    self.val.append(temp)

            else :
                self.div_jnt = []
                self.div_wgt = []
                tgt = self.tgt_lst[i]
                tgt_obj = tgt.split('.')
                temp = mc.connectionInfo('{}.inMesh'.format(tgt_obj[0]), sfd=True)
                self.tgt_skn = temp.split('.')
                self.tgt_jnt = mc.skinCluster(self.tgt_lst[i], q=True, inf=True)
                self.tgt_wgt = mc.skinPercent(self.tgt_skn[0], self.tgt_lst[i], q=True, v=True)

                for f in range(len(self.src_jnt)):
                    if self.src_jnt[f] in self.tgt_jnt:
                        idx = self.tgt_jnt.index(self.src_jnt[f])
                        self.div_jnt.append(self.src_jnt[f])
                        self.div_wgt.append(self.src_wgt[f] * self.div + self.tgt_wgt[idx] * (1.00 - self.div))
                    else:
                        self.div_jnt.append(self.src_jnt[f])
                        self.div_wgt.append(self.src_wgt[f] * self.div)

                for f in range(len(self.tgt_jnt)):
                    if self.tgt_jnt[f] not in self.div_jnt:
                        self.div_jnt.append(self.tgt_jnt[f])
                        self.div_wgt.append(self.tgt_wgt[f] * (1.00 - self.div))

                for f in range(len(self.div_jnt)):
                    temp = ('{}'.format(self.div_jnt[f]), self.div_wgt[f])
                    self.val.append(temp)

            tmpd[self.tgt_lst[i]] = self.val
            self.inf.append(tmpd)


def openSkinclusterClipboard(*args):
    for i in shiboken2.wrapInstance(long(omui.MQtUtil.mainWindow()), QMainWindow).findChildren(SkinclusterClipboard):
        i.close()

    if not mc.selectPref(q=True, tso=True):
        mc.selectPref(tso=True)

    SCB = SkinclusterClipboard()
    SCB.show()