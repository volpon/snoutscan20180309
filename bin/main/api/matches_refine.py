def matches_refine(subjectKPPos, friendKPPos, matchedQueryTrainIds, matchDist):
    '''
    This function refines a set of matches to keep only the ones that are geomentrically consistent.
   
    Inputs:
        subjectKPPos            - A  numSubjectFeatures x 2 numpy array giving the (x,y) positions 
                                  of each subject feature.
                                  
        subjectKPPos            - A  numFriendFeatures x 2 numpy array giving the (x,y) positions 
                                  of each friend feature.
                                  
        matchedQueryTrainIds    - A numMatches x 2 np array of featureIds, where each row=(a,b)
                                  shows that the a_th feature of the subject image matched the
                                  b_th feature in the array of friend features.
                                  
        matchDist               - A np vector of length numMatches specifying the distance 
                                  metric fort each match.
                                  
    Outputs:
        matchedQueryTrainIds    - A subset of the rows of matchedQueryTrainIds, showing only the 
                                  geometrically self-consistent set of matches.
                                  
        matchDist               - The corresponding distances for these matches.
    '''
    
    return (matchedQueryTrainIds, matchDist)