import multiprocessing
import multiprocessing.dummy as mpThreadding
from functools import wraps
from copy import deepcopy
from io import StringIO
from time import sleep
import random
import pickle
import sys
import os

#Only import if it's not called as a command line tool.  Otherwise import when calling.
if __name__=="__main__":
    #Import a path to the TicToc module:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'..', "..", 'main', 'api'));                                                      

from TicToc import tt as ttDefault

def TTMap(functionToRun, collectionOfInputs, tt, concurrency='multiprocessing', numJobs=None):
    '''
    This function runs the functionToRun with each entry of collectionOfInputs, in parallel,
    in such a way so that their TT output doesn't get garbled with eachother.
    
    Inputs:
        functionToRun         - The function to run.  Must be threadsafe, and must accept an 
                                argument as the last argument, named tt, that specifies which  
                                ticToc instance to use.
        collectionOfInputs    - A collection of tuples of the inputs for each call to the function, 
                                excluding the tt argument.
        tt                    - a specific ticToc instance to start with.  If None, use the global
                                one.
        concurrency           - A string of either 'multiprocessing' or 'threading', representing
                                which type of parallelization to use.  Threadding is really only
                                useful for code that releases the Global Interpreter Lock.
        numJobs               - How many parallel processes to start.  None= ask the system for how 
                                many cpus it sees and use that many processes.
                                
    Outputs:
        resultsList           - a list of whatever each run of the function output.  One entry per 
                                entry in collectionOfInputs.
    '''
    
    if concurrency=='multiprocessing':
        mp=multiprocessing
    elif concurrency=='threading':
        mp=mpThreadding
    else:
        assert False, 'Unexpected concurrency argument: %s' % concurrency      
    
    #Make our pool:
    pool=mp.Pool(numJobs)
    
    #Holds the results of all of our async calls:
    asyncResultsList=[]
    
    #Iterate over all of the inputs we have:
    for inputs in collectionOfInputs:
        
        wrappedFunction=_TTStringIOWrap(functionToRun, tt)
        
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
    to stderr all at once.
    '''
    #Extract myStderr:
    outString, _ = result
    
    #Print it:
    print(outString, file=sys.stderr)
   
class _TTStringIOWrap(object):
    '''
    This decorator redirects all TT() used in the functionToRun to use a StringIO temporarily and
    then ouput anything written to the StringIO as an additional string output at the beginning 
    of the output list.
    '''
    
    def __init__(self, functionToWrap, tt):
        self.functionToWrap=functionToWrap
        self.tt=tt
            
    def __call__(self, *args, **kwargs):
        #Make a stringIO:
        myStderr=StringIO()
        
        #Make a special copy of the TT class and edit that one:
        ticTocNew=deepcopy(self.tt)
        
        #Manually copy the list in the class - the deep copy did not seem to do it:
        ticTocNew.startTimesForTictoc=ticTocNew.startTimesForTictoc[:]
        
        #print('deep copy worked:', self.tt.startTimesForTictoc is not ticTocNew.startTimesForTictoc, file=sys.stderr)
        #print('ids:', id(self.tt.startTimesForTictoc), id(ticTocNew.startTimesForTictoc), file=sys.stderr)
            
        #Change the outFile for this copy:
        ticTocNew.outFile=myStderr
        
        result=self.functionToWrap(*args, tt=ticTocNew, **kwargs,)
        
        outString=myStderr.getvalue()
        
        #Get rid of the last \n, if we have one, so we can print it with the endl:
        if len(outString)>1 and outString[-1]=='\n':
            outString=outString[0:-1]
        
        return outString, result
    
def _testFunction(n, tt):
    
    with tt.TT('Inside function'):
        with tt.TT('Calculating something'):
            sleep(random.random())
    return (n+0,n+1,n+2,n+3)
        
if __name__=="__main__":
    
    inputs=[(i,) for i in range(5) ]
    
    concurrency='threading'
    concurrency='multiprocessing'
    
    for concurrency in ('multiprocessing', 'threading'):
        with ttDefault.TT('Running _testFunction in parallel using: concurrency=%s' % concurrency):
            print(TTMap(_testFunction, inputs, ttDefault, concurrency))
        
     

    
    