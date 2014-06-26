# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TerrainDataManipulator
                                 A QGIS plugin
 TerrainDataManipulator
                              -------------------
        begin                : 2014-04-03
        copyright            : (C) 2014 by Sensormap
        email                : TerrainDataManipulator@TerrainDataManipulator
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from Includes import *
from ControlModel import *
from GSDCalcModel import *
from WebModel import *

class TerrainDataManipulator:

    def __init__(self, iface):
 
        self.iface = iface
 
        self.fileDir = os.path.dirname(os.path.realpath(__file__)) 
        self.fileDir = self.fileDir.replace("\\","/")
        self.fileDir = self.fileDir.replace(" ","")
        
        import win32api
        self.tempDir = win32api.GetLongPathName(self.fileDir)
        self.tempDir = self.tempDir + "/__RasterCache__/Temp/"
 
        path = os.path.dirname( os.path.abspath(__file__) ) + "/__TDMSettings__.ini"
        self.settings = QtCore.QSettings( path, QtCore.QSettings.IniFormat)
        
        self.controlModel = ControlModel(self.iface,100)
        self.gsdCalcModel = GSDCalcModel(self.iface)
        self.webModel = WebModel(self.iface)
 
        self.canvas = self.iface.mapCanvas()
        self.canvas.enableAntiAliasing(True)
        self.canvas.setCanvasColor(QtCore.Qt.white) 
        
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        self.canvas.setMapTool(self.clickTool)
        
        path = os.path.dirname( os.path.abspath(__file__) )
        self.dock = uic.loadUi( os.path.join( path, "EDMDockWidgetForm.ui" ) )

        self.elevLEdit = QtGui.QLineEdit(None)
        self.elevLEdit.setText("0.000000 m")
        self.elevLEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.elevLEdit.setGeometry(QtCore.QRect(0, self.dock.height() - 20,self.dock.width(),20))
        self.elevLEdit.setParent(self.dock)
        self.elevLEdit.show()

        self.dock.setWidget(self.elevLEdit)
        
        self.CSC = False
        self.FST = True

        QtCore.QObject.connect(self.canvas,QtCore.SIGNAL("mapCanvasRefreshed()"), self.controlModel.updateLayersColouring)
        QtCore.QObject.connect(self.canvas, QtCore.SIGNAL("xyCoordinates(const QgsPoint)"), self.handleMouseMove)
        
        #QtCore.QObject.connect(self.gsdCalcModel, QtCore.SIGNAL("espChanged(float)"), self.test) 

    def initGui(self):
        # Create action that will start plugin configuration
        #self.action1 = QtGui.QAction(QtGui.QIcon(":/plugins/terraindatamanipulator/icon.png"),"Calculate Values", self.iface.mainWindow())
        #self.action2 = QtGui.QAction(QtGui.QIcon(":/plugins/terraindatamanipulator/icon.png"),"Add a KMZ file", self.iface.mainWindow())
        self.action3 = QtGui.QAction(QtGui.QIcon(":/plugins/terraindatamanipulator/icon.png"),"Generate GSD Polygons", self.iface.mainWindow())
        self.action4 = QtGui.QAction(QtGui.QIcon(":/plugins/terraindatamanipulator/icon.png"),"Get DEM(s)", self.iface.mainWindow())
        
        # connect the action to the run method
        #QtCore.QObject.connect(self.action1, QtCore.SIGNAL("activated()"), self.callScreenGSD)
        #QtCore.QObject.connect(self.action2, QtCore.SIGNAL("activated()"), self.handleLayerAdded)
        QtCore.QObject.connect(self.action3, QtCore.SIGNAL("activated()"), self.callScreenControl)
        QtCore.QObject.connect(self.action4, QtCore.SIGNAL("activated()"), self.callScreenGetDEM)
        
        # Add toolbar button and menu item
        #self.iface.addPluginToMenu("&DEM Manipulation", self.action1) 
        #self.iface.addPluginToMenu("&DEM Manipulation", self.action2)
        self.iface.addPluginToMenu("&DEM Manipulation", self.action3)
        self.iface.addPluginToMenu("&DEM Manipulation", self.action4)

        self.iface.addDockWidget(QtCore.Qt.LeftDockWidgetArea,  self.dock )

    def unload(self):
 
        self.iface.removeDockWidget(self.dock)
        #self.iface.removePluginMenu("&DEM Manipulation",self.action1)
        #self.iface.removePluginMenu("&DEM Manipulation",self.action2)
        self.iface.removePluginMenu("&DEM Manipulation",self.action3)
        self.iface.removePluginMenu("&DEM Manipulation",self.action4)
 
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------

    def handleMouseMove(self, point):

        elev = self.gsdCalcModel.getElevation(point)
        self.elevLEdit.setText("%f m" % float(elev))

