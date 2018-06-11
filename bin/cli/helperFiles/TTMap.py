import multiprocessing as mp
from functools import wraps
from copy import deepcopy
from io import StringIO
import sys
import os
import pickle

#Only import if it's not called as a command line tool.  Otherwise import when calling.
if __name__=="__main__":
    #Import a path to the TicToc module:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'..', "..", 'main', 'api'));                                                      

from TicToc import ticTockGlobalInstance

def TTMap(functionToRun, collectionOfInputs, numJobs=None, ticToc=None):
    '''
    This function runs the functionToRun with each entry of collectionOfInputs, in parallel,
    in such a way so that their TT output doesn't get garbled with eachother.
    
    Inputs:
        functionToRun         - The function to run.  Must be threadsafe, and must accept an argument
                                as the last argument, named ticToc, that specifies which ticToc 
                                instance to use.
        collectionOfInputs    - A collection of tuples of the inputs for each call to the function.
        numJobs               - How many parallel processes to start.  None= ask the system for how 
                                many cpus it sees and use that many processes.
        ticToc                - a specific ticToc instance to start with.  If None, use the global
                                one.
                                
    Outputs:
        resultsList           - a list of whatever each run of the function output.  One entry per 
                                entry in collectionOfInputs.
    '''
    
    #Make sure we have a ticToc to use:
    if ticToc is None:
        ticToc=ticTockGlobalInstance
    
    #Make our pool:
    pool=mp.Pool(numJobs)
    
    #Holds the results of all of our async calls:
    asyncResultsList=[]
    
    #Iterate over all of the inputs we have:
    for inputs in collectionOfInputs:
        
        wrappedFunction=_TTStringIOWrap(functionToRun, ticToc)
        
        asyncResult=pool.apply_async(func=wrappedFunction, args=inputs, 
                                            callback=_WorkerResultsProcess)
        
        ##For testing:
        #wrappedFunction(*inputs)
        
        #Get the result (not the result of the function call, but the result of the async call)
        asyncResultsList.append(asyncResult)
        
    pool.close()
    pool.join()

    resultList=[]
    
    #Get the results from the asyncResultList, ignoring the myStderr result:
    for asyncResult in asyncResultsList:
        myStderr, results=asyncResult.get() 
        resultList.append(results)
    
    return resultList
    
    
    
def _WorkerResultsProcess(result):
    '''
    This function writes whatever was written to stderr through TT during the worker thread
    to stdout all at once.
    '''
    #Extract myStderr:
    outString, _ = result
    
    #Print it:
    print(outString, file=sys.stderr, end='')
   
class _TTStringIOWrap(object):
    '''
    This decorator redirects all TT() used in the functionToRun to use a StringIO temporarily and
    then ouput anything written to the StringIO as an additional string output at the beginning 
    of the output list.
    '''
    
    def __init__(self, functionToWrap, ticToc):
        self.functionToWrap=functionToWrap
        self.ticToc=ticToc
            
    def __call__(self, *args, **kwargs):
        #Make a stringIO:
        myStderr=StringIO()
        
        #Make a special copy of the TT class and edit that one:
        ticTocNew=deepcopy(self.ticToc)
            
        #Change the outFile for this copy:
        ticTocNew.outFile=myStderr
        
        result=self.functionToWrap(*args, ticToc=ticTocNew, **kwargs,)
        
        outString=myStderr.getvalue()
        
        return outString, result
    
def _testFunction(n, ticToc):
    
    with ticToc.TT('Inside function'):
        pass
    return (n+0,n+1,n+2,n+3)
        
if __name__=="__main__":
    
    inputs=[(1,),(2,),(3,)]
    
    print(TTMap(_testFunction, inputs))
        
     

    
    