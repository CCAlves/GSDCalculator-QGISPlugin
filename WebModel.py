# -*- coding: utf-8 -*-
"""
Created on Thu May 22 11:29:18 2014

@author: Sensormap3
"""

from Includes import *

"""========================================================================="""


class WebModel:
    
    def __init__(self, iface):
        self.dirPath = os.path.dirname( os.path.abspath(__file__) )
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

#-------------------------------------------------------------------------------               
       
    def testCompatibility(self, shpLayer):
        if not str(shpLayer.crs().authid()) == "EPSG:4326":
            return False
        return True
 
#-------------------------------------------------------------------------------               
       
    def convertToEPSG4326(self, layer): 
            
        fileDir = os.path.dirname(os.path.realpath(__file__)) + "/__RasterCache__/Temp/"
        fileDir = fileDir.replace("\\","/")
        fileDir = fileDir.replace(" ","")
        
        import win32api
        fileDir = win32api.GetLongPathName(fileDir)
        
        output = fileDir + "espg4326.shp"
        inputt = str(layer.source())
        
        pipe = subprocess.call(["ogr2ogr", "-t_srs", "EPSG:4326", output, inputt],shell = True) 
        
        shpLayer = QgsVectorLayer( output, "polygonLayer", "ogr", True)
        
        return shpLayer 
#-------------------------------------------------------------------------------               
       
    def listOfLayersNameByPolygon(self, layerId):
        
        points = []

        shpLayer = QgsMapLayerRegistry.instance().mapLayer(str(layerId))
 
        if not self.testCompatibility(shpLayer):
            shpLayer = self.convertToEPSG4326(shpLayer)

        request = QgsFeatureRequest()
        features = shpLayer.getFeatures(request)
 
        for feat in features:
        
            geom = feat.geometry()
            boundBox = geom.boundingBox()
 
            X = boundBox.xMinimum()  
            Y = boundBox.yMinimum()  
            
            maxX = boundBox.xMaximum() 
            maxY = boundBox.yMaximum() 
        
            points.append(QgsPoint(X + 0.001,Y + 0.001))
            points.append(QgsPoint(maxX - 0.001,Y + 0.001))
            points.append(QgsPoint(X + 0.001,maxY - 0.001))
            points.append(QgsPoint(maxX - 0.001,maxY - 0.001))
  
            while (X < maxX):
                
                while (Y < maxY):
                    if (geom.contains(QgsPoint(X,Y))):
                        points.append(QgsPoint(X,Y))
                        
                    Y = Y + 0.1
                    
                X = X + 0.15
                Y = boundBox.yMinimum() 

        preFileNames = [] 
      
        for point in points:
                         
            preFileName = ""                              
                         
            if(math.fabs(point.y())<10):
                preFileName = "0"                  
        
            yElem = str(math.floor(int(point.y())))
   
            xElem = self.ajustXElem(math.floor(point.x()*10)/10)

        
            if (math.floor(point.y()) <= 0):
                
                if ( point.y() < 1 and point.y() > 0):
                    yElem = str(math.ceil(point.y()))     
                    preFileName = preFileName + yElem + "N" + xElem
                    
                else:
                    preFileName = preFileName + yElem + "S" + xElem
                
            else:
                yElem = str(math.ceil(point.y()))                        
                preFileName = preFileName + yElem + "N" + xElem
            
            preFileName = preFileName.replace(".0","")
            preFileName = preFileName.replace("-","")
            preFileName = preFileName + "ZN"
            preFileNames.append(preFileName)
        
        fileNames = self.removeDuplicates(preFileNames)
        
        return fileNames
        
#-------------------------------------------------------------------------------                 
                
    def ajustXElem(self, X):
  
        X = float(math.fabs(X))
        
        col = 360
        
        while( col <= X*10 ):     
            col = col + 15
    
        if ( col % 10 == 0 ):
            return(str(col/10) + "_")
        else:
            return(str(col))
           
#-------------------------------------------------------------------------------               
             
    def removeDuplicates(self, listItens):
        
        newList = []
        
        self.count = 0
        
        for item in listItens:
            repeat = False

            for finalItem in newList:
                if (item == finalItem):
                    repeat = True
                    
            if (not repeat):
                newList.append(item)
                self.count = self.count + 1
                
        return newList

            
