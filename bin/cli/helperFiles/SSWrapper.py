from GlobalConstants import searchVarNamesInOrder, fixedParamDict
from CBOptProgressPlot import CBOptProgressPlot
from shared import savedParametersFile
from StringIndent import StringIndent
from crystalBall import CrystalBall
from Namespace import Namespace
from pprint import pformat
from TicToc import TT
from math import log
import traceback
import pickle
import time
import sys

def CBWrapper(dataFiles, predictVariables, modelFile, modelSidekicksFile, numJobs, parameters):
    '''
    This function wraps CrystalBall(), and returns a cost that takes into account how much time
    was spent training.  Models of equal quality that take less time are lower-cost.
    
     Inputs:
        dataFiles                   - a list of paths (strings) to input data files to process
        
        predictVariables            - a list of variable names from the input files
                                      to train to predict.  If empty, then not in 
                                      training mode.
                                      
        modelFile                   - The model file to read from or write to.
        
        modelSidekicksFile          - The file to store additional information corresponding with 
                                      the model file.  Ideally this information would go to the
                                      same file as the model, but keras limits how models are
                                      saved a bit.
                                      
        numJobs                     - How many concurrent jobs (threads or processes)
                                      to start.
    
        parameters                  - a Tuple of the parameter values we're currently using.
        
    Outputs:
        costIncludingTime           - A number that reflects the accuracy of the model and the 
                                      time the model required to train (lower is better).
    '''

    with TT('Running CBWrapper'):
        timeImportantance=0
        errorIndentLevel=6
        paramIndentLevel=2
        
        gAsDict=dict()
        
        assert len(parameters)==len(searchVarNamesInOrder), \
            'Different number of parameters than expected.'
        
        #Convert our parameters into a g that CrystalBall can use:
        
        #Iterate over the paramter names in the designated order:
        for i, pName in enumerate(searchVarNamesInOrder):
            #Add this parameter name and value to gAsDict:
            gAsDict.update({pName: parameters[i]})
        
        with TT("Fixed Parameters: \n" + StringIndent(pformat(fixedParamDict),paramIndentLevel)):
            pass
        
        with TT("Variable Parameters: \n" + StringIndent(pformat(gAsDict),paramIndentLevel)):
            pass
        
        
        #Also add our fixed variables:
        gAsDict.update(fixedParamDict)
        
        #Create our g out of it:
        g=Namespace(gAsDict)
        
        #Save it so that if there is an error we can run crystalBall and get the same parameters to 
        #inspect.
        pickle.dump(g, open(savedParametersFile, 'wb'))
        
        #Get our start time in seconds since the epoch.
        startTime=time.time()
        
        ##Use this instead of the stuff below if you want to break for pdb on errors:
        #(model, validationLoss)=CrystalBall(dataFiles, predictVariables, modelFile, \
                                            #modelSidekicksFile, numJobs, g, False)

        
        #with TT("Trying parameters: \n" + StringIndent(pformat(gAsDict),paramIndentLevel)):
        with TT("Training"):
            try: 
                #Call CrystalBall, and get the model and cost back.
                (model, modelSidekick, validationLoss, testing3D)=\
                    CrystalBall(dataFiles, predictVariables, modelFile, modelSidekicksFile, 
                                numJobs, g, False)
            except Exception as e:
                print(StringIndent('Error:  '+ str(e),errorIndentLevel), file=sys.stderr)
                print(StringIndent(traceback.format_exc(),errorIndentLevel+2), file=sys.stderr)
                
                #Assign a very high cost to this:
                validationLoss=float('Inf')
            
        #Get our end time in seconds since the epoch.
        endTime=time.time()
        
        elapsedSec=endTime-startTime
        
        costFromAccuracy=log(validationLoss+1,2)
        costFromTime=timeImportantance*log(elapsedSec+1,2)
        
        #Combine the cost returned by crystalBall and the elapsed time to make a new cost.
        compositeCost=costFromAccuracy+costFromTime
        
        print('CBWrapper: compositeCost: %f\tcostFromAccuracy: %f\tcostFromTime: %f' % \
            (compositeCost, costFromAccuracy, costFromTime))

        #If that new cost is the lowest we've seen so far, save the model in memory for cbOptimize to 
        #use when we're done:
        if compositeCost < CBWrapper.bestCompositeCost:
            with TT('Best model so far.  Saving'):
                CBWrapper.bestCompositeCost=compositeCost
                CBWrapper.bestModel=model
                CBWrapper.bestG=g
                CBWrapper.bestModelSidekicks=modelSidekick
                CBWrapper.bestTesting3D=testing3D
                
                #Save our best g to savedParametersFile so if we stop early we don't lose everything.
                pickle.dump(CBWrapper.bestG, open(savedParametersFile, 'wb'))
                
                #We could also save the model, but that might take a while (they can be huge).
                        
        #Save some data for plotting:
        CBWrapper.compositeCosts.append(compositeCost)
        CBWrapper.costsFromAccuracy.append(costFromAccuracy)
        CBWrapper.costsFromTime.append(costFromTime)
       
        #Plot them:
        CBOptProgressPlot(CBWrapper.compositeCosts, 
                          CBWrapper.costsFromAccuracy, 
                          CBWrapper.costsFromTime)
                    
    return compositeCost

#Some variables we'll be using to keep track of the best:
CBWrapper.bestCompositeCost=float('Inf')
#We check to see if this is None as a way if checking if we've run at least once.
CBWrapper.bestModel=None

#Some data for plotting as we go:
CBWrapper.compositeCosts=[]
CBWrapper.costsFromAccuracy=[]
CBWrapper.costsFromTime=[]
