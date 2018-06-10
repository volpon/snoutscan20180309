import multiprocessing as mp
from functools import wraps
from copy import deepcopy
from io import StringIO
import sys
import os

#Only import if it's not called as a command line tool.  Otherwise import when calling.
if __name__=="__main__":
    #Import a path to the TicToc module:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'..', "..", 'main', 'api'));                                                      

from TicToc import TT, TicToc

def TTMap(functionToRun, collectionOfInputs, numJobs=None, timeout=None):
    '''
    This function runs the functionToRun with each entry of collectionOfInputs, in parallel,
    in such a way so that their TT output doesn't get garbled with eachother.
    
    Inputs:
        functionToRun         - The function to run.  Must be threadsafe, and must accept an argument
                                named tt that specifies which TT to use.
        collectionOfInputs    - A collection of tuples of the inputs for each call to the function.
        numJobs               - How many parallel processes to start.  None= ask the system for how 
                                many cpus it sees and use that many processes.
        timeout               - How long to let each function call go before we interrupt it.
                                
    Outputs:
        resultsList           - a list of whatever each run of the function output.  One entry per 
                                entry in collectionOfInputs.
    '''
    
    #Make our pool:
    pool=mp.Pool(numJobs)
    
    #Holds the results of all of our async calls:
    asyncResultsList=[]
    
    #Iterate over all of the inputs we have:
    for inputs in collectionOfInputs:
        
        wrappedFunction=_TTStringIOWrap(functionToRun)
        
        asyncResult=pool.apply_async(func=wrappedFunction, args=inputs, 
                                            callback=_WorkerResultsProcess)
        
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
    myStderr, _ = result
    
    #Print it:
    print(myStderr.getvalue(),file=sys.stderr, end='')
   
def _TTStringIOWrap(functionToWrap):
    '''
    This function redirects all TT() used in the functionToRun to use a StringIO temporarily and
    then ouput the StringIO as an additional output at the beginning of the output list.
    
    The output can be read with myStderr.getvalue()
    '''
    
    @wraps(functionToWrap)
    def decorated(*args, **kwargs):
        print('Before')
        
        #Make a stringIO:
        myStderr=StringIO()
        
        #Make a TicToc that uses it:
        t=TicToc(outFile=myStderr, labelEnding=', soThere!')
        
        #Make a special copy of the TT class and edit that one:
        TTNew=deepcopy(TT)
            
        #Set the ticTocInstance for this TT to t:
        TTNew.ticTocInstance=t
        
        result=functionToWrap(*args, tt=TTNew, **kwargs,)
        
        print('After')
        return myStderr, result
    
    return decorated

def _testFunction(TT, n):
    with TT('Inside function.'):
        pass
    return (n+1,n+2,n+3,n+4)
        
if __name__=="__main__":
    
    
    inputs=[(1,),(2,),(3,)]
    
    print(TTMap(_testFunction, inputs))
        
     

    
    