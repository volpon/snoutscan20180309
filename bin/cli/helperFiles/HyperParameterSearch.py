import sys,os; sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"helperFiles"));
from PredictionsMakeAndEvaluate import PredictionsMakeAndEvaluate
from CBOptimizeArgsParse import CBOptimizeArgsParse
from shared import modelFile, modelSidekicksFile
from GlobalConstants import searchSpace
from StringIndent import StringIndent
from shared import crystalBallDir
from CBWrapper import CBWrapper
from hyperopt import fmin, tpe
from pprint import pformat
from TicToc import TT
import pickle
import glob
import os

#How many trainings we want to do:
numIterations=1000

from shared import savedParametersFile
    
def HyperParameterSearch(objectiveFn):
    '''
    This function performs a hyperparameter search on the paramters defined in GlobalConstants.py
    for the function objectiveFn, and outputs them.
    
    Inputs:
        objectiveFn     - This is the objective function that can be run with one no parameters.
                          It is likely going to be some sort of lambda function so that the other 
                          arguments needed can be passed at runtime.
    Outputs:
        bestGlobalConstants -
    '''
    
    assert len(searchSpace)>0, 'All variables are fixed.  There\'s no point in running this.'
    
    try:
        with TT('Searching for optimal hyper-parameters'):
            #Do the search:
            bestArgs=fmin(  fn=objectiveFn,
                            space=searchSpace,
                            algo=tpe.suggest,
                            max_evals=numIterations)

    #Ignore KeyboardInterrupts:
    except KeyboardInterrupt:
        with TT('CKeyboardInterrupt received.  Exiting early.'):
            pass

    #Always do this cleanup, even if we run into an error or do a ctrl-C
    finally:
        #If we ran at least once and have a "best model"
        if CBWrapper.bestModel != None:
            with TT("Saving Best Parameters, which had compositeCost=%f: \n" \
                        % CBWrapper.bestCompositeCost \
                            + StringIndent(pformat(CBWrapper.bestG.__dict__),2)):
                
                #Save our best g to savedParametersFile:
                pickle.dump(CBWrapper.bestG, open(savedParametersFile, 'wb'))
                
                model=CBWrapper.bestModel
                #Save the best model to our model file 
                #NOTE:  This needs to be the same format as in crystalBall.
                model.save(modelFile)
                
                #Break out some variables:
                (termsThatMatter, featuresScaler, groundtruthScaler)=CBWrapper.bestModelSidekicks
                
                #Save our modelSidekicks as well:
                #NOTE:  This needs to be the same format as in crystalBall.
                with open(modelSidekicksFile, 'wb') as modelSidekicksHandle:
                    pickle.dump(CBWrapper.bestModelSidekicks, modelSidekicksHandle)
                
            with TT('Making and evaluating predictions:'):
                #Get predictions for the testing set corresponding to the best model,
                #and evaluate them against the groundtruth.
                PredictionsMakeAndEvaluate(model, CBWrapper.bestTesting3D, groundtruthScaler)
        else:
            with TT("No best model yet to save."):
                pass
    
#If this is called as a program and not imported:
if __name__=="__main__":
    #Parse our command line options into a dictionary.
    args=CBOptimizeArgsParse()
    
    CBOptimize(args.dataFiles, args.predictVariables, args.num_jobs);