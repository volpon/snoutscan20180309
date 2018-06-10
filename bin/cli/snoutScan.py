#!/.condaUser/.anaconda3/envs/snoutScan/bin/python3 
import sys,os; sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                            "helperFiles"));

#Also add up a diretory so it can find main.
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),".."));

#Also add the path to main.api too:
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"..", 'main', 'api'));                                                      
                                            
from main.api.matcher import matcher_info_create, find_best_match
from ResultsJudge import ResultsJudge
from StringIndent import StringIndent
from collections import OrderedDict
from TicToc import TT as TTDefault
from FriendLoad import FriendLoad
from ArgsParse import ArgsParse
from GlobalConstants import g
import multiprocessing as mp
import HyperparameterSearch
from TicToc import TT
import pandas as pd
import numpy as np
import traceback
import sys
import cv2
import os


def SSMatchAll(friendDirectories, indexDefinition, g, displayImages=True, mpQueue=None, TT=None):
    '''
    This function matches each of the friend images of specific dogs with each of the other 
    friend images and outputs a confusion matrix showing how many of each dog was matched with
    each of the other dogs (many friend images per dog).
    
    
    Inputs:
        friendDirectories      - A list of strings giving paths to the directories that hold our
                                images of each dog we want to analyze.  The directory names
                                are the names of the dogs.
                                
        indexDefinition        - A string representing the faiss index setup to use, or ''
                                 or None to represent "use the default"
        
        displayImages          - Says if we should display images for debugging purposes.
        
        g                      - Our global constants.
        
        mpQueue                - This is an instance of multiprocessing.Queue() that we can use to
                                 return the output if this is run as a separate process instead of
                                 a function.
                                          
        TT                     - Which TT to use.
        
    Outputs:
    
        confusionMatrix        - A pandas array confusion matrix, labeled with dog names.
                                 Each position (i,j) says how many images that were of a given dog 
                                 name (i) were recognized as being of a dog name (j) instead. 
    '''
    
    if TT is None:
        TT=TTDefault
    
    errorIndentLevel=6
    
    #Get a default confusionMatrix in case we need to return something in case of an error:
    confusionMatrix=pd.DataFrame()
    
    try:
        #We only use the keys, not the values.  This is essentially an OrderedSet
        dogNamesOD=OrderedDict()
        
        ###########
        # Load our images, as one friend per image:
        ###########
        
        friendLoadArgsList=[]
        
        with TT('Finding images.'):
            #For each directory:
            for friendDir in friendDirectories:
                #Extract the dog name:
                dogName=os.path.basename(friendDir)
                
                #Add our dogName
                dogNamesOD[dogName]=None

                with TT('Finding images for %s' % dogName):
                    #Get the files in that directory:
                    (root, dirs, files)= next(os.walk(friendDir))
                    
                    assert len(files)>1, 'Must have at least 2 pictures of every dog.'
                    
                    #For each file in the directory:
                    for thisFile in files:
                        #with TT('Preparing to load %s' %K thisFile):
                        
                        #Get the full file path:
                        imgFilePath=os.path.join(root,thisFile)
                        
                        #Add this entry to our list:
                        friendLoadArgsList.append((dogName,imgFilePath,g))
                        
        with TT('These images found: \n%s' % str([imgFilePath for (dogName, imgFilePath, g) 
                                                  in friendLoadArgsList])):
            pass
        
        #Create a multiprocessing pool we can use to load images and compute features in parallel:
        friendLoadPool=mp.Pool()
    
        with TT('Loading all images and computing features in parallel'):
#            #The sequential version (for debugging only):
#            friends=[]
#            for friendLoadArgs in friendLoadArgsList:
#                friends.append(FriendLoad(friendLoadArgs))
            
            friends=friendLoadPool.map(FriendLoad, friendLoadArgsList)
            
        numFriends=len(friends)
        
        #Get a list of our dogNames:
        dogNames=list(dogNamesOD.keys())
        
        numDogNames=len(dogNames)
        
        # Initialize our confusionMatrixData:
        confusionMatrixData=np.zeros((numDogNames, numDogNames))
        
        with TT('Creating friend index'):
            #Initialize our matcherInfo as None so we build it on the first use:
            matcherInfo=matcher_info_create(friends,indexDefinition, g)
                
        with TT('Matching'):
            #For each friend:
            for friendNum in range(numFriends):
                #Get the friend:
                friend=friends[friendNum]
                with TT('Finding matches for %s' % friend.breed):
                    
                    #This is a list of friendIds to not consider as a candidate for "best friend" - 
                    #basically, exclude the current image so we don't match to it:
                    fIdsExcluded=[friendNum]
                    
                    subjectImgBinary,subjectImgType=friend.photo.get_binary()
                    
                    #Find the other friend that matches this friend best:
                    best_db_id, percentOfSubjectFeaturesMatched, best_index, matcherInfo= \
                        find_best_match(subjectImgBinary, subjectImgType, friends, g,
                                        indexDefinition, fIdsExcluded, matcherInfo)
                    
                    #Get our names:
                    dogName=friend.name
                    matchedDogName=friends[best_index].name
                    
                    #Get our file names:
                    actualDogFile=friend.breed
                    matchedDogFile=friends[best_index].breed
                    
                    #Convert them to indicies to dogNames:
                    dogNameIndex=dogNames.index(dogName)
                    matchedDogNameIndex=dogNames.index(matchedDogName)
                    
                    #Increment that position in the confusion matrix:
                    confusionMatrixData[dogNameIndex][matchedDogNameIndex]+=1
                    
                    #Print info about this best match:
                    print('      %s:\t%s (%s) => %s (%s):\t%f' %(
                                str(dogName == matchedDogName),
                                actualDogFile, dogName, matchedDogFile, matchedDogName, 
                                percentOfSubjectFeaturesMatched), 
                                file=sys.stderr)
        
        #Make a pandas array that bundles the dog names and confusion matrix together for display:
        confusionMatrix=pd.DataFrame(data=confusionMatrixData, index=dogNames, columns=dogNames,
                                    dtype=int)
    except Exception as e:
        print(StringIndent('Error in SSMatchAll:  '+ str(e),errorIndentLevel), file=sys.stderr)
        print(StringIndent(traceback.format_exc(),errorIndentLevel+2), file=sys.stderr)
        raise
                
    #Make sure this runs, even if there is an exception:
    finally:
        #If we have a queue, use it to output the confusionMatrix:
        if mpQueue is not None:
            mpQueue.put(confusionMatrix)
        
    return confusionMatrix
        
            
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
        
    if (args.optimizeHyperparameters):
        with TT('Running HyperParmeterSearch'):
            HyperparameterSearch.HyperparameterSearch(args.friendDirectories, args.indexDefinition)
        sys.exit()
    else:
        with TT('Running SSMatchAll'):
            confusionMatrix=SSMatchAll(args.friendDirectories, args.indexDefinition, g, False, )
            
    print('Confusion Matrix:')
    print('=================')
    print('')
    print('Actual:  Matched with:')
    print(confusionMatrix)
    
    percentCorrect=ResultsJudge(confusionMatrix)
    
    print('\n')
    print('Proportion of subject images correctly matched: %0.2f' % percentCorrect)
    
    