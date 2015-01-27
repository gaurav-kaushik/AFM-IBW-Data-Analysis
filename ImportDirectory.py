# -*- coding: utf-8 -*-
"""
Created on Sun Oct 12 23:47:32 2014

@author: Gaurav
"""

from os import walk, path

class ImportDirectory():
    
    def __init__(self,dirs=None):
        self.directory = dirs
        self.files = []
        self.filesonly = []
        if dirs:
            self.populateFilesFromDir()
        
    def __str__(self):
        return self.directory
        
    def addDirectory(self, dirs):
        self.directory = dirs
        self.populateFilesFromDir()
        
    def populateFilesFromDir(self):
        for root,dirs,files in walk(self.directory,topdown=True):
            for name in files:
                if name.endswith(".ibw"):
                    # path.join creates the slash inconsistency
                    #   so use path.normpath on windows to fix
                    filepath = path.join(root,name)
                    filepath = path.normpath(filepath)
                    self.files.append(filepath)
                    self.filesonly.append(name)   
        return
        
    def getDirectory(self):
        return self.directory        

    def getFilePaths(self):
#        if not self.files and self.directory:
#            self.populateFilesFromDir()
        return self.files
    
    def getFilesOnly(self):
        return self.filesonly   
        
    def hasDir(self):
        if self.directory:
            return True
        else:
            return False