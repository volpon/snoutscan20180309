#!/.condaUser/.anaconda3/envs/snoutScan/bin/python3 
import sys,os; sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                            "helperFiles"));

#Also add up a diretory so it can find main.
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),".."));

#Also add the path to main.api too:
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"..", 'main', 'api'));                                                      
                                            
from ResultsJudge import ResultsJudge
from SSMatchAll import SSMatchAll
from ArgsParse import ArgsParse
from GlobalConstants import g
import HyperparameterSearch
from TicToc import TicToc
import pandas as pd
import sys
import os

#If this is called as a program and not imported:
if __name__=="__main__":
    #Parse our command line options into a dictionary.
    args=ArgsParse()
    
    #Set some numpy options that let us print better:
    #np.set_printoptions(threshold=np.nan)  
    
    #Set some pandas options that let us print better:
    pd.set_option('display.height', 10000)
    pd.set_option('display.max_rows', 5000)
    pd.set_option('display.max_columns', 5000)
    pd.set_option('display.width', 10000)
    
    #Make a ticToc instance:
    tt=TicToc()
    TT=tt.TT
        
    if (args.optimizeHyperparameters):
        with TT('Running HyperParmeterSearch'):
            HyperparameterSearch.HyperparameterSearch(args.friendDirectories, args.indexDefinition,
                                                      tt)
        sys.exit()
    else:
        with TT('Running SSMatchAll'):
            confusionMatrix=SSMatchAll(args.friendDirectories, args.indexDefinition, g, tt, False,
                                       None)
            
    print('Confusion Matrix:')
    print('=================')
    print('')
    print('Actual:  Matched with:')
    print(confusionMatrix)
    
    percentCorrect=ResultsJudge(confusionMatrix)
    
    print('\n')
    print('Proportion of subject images correctly matched: %0.2f' % percentCorrect)
    
    