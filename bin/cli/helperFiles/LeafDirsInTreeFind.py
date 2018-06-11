#Make python 2 and 3 compliant so that ArgsParseOptimize (written in python2 so it can be used with 
# MOE) can use it:
import os

def LeafDirsInTreeFind(inputRootDirs):
    '''This function finds all directories that do not have subdirectories in a set of 
    directory tree roots .

    Input:
        inputRootDirs         - A list of directories.
                                
    Output:
        a list of strings showing the path to all of the matching directories.
    '''

    outDirList=[];
        
    #import pdb; pdb.set_trace();
    
    for inputRoot in inputRootDirs:            
        #Walk the directory tree:
        for dirPath, subdirList, fileList in os.walk(inputRoot, followlinks=True):
            
            #print('dirPath:', dirPath, '\tsubdirList:', subdirList, '\tfileList:', fileList)
            
            #If we found a directory with no subdirectories, add it:
            if len(subdirList)==0:
                outDirList.append(dirPath);

    #print('outDirList:', outDirList);

    return outDirList