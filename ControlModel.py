# -*- coding: utf-8 -*-
"""
Created on Thu May 22 10:18:58 2014

@author: Sensormap3
"""
from Includes import *
from GSDCalcModel import *
from WebModel import *
 
"""========================================================================="""

class ControlModel:
    
    def __init__(self, iface, esp):
        
        self.esp = esp  
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.gsdCalcModel = GSDCalcModel(self.iface)
        self.webModel = WebModel(self.iface)
 
        self.fileDir = os.path.dirname(os.path.realpath(__file__)) + "/__RasterCache__/Temp/"
        self.fileDir = self.fileDir.replace("\\","/")
        self.fileDir = self.fileDir.replace(" ","")
        
        import win32api
        self.fileDir = win32api.GetLongPathName(self.fileDir)
          
#------------------------------------------------------------------------------- 
    
    def generatePolygonLayer(self, layerId, values, finalOutput):
 
        self.esp = self.gsdCalcModel.getEsp(values)

        finalOutput = finalOutput.replace(".shp","") + ".shp"
 
        shpLayer = QgsMapLayerRegistry.instance().mapLayer(str(layerId))
                            
        if not self.webModel.testCompatibility(shpLayer):
            shpLayer = self.webModel.convertToEPSG4326(shpLayer)
            
        maskPath = str(shpLayer.source())
  
        rasterNameList = self.webModel.listOfLayersNameByPolygon(layerId)
        layerId = shpLayer.name()
        
        output = self.fileDir + layerId + "merge.tif"
        mergeLayerPath = self.mergeRasters(rasterNameList,output)
         
        output = self.fileDir + layerId + "crop.tif"
        cropLayerPath = self.cropRaster(mergeLayerPath,maskPath,output)
 
        output = self.fileDir + layerId + "mergeReclas.tif"
        reclasLayerPath = self.reclassifyRasterData(cropLayerPath,output)
 
        output = self.fileDir + layerId + "polygonLayer.shp"
        polygonLayerPath = self.vectorizeRaster(reclasLayerPath,output)
 
        polygonLayer = QgsVectorLayer( polygonLayerPath, "polygonLayer", "ogr", True)

        overlayAnalyzer = QgsOverlayAnalyzer()
        overlayAnalyzer.intersection(polygonLayer, shpLayer, finalOutput)

        self.gsdCalcModel.setGSDAttributes(finalOutput,values)
 
        return finalOutput

#------------------------------------------------------------------------------- 
    def reclassifyRasterData(self, rasterName, output):
        
        rasterName = str(rasterName)
        output = str(output)
        
        classificationValues = []
        classificationOutputValues = [] 
        
        cont1 = 0
        cont2 = 0
         
        while cont1 < 10000:
            
            cont1 = cont1 + self.esp
            cont2 = cont2 + 1
            
            classificationValues.append(cont1)
            classificationOutputValues.append(cont2)
 
        dataset = gdal.Open(rasterName, GA_ReadOnly )  
        band = dataset.GetRasterBand(1)  
 
        projectionfrom = dataset.GetProjection()  
        geotransform = dataset.GetGeoTransform()  
        xsize = band.XSize  
        ysize = band.YSize  
        datatype = band.DataType  
 
        values = band.ReadRaster( 0, 0, xsize, ysize, xsize, ysize, datatype )  
 
        dataTypes ={'Byte':'B','UInt16':'H','Int16':'h','UInt32':'I','Int32':'i','Float32':'f','Float64':'d'}  
        values = struct.unpack(dataTypes[gdal.GetDataTypeName(band.DataType)]*xsize*ysize,values)  
 
        outStr = ''  
        for value in values:  
            index = 0  
            for clValue in classificationValues:  
                if value <= clValue:  
                    outStr = outStr + struct.pack('B',classificationOutputValues[index])  
                    break  
                index = index + 1  
       
        gtiff = gdal.GetDriverByName('GTiff')   
        outputDataset = gtiff.Create(output, xsize, ysize, 4)  
        outputDataset.SetProjection(projectionfrom)  
        outputDataset.SetGeoTransform(geotransform)  
          
        outputDataset.GetRasterBand(1).WriteRaster( 0, 0, xsize, ysize, outStr )
        outputDataset = None  
        
        return output
