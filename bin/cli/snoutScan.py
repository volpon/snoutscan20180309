#!/.condaUser/.anaconda3/envs/snoutScan/bin/python3 
import sys,os; sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                            "helperFiles"));

#Also add up a diretory:
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),".."));

from main.api.matcher import find_best_match
from collections import OrderedDict
from FriendMake import FriendMake
from ArgsParse import ArgsParse
from TicToc import TT
import numpy as np
import sys
import cv2
import os
import pandas as pd

def SSMatchAll(friendDirectories, indexDefinition, displayImages=True):
    '''
    This function matches each of the friend images with each of the other friend images and 
    
    
    Inputs:
        friendDirectories      - A list of strings giving paths to the directories that hold our
                                images of each dog we want to analyze.  The directory names
                                are the names of the dogs.
                                
        indexDefinition        - A string representing the faiss index setup to use, or ''
                                 or None to represent "use the default"
        
        displayImages          - Says if we should display images for debugging purposes.
                                          
    Outputs:
    
        dogNames               - A list of unique dog names, corresponding to each of the rows and
                                 collumns of the confusionMatrixData.
    
        confusionMatrixData        - A confusion matrix, with each position (i,j) saying how many 
                                 images that were of friendDirectories[i], were recognized as being 
                                 of friend friendDirectories[j] instead. 
                                 (Pandas array, of size (numDogNames x numDogNames), with the 
                                 dog names as row and column labels)
    '''
    
    #Our list of friends:
    friends=[]
    
    #We only use the keys, not the values.  This is essentially an OrderedSet
    dogNamesOD=OrderedDict()
    
    ###########
    # Load our images, as one friend per image:
    ###########
    
    with TT('Loading images'):
        #For each directory:
        for friendDir in friendDirectories:
            #Extract the dog name:
            dogName=os.path.basename(friendDir)
            
            #Add our dogName
            dogNamesOD[dogName]=None

            with TT('Loading images for %s' % dogName):
                #Get the files in that directory:
                (root, dirs, files)= next(os.walk(friendDir))
                
                assert len(files)>1, 'Must have at least 2 pictures of every dog.'
                
                #For each file in the directory:
                for thisFile in files:
                    with TT('Loading %s' % thisFile):
                        
                        imgFilePath=os.path.join(root,thisFile)
                        
                        #Load image.
                        img=cv2.imread(imgFilePath)
                        
                        #Create a Friend object from it with the dog name connected to it.
                        friend=FriendMake(dogName, imgFilePath, img)
                        
                        #Add it to a list of friends.
                        friends.append(friend)
    
   
    numFriends=len(friends)
    
    #Get a list of our dogNames:
    dogNames=list(dogNamesOD.keys())
    
    numDogNames=len(dogNames)
    
    # Initialize our confusionMatrixData:
    confusionMatrixData=np.zeros((numDogNames, numDogNames))
    
    #Initialize our matcher as None so we build it on the first use:
    matcher=None
        
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
                best_db_id, best_match_score, best_index, matcher= \
                    find_best_match(subjectImgBinary, subjectImgType, friends, 
                                    indexDefinition, fIdsExcluded, matcher)
                
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
                print('      %s:\t%s (%s) => %s (%s):\t%i' %(
                               str(dogName == matchedDogName),
                               actualDogFile, dogName, matchedDogFile, matchedDogName, 
                               best_match_score), 
                            file=sys.stderr)
    
    #Make a pandas array that bundles the dog names and confusion matrix together for display:
    
    confusionMatrix=pd.DataFrame(data=confusionMatrixData, index=dogNames, columns=dogNames,
                                 dtype=int)
    
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
    
    with TT('Running SSMatchAll'):
        confusionMatrix=SSMatchAll(args.friendDirectories, args.indexDefinition, False, )
        
    numDogNames,_=confusionMatrix.shape
    
    print('Confusion Matrix:')
    print('=================')
    print('')
    print('Actual:  Matched with:')
    print(confusionMatrix)
    
    #Sum the diagonal
    numCorrect=np.trace(confusionMatrix)
    numTried=np.sum(np.sum(confusionMatrix))
    
    percentCorrect=numCorrect/numTried
    
    print('\n')
    print('Proportion of subject images correctly matched: %0.2f' % percentCorrect)
    
    