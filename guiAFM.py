# -*- coding: utf-8 -*-
"""
Created on Sat Nov 15 19:18:27 2014

@author: Gaurav
"""

import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from readIBW import readIBW
from AFM import AFMscript
from ImportDirectory import ImportDirectory
import numpy as np
import xlwt
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

# MODEL FORM
class modelForm(QDialog):
    
    def __init__(self, parent=None):
        super(modelForm, self).__init__(parent)
        settings = QSettings()
        
        # LABELS
        modelLabel = QLabel("Indenter Model:")
        poissonLabel = QLabel("Poisson's Ratio:")
        radiusLabel = QLabel("Sphere Radius [um]:")
        tipAngleLabel = QLabel("Tip Angle [deg]:")
        modelLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        poissonLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Raised)
        radiusLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Raised)
        tipAngleLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Raised)
        
        # COMBO, SPIN, BUTTON
        self.modelComboBox = QComboBox()       
        models = [QString(""), QString("Sphere"), QString("Pyramid")]
        for model in models:
            self.modelComboBox.addItem(model)        
        self.radiusSpinBox = QDoubleSpinBox()
        self.radiusSpinBox.setRange(1.0, 100.0)
        self.radiusSpinBox.setSingleStep(0.5)
        self.radiusSpinBox.setValue(2)
        self.tipAngleSpinBox = QDoubleSpinBox()
        self.tipAngleSpinBox.setRange(1.0, 179.0)
        self.tipAngleSpinBox.setSingleStep(0.5)
        self.tipAngleSpinBox.setValue(35.0)
        self.poissonSpinBox = QDoubleSpinBox()
        self.poissonSpinBox.setRange(0.01, 0.49)
        self.poissonSpinBox.setSingleStep(0.01)
        self.poissonSpinBox.setValue(0.33)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        
        # STACK and LAY WIDGETS
        self.stackedWidget = QStackedWidget()
        sphereWidget = QWidget()
        sphereLayout = QGridLayout()
        sphereLayout.addWidget(radiusLabel, 0, 0)
        sphereLayout.addWidget(self.radiusSpinBox, 0, 1)
        sphereWidget.setLayout(sphereLayout)
        self.stackedWidget.addWidget(sphereWidget)
        pyramidWidget = QWidget()
        pyramidLayout = QGridLayout()
        pyramidLayout.addWidget(tipAngleLabel, 0, 0)
        pyramidLayout.addWidget(self.tipAngleSpinBox, 0, 1)
        pyramidWidget.setLayout(pyramidLayout)
        self.stackedWidget.addWidget(pyramidWidget)
        modelLayout = QGridLayout()
        modelLayout.addWidget(modelLabel, 0, 0)
        modelLayout.addWidget(self.modelComboBox, 0, 1)
        modelLayout.addWidget(poissonLabel, 1, 0)
        modelLayout.addWidget(self.poissonSpinBox, 1, 1)
        
        # FINAL LAYOUT
        layout = QVBoxLayout()
        layout.addLayout(modelLayout)
        layout.addWidget(self.stackedWidget)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        # CONNECTIONS
        self.buttonBox.accepted.connect(self.accept)
        self.connect(self.modelComboBox, 
                         SIGNAL("currentIndexChanged(QString)"), 
                         self.setWidgetStack)
        
    def accept(self):
        # write variables to SELF when done
        self.nu = self.poissonSpinBox.value()
        self.radius = self.radiusSpinBox.value()
        self.alpha = self.tipAngleSpinBox.value()
        QDialog.accept(self)
    
    def setWidgetStack(self, text):
        # change stackWidget index based on modelComboBox
        if text == "Sphere":
            self.stackedWidget.setCurrentIndex(0)
            self.indenterIndex = 0
        else:
            self.stackedWidget.setCurrentIndex(1)
            self.indenterIndex = 1

