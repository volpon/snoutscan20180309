from shared import savedParametersFile
from Namespace import Namespace        
from pprint import pformat
from TicToc import tt
import pickle
import os


def GCExtract(gc):
    '''
    This function takes the gc list of tuples and creates g and our searchSpace.
    
    Inputs:
        gc                  - a list of tuples.  Each tuple has these elements:
            parameterName       - The parameter name
            distributionFn      - The function from hyperopt.hp that specifies the distribution.
            distributionFnArgs  - The arguments to that function, in a tuple, skipping the label.
            fixedValue          - The fixed value to use if varry=1:
            varry=1 (optional)  - If we should let this variable varry (1) or stay fixed(0).
                                  
    Outputs:
        g                       - a Namespace() object representing name.value pairs that are 
                                  loaded or created from the "fixedValue" if no saved values exist 
                                  yet.
                                  
        searchVarNamesInOrder   - This is a list of parameterNames that are not fixed, in the order
                                  in which they're defined in the search space.
                                  
        fixedParamDict          - This is a dictionary of variables that are fixed (names:values).
                                  
        searchSpace             - a valid hyperopt search space for each non-fixed parameter, 
                                  as defined by: https://github.com/hyperopt/hyperopt/wiki/FMin
    '''
    #Note: g stands for "global constants".  Elements can be retrieved with g.<name>
    
    with tt.TT('Loading parameters'):
        #If a saved parameters file exists:
        if os.access(savedParametersFile, os.R_OK):
            
            #Load it.
            g=pickle.load(open(savedParametersFile, 'rb'))
                
            tt.print('Saved parameters found: \n%s\n' % pformat(g.__dict__))
        else:
            with tt.TT('No saved parameters found.  Using defaults.'):
                #Make g from the fixedValues (just a backup.)
                
                #the dictionary is :{parameterName: fixedValue, ...}
                gcAsDict={ c[0] : c[3] for c in gc }
    
                # Make g from gc's fixedValues:
                g=Namespace(gcAsDict)

    # Make the searchSpace from gc:
    searchSpace=[]
    
    searchVarNamesInOrder=[]
    
    fixedParamDict=dict()
    
    #For each tuple in our gc list:
    for c in gc:

        #Distribute our values:
        if len(c)==5:
            (name, distFn, distFnArgs, fixedValue, varry) = c
        elif len(c)==4:
            (name, distFn, distFnArgs, fixedValue) = c
            varry=1
        else:
            assert 0, 'Incorrect number of values in a gc element.'

        #Add it to the search space if it's not a "fixed value'.
        if varry:
            
            #Add this to a list we use to keep track of our order:
            searchVarNamesInOrder.append(name)
            
            #Add the corresponding distFn to our searchSpace:
            searchSpace.append(distFn(name, *distFnArgs))
        else:
            #Update our fixedParamDict:
            fixedParamDict.update({name: fixedValue})

    return (g, searchVarNamesInOrder, fixedParamDict, searchSpace)

