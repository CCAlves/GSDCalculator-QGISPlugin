# -*- coding: utf-8 -*-
"""
Created on Thu May 22 10:24:20 2014

@author: Sensormap3
"""

"""========================================================================="""

import numpy
import operator
import subprocess
import shlex
import Image
import ImageDraw
import win32api
import os
import sys
import math
import decimal
import struct 

"""========================================================================="""

from qgis import *
from qgis.core import *
from qgis.gui import *
from qgis.analysis import *

from gdalconst import *

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtWebKit
from PyQt4 import uic

"""========================================================================="""

try:
    from osgeo import gdal
    from osgeo import osr
    from osgeo import ogr
    from osgeo import gdalnumeric

except:
    import gdal
    import osr
    import ogr
    import gdalnumeric
    
             
"""========================================================================="""