class reviewForm(QDialog):

    def __init__(self, parent=None, files=None, moduli=None):
        super(reviewForm, self).__init__(parent)
        
        if files is not None:
            self.files = files
        else:
            self.files = ['No files analyzed']  
        if moduli is not None:
            self.moduli = moduli
        else:
            self.moduli = ['0']
        
        self.initTable()
        self.setDataToTable()

    def initTable(self, label=None):
        # TABLE 
        self.table = QTableWidget()
        self.table.setRowCount(100) # default
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["File", "Modulus [kPa]"])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.tableLabel = QLabel("Double-click file to plot")
        self.tableLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
    
        # PLOT
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        # TABLE -- group box approach
        tableGroupBox = QGroupBox("Files and Moduli")
        tableLayout = QGridLayout()
        tableLayout.addWidget(self.tableLabel, 0, 0)
        tableLayout.addWidget(self.table, 1, 0)
        tableGroupBox.setLayout(tableLayout)
        # PLOT -- standard QVBox approach
        plotGroupBox = QGroupBox("Force vs Z-Pos Plot")
        plotLayout = QVBoxLayout()
        plotLayout.addWidget(self.toolbar)
        plotLayout.addWidget(self.canvas)
        plotGroupBox.setLayout(plotLayout)
         # MASTER LAYOUT -- treat GroupBox's as widgets
        layout = QHBoxLayout()
        layout.addWidget(tableGroupBox)
        layout.addWidget(plotGroupBox)
        self.setLayout(layout)
        self.setWindowTitle("Review Force Curve Data")

        # CREATE CONNECTIONS BELOW
        self.table.cellDoubleClicked.connect(self.cellWasClicked)
            
    def setDataToTable(self):
        
        # refresh table and headers
        self.table.clear()
        self.table.setSortingEnabled(False)
        
        if self.moduli is not None:            
            self.moduli = [str(i) for i in self.moduli] 
                 
        rows = len(self.files)
        self.table.setRowCount(rows)
        self.table.setColumnCount(2)
        headers = ["File", "Modulus [kPa]"]
        self.table.setHorizontalHeaderLabels(headers)
        
        for i in range(len(self.files)):
            itemc0 = QTableWidgetItem(QString(self.files[i]))
            itemc1 = QTableWidgetItem(QString(self.moduli[i]))
            self.table.setItem(i,0,itemc0) # for row i, write to col0
            self.table.setItem(i,1,itemc1) # for row i, write to col1

        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()

    def cellWasClicked(self):

        files = self.files
        # get filename from row selected
        row = self.table.currentItem().row()
        f = files[row]
        f = unicode(f, "utf-8", errors="ignore")
        readFile = readIBW()
        readFile.run(['--infile', f])
        wave  = readFile.getWaveData()
        zpos = wave[:,0]
        force_raw = wave[:,1]
        instAFM = AFMscript(zpos,
                            force_raw,
                            indenterModel=0,
                            nu = 0.33,
                            radius=2.0, 
                            tipAngle=35.0)
        instAFM.fitMonophasic()

        reviewForm.fcPlot(self,
                        x1=instAFM.indent,
                        y1=instAFM.indentforce,
                        x2=instAFM.indfit,
                        y2=instAFM.forcefit)

    def fcPlot(self, x1=None, y1=None, x2=None, y2=None):
        # Create axis
        ax = self.figure.add_subplot(111)
        # Clear plot
        ax.hold(False)
        
        if x1 is not None:
            x1 = [x*(10**6) for x in x1]
            x2 = [x*(10**6) for x in x2]
            y1 = [y*(10**8) for y in y1]
            y2 = [y*(10**8) for y in y2]

            ax.plot(x1,y1,'k*',x2,y2,'c+')
#            ax.plot(x1, y1, '*-', x2,y2, '+-')
            ax.set_xlabel('Z-position [um]')
            ax.set_ylabel('Force [nN]')
        else:
            data = [random.random() for i in range(10)]
            ax.plot(data)
        # Refresh canvas
        self.canvas.draw()