#-------------------------------------------------------------------------------               
    def mergeRasters(self, rasterList, output):
   
        #try:
        newRstList = []
        cont = 0
 
        for fileName in rasterList:
            cont = cont + 1
            newRstList.append(str(self.fileDir.replace("Temp/","") + fileName + ".tif"))

        if( cont == 1):
            return newRstList[0]
        if( cont == 2):
            pipe = subprocess.call(["gdal_merge.bat","-of","GTiff","-o",output,newRstList[0],newRstList[1]],shell = True) 
        if( cont == 3):
            pipe = subprocess.call(["gdal_merge.bat","-of","GTiff","-o",output,newRstList[0],newRstList[1],newRstList[2]],shell = True) 
        if( cont == 4):
            pipe = subprocess.call(["gdal_merge.bat","-of","GTiff","-o",output,newRstList[0],newRstList[1],newRstList[2],newRstList[3]],shell = True) 
        if( cont == 5):
            pipe = subprocess.call(["gdal_merge.bat","-of","GTiff","-o",output,newRstList[0],newRstList[1],newRstList[2],newRstList[3],newRstList[4]],shell = True) 
        if( cont == 6):
            pipe = subprocess.call(["gdal_merge.bat","-of","GTiff","-o",output,newRstList[0],newRstList[1],newRstList[2],newRstList[3],newRstList[4],newRstList[5]],shell = True) 
        if( cont == 7):
            pipe = subprocess.call(["gdal_merge.bat","-of","GTiff","-o",output,newRstList[0],newRstList[1],newRstList[2],newRstList[3],newRstList[4],newRstList[5],newRstList[6]],shell = True) 
        if( cont == 8):
            pipe = subprocess.call(["gdal_merge.bat","-of","GTiff","-o",output,newRstList[0],newRstList[1],newRstList[2],newRstList[3],newRstList[4],newRstList[5],newRstList[6],newRstList[7]],shell = True) 
        if( cont >= 9):
            QtGui.QMessageBox.about(None, 'Error','Exceeded maximum number of layers (Layers <= 6)')
            return 

        return output

        
#-------------------------------------------------------------------------------               
    def cropRaster(self, rasterPath, maskPath, output):
        try:
            pipe = subprocess.call(["gdalwarp","-dstnodata","0","-q","-cutline",maskPath,"-crop_to_cutline","-of","GTiff",rasterPath,output,"-s_srs","EPSG:4326"], shell = True)
            return output
        except:
            return
           
#-------------------------------------------------------------------------------       
    def vectorizeRaster(self, rasterName, output):
        try:
            pipe = subprocess.call(["gdal_polygonize",str(rasterName),"-mask",str(rasterName),"-f","ESRI Shapefile",str(output),"polygonLayer","DN"], shell = True)
            return output
        except:
            return 
 
#-------------------------------------------------------------------------------               
           
    def updateLayersColouring(self):
        
        self.updateElevValues()
        
        layers = self.canvas.layers()
    
        for layer in layers:
            if (layer.type() == QgsMapLayer.RasterLayer):     
 
                rangeElev = self.MAXElev - self.MINElev
 
                colFactor = 255/(rangeElev/self.esp)
                
                alt = 0
                R = 0
                B = 0
                G = 0
                
                rampItens = []  
                
                while (alt <  self.MAXElev):
                    alt = alt + self.esp
                
                    if(alt > (self.MINElev - self.esp)):
   
                        if (B > 255):
                            B = G = 200
                            R = R - colFactor

                        rampItens.append(QgsColorRampShader.ColorRampItem(alt, QtGui.QColor(G,B,150)))
 
                        if (B < 255):
                            R = R + colFactor
                            B = B + colFactor
                            G = G + colFactor
 
                rampShader = QgsColorRampShader()
                rampShader.setColorRampItemList(rampItens)
            
                rasterShader = QgsRasterShader()
                rasterShader.setRasterShaderFunction(rampShader)
                
                rendereStyleColor = QgsSingleBandPseudoColorRenderer(layer.dataProvider().clone(),1,rasterShader)
                layer.setRenderer(rendereStyleColor)
 
#-------------------------------------------------------------------------------               
                   
    def updateElevValues(self):
 
        self.MAXElev = 0
        self.MINElev = 9999
        
        layers = self.canvas.layers()

        for layer in layers:
            layerType = layer.type()
    
            if layerType == QgsMapLayer.RasterLayer:
 
                ds = gdal.Open(str(layer.source()), GA_ReadOnly)
                pipe = subprocess.call(["gdalinfo", "-stats", str(layer.source())], shell = True)
                stats = ds.GetRasterBand(1).GetStatistics(0,1)
          
                if(self.MAXElev < stats[1]):
                    self.MAXElev = stats[1]
                    
                if(self.MINElev > stats[0]):
                    self.MINElev = stats[0]
                    
        return (self.MINElev - 50 ,self.MAXElev + 50)
