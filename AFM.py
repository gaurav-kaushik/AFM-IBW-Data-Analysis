# -*- coding: utf-8 -*-
"""
Created on Wed Oct 08 20:40:26 2014

@author: Gaurav
"""
import numpy as np
import matplotlib.pyplot as plt
from SG_filter import savitzky_golay as sgf

class AFMscript(): 
        
    def __init__(self, zpos, force_raw, indenterModel, nu, radius, tipAngle):
        self.zpos = zpos
        self.force_raw = force_raw
        self.nu = nu
        self.rad = radius
        self.alpha = tipAngle
        self.indmodel = indenterModel
#        return

    def dataSeparate(self):
        z = self.zpos
        f = self.force_raw                
        fmax = np.argmax(f)                
        self.indent = z[0:fmax]        
        self.indentforce = f[0:fmax]                   
        self.retract = z[fmax+1:-1]
        self.retractforce = f[fmax+1:-1]
#        return
        
    def dataNormalize(self):
        # normalize separated data
        minindent = np.min(self.indent)
        minforce = np.min(self.indentforce)
        self.indent = [x - minindent for x in self.indent]
        self.indentforce = [x - minforce for x in self.indentforce]
        # Smooth, trim, and return data
        self.indentforce = sgf(self.indentforce,1001,1)
        oneper=int(-1*np.round(0.01*(len(self.indent))))
        self.indent=self.indent[1:oneper]
        self.indentforce=self.indentforce[1:oneper]
#        return
        
    def linearTransform(self):
        # create linear transform of force data
        if self.indmodel == 0:
            self.forceLT = [x**(2.0/3.0) for x in self.indentforce]
        elif self.indmodel == 1:
            self.forceLT = [x**(1.0/2.0) for x in self.indentforce]
#        return
        
    def firstFit(self):
        Ind = self.indent
        ForceLT = self.forceLT
        start = len(Ind) - 100
        Rsq=1
        thresh=0.99
#        while (1):
        j = 0
        while j < 10:
            if Rsq > thresh:
                if (start < len(Ind)):
                    start-=100
                    Ind_fit = Ind[start:-50]
                    Force_fit = ForceLT[start:-50]
                    
                    # polys[0] is slope, polys[1] is y-int
                    Polys=np.polyfit(Ind_fit,Force_fit,1)
                    Line = np.poly1d([Polys[0],Polys[1]])
                    Fpred = Line(Ind_fit)
                    
                    # Calculate Rsq
#                    Fdev=Force_fit - np.mean(Force_fit)
                    Fdev = [x - np.mean(Force_fit) for x in Force_fit] 
                    sqFdev = [x**2.0 for x in Fdev]                           
                    SST=np.sum(sqFdev)
#                    Fresid=Force_fit - Fpred
                    Fresid = np.subtract(Force_fit,Fpred)
                    sqFresid = [x**2.0 for x in Fresid]
                    SSE=np.sum(sqFresid)
                    
                    Rsq=1-(SSE/SST)
                    j+=1
            else:
                j+=1
                break
                
        self.indfit = Ind_fit
        self.forcefit = [x**(3.0/2.0) for x in Force_fit]
        self.residual = Rsq
        self.slope = Polys[0]
#        return

    def slopeToModulus(self):
        m = self.slope
        alph = self.alpha
        rad = self.rad
        nu = self.nu
        tan_alpha = np.tan(np.deg2rad(alph))
        
        if self.indmodel == 0:
            # HERTZ model for spherical indenter
            self.modulus = (10**-3.0)*(3.0/4.0)*(1-nu**2.0)*(rad**(-1.0/2.0))*(m**(3.0/2.0))
        elif self.indmodel == 1:
            # BILODEAU solution for pyramidal indenter
            self.modulus = (10**-3.0)*(2.0/1.4906)*(1-nu**2.0)*(tan_alpha**-1)*(m**2.0)
        else:
            self.modulus = np.NaN
#        return
                
    def fitPlot(self):
        plt.figure(1)
        plt.plot(self.indent,self.indentforce,self.indfit,self.forcefit,'ro')
        plt.ylabel('Force [nN]')
        plt.xlabel('Z-pos [um]')
        plt.show()
#        return
    
    def fitMonophasic(self):
        self.dataSeparate()
        self.dataNormalize()
        self.linearTransform()
        self.firstFit()
        self.slopeToModulus()
        return

#    def fitContactPoint(self):
""" check Chang YR, et al. Automated AFM Curve force curve analysis
            J Mech Behav Biomed Mater 2014
            http://www.ncbi.nlm.nih.gov/pubmed/24951927 """