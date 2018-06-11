from main.api.matcher import find_best_match

def FriendMatch(matcherInfo, friend, friendNum, g, tt):
    '''
    This function takes matcherInfo and finds the best match of a certain friend, 
    with a certain friendNum in the friends list that the index was trained on.
    
    Inputs:
        matcherInfo     - A tuple including a matcher and some other internal variables that can be
                          re-used between calls if friends and matcerh_info stay the same 
                          to save computations.
        friend          - The friend to search for.
        friendNum       - The index into the friends object that the matcher index was trained on
                          that represents where the friend object is.
        g               - global constants.
        tt              - Which TicToc instance to use.
        
    Outputs:
        friend          - the friend we're matching.  For convenience.
        best_index      - the index to the friends[] list of where the best matching friend is.
        percentOfSubjectFeaturesMatched
                        - A quality metric for the match.  0-1.  It's the percentage of the subject
                          image features that are matched with the friend image.
    '''
    
    with tt.TT('Finding matches for %s' % friend.breed):
                
        #This is a list of friendIds to not consider as a candidate for "best friend" - 
        #basically, exclude the current image so we don't match to it:
        fIdsExcluded=[friendNum]
        
        subjectImgBinary,subjectImgType=friend.photo.get_binary()
        
        #Find the other friend that matches this friend best:
        best_db_id, percentOfSubjectFeaturesMatched, best_index, matcherInfo= \
            find_best_match(subjectImgBinary, subjectImgType, None, g,
                            None, fIdsExcluded, matcherInfo, tt)
            
        return (friend, best_index, percentOfSubjectFeaturesMatched)