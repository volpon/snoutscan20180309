from main.api.matcher import matcher_info_create
from collections import OrderedDict
from FriendMatch import FriendMatch
from FriendLoad import FriendLoad
from TTMap import TTMap
import pandas as pd
import numpy as np
import traceback
import pickle
import os

def SSMatchAll(friendDirectories, indexDefinition, g, tt, displayImages=True, mpQueue=None):
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
                                          
        tt                     - Which TicToc instance to use.
        
    Outputs:
    
        confusionMatrix        - A pandas array confusion matrix, labeled with dog names.
                                 Each position (i,j) says how many images that were of a given dog 
                                 name (i) were recognized as being of a dog name (j) instead. 
    '''
    
    TT=tt.TT
    
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
        
        with TT('Loading all images and computing features in parallel'):
#            #The sequential version (for debugging only):
#            friends=[]
#            for friendLoadArgs in friendLoadArgsList:
#                friends.append(FriendLoad(friendLoadArgs))
            
            friends=TTMap(FriendLoad, friendLoadArgsList, tt)
            
        #Get a list of our dogNames:
        dogNames=list(dogNamesOD.keys())
        
        numDogNames=len(dogNames)
        
        # Initialize our confusionMatrixData:
        confusionMatrixData=np.zeros((numDogNames, numDogNames))
        
        with TT('Creating friend index'):
            #Initialize our matcherInfo as None so we build it on the first use:
            matcherInfo=matcher_info_create(friends,indexDefinition, g, tt)
                
        with TT('Matching friends in parallel'):
            
            #Make a big list of all of the arguments we'll use for FriendMatch:
            friendMatchArgs=[(matcherInfo, friend, friendNum, g)
                                for (friendNum, friend) in enumerate(friends)]
            
            #The sequential version, for debugging:
            matchResults=[]
            for (matcherInfo, friend, friendNum, g) in friendMatchArgs:
                matchResults.append(FriendMatch(matcherInfo, friend, friendNum, g, tt))
                
            #matchResults=TTMap(FriendMatch, friendMatchArgs, tt, 'threading')
        
        with TT('Displaying results:'):
            #Output the results, and update our confusion matrix:
            for (friend, best_index, percentOfSubjectFeaturesMatched) in matchResults:
                
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
                tt.print('%s:\t%s (%s) => %s (%s):\t%f' %(
                            str(dogName == matchedDogName),
                            actualDogFile, dogName, matchedDogFile, matchedDogName, 
                            percentOfSubjectFeaturesMatched))
    
        #Make a pandas array that bundles the dog names and confusion matrix together for display:
        confusionMatrix=pd.DataFrame(data=confusionMatrixData, index=dogNames, columns=dogNames,
                                    dtype=int)
    except Exception as e:
        tt.print('Error in SSMatchAll:  '+ str(e))
        tt.print(traceback.format_exc())
        raise
                
    #Make sure this runs, even if there is an exception:
    finally:
        #If we have a queue, use it to output the confusionMatrix:
        if mpQueue is not None:
            mpQueue.put(confusionMatrix)
        
    return confusionMatrix