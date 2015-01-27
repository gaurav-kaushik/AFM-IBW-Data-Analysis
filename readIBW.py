# -*- coding: utf-8 -*-
"""
Created on Wed Oct 01 22:02:31 2014

@author: Gaurav
"""

"Reads a single IBW and outputs a Nx2 matrix [Z-Pos Force]"

from igor.binarywave import load
from igor.script import Script
import numpy as np

class readIBW(Script):
    
    def _run(self,args):
        self.wave = load(args.infile) #wave contains the data with col1 as ind and col2 as force
        if self.wave:
            self.wData = np.delete(self.wave['wave']['wData'],2,1)
        return
        
    def getWaveData(self):
        return self.wData