class Form(QMainWindow):
    
    def __init__(self, parent = None):
        super(Form, self).__init__(parent)
        pathLabel = QLabel("Path:")        
        settings = QSettings()
        # SET CHECKS FOR FUNCS
        self.files = None # cannot save data unless files exists
        self.indenterIndex = None # cannot Analyze unless indenter selected
        
        # CREATE SET PATH
        path = (sys.argv[1] if len(sys.argv) > 1 and QFile.exists(sys.argv[1]) else os.getcwd())
        self.pathLabel = QLabel(path)
        self.pathLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        self.pathLabel.setToolTip("The path containing your files of interest.")
        self.pathButton = QPushButton("&Path...")
        self.pathButton.setToolTip(self.pathLabel.toolTip().replace("The", "Sets the"))
        
        # CREATE MODEL MENU with checkable/radio selection
        self.buttonMenuBox = QDialogButtonBox()
        menu = QMenu(self)
        presetGroup = QActionGroup(self)        
        pyramidAction = presetGroup.addAction(QAction("Hertz: Pyramid", self, checkable=True))
        sphereAction = presetGroup.addAction(QAction("Hertz: Sphere", self, checkable=True))
        customAction = presetGroup.addAction(QAction("Custom...", self, checkable=True))
        menu.addAction(pyramidAction)
        menu.addAction(sphereAction)
        menu.addAction(customAction)
        self.modelButton = self.buttonMenuBox.addButton("&Indenter Model...", QDialogButtonBox.ActionRole)
        self.modelButton.setMenu(menu)
        self.modelButton.setToolTip("Select indenter model (preset or custom)")
        
        # CREATE BUTTON BOX
        self.buttonBox = QDialogButtonBox()
        self.analyzeButton = self.buttonBox.addButton("&Analyze", QDialogButtonBox.ActionRole)
        self.reviewButton = self.buttonBox.addButton("&Review", QDialogButtonBox.ActionRole)
        self.saveButton = self.buttonBox.addButton("&Save", QDialogButtonBox.ActionRole)
        quitButton = self.buttonBox.addButton("&Quit", QDialogButtonBox.RejectRole)

        # CREATE LAYOUT                         
        layoutPath = QHBoxLayout()
        layoutPath.addWidget(pathLabel)
        layoutPath.addWidget(self.pathLabel, 1)
        layoutPath.addWidget(self.pathButton)
        layoutPath.addWidget(self.buttonMenuBox)
        layoutButton = QHBoxLayout()   
        layoutButton.addStretch()
        layoutButton.addWidget(self.buttonBox)       
        # CREATE MASTER LAYOUT -- add in desired order
        layoutMaster = QVBoxLayout()
        layoutMaster.addLayout(layoutPath)
        layoutMaster.addLayout(layoutButton)
        # master Widget setup
        masterWidget = QWidget()
        masterWidget.setLayout(layoutMaster)
        self.setCentralWidget(masterWidget)
        self.setWindowTitle("Force Curve Analysis")

        # CONNECT actions to buttons
        # triggers
        self.connect(customAction, SIGNAL("triggered()"), self.openSetModel)
        self.connect(pyramidAction, SIGNAL("triggered()"), self.setPyramid)
        self.connect(sphereAction, SIGNAL("triggered()"), self.setSphere)
        # clicks 
        self.connect(self.pathButton, SIGNAL("clicked()"), self.setPath)
        self.connect(self.analyzeButton, SIGNAL("clicked()"), self.runAnalysis)
        self.connect(self.reviewButton, SIGNAL("clicked()"), self.openReview)
        self.connect(self.saveButton, SIGNAL("clicked()"), self.runSaveData)
        self.connect(quitButton, SIGNAL("clicked()"), self.close)
         
    def setPath(self):
        # path is the filepath or directory as a QString()
        path = QFileDialog.getExistingDirectory(self,
                                                "Set Path", 
                                                self.pathLabel.text(),
                                                QFileDialog.ShowDirsOnly)
        self.directory = str(path)
        if path:
            self.pathLabel.setText(QDir.toNativeSeparators(path))
            self.analyzeButton.setText("Analyze")

    
    def runSaveData(self):
        if self.files is not None:
            # path is the filepath or directory
            xlsdatafilename = time.strftime('/AFM_Data_%y%m%d_%H%M.xls')
            saveFilePath = QFileDialog.getSaveFileName(self, 
                                                       'Save Moduli to Excel', 
                                                       str(xlsdatafilename), 
                                                       selectedFilter='*.xls')
            outputBook = xlwt.Workbook(encoding="utf-8")
            sheet1 = outputBook.add_sheet("Data")    
            sheet1.write(0,0,"Filepath")
            sheet1.write(0,1,"Modulus [kPa]")        
            for i in range(len(self.files)):
                sheet1.write(i+1,0,self.files[i])  
                sheet1.write(i+1,1,self.moduli[i])  
            # Write data as XLS with data and timestamp
            outputBook.save(saveFilePath)
            return
        else:
            pass
        
    def openReview(self):
        try:
            dlg = reviewForm(self, files=self.files, moduli=self.moduli)
        except:
            dlg = reviewForm(self)
        dlg.exec_()

    def openSetModel(self):
        dlgModel = modelForm(self)
        dlgModel.exec_()
        try:
            self.nu = dlgModel.nu
            self.radius = dlgModel.radius
            self.alpha = dlgModel.alpha
            self.indenterIndex = dlgModel.indenterIndex
            self.modelButton.setText("Custom")
        except:
            pass
    
    def setPyramid(self):
        self.indenterType = "Pyramid"
        self.indenterIndex = 1
        self.alpha = 35.0
        self.radius = []
        self.nu = 0.333
        self.modelButton.setText("Pyramid")

    def setSphere(self):
        self.indenterType = "Sphere"
        self.indenterIndex = 0
        self.radius = 2.0
        self.alpha = []
        self.nu = 0.333
        self.modelButton.setText("Sphere")

    def runAnalysis(self):        
        # First take the directory and populate files
        if self.indenterIndex is not None:
            if self.directory:
                self.moduli=[]
                self.analyzeButton.setText("Analyzing...")
                QApplication.processEvents() # must use to update text in prev line
                instImport = ImportDirectory(dirs=self.directory)
                instImport.addDirectory(dirs=self.directory) # will process and populateFilesFromDir()
                if instImport.hasDir():
                    self.selected_directory = instImport.getDirectory()
                    files = instImport.getFilePaths()
                    files = files[0:(len(files)/2)] ## TEMP FIX TO DOUBLE IMPORTING
                    self.files = files
    
            # Iterate over files to get IGOR Wave Data (wData)      
            if files:
                waves = {}
                for i in range(len(instImport.files)):
                    instRead = readIBW()
                    instRead.run(['--infile', instImport.files[i]])
                    wData = np.delete(instRead.wave['wave']['wData'],2,1)
                    waves[i] = wData
            wavelength = len(waves.keys())
            waverange = np.arange(wavelength)        
            vals = waves.values() 
            if vals:
                for j in waverange:   
                    wave_array = vals[j]
                    zpos = wave_array[:,0]
                    force_raw = wave_array[:,1]
                    instAFM = AFMscript(zpos, 
                                        force_raw,
                                        indenterModel=self.indenterIndex,
                                        tipAngle=self.alpha,
                                        radius=self.radius,
                                        nu=self.nu)
                    instAFM.fitMonophasic()
                    modulus = instAFM.modulus
                    self.moduli.append(modulus)
            self.analyzeButton.setText("Analysis Done")
            return
        else:
            pass
                        
def main():
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    app.exec_()
#    sys.exit(app.exec_())

if __name__ == '__main__':
    main()