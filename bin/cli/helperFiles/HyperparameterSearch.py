#Add the api directory to our path:
import sys,os; sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                            '..', '..', 'main', 'api'));

from shared import savedParametersFile
from GlobalConstants import searchSpace
from StringIndent import StringIndent
from SSWrapper import SSWrapper
from hyperopt import fmin, tpe
from pprint import pformat
from TicToc import TT
import pickle

#How many trainings we want to do:
numIterations=1000
    
def HyperparameterSearch(friendDirectories, indexDefinition):
    '''
    This function performs a hyperparameter search on the paramters defined in GlobalConstants.py
    to optimize an objective function output by SSWrapper.
    
    
    Inputs:
        friendDirectories      - A list of strings giving paths to the directories that hold our
                                images of each dog we want to analyze.  The directory names
                                are the names of the dogs.
                                
        indexDefinition        - A string representing the faiss index setup to use, or ''
                                 or None to represent "use the default"
    '''
    
    assert len(searchSpace)>0, 'All variables are fixed.  There\'s no point in running this.'
    
    try:
        with TT('Searching for optimal hyper-parameters'):
            #Do the search:
            bestArgs=fmin(  fn=lambda parameters: SSWrapper(friendDirectories, indexDefinition, 
                                                            parameters),
                            space=searchSpace,
                            algo=tpe.suggest,
                            max_evals=numIterations)

    #Ignore KeyboardInterrupts:
    except KeyboardInterrupt:
        with TT('KeyboardInterrupt received.  Exiting early.'):
            pass

    #Always do this cleanup, even if we run into an error or do a ctrl-C
    finally:
        #If we ran at least once and have a "best model"
        if SSWrapper.bestG != None:
            with TT("Saving Best Parameters, which had compositeCost=%f: \n" \
                        % SSWrapper.bestCompositeCost \
                            + StringIndent(pformat(SSWrapper.bestG.__dict__),2)):
                
                #Save our best g to savedParametersFile:
                pickle.dump(SSWrapper.bestG, open(savedParametersFile, 'wb'))
                
        else:
            with TT("No best parameters yet to save."):
                pass
            