import numpy as np
import cv2

def matches_refine(subjectKPPos, friendKPPos, friendIds, matchedQueryTrainIds, matchDist):
    '''
    This function refines a set of matches to keep only the ones that are geomentrically consistent.
   
    Inputs:
        subjectKPPos            - A  numSubjectFeatures x 2 numpy array giving the (x,y) positions 
                                  of each subject feature.
                                  
        friendKPPos             - A  numFriendFeatures x 2 numpy array giving the (x,y) positions 
                                  of each friend feature.
                                  
        friendIds               - A numpy array of length numFriendFeatures specifying the friendId
                                  of each row of friendKPPos.
                                  
        matchedQueryTrainIds    - A numMatches x 2 np array of featureIds, where each row=(a,b)
                                  shows that the a_th feature of the subject image matched the
                                  b_th feature in the array of friend features.
                                  
        matchDist               - A np vector of length numMatches specifying the distance 
                                  metric fort each match.
                                  
    Outputs:
        newMatchedQueryTrainIds    - A subset of the rows of matchedQueryTrainIds, showing only the 
                                  geometrically self-consistent set of matches.
                                  
        newMatchDist               - The corresponding distances for these matches.
    '''
    
    #Maximum allowed reprojection error to treat a point pair as an inlier:
    ransacReprojectThreshold=10
    
    #Maximum number of RANSAC iterations:
    ransacMaxIters=2000
    
    #A confidence threshold for the result:
    ransacConfidence=.995
    
    #These are the friendIds used in matchedQueryTraineIds:
    friendIdsMatched=np.unique(friendIds[matchedQueryTrainIds[:,1]])
    
    #Each row of this is subjectX, subjectY, friendX, friendY for a match in matchedQueryTrainIds:
    matchPositions=np.hstack((subjectKPPos[matchedQueryTrainIds[:,0],:],
                              friendKPPos [matchedQueryTrainIds[:,1],:]))

    #This is the friend id of every match:
    matchedFriendIds=friendIds[matchedQueryTrainIds[:,1]]
    
    #Our new values:
    newMatchedQueryTrainIdsList=[]
    newMatchDistList=[]
    
    #for each friend we matched a subject feature to:
    for friendId in friendIdsMatched:
        
        #Says if a given match is specifically for this friend:
        matchIsForThisFriend=matchedFriendIds==friendId

        #The subset of matches in matchedQueryTrainIds specifically for this friend:        
        matchesForFriend=matchedQueryTrainIds[matchIsForThisFriend,:]
        
        matchDistForFriend=matchDist[matchIsForThisFriend]

        #the matchPos for this friend:
        matchPosForFriend=matchPositions[matchIsForThisFriend,:]
        
        #Find the inlier set using RANSAC:
        #https://docs.opencv.org/3.4.1/d9/d0c/group__calib3d.html#ga4abc2ece9fab9398f2e560d53c8c9780
        H, mask=cv2.findHomography(matchPosForFriend[:,0:2], matchPosForFriend[:,2:4],
                                  cv2.RANSAC, ransacReprojectThreshold, None, ransacMaxIters, 
                                  ransacConfidence)
        
        #Convert to a boolean mask:
        maskBool=mask.ravel().astype(bool)
        
        #Add only the inliers
        newMatchedQueryTrainIdsList.append(matchesForFriend[maskBool,:])
        newMatchDistList.append(matchDistForFriend[maskBool])
        
    #Take care of a special case for when there aren't any matches:
    if len(newMatchedQueryTrainIdsList)==0:
        newMatchedQueryTrainIds=np.zeros((0,2), dtype='int')
        newMatchDist=np.zeros((0), dtype='float32')
    else:
        #Convert them to numpy arrays:
        newMatchedQueryTrainIds=np.vstack(newMatchedQueryTrainIdsList)
        newMatchDist=np.concatenate(newMatchDistList)
    
    return (newMatchedQueryTrainIds, newMatchDist)