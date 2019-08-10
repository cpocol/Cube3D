#author: Ciprian Pocol

import sys
import random
import math

from PySide2.QtCore import QPoint, QTimer
from PySide2 import QtWidgets
from PySide2.QtWidgets import QApplication, QPushButton, QWidget, QMainWindow, QGridLayout
from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.QtGui import QVector3D, QMatrix4x4, QColor, QMouseEvent

class Cube(Qt3DCore.QEntity):
    def __init__(self, parentEntity):
        super(Cube, self).__init__()

        # build the cube
        side = 15
        self.cubeEntity = Qt3DCore.QEntity(parentEntity)

        # init params of the 6 planes
        planeTranslations = [[      0, -side/2, 0],
                             [      0, +side/2, 0],
                             [-side/2,       0, 0],
                             [+side/2,       0, 0],
                             [      0,       0, -side/2],
                             [      0,       0, +side/2]]
        planeRotations = [[  0,  0, 180],
                          [  0,  0,   0],
                          [  0,  0,  90],
                          [  0,  0, 270],
                          [270,  0,   0],
                          [ 90,  0,   0]]

        # allocate planes
        self.planeEntities   = [None for i in range(6)]
        self.planeMeshes     = [None for i in range(6)]
        self.planeTransforms = [None for i in range(6)]
        self.materials       = [None for i in range(6)]

        # build the planes
        for i in range(0, 6):
            self.planeMeshes[i] = Qt3DExtras.QPlaneMesh()
            self.planeMeshes[i].setWidth(side)
            self.planeMeshes[i].setHeight(side)

            self.planeTransforms[i] = Qt3DCore.QTransform()
            self.planeTransforms[i].setRotationX(planeRotations[i][0])
            self.planeTransforms[i].setRotationY(planeRotations[i][1])
            self.planeTransforms[i].setRotationZ(planeRotations[i][2])
            self.planeTransforms[i].setTranslation(QVector3D(planeTranslations[i][0], planeTranslations[i][1], planeTranslations[i][2]))

            self.materials[i] = Qt3DExtras.QPhongMaterial(self.cubeEntity)
            self.materials[i].setAmbient(QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

            self.planeEntities[i] = Qt3DCore.QEntity(self.cubeEntity)
            self.planeEntities[i].addComponent(self.planeMeshes[i])
            self.planeEntities[i].addComponent(self.planeTransforms[i])
            self.planeEntities[i].addComponent(self.materials[i])

        #initial rotation
        self.yaw = -15
        self.pitch = 15
        self.yawSpeed = 0
        self.pitchSpeed = 0
        self.cubeTransform = Qt3DCore.QTransform()
        self.cubeEntity.addComponent(self.cubeTransform)
        self.rotate(0, 0) #trigger the computation of the rotation matrix for the initial rotation

    def rotate(self, dx, dy):
        #Variant1: default rotation order - rotate around X then around Y
        #newYaw   = self.cubeTransform.rotationY() + dx/4
        #newPitch = self.cubeTransform.rotationX() + dy/4
        #self.cubeTransform.setRotationX(newPitch)
        #self.cubeTransform.setRotationY(newYaw)

        #Variant2: custom rotation order - rotate around Y then around X
        self.yaw   += dx
        self.pitch += dy
        a = self.yaw*3.14/180
        yawMat = QMatrix4x4(math.cos(a),    0, math.sin(a),    0,
                                      0,    1,           0,    0,
                           -math.sin(a),    0, math.cos(a),    0,
                                      0,    0,           0,    1)
        a = self.pitch*3.14/180
        pitchMat = QMatrix4x4(1,           0,            0,    0,
                              0, math.cos(a), -math.sin(a),    0,
                              0, math.sin(a),  math.cos(a),    0,
                              0,           0,            0,    1)
        rotMat = pitchMat*yawMat
        self.cubeTransform.setMatrix(rotMat)


class Cube3DWindow(Qt3DExtras.Qt3DWindow):
    cube = None
    mouseDist = None

    def onTimer(self):
        if self.cube.yawSpeed == 0 and self.cube.pitchSpeed == 0:
            self.timer.stop()
        else:
            if self.cube.yawSpeed >= 1:
                self.cube.yawSpeed -= 1
            elif self.cube.yawSpeed <= -1:
                self.cube.yawSpeed += 1
            else:
                self.cube.yawSpeed = 0

            if self.cube.pitchSpeed >= 1:
                self.cube.pitchSpeed -= 1
            elif self.cube.pitchSpeed <= -1:
                self.cube.pitchSpeed += 1
            else:
                self.cube.pitchSpeed = 0

            self.cube.rotate(self.cube.yawSpeed, self.cube.pitchSpeed)

    def __init__(self):
        super(Cube3DWindow, self).__init__()

        # Root entity
        self.rootEntity = Qt3DCore.QEntity()
        self.setRootEntity(self.rootEntity)

        # Camera
        self.camera().lens().setPerspectiveProjection(45, 16 / 9, 0.1, 1000)
        self.camera().setPosition(QVector3D(0, 0, 40))
        self.camera().setViewCenter(QVector3D(0, 0, 0))

        self.mouseLastPos = QPoint()
        self.mouseDown = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.onTimer)

    def addCube(self):
        self.cube = Cube(self.rootEntity)

    def mouseMoveEvent(self, event):
        if self.cube is not None:
            self.mousePos = event.pos()
            if self.mouseDown :
                self.timer.stop()
                if self.mousePos != self.mouseLastPos :
                    self.mouseDist = self.mousePos - self.mouseLastPos
                    self.cube.rotate(self.mouseDist.x()/10, self.mouseDist.y()/10)
                    self.mouseLastPos = self.mousePos

    def mousePressEvent(self, event):
        if self.cube is not None:
            self.mouseDown = True
            self.mouseLastPos = event.pos()
            self.timer.stop()

    def mouseReleaseEvent(self, event):
        if self.cube is not None:
            self.mouseDown = False
            if self.mouseDist is not None:
                self.cube.yawSpeed   = self.mouseDist.x()
                self.cube.pitchSpeed = self.mouseDist.y()
            self.timer.start(20)


class MainWindow(QMainWindow):
    button = None

    def addCubeButtonPressed(self):
        self.button.setEnabled(False)
        self.window3D.addCube()

    def __init__(self):
        super(MainWindow, self).__init__()

        self.window3D = Cube3DWindow()
        self.widget3D = self.createWindowContainer(self.window3D)  # QWidget* QWidget::createWindowContainer()

        self.button = QPushButton("Add Cube")
        self.button.clicked.connect(self.addCubeButtonPressed)
        self.central_widget = QWidget()
        self.central_widget_layout = QGridLayout()
        self.central_widget_layout.addWidget(self.button, 0, 1, 1, 1)
        self.central_widget_layout.addWidget(self.widget3D, 1, 0, 2, 3)
        self.central_widget.setLayout(self.central_widget_layout)
        self.resize(700, 700)
        self.setWindowTitle("Application")
        self.show()
        self.setCentralWidget(self.central_widget) #call it after show(), in order to avoid "QOpenGLContext::swapBuffers() called with non-exposed window, behavior is undefined"


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    mainWin = MainWindow()

    #sys.exit(app.exec_())
    app.exec_()
