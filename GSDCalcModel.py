# -*- coding: utf-8 -*-
"""
Created on Fri May 23 11:58:18 2014

@author: Sensormap3
"""

from Includes import *

"""========================================================================="""

class GSDCalcModel:
 
    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        
#------------------------------------------------------------------------------- 
  
    def setGSDAttributes(self, layerName, values):
        
        focal = values[0]
        pixels = values[1]
        GSD = values[2]

        terrainMElev = values[5]
        accValue = values[6]
                
        path = os.path.dirname( os.path.abspath(__file__) )
        self.screenProgBar = uic.loadUi( os.path.join( path, "ScreenProgBar.ui" ) )
        self.screenProgBar.progressBar.setMinimum(1)  
        self.screenProgBar.progressBar.setValue(1) 
         
        self.screenProgBar.show()
 
        shpLayer = QgsVectorLayer( layerName, "polygonLayer", "ogr", True)
 
        request = QgsFeatureRequest()
        features = shpLayer.getFeatures(request)
        provider = shpLayer.dataProvider()
 
        self.screenProgBar.progressBar.setMaximum(provider.featureCount()) 
 
        shpLayer.startEditing()
        
        attributeList = provider.fields()

        provider.deleteAttributes(attributeList)
        
        elevField = QgsField("ID", QtCore.QVariant.Int)
        
        elevField1 = QgsField("meanElev", QtCore.QVariant.Double)
        elevField2 = QgsField("maxElev", QtCore.QVariant.Double)
        elevField3 = QgsField("minElev", QtCore.QVariant.Double)
        elevField4 = QgsField("meanGSD", QtCore.QVariant.Double)
        elevField5 = QgsField("maxGSD", QtCore.QVariant.Double)
        elevField6 = QgsField("minGSD", QtCore.QVariant.Double)
     
        provider.addAttributes([ elevField, elevField1, elevField2, elevField3, elevField4, elevField5, elevField6 ])   
        shpLayer.commitChanges()

        cont = 0
 
        for feat in features:
            
            self.screenProgBar.progressBar.setValue(cont)
            cont = cont + 1 
            
            geom = feat.geometry()
            
            stats = self.getElevationValuesFromGeom(geom,accValue)
            
            AltMean = stats[0]
            AltMax = stats[1]
            AltMin = stats[2]
 
            AltMean = float("%.3f" % AltMean)
            AltMax = float("%.3f" % AltMax)
            AltMin = float("%.3f" % AltMin)
            
            HF = float((GSD * focal)/(pixels/1000.0))
            
            HFMean = HF + terrainMElev
            
            GSDMean = float((HFMean - AltMean)  * ((1000.0/(focal*1000000.0)) * pixels)) 
            GSDMax  = float((HFMean - AltMax)  * ((1000.0/(focal*1000000.0)) * pixels)) 
            GSDMin  = float((HFMean - AltMin)  * ((1000.0/(focal*1000000.0)) * pixels)) 
            
            GSDMean = float("%.3f" % GSDMean) 
            GSDMax  = float("%.3f" % GSDMax) 
            GSDMin  = float("%.3f" % GSDMin) 
 
            provider.changeAttributeValues({feat.id() : { feat.fieldNameIndex("ID"): cont }})

            provider.changeAttributeValues({feat.id() : { shpLayer.fieldNameIndex("meanElev"): AltMean }})
            provider.changeAttributeValues({feat.id() : { shpLayer.fieldNameIndex("maxElev") : AltMax }})
            provider.changeAttributeValues({feat.id() : { shpLayer.fieldNameIndex("minElev") : AltMin }})
            provider.changeAttributeValues({feat.id() : { shpLayer.fieldNameIndex("meanGSD") : GSDMean }})
            provider.changeAttributeValues({feat.id() : { shpLayer.fieldNameIndex("maxGSD")  : GSDMax }})
            provider.changeAttributeValues({feat.id() : { shpLayer.fieldNameIndex("minGSD")  : GSDMin }})
                        
        self.screenProgBar.close()
 
#------------------------------------------------------------------------------- 
  
    def getElevationValuesFromGeom(self, geom, precision):

        points = []

        try:
            rect = geom.boundingBox()

        except:
            return [0,0,0]
            
        xFac = rect.width()/precision
        yFac = rect.height()/precision
            
        x = rect.xMinimum()
        y = rect.yMinimum()

        maxX = rect.xMaximum()
        maxY = rect.yMaximum()

        totalElevation = 0
        contElevPoints = 0  
 
        while (x < maxX):
        
            while (y < maxY):
 
                if (geom.contains(QgsPoint(x,y))):
                    points.append(QgsPoint(x,y))
                    contElevPoints = contElevPoints + 1
                    
                y = y + yFac
              
            x = x + xFac
            y = rect.yMinimum()


        val = 0

        stdElev = aMax = aMin = self.getElevation(geom.centroid().asPoint())
        
        
        for point in points:
            pointElev = self.getElevation(point)
            
            if not pointElev == None:
                
                if pointElev > aMax:
                    aMax = pointElev
                    
                if pointElev < aMin:
                    aMin = pointElev
                    
                totalElevation = totalElevation + pointElev
                    
            else:
                contElevPoints = contElevPoints - 1
                
            val = val + 1    

        try:
            meanElevation = float(totalElevation/contElevPoints)
            return [meanElevation,aMax,aMin]    
            
        except:
            return [stdElev,aMax,aMin]
        
#------------------------------------------------------------------------------- 
            
    def getElevation(self, point):
      
        layers = self.iface.legendInterface().layers()

        for layer in layers:
            layerType = layer.type()
          
            if layerType == QgsMapLayer.RasterLayer:

                elev = self.getBandValueAtPoint(str(layer.source()), 1, point)

                if (elev == 0):
                    continue
 
                else:
                    return elev

        return 0

#------------------------------------------------------------------------------- 
    def getEsp(self, values):
 
        focal = values[0]
        pixels = values[1]
        GSD = values[2]
        erPlus = values[3]
        erMinus = values[4]
 
        HF1 = float(((GSD - erMinus)* focal)/(pixels/1000.0))
        HF2 = float(((GSD + erPlus) * focal)/(pixels/1000.0))

        return HF2 - HF1
    
#------------------------------------------------------------------------------- 
    def getBandValueAtPoint(self, filename, bandIndex, point):

        ds = gdal.Open(filename, GA_ReadOnly)
 
        transform = ds.GetGeoTransform()
      
        xOrigin = transform[0]
        yOrigin = transform[3]
      
        pixelWidth = transform[1]
        pixelHeight = transform[5]
 
        xOffset = int((point.x() - xOrigin) / pixelWidth)
        yOffset = int((point.y() - yOrigin) / pixelHeight)

        band = ds.GetRasterBand(bandIndex) 
 
        try:
            data = band.ReadAsArray(xOffset, yOffset, 1, 1)
            value = float(data[0])

            return value
          
        except:
            return 0