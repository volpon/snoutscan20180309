#!/.condaUser/.anaconda3/envs/snoutScan/bin/python3 
import sys,os; sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"helperFiles"));

#Also add up a diretory:
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),".."));

from main.api.matcher import find_best_match
from collections import OrderedDict
from FriendMake import FriendMake
from ArgsParse import ArgsParse
from TicToc import TT
from copy import copy
import numpy as np
import sys
import cv2
import os
import pandas as pd

def SSMatchAll(friendDirectories, displayImages=True):
    '''
    This function matches each of the friend images with each of the other friend images and 
    
    
    Inputs:
        friendDirectories      - A list of strings giving paths to the directories that hold our
                                images of each dog we want to analyze.  The directory names
                                are the names of the dogs.
        
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
                        image=cv2.imread(imgFilePath)
                        
                        #if displayImages:
                            ##Show the image (requires a display connection, which is complicated in docker)
                            #cv2.imshow(imgFilePath, image)
                        
                        #Create a Friend object from it with the dog name connected to it.
                        friend=FriendMake(dogName, imgFilePath, image)
                        
                        #Add it to a list of friends.
                        friends.append(friend)
    
    #if displayImages:
        ##Press any key to exit.
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()    
    
    numFriends=len(friends)
    
    #Get a list of our dogNames:
    dogNames=list(dogNamesOD.keys())
    
    numDogNames=len(dogNames)
    
    # Initialize our confusionMatrixData:
    confusionMatrixData=np.zeros((numDogNames, numDogNames))
        
    with TT('Matching'):
        #For each friend:
        for friendNum in range(numFriends):
            #Get the friend:
            friend=friends[friendNum]
            with TT('Finding matches for %s' % friend.breed):
                
                #Get a list of our ids:
                friendIdsNotThisOne=list(range(numFriends))
                
                #Make a copy of our friends
                friendsNotThisOne=copy(friends)
                
                #remove this one friend:
                del friendIdsNotThisOne[friendNum]
                del friendsNotThisOne[friendNum]
                
                friendImgBinary,friendImgType=friend.photo.get_binary()
                
                #Find the other friend that matches this friend best:
                best_db_id, best_match_score, best_index= \
                    find_best_match(friendImgBinary, friendImgType,friendsNotThisOne, displayImages)
                
                #Translate the id since we deleted one:
                actualBestId=friendIdsNotThisOne[best_index]
                
                #Get our names:
                actualDogName=friend.name
                matchedDogName=friends[actualBestId].name
                
                #Convert them to indicies to dogNames:
                actualDogNameIndex=dogNames.index(actualDogName)
                matchedDogNameIndex=dogNames.index(matchedDogName)
                
                #Increment that position in the confusion matrix:
                confusionMatrixData[actualDogNameIndex][matchedDogNameIndex]+=1
    
    #Make a pandas array that bundles the dog names and confusion matrix together for display:
    
    confusionMatrix=pd.DataFrame(data=confusionMatrixData, index=dogNames, columns=dogNames,
                                 dtype=int)
    
    return confusionMatrix
        
            
#If this is called as a program and not imported:
if __name__=="__main__":
    #Parse our command line options into a dictionary.
    args=ArgsParse()
    
    #Set some pandas options that let us print better:
    pd.set_option('display.height', 10000)
    pd.set_option('display.max_rows', 5000)
    pd.set_option('display.max_columns', 5000)
    pd.set_option('display.width', 10000)
    
    with TT('Running SSMatchAll'):
        confusionMatrix=SSMatchAll(args.friendDirectories, True)
    
    print('Confusion Matrix:')
    print('=================')
    print('')
    print('Actual:  Matched with:')
    print(confusionMatrix)
    