#------------------------------------------------------------------------------

    def setMeanElevationLine(self, value):

        self.screenControl.meanElevationLine.setText("%d m" % float(value))

#------------------------------------------------------------------------------- 
  
    def callScreenControl(self):
     
        path = os.path.dirname( os.path.abspath(__file__) )
        self.screenControl = uic.loadUi( os.path.join( path, "ScreenControl.ui" ) )
        self.screenControl.move(self.screenControl.mapToParent(QtCore.QPoint(700,100)))
        self.screenControl.accLine.setValue(15)
 
        if self.fillCombosOnScreenControl():
            self.setValuesOnScreenControl()
            
            self.screenControl.show()

            QtCore.QObject.connect(self.screenControl.Trigger, QtCore.SIGNAL("clicked()"), self.triggerPolygonGenerator)
            QtCore.QObject.connect(self.screenControl.Cancel, QtCore.SIGNAL("clicked()"), self.screenControl.close)
            QtCore.QObject.connect(self.screenControl.selectOutput, QtCore.SIGNAL("clicked()"), self.getOutputFileNameForScreenContour)
          
        else:
            self.screenControl.close()  
            return

#------------------------------------------------------------------------------- 
 
    def fillCombosOnScreenControl(self):
             
        layers = self.iface.legendInterface().layers()
        
        i = 0
 
        POLY = RST = False 
      
        for layer in layers:
            layerType = layer.type()
            
            if layerType == QgsMapLayer.RasterLayer:
               RST = True

            if layerType == QgsMapLayer.VectorLayer:
                
                  geomType = layer.wkbType()
 
                  if ( geomType == QGis.WKBPolygon and layer.featureCount() < 8):
                        
                      POLY = True
                      self.screenControl.comboBox.insertItem(i,layer.name(),layer.id())
                      i = i + 1
 
        if( not POLY):
            QtGui.QMessageBox.about(None, 'Error','You need a shapefile with one polygon.')
            return False
              
        if (not RST):
            reply = QtGui.QMessageBox.question(None,'Error','You need raster layers. Do you want it now?', QtGui.QMessageBox.Yes | QtGui.QMessageBox.No )
            
            if reply == QtGui.QMessageBox.Yes:
                self.CSC = True
                self.callScreenGetDEM()
                return False
                
            else:
                return False
                
        return True