#-------------------------------------------------------------------------------               
               
    def openRasterCacheDir(self):
        import subprocess
        path = os.path.dirname( os.path.abspath(__file__) )
        totalPath = os.path.join( path, "__RasterCache__" ) 
        
        pipe = subprocess.call(['explorer', totalPath], shell = True)        
        
        
#------------------------------------------------------------------------------
      
    def downloadRasterRequested(self, layerId):
 
        try:
            rasterList = self.listOfLayersNameByPolygon(layerId)
            
        except:
            QtGui.QMessageBox.about(None, 'Error','Input may be wrong, vector layer is not valid')
            return
        
        cont = 0
        
        path = os.path.dirname( os.path.abspath(__file__) )
        fileDir = os.path.dirname(os.path.realpath(__file__)) + "/__RasterCache__/"
        fileDir = fileDir.replace("\\","/")
        fileDir = fileDir.replace(" ","")
        
        import win32api
        fileDir = win32api.GetLongPathName(fileDir)

        rasterLayers = []

        for rasterName in rasterList:
            
            if( not self.layerAlreadyExist(rasterName) ):
                
                cont = cont + 1
                fileName = fileDir + rasterName 
                
                if(os.path.exists(fileName + ".tif")):
                    
                    try:
                        os.remove(fileName + ".zip")
                        fileName = rasterName + ".tif"
                        rasterLayers.append(fileName)
                        
                    except:
                        fileName = fileName + ".tif"
                        rasterLayers.append(fileName)
                    
                else:
                    
                    try:
                        rasterRequested = "http://www.dsr.inpe.br/topodata/data/geotiff/" + rasterName + ".zip"
                        url = str(rasterRequested)
                        
                       # if ( not self.checkConnectivity(url) ):
                        #    QtGui.QMessageBox.about(None, 'Error','Network not available.')
                        #    return
         
                        import urllib2
                    
                        u = urllib2.urlopen(url)
                        f = open(fileName + ".zip", 'wb')
                        meta = u.info()
                        fileSize = int(meta.getheaders("Content-Length")[0])
                
                        path = os.path.dirname( os.path.abspath(__file__) )
                        self.screenProgBar = uic.loadUi( os.path.join( path, "ScreenProgBar.ui" ) )
                        self.screenProgBar.setWindowTitle("Wait few seconds... (%d of %d)" % (cont,self.count))
                        self.screenProgBar.progressBar.setMinimum(1)  
                        self.screenProgBar.progressBar.setMaximum(fileSize)  
                        self.screenProgBar.progressBar.setValue(1)
                        self.screenProgBar.show()
                
                        fileSizeDL = 0
                        blockSZ = 8192
                        
                        while True:
                            buffer = u.read(blockSZ)
                            if not buffer:
                                break
            
                            fileSizeDL += len(buffer)
                            f.write(buffer)
                            self.screenProgBar.progressBar.setValue(fileSizeDL)
                            
                        self.screenProgBar.close()
                        f.close()
         
                        import zipfile
            
                        with zipfile.ZipFile(fileName + ".zip", "r") as z:
                            z.extractall(fileDir)
                        
                        os.remove(fileName + ".zip")
                        
                    except:
                        QtGui.QMessageBox.about(None, 'Failure !', '%s do not exist, polygon has some vertex out of the database range.' % (rasterName))
                        pass
 
                fileName = fileName + ".tif"
                rasterLayers.append(fileName)
 
        if (cont == 0):
            QtGui.QMessageBox.about(None, 'Success !', 'Layers were already loaded.')
            
        else:
            QtGui.QMessageBox.about(None, 'Success !', 'The digital data models will be loaded.')
            
            for rasterName in rasterLayers:

                fileInfo = QtCore.QFileInfo(rasterName)
                baseName = fileInfo.baseName()
                rasterLayer = QgsRasterLayer(rasterName, baseName)
                QgsMapLayerRegistry.instance().addMapLayer(rasterLayer,True)       
        
#-------------------------------------------------------------------------------               
  
    def layerAlreadyExist(self, fileName):
        
        layers = self.iface.legendInterface().layers()

        for layer in layers:
            if(layer.name() == fileName):
                return True
                
        return False
              
#-------------------------------------------------------------------------------               
