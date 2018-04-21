#!/usr/bin/python3
import sys,os; sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"helperFiles"));

from ArgsParse import ArgsParse
from TicToc import TT
import sys
import os

##Prevent tensorflow warnings from showing:
#os.environ['TF_CPP_MIN_LOG_LEVEL']='2'


def Fun():
    '''
    This function ....
    
    Inputs:
        dauDataDirectories      - A list of strings giving paths to the directories that hold our
                                  dauCapture data for each of the sports cards we want to analyze.
                                  
        train                   - Boolean.  Says if we should be in training mode or not 
                                  (just predictions).
        
        numJobs                 - How many CPU processes we can start in parallel to do work 
                                  concurrently.
        
    Outputs:
        The predictions are written to stdout.
    '''
    
    with TT('Hello World'):
        pass
            
#If this is called as a program and not imported:
if __name__=="__main__":
    #Parse our command line options into a dictionary.
    args=ArgsParse()
    
    with TT('Running Fun'):
        Fun()
    