#------------------------------------------------------------------------------- 
 
    def setValuesOnScreenControl(self):
        
        layerId = str(self.screenControl.comboBox.itemData(self.screenControl.comboBox.currentIndex()))

        try:
            self.setMeanElevationSliderValues(layerId)
        except:
            self.setMeanElevationLine(0)
        
        QtCore.QObject.connect(self.screenControl.meanElevationSlider, QtCore.SIGNAL('valueChanged(int)'), self.setMeanElevationLine)
        QtCore.QObject.connect(self.screenControl.comboBox, QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.setMeanElevationSliderValues)
 
        focalValue = str(self.settings.value("focalKey"))
        pixelsValue = str(self.settings.value("pixelsKey"))
        GSDValue  = str(self.settings.value("GSDKey"))       
        perCentValue = int(self.settings.value("perCentKey"))
        minusErValue = str(self.settings.value("minusErKey"))
        plusErValue = str(self.settings.value("plusErKey"))
 
        self.screenControl.focalLine.setText(focalValue)
        self.screenControl.pixelsLine.setText(pixelsValue)
        self.screenControl.GSDLine.setText(GSDValue)
        
        self.screenControl.pixelsLine.setText(pixelsValue)
        self.screenControl.GSDLine.setText(GSDValue)
        
        self.screenControl.plusErrorLine.setText(plusErValue)
        self.screenControl.minusErrorLine.setText(minusErValue)
        
        self.screenControl.perCentLine.setValue(perCentValue)
 
        self.screenControl.outputLine.setText("C:/Users/Sensormap3/Desktop/pattern")
      
 
#------------------------------------------------------------------------------- 
 
    def triggerPolygonGenerator(self):
        
        self.cleanGarbage()
        
        try:  
            layerId = str(self.screenControl.comboBox.itemData(self.screenControl.comboBox.currentIndex()))
            layerName = str(self.screenControl.comboBox.currentText())
            
            values = self.getValuesForPolygonGenerator()
            output = self.verifyOutputValue()
        
        except:
            self.screenControl.close()
                 
            return self.callScreenControl()

        layerAddress = self.controlModel.generatePolygonLayer(layerId, values, output)
 
        polygonLayer = QgsVectorLayer( layerAddress, layerName + "_GSD_" + str(int(values[2]*100)) + "cm", "ogr", True)
 
        if (self.screenControl.checkBox.isChecked() and polygonLayer.isValid()):
            QgsMapLayerRegistry.instance().addMapLayer(polygonLayer)
            self.setPolygonLayerOnTop(polygonLayer, True)

        else:
            if (not self.screenControl.checkBox.isChecked() and polygonLayer.isValid()):
                QtGui.QMessageBox.about(None, 'Error','Shapefile created in %s.' % str(polygonLayer.source()))

            else:
                QtGui.QMessageBox.about(None, 'Error','Something went wrong.')

        self.canvas.refresh()
        self.screenControl.close()

        self.cleanGarbage()
 
#------------------------------------------------------------------------------- 
 
    def getValuesForPolygonGenerator(self): 
                 
        FPG = self.verifyValues()
        
        focal = FPG[0]
        pixels = FPG[1]
        GSD = FPG[2]
            
        PM = self.verifyErrorValue()
        
        erPlus = PM[0]
        erMinus = PM[1]
        
        terrainMElev = self.verifyTerrainValue()
        accValue = self.verifyAccValue()
        
        return [focal,pixels,GSD,erPlus,erMinus,terrainMElev,accValue]
        
#-------------------------------------------------------------------------------               
       
    def verifyValues(self):
        
        try:       
            focal = float(self.screenControl.focalLine.text())
            self.settings.setValue("focalKey", focal)
                        
            pixels = float(self.screenControl.pixelsLine.text())
            self.settings.setValue("pixelsKey", pixels)
 
            GSD = float(self.screenControl.GSDLine.text())
            self.settings.setValue("GSDKey", GSD)
  
            return [focal,pixels,GSD]

        except:
            QtGui.QMessageBox.about(None, 'Error','Input values may be wrong.')
            return 
            
#-------------------------------------------------------------------------------               
                         
    def verifyPercentErrorValue(self):    
 
        try:
            GSD = float(self.screenControl.GSDLine.text())
            uncert = float(self.screenControl.perCentLine.value())
 
            if uncert > 50:
                 QtGui.QMessageBox.about(None, 'Error','Uncertain must be less than 50%.')
                 return 
             
            erPlus = float(GSD*(float(uncert/100)))
            erMinus = float(GSD*(float(uncert/100)))
            
            return (erPlus,erMinus)
            
        except:
            QtGui.QMessageBox.about(None, 'Error','Uncertain input error may be wrong.')
            return 
 
