from GlobalConstants import searchVarNamesInOrder, fixedParamDict
from SSOptProgressPlot import SSOptProgressPlot
from shared import savedParametersFile
from ResultsJudge import ResultsJudge
from StringIndent import StringIndent
from snoutScan import SSMatchAll
from Namespace import Namespace
import multiprocessing as mp
from pprint import pformat
from random import random
from TicToc import ticTockGlobalInstance
from math import log
import traceback
import pickle
import time
import sys

def SSWrapper(friendDirectories, indexDefinition, parameters, ticToc=None):
    '''
    This function wraps SSMatchAll(), and returns a cost that takes into account how much time
    was spent training.  
    
     Inputs:
        friendDirectories      - A list of strings giving paths to the directories that hold our
                                images of each dog we want to analyze.  The directory names
                                are the names of the dogs.
                                
        indexDefinition        - A string representing the faiss index setup to use, or ''
                                 or None to represent "use the default"
                                 
        parameters             - a Tuple of the parameter values we're currently using.
        
        ticToc                 - an instance of TicToc to use for output, or None to use the 
                                 global one.
        
    Outputs:
        costIncludingTime           - A number that reflects the accuracy of the model and the 
                                      time the model required to train (lower is better).
    '''
    
    #Set our default ticToc if we don't have one:
    if ticToc is None:
        ticToc=ticTockGlobalInstance

    #Make a shorthand for ticToc.TT:
    TT=ticToc.TT

    with TT('Running SSWrapper'):
        timeImportantance=.01
        errorIndentLevel=8
        paramIndentLevel=8
        
        #How many seconds to let ssMatchRun before killing it:
        ssMatchTimeoutSec=1000
        
        gAsDict=dict()
        
        assert len(parameters)==len(searchVarNamesInOrder), \
            'Different number of parameters than expected.'
        
        #Convert our parameters into a g that SnoutScan can use:
        
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
        
        #Save it so that if there is an error we can run SSMatchAll and get the same parameters to 
        #inspect.
        pickle.dump(g, open(savedParametersFile, 'wb'))
        
        #Get our start time in seconds since the epoch.
        startTime=time.time()
        
        ##Use this instead of the stuff below if you want to break for pdb on errors:
        #confusionMatrix=SSMatchAll(friendDirectories, indexDefinition, g)
        #percentCorrect=ResultsJudge(confusionMatrix)
        
        #with TT("Trying parameters: \n" + StringIndent(pformat(gAsDict),paramIndentLevel)):
        with TT("Running the benchmark in a separate process:"):
            try: 
                #Call SSMatch, and get the model and cost back, but do it in it's own process.
                #This prevents segfaults or memory leaks in an opencv implementation from stoping
                #the optimization (which has happened already):
                
                #Set up a multiprocessing queue we can use to get the return value from SSMatchAll:
                ssQueue=mp.Queue()
                
                #Set up a Process object.
                ssProc= mp.Process( target=SSMatchAll, 
                                    args=(friendDirectories, indexDefinition, g, False, ssQueue),
                                    name='SSMatchAll')
                
                #Start the process running SSMatchAll.
                ssProc.start()
                
                #Get our confusion matrix from the queue.  Wait at most ssMatchTimeoutSec for it 
                # to be available.  Needs to be done before the join.
                confusionMatrix=ssQueue.get(block=True, timeout=ssMatchTimeoutSec)
                
                #At this point, it should be done.  Join it.  If it takes longer than 15 seconds, 
                #something is wrong.
                ssProc.join(timeout=15)
                
                #We return an empty pandas array if there was an exception.  If the child has an 
                #exceptuion raise one in the parent too to keep things consistent.
                assert confusionMatrix.empty == False, 'SSMatchAll exited with an exception.'
                
                #Calculate our percentCorrect from that:
                percentCorrect=ResultsJudge(confusionMatrix)

            except Exception as e:
                print(StringIndent('Error:  '+ str(e),errorIndentLevel), file=sys.stderr)
                print(StringIndent(traceback.format_exc(),errorIndentLevel+2), file=sys.stderr)
                #If we got an error there was 0 correct:
                percentCorrect=0
                raise
            
        #Get our end time in seconds since the epoch.
        endTime=time.time()
        
        elapsedSec=endTime-startTime
        
        #A log scale represents the fact that getting the first 10% accuracy is easier than getting
        #the last 10% accuracy:
        costFromAccuracy=log(2-percentCorrect,2)
        costFromTime=timeImportantance*log(elapsedSec+1,2)
        
        #Combine the cost returned by SSMatchAll and the elapsed time to make a new cost.
        compositeCost=costFromAccuracy+costFromTime
        
        print('SSWrapper: compositeCost: %f\tcostFromAccuracy: %f\tcostFromTime: %f' % \
            (compositeCost, costFromAccuracy, costFromTime))

        #If that new cost is the lowest we've seen so far, save the model in memory for cbOptimize to 
        #use when we're done:
        if compositeCost < SSWrapper.bestCompositeCost:
            with TT('Best model so far.  Saving'):
                SSWrapper.bestCompositeCost=compositeCost
                SSWrapper.bestG=g
                
                #Save our best g to savedParametersFile so if we stop early we don't lose everything.
                pickle.dump(SSWrapper.bestG, open(savedParametersFile, 'wb'))
                
                #We could also save the model, but that might take a while (they can be huge).
                        
        #Save some data for plotting:
        SSWrapper.compositeCosts.append(compositeCost)
        SSWrapper.costsFromAccuracy.append(costFromAccuracy)
        SSWrapper.costsFromTime.append(costFromTime)
       
        #Plot them:
        SSOptProgressPlot(SSWrapper.compositeCosts, 
                          SSWrapper.costsFromAccuracy, 
                          SSWrapper.costsFromTime)
                    
    return compositeCost

#Some variables we'll be using to keep track of the best:
SSWrapper.bestCompositeCost=float('Inf')
SSWrapper.bestG=None

#Some data for plotting as we go:
SSWrapper.compositeCosts=[]
SSWrapper.costsFromAccuracy=[]
SSWrapper.costsFromTime=[]