#-------------------------------------------------------------------------------               
                         
    def verifyUncertErrorValue(self):    
                       
        try: 
            GSD = float(self.screenControl.GSDLine.text())
            
            erPlus = float(self.screenControl.plusErrorLine.text())
            erMinus = float(self.screenControl.minusErrorLine.text())
            
            if erPlus > GSD/2 or erMinus > GSD/2 :
                QtGui.QMessageBox.about(None, 'Error','Uncertain values must be less than %.2f.' % (GSD/2))
                return
                
            self.settings.setValue("minusErKey", erMinus)
            self.settings.setValue("plusErKey", erPlus)
            
            return (erPlus,erMinus)    
            
        except:
            QtGui.QMessageBox.about(None, 'Error','Uncertain input error may be wrong.')
            return 
                  
#-------------------------------------------------------------------------------               
                         
    def verifyErrorValue(self):    
        
        if (self.screenControl.perCentRadioButton.isChecked()):
            return self.verifyPercentErrorValue()
 
        else:
            return self.verifyUncertErrorValue()

#-------------------------------------------------------------------------------               
                         
    def verifyTerrainValue(self):
        try:
            terrainMElev = float(self.screenControl.meanElevationLine.text().replace(" m",""))
            
            if terrainMElev == 0:
                QtGui.QMessageBox.about(None, 'Error','Shapefile must have only one polygon')
                return
                
            if terrainMElev < 0 or terrainMElev > 10000:
                QtGui.QMessageBox.about(None, 'Error','Terrain mean elevation is invalid')
                return
            
            return terrainMElev
                
        except:
            QtGui.QMessageBox.about(None, 'Error','Input terrain value value may be wrong.')
            return
                   
#-------------------------------------------------------------------------------               
                         
    def verifyAccValue(self):
        
        try:
            accValue = int(self.screenControl.accLine.value())
            
            if accValue < 1 or accValue > 99:
                QtGui.QMessageBox.about(None, 'Error','Accuracy must be between 1 and 99.')
                return
                 
            return accValue     
 
        except:
            QtGui.QMessageBox.about(None, 'Error','Input scan accuracy value may be wrong.')
            return
      
                
#-------------------------------------------------------------------------------               
                         
    def verifyOutputValue(self):
        
        try:
            output = str(self.screenControl.outputLine.text())
            
            return output
            
        except:
            QtGui.QMessageBox.about(None, 'Error','Input invalid.')
            return
#-------------------------------------------------------------------------------               
       
    def getOutputFileNameForScreenContour(self):
      
        fileName =  QtGui.QFileDialog.getSaveFileName(None, 'Output', '.')
        self.screenControl.outputLine.setText(fileName)
 
#-------------------------------------------------------------------------------               
              
    def callScreenGetDEM(self):
        
        path = os.path.dirname( os.path.abspath(__file__) )
        self.screenGetRaster = uic.loadUi( os.path.join( path, "ScreenGetDEM.ui" ) )
 
        layers = self.iface.legendInterface().layers()

        i = 0
      
        POLY = False
        
        for layer in layers:
            layerType = layer.type()
            
            if layerType == QgsMapLayer.VectorLayer:
                geomType = layer.wkbType()
 
                if ( geomType == QGis.WKBPolygon ):

                    POLY = True
                    self.screenGetRaster.comboBox.insertItem(i,layer.name(),layer.id())
                    i +=1
                    
        if( not POLY):
            QtGui.QMessageBox.about(None, 'Error','You need a polygon layer first.')
            return

        self.screenGetRaster.show()

        QtCore.QObject.connect(self.screenGetRaster.pushButton, QtCore.SIGNAL("clicked()"), self.triggerGetDEM)
        QtCore.QObject.connect(self.screenGetRaster.pushButton_2, QtCore.SIGNAL("clicked()"), self.screenGetRaster.close)
        QtCore.QObject.connect(self.screenGetRaster.pushButton_3, QtCore.SIGNAL("clicked()"), self.webModel.openRasterCacheDir)
          
#-------------------------------------------------------------------------------               
       
    def showLabels(self, shpLayer, fieldName, pos ):
        
        palyr = QgsPalLayerSettings()
    
        palyr.readFromLayer(shpLayer)
        palyr.enabled = True 
        palyr.fieldName = fieldName
        palyr.placement = pos
        palyr.setDataDefinedProperty(10,True,True,"8","")
        palyr.writeToLayer(shpLayer)
            
#------------------------------------------------------------------------------            
       
    def triggerGetDEM(self):
        
        try:
            layerId = str(self.screenGetRaster.comboBox.itemData(self.screenGetRaster.comboBox.currentIndex()))
            
            self.webModel.downloadRasterRequested(layerId)
     
            shpLayer = QgsMapLayerRegistry.instance().mapLayer(str(layerId))
 
            self.screenGetRaster.close()
            
            if (self.CSC):
                self.CSC = False
                self.callScreenControl()
 
            self.setPolygonLayerOnTop(shpLayer,False)
            
        except:
            self.screenGetRaster.close()
            pass
            
#------------------------------------------------------------------------------            
                  
    def setMeanElevationSliderValues(self, layerId):

        try:        
            layerId = str(self.screenControl.comboBox.itemData(self.screenControl.comboBox.currentIndex()))

            shpLayer = QgsMapLayerRegistry.instance().mapLayer(str(layerId))
                                  
            if not self.webModel.testCompatibility(shpLayer):
                shpLayer = self.webModel.convertToEPSG4326(shpLayer)
                
            terrainStats = self.getTerrainStats(shpLayer)
 
            self.screenControl.meanElevationSlider.setMaximum(terrainStats[1])
            self.screenControl.meanElevationSlider.setMinimum(terrainStats[2])
            self.screenControl.meanElevationSlider.setValue(terrainStats[0])
     
            self.setMeanElevationLine(terrainStats[0])
            
        except:
            QtGui.QMessageBox.about(None, 'Error','This polygon layer is invalid.')
            self.setMeanElevationLine(0)
      
#------------------------------------------------------------------------------            
                  
    def getTerrainStats(self, shpLayer):
        
        request = QgsFeatureRequest()
        features = shpLayer.getFeatures(request)
 
        for feat in features:
 
            geom = feat.geometry()
            stats = self.gsdCalcModel.getElevationValuesFromGeom(geom,20)
            
            return stats
        
#------------------------------------------------------------------------------            
    def cleanGarbage(self):
        
        dirPath = self.tempDir
        
        try:
            for root, dirs, files in os.walk(dirPath, topdown = False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name)) 
        except:
            pass
            
#------------------------------------------------------------------------------
    def setPolygonLayerOnTop(self, polyLayer, showGSDLabels):
        
        self.canvas.setLayerSet([QgsMapCanvasLayer(polyLayer)])
        
        mw = self.iface.mainWindow()
        lgd = mw.findChild(QtGui.QTreeWidget, "theMapLegend")
        
        li = self.iface.legendInterface()
        
        if self.FST:
            li.addGroup('Polygons')
            li.addGroup('Rasters')
            
            self.FST = False
        
        for l in li.layers():
            
            if l.type() == QgsMapLayer.VectorLayer and l.geometryType() == QGis.Polygon:
                li.moveLayer(l, 0)
                
            elif l.type() == QgsMapLayer.RasterLayer:
                li.moveLayer(l, 1)
                li.setLayerVisible(l, True)

        lgd.sortItems(0, QtCore.Qt.AscendingOrder)
        
        if showGSDLabels:
            self.showLabels(polyLayer,"meanGSD", QgsPalLayerSettings.Free)
                        
        li.setLayerVisible(polyLayer, False)
        li.setLayerVisible(polyLayer, True)
        
        self.canvas.updateOverview()
        self.canvas.updateFullExtent()
        self.canvas.refresh()

#------------------------------------------------------------------------------             
 